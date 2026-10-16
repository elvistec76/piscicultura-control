/* Pure historical projection shared by the UI and Node verification. No I/O. */
((scope) => {
  'use strict';
  const finite = v => typeof v === 'number' && Number.isFinite(v) ? v : null;
  const at = (rows, t, key = 'time_s') => {
    let lo = 0, hi = rows.length;
    while (lo < hi) { const mid = (lo + hi) >>> 1; if (rows[mid][key] <= t) lo = mid + 1; else hi = mid; }
    return lo ? rows[lo - 1] : null;
  };
  function create(base, history) {
    const run = history.run, c = run.config;
    const samples = [...history.samples].sort((a,b) => a.time_s-b.time_s || a.sample_index-b.sample_index);
    const decisions = [...history.decisions].sort((a,b) => a.time_s-b.time_s || a.decision_index-b.decision_index);
    const events = [...history.events].sort((a,b) => a.time_s-b.time_s || a.event_seq-b.event_seq);
    const channels = [[0,1],[0,-1],[1,1],[2,1],[2,-1],[3,1],[4,1],[4,-1]];
    const grouped = base.actuators.map(a => history.actuator_records.filter(r => r.actuator_id === a.key).sort((a,b) => a.start_s-b.start_s));
    const sampleIndex = new Map(samples.map(s => [s.sample_index,s]));
    const duration = run.time_s;
    const times = [...new Set([0,duration,...samples.map(s=>s.time_s),...decisions.map(d=>d.time_s),...events.map(e=>e.time_s),...history.actuator_records.flatMap(a=>[a.start_s,a.end_s])])].filter(t=>t>=0&&t<=duration).sort((a,b)=>a-b);
    function project(requested) {
      const t = Math.max(0,Math.min(duration,finite(requested) ?? 0));
      const s = at(samples,t), d = at(decisions,t);
      // Hold a recorded exact state. A terminal partial state has its own time.
      const terminal = t === duration;
      const state = (terminal ? run.state : s ? s.x : c.x0).slice(0,5).map(finite);
      const stateTime = terminal ? duration : s ? s.time_s : 0;
      const activeAlarms = new Map();
      events.filter(e=>e.time_s<=t&&e.category==='alarm').forEach(e=>{
        const key=e.target+'|'+e.code;
        if(e.transition==='activation')activeAlarms.set(key,e);
        if(e.transition==='clear')activeAlarms.delete(key);
      });
      const actuators = base.actuators.map((a,i)=>{
        const row=at(grouped[i],t,'start_s');
        // [start,end), except the final endpoint which describes its last interval.
        const r=row && (t<row.end_s || (terminal&&t===row.end_s)) ? row : null;
        const raw=r?finite(r.command[channels[i][0]]):null;
        const effective=r?finite(r.mean_effective):null;
        return {...a,command:raw===null?null:Math.max(0,raw*channels[i][1]),availability:r?finite(r.availability):null,effective,active:effective!==null&&effective>0,
          reason:r?r.limit_reason:'SIN_INTERVALO',interval_s:r?[r.start_s,r.end_s]:null,record_index:r?r.record_index:null};
      });
      const intervals=actuators.filter(a=>a.interval_s).map(a=>a.interval_s);
      const input=d?sampleIndex.get(d.input_sample_index):null;
      // Never expose an input measurement from the future, even in damaged data.
      const controllerInput=input&&input.time_s<=d.time_s&&input.time_s<=t?input:null;
      const nextSample=d?(samples.find(row=>row.time_s>d.time_s&&row.time_s<=t)||null):null;
      const sensors=base.sensors.map((sensor,j)=>{
        let quality=s?s.qualities[j]:'MISSING', value=s?finite(s.values[j]):null;
        if(!['GOOD','MISSING','INVALID'].includes(quality)||quality==='GOOD'&&value===null)quality='INVALID';
        if(quality!=='GOOD')value=null;
        return {...sensor,exact:state[j],quality,value,diagnosis:s?s.diagnostics[j]:'SIN_MUESTRA'};
      });
      return {...base,state,state_time_s:stateTime,sample_time_s:s?s.time_s:null,selected_time_s:t,
        volume_m3:state[4]===null?null:base.geometry.area_m2*state[4],sensors,actuators,
        interval_s:intervals.length?intervals[0]:null,alarms:[...activeAlarms.values()],
        warnings:state[4]===null||state[4]<0||state[4]>base.geometry.height_m?['Nivel exacto fuera de la geometría o no finito; sin recorte.']:[],
        decision:d,controller_input:controllerInput,observed_sample:nextSample,
        events:events.filter(e=>e.time_s<=t),state_policy:stateTime===t?'Estado exacto registrado':'Estado exacto retenido, sin interpolación'};
    }
    // Guided stops refer exclusively to existing records; absent stages are reported.
    const guide=[{time_s:0,label:'1 · Estado inicial registrado'}];
    const perturbation=events.find(e=>e.category==='injection'&&e.transition==='activation');
    if(perturbation){
      guide.push({time_s:perturbation.time_s,label:'2 · Perturbación registrada: '+perturbation.code});
      const before=at(samples,perturbation.time_s);
      const measured=before?samples.find(s=>s.time_s>perturbation.time_s&&s.values.some((v,j)=>
        s.qualities[j]!==before.qualities[j] || (s.qualities[j]==='GOOD'&&before.qualities[j]==='GOOD'&&finite(v)!==null&&finite(before.values[j])!==null&&v!==before.values[j]))):null;
      if(measured)guide.push({time_s:measured.time_s,label:'3 · Cambio registrado en valores o calidad; sin atribuir causa'});
      const decision=decisions.find(d=>d.time_s>=(measured?measured.time_s:perturbation.time_s));
      if(decision){
        guide.push({time_s:decision.time_s,label:'4 · Decisión registrada del controlador'});
        const action=history.actuator_records.find(a=>a.record_index===decision.decision_index&&a.mean_effective>0);
        if(action)guide.push({time_s:action.start_s,label:'5 · Acción efectiva media registrada'});
        const after=samples.find(s=>s.time_s>decision.time_s);
        if(after)guide.push({time_s:after.time_s,label:'6 · Evolución posterior observada; sin atribución causal'});
      }
    }
    guide.push({time_s:duration,label:'7 · Gráficas y resultados del tramo almacenado'});
    return {project,times,duration,samples,decisions,events,guide,hasPerturbation:!!perturbation};
  }
  class Clock {
    constructor(duration){this.duration=duration;this.time=duration;this.elapsed=0;this.speed=60;this.playing=false;this.last=null;}
    play(){if(this.time>=this.duration)this.time=0;this.playing=this.duration>0;this.last=null;}
    pause(){this.playing=false;this.last=null;}
    seek(t){this.time=Math.max(0,Math.min(this.duration,t));this.last=null;}
    reset(){this.pause();this.time=0;this.elapsed=0;}
    tick(stamp,visible=true){
      if(!this.playing||!visible){this.last=null;return this.time;}
      if(this.last!==null){const dt=Math.max(0,(stamp-this.last)/1000);this.elapsed+=dt;this.time=Math.min(this.duration,this.time+dt*this.speed);}
      this.last=stamp;if(this.time>=this.duration)this.pause();return this.time;
    }
  }
  scope.AquaReplay={create,Clock};
})(globalThis);
