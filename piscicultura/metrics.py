"""Indicadores con origen y unidades; sin integrales ocultas sobre ausencias."""
import numpy as np
from .config import VARIABLES,UNITS,ACTIONS


def series_metrics(t,x,reference,bands,start=0.):
    t=np.asarray(t,dtype=float);x=np.asarray(x,dtype=float)
    if len(t)<2: return None
    duration=float(t[-1]-t[0]); dt=np.diff(t)
    error=np.abs(x-np.asarray(reference))
    iae=np.sum((error[1:]+error[:-1])*.5*dt[:,None],axis=0)
    inside=(x>=np.array(bands)[:,0]) & (x<=np.array(bands)[:,1])
    if x.shape[1]==5: inside[:,3]=x[:,3]<=bands[3][1]
    outside=np.sum((~inside[:-1])*dt[:,None],axis=0)
    recovery=[]
    for j in range(x.shape[1]):
        recovered=None
        for i in range(len(t)):
            if t[i]<start or not inside[i,j]: continue
            end=int(np.searchsorted(t,t[i]+1800))
            if end<len(t) and np.all(inside[i:end+1,j]): recovered=float(t[i]-start);break
        recovery.append(recovered)
    return dict(iae=iae.tolist(),outside_s=outside.tolist(),in_band_fraction=(1-outside/duration).tolist(),recovery_s=recovery,duration_s=duration)


def evaluate(run,samples,actions,end_s=None):
    c=run['config']; r=c['profile']['references'];bands=c['profile']['operating_bands']
    pairs=[(s['time_s'],s['x']) for s in samples]
    term=run['termination_state']
    if term and (not pairs or term['time_s']>pairs[-1][0]): pairs.append((term['time_s'],term['state'][:5]))
    if end_s is not None and pairs and end_s<pairs[-1][0]:
        times=np.array([p[0] for p in pairs]);values=np.array([p[1] for p in pairs]);endpoint=[float(np.interp(end_s,times,values[:,j])) for j in range(5)]
        pairs=[p for p in pairs if p[0]<end_s]+[(end_s,endpoint)]
    t=[p[0] for p in pairs];x=[p[1] for p in pairs]
    xm=series_metrics(t,x,r,bands) if len(t)>1 else None
    scales=[(bands[0][1]-bands[0][0])/2,(bands[1][1]-bands[1][0])/2,.5,20,.1]
    J=float(np.mean(np.array(xm['iae'])/(np.array(scales)*xm['duration_s']))) if xm and xm['duration_s']>0 else None
    window=None
    if t and t[-1]>=43200:
        idx=[i for i,ti in enumerate(t) if 14400<=ti<=43200]
        window=series_metrics(np.array(t)[idx],np.array(x)[idx],r,bands)
    valid=np.array([[v is not None for v in s['values']] for s in samples],dtype=bool)
    coverage=valid.mean(axis=0).tolist() if samples else [0]*5
    ym=[]
    for j in range(5):
        if samples and all(valid[:,j]) and end_s is None:
            result=series_metrics([s['time_s'] for s in samples],[[s['values'][j]] for s in samples],[r[j]],[bands[j]])
        else: result=None
        ym.append(result)
    p=c['parameters'];integrals=np.zeros(8);flows=dict(rain_m3=0.,leak_m3=0.,evaporation_m3=0.,exchange_m3=0.)
    for a in actions:
        duration=a['end_s']-a['start_s']
        if end_s is not None:
            # Comparación común de consumos solo usa intervalos completos; se declara cobertura.
            if a['end_s']>end_s: continue
        j=ACTIONS.index(a['actuator_id']);integrals[j]+=a['mean_effective']*duration
        if j==0:
            flows['rain_m3']+=(p['rain_base_m3_s']+a['disturbances']['rain'])*duration
            flows['leak_m3']+=(p['leak_base_m3_s']+a['disturbances']['leak'])*duration
            flows['evaporation_m3']+=p['evaporation_m3_s']*duration
            flows['exchange_m3']+=p['exchange_m3_s']*duration
    energy=float(np.dot(integrals,[p['heater_max_W'],p['cooler_max_W']/p['cooling_COP'],p['air_power_W'],0,0,p['filter_power_W'],p['inlet_power_W'],p['outlet_power_W']])/3.6e6)
    return dict(formula_version='M-AGUA-DEMO-1/section14-v1',origin='x',variables=VARIABLES,units=UNITS,interval_s=[t[0],t[-1]] if t else [],x=xm,J=J,window_4_12h=window,y=dict(coverage=coverage,per_variable=ym,rule='IAE solo con cobertura completa; sin interpolación de ausencias'),joint_recovery_s=max(xm['recovery_s']) if xm and all(v is not None for v in xm['recovery_s']) else None,usage=dict(inlet_m3=float(integrals[6]*p['inlet_max_m3_s']+flows['exchange_m3']),outlet_m3=float(integrals[7]*p['outlet_max_m3_s']+flows['exchange_m3']),ph_base_normalized_s=float(integrals[3]),ph_acid_normalized_s=float(integrals[4]),partial_energy_kWh=energy,**flows),common_endpoint_policy='x interpolado linealmente si necesario; consumos comunes solo intervalos completos' if end_s is not None else 'termination_state irregular incluido solo en x')
