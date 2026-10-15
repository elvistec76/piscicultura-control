"""Orquestación provisional pura: publicación únicamente después de COMMIT."""
from copy import deepcopy
from dataclasses import dataclass,field,asdict
import numpy as np
from .config import VARIABLES,ACTIONS
from .control import decide
from .actuators import mean_actions,limit
from .model import integrate
from .scenarios import conditions
from .sensors import measure

@dataclass
class Runtime:
    state: np.ndarray
    time_s: float=0.
    k: int=0
    status: str='PREPARED'
    cause: str=''
    memory: list=field(default_factory=lambda:[0]*5)
    last_good: list=field(default_factory=lambda:[None]*5)
    frame: object=None
    event_active: set=field(default_factory=set)
    alarm_active: dict=field(default_factory=dict)
    event_seq: int=0
    termination_state: object=None

    def fork(self):
        new=Runtime(self.state.copy(),self.time_s,self.k,self.status,self.cause,self.memory.copy(),self.last_good.copy(),self.frame,self.event_active.copy(),self.alarm_active.copy(),self.event_seq,deepcopy(self.termination_state))
        return new


def initial(c): return Runtime(np.array(c['x0']+c['z0'],dtype=float))


def advance(runtime,c,noise):
    r=runtime.fork();r.status='RUNNING'
    batch=dict(samples=[],decisions=[],actions=[],events=[])
    def emit(t,category,target,severity,transition,code,data=None):
        batch['events'].append(dict(event_seq=r.event_seq,time_s=t,category=category,target=str(target),severity=severity,transition=transition,code=code,data=data or {}));r.event_seq+=1
    def sample(k,t):
        d,g,faults=conditions(c,t)
        active={i for i,e in enumerate(c['events']) if e['start_s']<=t<e['end_s']}
        for i in sorted(active-r.event_active): emit(t,'injection',c['events'][i]['target'],'AUDITORIA','activation',c['events'][i]['kind'],c['events'][i])
        for i in sorted(r.event_active-active): emit(t,'injection',c['events'][i]['target'],'AUDITORIA','clear',c['events'][i]['kind'],c['events'][i])
        r.event_active=active
        r.frame,r.last_good=measure(k,t,r.state[:5],noise[k],c,faults,r.last_good)
        batch['samples'].append(dict(sample_index=k,time_s=t,x=r.state[:5].tolist(),**{key:val for key,val in asdict(r.frame).items() if key not in ['index','time_s']}))
        for j in (1,3):
            if r.state[j]<0: emit(t,'audit',VARIABLES[j],'AUDITORIA','activation','RESIDUO_NUMERICO_NEGATIVO',{'value':float(r.state[j])})
        for j,q in enumerate(r.frame.qualities):
            val=r.frame.values[j]; bands=c['profile']['operating_bands'][j]; critical=c['profile']['critical_limits'][j]
            code=''
            if q!='GOOD': code='LECTURA_'+q
            elif val>critical[1] or (j!=3 and val<critical[0]): code='LIMITE_CRITICO'
            elif val>bands[1] or (j!=3 and val<bands[0]): code='FUERA_DE_BANDA'
            previous=r.alarm_active.get(j,'')
            if code!=previous:
                if previous: emit(t,'alarm',VARIABLES[j],'CRITICA' if previous!='FUERA_DE_BANDA' else 'AVISO','clear',previous,{'origin':'y'})
                if code: emit(t,'alarm',VARIABLES[j],'CRITICA' if code!='FUERA_DE_BANDA' else 'AVISO','activation',code,{'origin':'y','value':val})
                r.alarm_active[j]=code
        if c['strategy']=='closed' and any(q!='GOOD' for q in r.frame.qualities):
            r.status='FAILED';r.cause='LECTURA_REQUERIDA_INVALIDA'
            emit(t,'termination','run','CRITICA','activation',r.cause)
        return d,g
    if r.frame is None: sample(r.k,r.time_s)
    if r.status=='FAILED': return r,batch
    d,g,_=conditions(c,r.time_s)
    v,m,errors,reasons=decide(c['strategy'],c['profile']['references'],c['controller'],c['open_commands'],r.frame,r.memory)
    v,limited=limit(v)
    decision=dict(decision_index=r.k,time_s=r.time_s,strategy=c['strategy'],input_sample_index=r.frame.index,references=c['profile']['references'],errors=errors,commands=v.tolist(),reason_codes=reasons,limited=limited)
    batch['decisions'].append(decision);r.memory=m
    start=r.time_s; target=start+c['time']['control_interval_s'];z0=r.state[5:].copy()
    try:
        sol=integrate(start,r.state,target,v,g,d,c)
        r.state=sol.y[:,-1];r.time_s=float(sol.t[-1])
        if not sol.success or not np.isfinite(r.state).all():
            r.status='FAILED';r.cause='ERROR_NUMERICO: '+sol.message
        elif sol.status==1:
            r.status='FAILED';r.cause='CRUCE_DOMINIO'
        if r.status=='FAILED':
            r.termination_state=dict(time_s=r.time_s,state=r.state.tolist())
            emit(r.time_s,'termination','run','CRITICA','activation',r.cause,r.termination_state)
    except (ValueError,ArithmeticError,FloatingPointError) as exc:
        r.status='FAILED';r.cause='ERROR_NUMERICO: '+str(exc)
        emit(start,'termination','run','CRITICA','activation',r.cause)
    duration=r.time_s-start
    if duration>0:
        means=mean_actions(z0,v,duration,c['parameters']['actuator_tau_s'],g)
        for j,name in enumerate(ACTIONS):
            batch['actions'].append(dict(record_index=r.k,actuator_id=name,start_s=start,end_s=r.time_s,command=v.tolist(),z_initial=z0.tolist(),z_final=r.state[5:].tolist(),availability=float(g[j]),mean_effective=float(means[j]),limit_reason='INDISPONIBLE_O_REDUCIDA' if g[j]<1 else '',disturbances=d))
    if r.status!='FAILED':
        r.k+=1
        sample(r.k,r.time_s)
        if r.status!='FAILED' and r.time_s==c['time']['horizon_s']: r.status='COMPLETED'
    return r,batch
