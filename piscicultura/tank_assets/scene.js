/* Local renderer: consumes a snapshot, never sends commands or advances time. */
(() => {
  'use strict';
  let data = JSON.parse(document.getElementById('snapshot').textContent);
  const base = data;
  const replay = data.history ? AquaReplay.create(data, data.history) : null;
  const player = new AquaReplay.Clock(replay ? replay.duration : 0);
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  let refreshScene = () => {}, renderScene = () => {}, wakeScene = () => {};
  let quality = 'medium', disposed = false, chartsReady = false;
  const el = id => document.getElementById(id);
  const text = (id, value) => { el(id).textContent = value; };
  const num = (v, digits = 3) => v === null ? '—' : Number(v).toLocaleString('es', {maximumFractionDigits: digits});
  const pct = v => v === null ? '—' : v > 0 && v < .0001 ? '<0,01%' : num(v * 100, 2) + '%';
  const clock = t => t === null ? 'Sin muestra' : `${num(t, 3)} s · ${num(t / 3600, 4)} h`;
  const statuses = {PREPARED:'Preparada',RUNNING:'En ejecución',PAUSED:'Pausada',STOPPED:'Detenida',COMPLETED:'Completada',FAILED:'Fallida',INTERRUPTED:'Interrumpida'};
  const g = data.geometry, circular = g.shape === 'Circular';
  function updateDashboard() {
  ['sensors','actuators','alarms','decision-rows','event-rows','action-detail-rows'].forEach(id=>el(id).replaceChildren());
  text('run-badge', (statuses[data.status] || data.status).toUpperCase());
  if (data.status !== 'RUNNING') el('run-badge').classList.add(data.status === 'FAILED' ? 'failed' : 'still');
  text('shape-label', data.geometry.shape + ' industrial');
  text('profile', `${data.profile} · ${data.strategy === 'closed' ? 'Lazo cerrado' : 'Lazo abierto'} · ${data.run_id.slice(0, 10)}`);
  text('scenario',base.history?'Escenario '+base.history.run.config.scenario:'Escenario: consultar configuración congelada');
  text('state-time', clock(data.state_time_s));
  text('sample-time', 'Última muestra y: ' + clock(data.sample_time_s));
  const symbols = ['♨','O₂','pH','◌','↕'];
  data.sensors.forEach((s, j) => {
    const card = document.createElement('article'); card.className = 'sensor';
    const title = document.createElement('div'); title.className = 'sensor-top';
    const label = document.createElement('span'); label.textContent = s.label;
    const icon = document.createElement('span'); icon.className = 'sensor-icon'; icon.textContent = symbols[j];
    title.append(label, icon);
    const value = document.createElement('div'); value.className = 'sensor-value';
    value.textContent = s.value === null ? 'Sin lectura' : num(s.value, 4);
    const unit = document.createElement('small'); unit.textContent = s.unit; value.append(unit);
    const quality = document.createElement('div'); quality.className = 'sensor-quality' + (s.quality !== 'GOOD' ? ' bad' : '');
    const qualityText = document.createElement('span'); qualityText.textContent = {GOOD:'● Válida',MISSING:'○ Ausente',INVALID:'! Inválida'}[s.quality];
    const ref = document.createElement('span'); ref.textContent = 'Ref. ' + num(s.reference);
    quality.append(qualityText, ref); quality.title = s.diagnosis;
    card.append(title, value, quality);
    el('sensors').append(card);
  });
  text('water-label', `NIVEL EXACTO h = ${num(data.state[4], 5)} m`);
  text('volume-label', `V = A × h = ${num(data.volume_m3, 5)} m³`);
  text('dimensions', circular ? `A ${num(g.area_m2)} m² · r ${num(g.radius_m)} m · H ${num(g.height_m)} m` : `A ${num(g.area_m2)} m² · ${num(g.length_m)} × ${num(g.width_m)} m · H ${num(g.height_m)} m`);
  text('exact-caption', `t = ${num(data.state_time_s)} s · ${data.state_policy || 'Estado exacto registrado'}`);
  text('interval', data.interval_s ? `Media registrada en [${num(data.interval_s[0])}, ${num(data.interval_s[1])}) s${data.selected_time_s === player.duration ? ' · extremo final' : ''}` : 'Sin intervalo confirmado. No se infiere actividad.');
  data.actuators.forEach(a => {
    const row = document.createElement('div'); row.className = 'actuator-row' + (a.active ? ' active' : '');
    const name = document.createElement('span'); const dot = document.createElement('i'); name.append(dot, a.label); row.append(name);
    [a.command, a.availability, a.effective].forEach((v, i) => {
      const span = document.createElement('span'); span.textContent = i === 1 ? num(v, 3) : pct(v);
      if (i === 2) span.className = 'effective';
      if (i === 1 && v !== null && v < 1) span.className = 'unavailable'; row.append(span);
    });
    row.title = (a.reason || 'Registro confirmado') + (a.interval_s ? ` · [${a.interval_s.join(', ')}] s` : ''); el('actuators').append(row);
    const detail=document.createElement('tr');[a.label,a.record_index??'—',a.interval_s?`[${num(a.interval_s[0])}, ${num(a.interval_s[1])})`:'Sin intervalo',pct(a.command),num(a.availability),pct(a.effective),a.reason||'Sin limitación registrada'].forEach(v=>{const td=document.createElement('td');td.textContent=v;detail.append(td);});el('action-detail-rows').append(detail);
  });
  text('alarm-count', String(data.alarms.length));
  if (!data.alarms.length) { const p = document.createElement('div'); p.className = 'no-alarm'; p.textContent = data.sample_time_s === null ? '○ Aún no hay muestras para alarmas' : '✓ Sin alarmas activas registradas'; el('alarms').append(p); }
  data.alarms.forEach(a => {
    const row = document.createElement('div'); row.className = 'alarm' + (a.severity === 'CRITICA' ? ' critical' : '');
    const sensor = data.sensors.find(s => s.key === a.target);
    row.textContent = `${sensor ? sensor.label : a.target}: ${a.code.replaceAll('_', ' ')}`;
    const time = document.createElement('small'); time.textContent = `Activada en t = ${num(a.time_s)} s · ${a.severity}`; row.append(time); el('alarms').append(row);
  });
  updateMotionLabel();
  text('warnings', [...data.warnings, data.cause ? 'Terminación: ' + data.cause : ''].filter(Boolean).join(' '));
  updateDecision();
  (data.events || []).slice(-100).forEach(e=>{
    const tr=document.createElement('tr');[num(e.time_s),e.category,e.target,e.transition,e.code].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.append(td);});el('event-rows').append(tr);
  });
  }
  function updateMotionLabel() {
    const ambient=el('ambient').checked&&!reducedMotion.matches;
    text('motion-label',ambient?'Modo ambiente · animación decorativa':'Animación decorativa desactivada');
    text('motion-caption','Peces, ondas y reflejos son ilustrativos. El nivel solo cambia al seleccionar otro estado exacto. Burbujas y flujos requieren una media efectiva registrada > 0; no representan caudales instantáneos.');
    text('reduced-motion',reducedMotion.matches?'Movimiento reducido del sistema respetado':'');
  }
  function updateDecision() {
    const d=data.decision,input=data.controller_input,after=data.observed_sample;
    text('decision-summary',d?`Decisión #${d.decision_index} · t=${num(d.time_s)} s · ${[...new Set(d.reason_codes)].join(' / ')}`:'Aún no hay una decisión registrada.');
    text('controller-status',data.strategy==='open'?'LAZO ABIERTO · SIN CORRECCIÓN POR RETROALIMENTACIÓN':'LAZO CERRADO · HISTÉRESIS');
    text('decision-caption',d?`Decisión #${d.decision_index} · t = ${num(d.time_s)} s · entrada vinculada #${d.input_sample_index} · medición: ${input?clock(input.time_s):'registro ausente'}`:'Sin decisión registrada para este instante.');
    text('decision-note',data.strategy==='open'?'El programa constante no usa la medición para corregir órdenes. La lectura vinculada se conserva para auditoría.':'Errores y códigos proceden de la decisión registrada. Disponibilidad y acción efectiva: panel de ocho canales. La observación posterior no prueba causalidad.');
    const channelGroups=[[0,1],[2],[3,4],[5],[6,7]];
    data.sensors.forEach((s,j)=>{
      const tr=document.createElement('tr');
      const measurement=input?(input.qualities[j]==='GOOD'?num(input.values[j],4)+' '+s.unit:input.qualities[j]):'Sin registro';
      const observed=after?(after.qualities[j]==='GOOD'?num(after.values[j],4)+' '+s.unit:after.qualities[j])+` · t=${num(after.time_s)} s`:'Aún sin muestra posterior';
      const mapping=[[0,1],[0,-1],[1,1],[2,1],[2,-1],[3,1],[4,1],[4,-1]];
      const orders=d?channelGroups[j].map(i=>`${data.actuators[i].label}: ${pct(Math.max(0,d.commands[mapping[i][0]]*mapping[i][1]))}`).join(' / '):'Sin decisión';
      [s.label,measurement,d?num(d.references[j]):'—',d?num(d.errors[j],4):'—',d?d.reason_codes[j]+' · '+orders:'—',observed].forEach(v=>{const td=document.createElement('td');td.textContent=v;tr.append(td);});el('decision-rows').append(tr);
    });
    // The audit shows a reference/measurement link, not a feedback loop for open control.
    document.querySelector('.control-loop').textContent=data.strategy==='open'?'PROGRAMA CONSTANTE → ACTUADOR → ESTANQUE → SENSOR · SIN CORRECCIÓN POR RETROALIMENTACIÓN':'REFERENCIA → CONTROLADOR → ACTUADOR → ESTANQUE → SENSOR → RETROALIMENTACIÓN';
  }
  function updatePlayer() {
    if(!replay)return;
    el('timeline').value=player.time;el('selected-time').value=Number(player.time.toFixed(3));
    text('playback-time',`Tiempo de reproducción: ${num(player.elapsed,1)} s reales · ${player.speed}×`);
    text('source-times',`Estado x: ${num(data.state_time_s)} s · Medición y: ${data.sample_time_s===null?'ausente':num(data.sample_time_s)+' s'} · Cursor: ${num(player.time)} s`);
    text('exact-caption',`t = ${num(data.state_time_s)} s · ${data.state_policy}`);
    const guideIndex=el('guide').value;
    if(guideIndex!==''&&replay.guide[Number(guideIndex)].time_s!==player.time)el('guide').value='';
    text('playback-status',player.playing?'REPRODUCIENDO':'EN PAUSA');
    el('play').disabled=player.playing||!replay.duration;el('pause').disabled=!player.playing;
  }
  let previousProjection='',lastChartStamp=0;
  function selectTime(t,force=false) {
    if(!replay)return;
    player.seek(t);applyTime(force);
  }
  function applyTime(force=false) {
    data=replay.project(player.time);
    const signature=JSON.stringify([data.state_time_s,data.sample_time_s,data.decision?.decision_index,data.actuators.map(a=>a.record_index),data.alarms.map(a=>a.event_seq),data.events.length]);
    if(force||signature!==previousProjection){updateDashboard();refreshScene();previousProjection=signature;}
    updatePlayer();
    if(chartsReady&&(force||performance.now()-lastChartStamp>250)){updateChartCursor();lastChartStamp=performance.now();}
  }
  function seekUser(t){player.pause();selectTime(t,true);renderScene();}
  el('ambient').checked=!reducedMotion.matches;
  el('ambient').onchange=()=>{updateMotionLabel();if(!el('ambient').checked&&!player.playing)suspend();else wakeScene();};
  reducedMotion.addEventListener('change',()=>{if(reducedMotion.matches)el('ambient').checked=false;updateMotionLabel();if(!player.playing&&reducedMotion.matches)suspend();else wakeScene();});
  el('quality').onchange=()=>{quality=el('quality').value;refreshScene();wakeScene();};
  el('presentation').onclick=()=>{document.body.classList.toggle('presentation');el('presentation').textContent=document.body.classList.contains('presentation')?'Restaurar distribución':'Ampliar estanque';window.dispatchEvent(new Event('resize'));};
  document.querySelector('a[href="#decision-detail"]').onclick=()=>{el('decision-detail').open=true;};
  if(replay){
    el('timeline').max=replay.duration;el('selected-time').max=replay.duration;
    el('play').onclick=()=>{player.play();applyTime(true);wakeScene();};
    el('pause').onclick=()=>{player.pause();updatePlayer();if(!el('ambient').checked)suspend();};
    el('restart').onclick=()=>{player.reset();applyTime(true);renderScene();};
    el('timeline').oninput=e=>seekUser(Number(e.target.value));el('selected-time').onchange=e=>seekUser(Number(e.target.value));
    el('speed').onchange=e=>{player.speed=Number(e.target.value);player.last=null;updatePlayer();};
    el('previous').onclick=()=>seekUser([...replay.times].reverse().find(t=>t<player.time)??0);
    el('next').onclick=()=>seekUser(replay.times.find(t=>t>player.time)??replay.duration);
    replay.guide.forEach((g,i)=>{const o=document.createElement('option');o.value=i;o.textContent=g.label;el('guide').append(o);});
    el('guide').onchange=e=>{if(e.target.value!=='')seekUser(replay.guide[Number(e.target.value)].time_s);};
    el('guide-next').onclick=()=>{const i=el('guide').value===''?0:(Number(el('guide').value)+1)%replay.guide.length;el('guide').value=i;seekUser(replay.guide[i].time_s);if(i===replay.guide.length-1)el('historical-charts').scrollIntoView({block:'start',behavior:'instant'});};
    text('guide-note',replay.hasPerturbation?'Solo etapas respaldadas por registros; sin atribución causal.':'No hay perturbación registrada; las etapas sin evidencia se omiten.');
    selectTime(replay.duration,true);
  }else{el('playback').hidden=true;el('historical-charts').hidden=true;updateDashboard();}
  const cursorShape=()=>({type:'line',xref:'x',yref:'paper',x0:player.time,x1:player.time,y0:0,y1:1,line:{color:'#55d7e9',width:2}});
  function updateChartCursor(){
    ['state-chart','action-chart'].forEach(id=>Plotly.relayout(el(id),{shapes:[cursorShape()]}));
  }
  function drawStateChart(){
    const j=Number(el('chart-variable').value),sensor=data.sensors[j];
    const samples=replay.samples;
    const exact={x:samples.map(s=>s.time_s),y:samples.map(s=>s.x[j]),name:'Estado exacto x (retenido)',mode:'lines+markers',line:{color:'#4bd6e9',shape:'hv',width:2},marker:{size:4}};
    // Include a failed partial terminal state without inventing a sensor frame.
    if(!samples.some(s=>s.time_s===replay.duration)){exact.x.push(replay.duration);exact.y.push(base.history.run.state[j]);}
    const measured={x:samples.map(s=>s.time_s),y:samples.map(s=>s.qualities[j]==='GOOD'?s.values[j]:null),customdata:samples.map(s=>s.qualities[j]),name:'Medición y · sin interpolación',mode:'markers',marker:{size:5,color:'#ffc570'},hovertemplate:'t=%{x} s<br>y=%{y}<br>Calidad: %{customdata}<extra></extra>'};
    const events={x:replay.events.map(e=>e.time_s),y:replay.events.map(e=>e.category==='alarm'?.97:.88),yaxis:'y2',mode:'markers',name:'Eventos / alarmas',marker:{symbol:'diamond',size:7,color:replay.events.map(e=>e.category==='alarm'?'#ff8394':'#a994f8')},customdata:replay.events.map(e=>e.category+' · '+e.transition+' · '+e.code),hovertemplate:'t=%{x} s<br>%{customdata}<extra></extra>'};
    const layout=chartLayout(sensor.label+' · '+sensor.unit,300);layout.yaxis2={overlaying:'y',range:[0,1],visible:false,fixedrange:true};
    // Reference is a separate trace so cursor updates cannot remove it.
    const reference={x:[0,replay.duration],y:[sensor.reference,sensor.reference],mode:'lines',name:'Referencia',line:{color:'#6de4ba',dash:'dash',width:1},hoverinfo:'skip'};
    Plotly.react(el('state-chart'),[exact,measured,reference,events],layout,{responsive:true,displayModeBar:false});
  }
  function chartLayout(title,height){return {title:{text:title,font:{size:12}},height,paper_bgcolor:'#0d1e2f',plot_bgcolor:'#0d1e2f',font:{color:'#9eb6c8',size:10},margin:{l:55,r:20,t:36,b:48},xaxis:{title:{text:'Tiempo simulado (s)'},range:[0,Math.max(1,replay.duration)],gridcolor:'#20364a'},yaxis:{gridcolor:'#20364a'},legend:{orientation:'h',y:-.25,font:{size:9}},shapes:[cursorShape()],uirevision:'history'};}
  function initCharts(){
    if(!replay||typeof Plotly==='undefined')return;
    data.sensors.forEach((s,j)=>{const o=document.createElement('option');o.value=j;o.textContent=s.label;el('chart-variable').append(o);});
    el('chart-variable').onchange=drawStateChart;drawStateChart();
    const traces=base.actuators.map(a=>{const rows=base.history.actuator_records.filter(r=>r.actuator_id===a.key);return {x:rows.flatMap(r=>[r.start_s,r.end_s,null]),y:rows.flatMap(r=>[r.mean_effective,r.mean_effective,null]),mode:'lines',name:a.label,connectgaps:false,hovertemplate:'t=%{x} s<br>media efectiva=%{y}<extra>%{fullData.name}</extra>'};});
    const actionLayout=chartLayout('Acciones efectivas medias · intervalos registrados',270);actionLayout.margin.b=85;actionLayout.legend.y=-.35;
    Plotly.newPlot(el('action-chart'),traces,actionLayout,{responsive:true,displayModeBar:false});
    ['state-chart','action-chart'].forEach(id=>el(id).on('plotly_click',e=>{if(e.points.length)seekUser(e.points[0].x);}));
    chartsReady=true;
  }

  const viewport = el('viewport');
  let renderer, raf = null, running = false;
  let sceneTick=()=>{},frameCount=0,elapsed=0,lastTick=null,lastFrame=null,pageVisible=true,viewportVisible=true;
  const api={get snapshot(){return data;},get frames(){return frameCount;},get static(){return !el('ambient').checked||reducedMotion.matches;},player,replay,
    get suspended(){return !pageVisible||document.visibilityState!=='visible';},seek:seekUser};
  window.__aquacontrol=api;
  function schedule(){
    if(raf===null&&!disposed&&pageVisible&&document.visibilityState==='visible'&&(player.playing||(api.mode==='3D'&&viewportVisible&&el('ambient').checked&&!reducedMotion.matches)))raf=requestAnimationFrame(tick);
  }
  wakeScene=()=>{lastTick=null;lastFrame=null;schedule();};
  function tick(stamp){
    raf=null;if(disposed||!pageVisible||document.visibilityState!=='visible')return;
    const fps=quality==='low'?20:30;
    if(lastFrame===null||stamp-lastFrame>=1000/fps){
      const dt=lastTick===null?0:Math.min((stamp-lastTick)/1000,.5);lastTick=stamp;lastFrame=stamp;
      if(player.playing){player.tick(stamp);applyTime();}
      if(viewportVisible){
        if(el('ambient').checked&&!reducedMotion.matches){elapsed+=dt;sceneTick(elapsed);}
        renderScene();frameCount++;
      }
    }
    schedule();
  }
  function suspend(){if(raf!==null)cancelAnimationFrame(raf);raf=null;lastTick=null;lastFrame=null;player.last=null;}
  const pageObserver=new IntersectionObserver(entries=>{pageVisible=entries[0].isIntersecting;if(!pageVisible)suspend();else schedule();});pageObserver.observe(document.body);
  const sceneObserver=new IntersectionObserver(entries=>{viewportVisible=entries[0].isIntersecting;if(!viewportVisible&&!player.playing)suspend();else schedule();});sceneObserver.observe(viewport);
  document.addEventListener('visibilitychange',()=>{if(document.visibilityState!=='visible')suspend();else schedule();});
  window.addEventListener('pagehide',()=>{disposed=true;suspend();pageObserver.disconnect();sceneObserver.disconnect();},{once:true});
  function fallback(reason) {
    running = false; if (raf !== null) cancelAnimationFrame(raf);
    raf=null;
    if (renderer) { renderer.domElement.remove(); renderer.dispose();renderer=null; }
    text('render-badge', 'VISTA 2.5D · ' + reason);
    text('motion-label', 'Vista 2.5D · proyección fija del instante seleccionado');
    const target = el('fallback'); target.style.display = 'block';
    document.querySelectorAll('.view-controls button').forEach(b => {b.disabled = true;});
    // Orthographic isometric projection in metres. Water height is never clamped.
    const L = circular ? 2 * g.radius_m : g.length_m, W = circular ? 2 * g.radius_m : g.width_m, H = g.height_m;
    const scale = 340 / Math.max(L, W, H * 2), h = data.state[4];
    const project = (x,y,z) => [390 + (x - z) * scale * .72, 260 + (x + z) * scale * .28 - y * scale];
    const point = p => project(...p).join(',');
    const poly = (ps, fill, stroke = '#7995a9', extra = '') => `<polygon points="${ps.map(point).join(' ')}" fill="${fill}" stroke="${stroke}" stroke-width="1.4" ${extra}/>`;
    const perimeter = y => circular ? Array.from({length:65},(_,i) => {const a=i/64*Math.PI*2;return [Math.cos(a)*L/2,y,Math.sin(a)*W/2];}) : [[-L/2,y,-W/2],[L/2,y,-W/2],[L/2,y,W/2],[-L/2,y,W/2]];
    let svg = `<svg viewBox="0 0 780 420" xmlns="http://www.w3.org/2000/svg" aria-label="${g.shape} 2.5D"><defs><linearGradient id="water"><stop stop-color="#138b9c" stop-opacity=".7"/><stop offset="1" stop-color="#377f96" stop-opacity=".3"/></linearGradient></defs>`;
    svg += poly([[-L*.7,-.12,-W*.8],[L*.8,-.12,-W*.8],[L*.8,-.12,W*.8],[-L*.7,-.12,W*.8]],'#132c3e','#304d62');
    const base = perimeter(0), top = perimeter(H);
    svg += poly(base,'#344d5e');
    if (h !== null && h > 0) {
      const water = perimeter(h);
      for (let i=0;i<base.length-1;i++) svg += poly([base[i],base[i+1],water[i+1],water[i]],'url(#water)','#39788a');
      if (!circular) svg += poly([base[3],base[0],water[0],water[3]],'url(#water)','#39788a');
      svg += poly(water,'url(#water)','#75d9e5');
      for (let i=0;i<10;i++) {const p=project(Math.sin(i*4)*L*.25,h*.45,Math.cos(i*3)*W*.22);svg += `<ellipse cx="${p[0]}" cy="${p[1]}" rx="8" ry="3" fill="#a9d1d5"/><path d="M${p[0]+6},${p[1]} l7,-4 v8 z" fill="#a9d1d5"/>`;}
    }
    svg += poly(top,'none','#b6cfda','stroke-width="3"');
    for(let i=0;i<(circular?16:4);i++){const a=i/16*Math.PI*2,p=circular?[Math.cos(a)*L/2,0,Math.sin(a)*W/2]:base[i],q=[p[0],H,p[2]];svg+=`<polyline points="${point(p)} ${point(q)}" stroke="#86a4b7" stroke-opacity=".5"/>`;}
    const shortLabels=['CALOR','FRÍO','AIRE','pH+','pH−','FILTRO','ENTRADA','SALIDA'];
    data.actuators.forEach((a,i)=>{const x=65+(i%4)*195,y=352+Math.floor(i/4)*31;svg+=`<circle cx="${x}" cy="${y}" r="4" fill="${a.active?'#6de4ba':'#72899b'}"/><text x="${x+11}" y="${y+4}" fill="#bcd2df" font-family="Arial" font-size="10">${shortLabels[i]} ${pct(a.effective)}</text>`;});
    ['T','O₂','pH','U','h'].forEach((label,i)=>{const p=project(-L*.3+i*L*.15,H+.12,-W*.28);svg+=`<line x1="${p[0]}" y1="${p[1]}" x2="${p[0]}" y2="${p[1]+35}" stroke="#69ddeb" stroke-width="3"/><text x="${p[0]-7}" y="${p[1]-9}" fill="#b0e6ef" font-size="11">${label}</text>`;});
    if (data.actuators[2].active && h !== null && h>0) for(let i=0;i<9;i++){const p=project(L*.12,h*(.15+i*.08),W*.1);svg+=`<circle cx="${p[0]}" cy="${p[1]}" r="${2+i%3}" fill="none" stroke="#b2f0f6"/>`;}
    target.innerHTML = svg + '</svg>';
    api.mode='2.5D';api.reason=reason;
    sceneTick=()=>{};renderScene=()=>{};refreshScene=()=>fallback(reason);schedule();
  }

  function start3d() {
    const T = THREE;
    renderer = new T.WebGLRenderer({antialias:false,alpha:true,powerPreference:'low-power'});
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.25));
    renderer.setClearColor(0x0b1c2a, 0); renderer.shadowMap.enabled = false; renderer.shadowMap.type=T.PCFSoftShadowMap;
    renderer.toneMapping=T.ACESFilmicToneMapping; renderer.toneMappingExposure=1.5;
    viewport.prepend(renderer.domElement);
    const scene=new T.Scene(); const root=new T.Group(); scene.add(root);
    const L=circular?g.radius_m*2:g.length_m, W=circular?g.radius_m*2:g.width_m, H=g.height_m, span=Math.max(L,W,H*2), u=span/4;
    root.scale.setScalar(4/span);
    const camera=new T.PerspectiveCamera(38,1,.05,150);
    const hemi=new T.HemisphereLight(0xb4e7ff,0x223041,2.5);scene.add(hemi);
    const key=new T.DirectionalLight(0xdcefff,4);key.position.set(-3,8,5);key.castShadow=true;key.shadow.mapSize.set(1024,1024);scene.add(key);
    const fill=new T.DirectionalLight(0x43b8d5,2);fill.position.set(4,3,-5);scene.add(fill);
    const metal=new T.MeshStandardMaterial({color:0x7791a0,metalness:.8,roughness:.32});
    const dark=new T.MeshStandardMaterial({color:0x243e50,metalness:.6,roughness:.5});
    const concrete=new T.MeshStandardMaterial({color:0x233b4b,roughness:.9});
    const glass=new T.MeshPhysicalMaterial({color:0x86b7c9,metalness:.15,roughness:.16,transparent:true,opacity:.16,side:T.DoubleSide,depthWrite:false});
    const cyan=new T.MeshStandardMaterial({color:0x4bd6e9,emissive:0x12677d,emissiveIntensity:.45,metalness:.5,roughness:.25});
    const activity=i=>data.actuators[i].active;
    const statusMaterials=Array.from({length:8},()=>new T.MeshStandardMaterial({emissiveIntensity:.8}));
    const statusMaterial=i=>statusMaterials[i];
    function mesh(geometry,material,x=0,y=0,z=0,parent=root){const m=new T.Mesh(geometry,material);m.position.set(x,y,z);m.castShadow=!material.transparent;m.receiveShadow=true;parent.add(m);return m;}
    const box=(x,y,z,a,b,c,mat=metal,parent=root)=>mesh(new T.BoxGeometry(a,b,c),mat,x,y,z,parent);
    const cyl=(x,y,z,r,h,mat=metal,parent=root)=>mesh(new T.CylinderGeometry(r,r,h,48),mat,x,y,z,parent);
    function pipe(points,mat=metal,r=.035*u){const curve=new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p)),false,'catmullrom',.1);return mesh(new T.TubeGeometry(curve,48,r,10,false),mat);}
    function line(points,color=0x527c92){const geo=new T.BufferGeometry().setFromPoints(points.map(p=>new T.Vector3(...p)));const l=new T.Line(geo,new T.LineBasicMaterial({color}));root.add(l);return l;}
    function ring(x,y,z,r,mat=metal,tube=.025*u){const m=mesh(new T.TorusGeometry(r,tube,8,64),mat,x,y,z);m.rotation.x=Math.PI/2;return m;}
    function label(value,x,y,z,color='#b9d2df',size=.18*u){
      const c=document.createElement('canvas');c.width=512;c.height=80;const ctx=c.getContext('2d');
      ctx.font='500 35px Segoe UI, Arial';ctx.textAlign='center';ctx.fillStyle='#0b1c2de0';ctx.fillRect(0,0,512,80);ctx.fillStyle=color;ctx.fillText(value,256,51);
      const material=new T.SpriteMaterial({map:new T.CanvasTexture(c),transparent:true,depthTest:false});const s=new T.Sprite(material);s.position.set(x,y,z);s.scale.set(size*5,size*.8,1);root.add(s);return s;
    }
    box(0,-.14*u,0,L+1.8*u,.2*u,W+2.1*u,concrete);
    const grid=new T.GridHelper(10,20,0x304f64,0x1b3446);grid.position.y=-.27;scene.add(grid);
    if(circular){
      cyl(0,-.015*u,0,g.radius_m+.07*u,.12*u,dark);
      mesh(new T.CylinderGeometry(g.radius_m,g.radius_m,H,80,1,true),glass,0,H/2,0);
      [0,H*.5,H].forEach(y=>ring(0,y,0,g.radius_m,metal));
      ring(0,H+.19*u,0,g.radius_m+.02*u,metal,.018*u);
      for(let i=0;i<20;i++){const a=i/20*Math.PI*2,x=Math.cos(a)*g.radius_m,z=Math.sin(a)*g.radius_m; cyl(x,H/2,z,.015*u,H+.37*u,metal);}
    }else{
      box(0,-.015*u,0,L+.13*u,.12*u,W+.13*u,dark);
      box(0,H/2,-W/2,L,H,.015*u,glass);box(0,H/2,W/2,L,H,.015*u,glass);
      box(-L/2,H/2,0,.015*u,H,W,glass);box(L/2,H/2,0,.015*u,H,W,glass);
      [0,H,H+.19*u].forEach(y=>{box(0,y,-W/2,L,.035*u,.035*u);box(0,y,W/2,L,.035*u,.035*u);box(-L/2,y,0,.035*u,.035*u,W);box(L/2,y,0,.035*u,.035*u,W);});
      for(let i=0;i<9;i++)[-1,1].forEach(s=>cyl(-L/2+L*i/8,H/2,s*W/2,.014*u,H+.38*u,metal));
    }
    // Water geometry uses exact persisted h. Only optical appearance is bounded.
    let h=data.state[4]; const turbidity=data.state[3];
    const visualTurbidity=turbidity===null?0:Math.min(1,Math.max(0,turbidity/100));
    const waterColor=new T.Color(0x16899c).lerp(new T.Color(0x7e8357),visualTurbidity);
    const waterMat=new T.MeshPhysicalMaterial({color:waterColor,transparent:true,opacity:.22+.38*visualTurbidity,roughness:.2,metalness:.25,side:T.DoubleSide,depthWrite:false});
    const surfaceMat=new T.MeshPhysicalMaterial({color:waterColor,transparent:true,opacity:.47+.3*visualTurbidity,roughness:.12,metalness:.65,side:T.DoubleSide,depthWrite:false});
    const fish=[],ripples=[];
    const waterBody=circular?cyl(0,0,0,g.radius_m*.994,1,waterMat):box(0,0,0,L*.994,1,W*.994,waterMat);
    const surface=mesh(circular?new T.CircleGeometry(g.radius_m*.994,64):new T.PlaneGeometry(L*.994,W*.994,20,16),surfaceMat,0,h||0,0);surface.rotation.x=-Math.PI/2;
    const surfacePositions=surface.geometry.attributes.position, originalSurface=surfacePositions.array.slice();
    const fishGeometries={low:new T.SphereGeometry(.095*u,8,6),medium:new T.SphereGeometry(.095*u,12,8),high:new T.SphereGeometry(.095*u,18,12)};
    {
        const gleam=new T.MeshBasicMaterial({color:0xa5e6ec,transparent:true,opacity:.15,depthWrite:false});
        for(let i=0;i<5;i++){const ripple=ring((i-2)*L*.09,(h||0)+.006*u,Math.cos(i)*W*.18,(.12+i*.05)*u,gleam,.004*u);ripple.scale.z=.6;ripples.push(ripple);}
        const fishMat=new T.MeshStandardMaterial({color:0xa3c1b6,metalness:.35,roughness:.45});
        for(let i=0;i<13;i++){
          const f=new T.Group(),phase=i*2.399;f.position.set(Math.cos(phase)*L*.28,h*(.25+.4*(i%4)/4),Math.sin(phase)*W*.28);root.add(f);
          const body=mesh(fishGeometries.medium,fishMat,0,0,0,f);body.scale.set(1.9,.65,.65);
          const tail=mesh(new T.ConeGeometry(.085*u,.12*u,3),fishMat,-.19*u,0,0,f);tail.rotation.z=-Math.PI/2;tail.scale.z=.25;
          mesh(new T.SphereGeometry(.01*u,8,6),dark,.12*u,.022*u,.049*u,f);
          const fin=mesh(new T.ConeGeometry(.045*u,.09*u,3),fishMat,-.02*u,.07*u,0,f);fin.scale.z=.2;
          f.rotation.y=phase;fish.push({group:f,body,tail,phase,origin:f.position.clone(),depth:.25+.4*(i%4)/4});
        }
    }
    // Five probes and their cables, with quality colours from y, not x.
    const sensorNames=['T','O₂','pH','U','h'];
    const probeMaterials=[];
    for(let i=0;i<5;i++){
      const x=(i-2)*L*.135,z=-W*.28,y=H*.44;
      const material=new T.MeshStandardMaterial({color:0x4bd6e9,emissive:0x12677d});probeMaterials.push(material);
      cyl(x,y,z,.027*u,.25*u,metal);cyl(x,y-.11*u,z,.028*u,.06*u,material);
      pipe([[x,y+.12*u,z],[x,H+.12*u,z],[x,H+.17*u,-W/2-.17*u]],dark,.01*u);
      label(sensorNames[i],x,H+.32*u,z,'#68dce9',.13*u);
    }
    // Cabinet and controller are illustrative; no extra simulated sensor/channel.
    box(-L/2-.49*u,.49*u,-W/2-.27*u,.45*u,.98*u,.32*u,dark);
    box(-L/2-.49*u,.61*u,-W/2-.1*u,.28*u,.25*u,.015*u,cyan);
    label('CONTROL',-L/2-.49*u,1.12*u,-W/2-.27*u);
    const equipment=[],heatRings=[];
    const equipNames=['CALOR','FRÍO','AIREACIÓN','pH +','pH −','FILTRO'];
    for(let i=0;i<6;i++){
      const x=-L/2-.5*u+(i%3)*(L+u)/2,z=i<3?W/2+.48*u:-W/2-.52*u;
      const mat=statusMaterial(i);equipment.push({x,z});
      if(i===3||i===4){cyl(x,.24*u,z,.12*u,.44*u,dark);cyl(x,.48*u,z,.08*u,.05*u,metal);}
      else{box(x,.2*u,z,.36*u,.34*u,.32*u,dark);cyl(x,.45*u,z,.13*u,.21*u,metal);for(let k=0;k<4;k++)box(x,.4*u+k*.035*u,z,.29*u,.01*u,.25*u,dark);}
      cyl(x,.58*u,z,.03*u,.035*u,mat);label(equipNames[i],x,.85*u,z,'#9fb5c4',.13*u);
      const toZ=i<3?W*.3:-W*.3;
      pipe([[x,.14*u,z],[x,.14*u,z*.82],[x,H*.25,toZ]],metal,.025*u);
      if(i===0||i===1){const heat=new T.MeshBasicMaterial({color:i===0?0xff9064:0x5aaef5,transparent:true,opacity:.32,depthWrite:false});heatRings.push(ring(x,.35*u,z,.27*u,heat,.035*u));}
    }
    // Inlet/outlet pipes with hand valves and effective flow markers.
    const flows=[];
    [6,7].forEach((index,k)=>{
      const x=(k===0?-1:1)*(L/2+.23*u),z=W*.12;
      const points=[[x,-.08*u,z+W*.38],[x,H+.18*u,z+W*.38],[x,H+.18*u,z],[x+(k===0?.4:-.4)*u,H+.18*u,z],[x+(k===0?.4:-.4)*u,H*.55,z]];
      pipe(points,metal,.055*u);
      const valve=ring(x,H*.65,z+W*.38,.11*u,statusMaterial(index),.018*u);valve.rotation.x=0;valve.rotation.y=Math.PI/2;
      label(k===0?'ENTRADA':'SALIDA',x,H+.47*u,z+W*.38,'#9fb5c4',.13*u);
      {
        const curve=new T.CatmullRomCurve3((k===0?points:[...points].reverse()).map(p=>new T.Vector3(...p)),false,'catmullrom',.1);
        for(let i=0;i<6;i++){const bead=mesh(new T.SphereGeometry(.062*u,8,6),cyan);flows.push({mesh:bead,curve,phase:i/6,index});bead.position.copy(curve.getPoint(i/6));}
      }
    });
    // Submerged diffuser, bubbles driven exclusively by recorded mean air action.
    const diffuser=cyl(L*.12,.06*u,W*.08,.19*u,.07*u,dark);
    const bubbles=[];
    {
      const bubbleMat=new T.MeshPhysicalMaterial({color:0xb0f2fa,transparent:true,opacity:.6,roughness:.1,metalness:.3,depthWrite:false});
      for(let i=0;i<34;i++){const phase=i/34;const b=mesh(new T.SphereGeometry((.013+i%4*.005)*u,8,6),bubbleMat);const x=L*.12+Math.sin(i*4)*.15*u,z=W*.08+Math.cos(i*6)*.15*u;b.position.set(x,h*phase,z);bubbles.push({mesh:b,x,z,phase});}
    }
    // Filtration indication is an effective-action indicator, never an inferred order.
    const {x:rotorX,z:rotorZ}=equipment[5];const rotor=box(rotorX,.59*u,rotorZ,.22*u,.02*u,.03*u,statusMaterial(5));
    // Level ruler shows physical geometry; camera motion does not alter it.
    for(let i=0;i<=4;i++){const y=H*i/4;line([[L/2+.09*u,y,-W/2],[L/2+.18*u,y,-W/2]],0x7eaabc);}
    let azimuth=.78,elevation=.49,distance=9.1,dragging=false,lastX=0,lastY=0;
    const target=new T.Vector3(0,H*root.scale.y*.45,0);
    function render(){if(!viewportVisible||!pageVisible||document.visibilityState!=='visible')return;camera.position.set(target.x+distance*Math.cos(elevation)*Math.sin(azimuth),target.y+distance*Math.sin(elevation),target.z+distance*Math.cos(elevation)*Math.cos(azimuth));camera.lookAt(target);renderer.render(scene,camera);}
    function resize(){if(!running)return;renderer.setSize(viewport.clientWidth,viewport.clientHeight);camera.aspect=viewport.clientWidth/viewport.clientHeight;camera.updateProjectionMatrix();render();}
    function move(da,de,dd=0){azimuth+=da;elevation=Math.max(.12,Math.min(1.35,elevation+de));distance=Math.max(4,Math.min(18,distance+dd));render();}
    renderer.domElement.addEventListener('pointerdown',e=>{dragging=true;lastX=e.clientX;lastY=e.clientY;renderer.domElement.setPointerCapture(e.pointerId);});
    renderer.domElement.addEventListener('pointerup',()=>{dragging=false;});
    renderer.domElement.addEventListener('pointermove',e=>{if(!dragging)return;move(-(e.clientX-lastX)*.007,(e.clientY-lastY)*.007);lastX=e.clientX;lastY=e.clientY;});
    renderer.domElement.addEventListener('wheel',e=>{e.preventDefault();move(0,0,e.deltaY*.006);},{passive:false});
    el('rotate-left').onclick=()=>move(-.22,0);el('rotate-right').onclick=()=>move(.22,0);el('zoom-in').onclick=()=>move(0,0,-.6);el('zoom-out').onclick=()=>move(0,0,.6);
    el('reset').onclick=()=>{azimuth=.78;elevation=.49;distance=9.1;render();};
    renderer.domElement.addEventListener('webglcontextlost',e=>{e.preventDefault();fallback('WebGL no disponible');});
    running=true; const observer=new ResizeObserver(resize);observer.observe(viewport);resize();
    sceneTick=t=>{
      bubbles.forEach(b=>{if(b.mesh.visible)b.mesh.position.y=((b.phase+t*.25)%1)*h;});
      flows.forEach(f=>{if(f.mesh.visible)f.mesh.position.copy(f.curve.getPoint((f.phase+t*.16)%1));});
      fish.forEach((f,i)=>{
        if(!f.group.visible)return;
        const a=f.phase+t*(.13+(i%3)*.035),rx=L*(.22+(i%3)*.025),rz=W*(.22+(i%4)*.018);
        f.group.position.set(Math.cos(a)*rx,h*f.depth+Math.sin(t*.9+f.phase)*Math.min(.02*u,h*.03),Math.sin(a)*rz);
        f.group.rotation.y=Math.atan2(-rz*Math.cos(a),-rx*Math.sin(a));f.group.rotation.z=Math.sin(t*2+f.phase)*.035;
        f.tail.rotation.y=Math.sin(t*5+f.phase)*.55;
      });
      // Tiny optical displacement around the fixed exact h; never a state update.
      for(let i=0;i<surfacePositions.count;i++){
        const x=originalSurface[i*3],y=originalSurface[i*3+1];
        surfacePositions.array[i*3+2]=Math.sin(x/u*3+t*1.3)*Math.cos(y/u*3-t*.7)*.006*u;
      }
      surfacePositions.needsUpdate=true;surface.geometry.computeVertexNormals();
      ripples.forEach((r,i)=>{r.scale.setScalar(1+Math.sin(t*1.2+i)*.15);r.rotation.z=t*.12+i;});
      surfaceMat.roughness=.12+Math.sin(t*.8)*.035;
      if(rotor.visible)rotor.rotation.y=t*2;
    };
    let previousQuality='';
    refreshScene=()=>{
      if(!running||!renderer)return;
      h=data.state[4];waterBody.visible=h!==null&&h>0;waterBody.scale.y=h||0;waterBody.position.y=(h||0)/2;
      surface.visible=h!==null;surface.position.y=h||0;
      const optical=data.state[3]===null?0:Math.min(1,Math.max(0,data.state[3]/100));
      waterColor.set(0x16899c).lerp(new T.Color(0x7e8357),optical);waterMat.color.copy(waterColor);surfaceMat.color.copy(waterColor);
      waterMat.opacity=.22+.38*optical;surfaceMat.opacity=.47+.3*optical;
      const fishCount=quality==='low'?5:quality==='medium'?9:13,bubbleCount=quality==='low'?10:quality==='medium'?20:34;
      fish.forEach((f,i)=>{f.group.visible=h>0&&i<fishCount;f.group.position.y=(h||0)*f.depth;f.body.geometry=fishGeometries[quality];});
      bubbles.forEach((b,i)=>{b.mesh.visible=activity(2)&&h>0&&i<bubbleCount;b.mesh.position.y=(h||0)*b.phase;});
      flows.forEach((f,i)=>{f.mesh.visible=activity(f.index)&&(quality!=='low'||i%2===0);});
      heatRings.forEach((r,i)=>{r.visible=activity(i);});rotor.visible=activity(5);
      ripples.forEach((r,i)=>{r.position.y=(h||0)+.006*u;r.visible=h>0&&(quality!=='low'||i<2);});
      probeMaterials.forEach((m,i)=>{m.color.setHex(data.sensors[i].quality==='GOOD'?0x4bd6e9:0xffad7d);});
      statusMaterials.forEach((m,i)=>{m.color.setHex(activity(i)?0x69e9bc:0x566e80);m.emissive.setHex(activity(i)?0x2e9a70:0);});
      if(previousQuality!==quality){renderer.shadowMap.enabled=quality==='high';renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,quality==='high'?1.7:quality==='medium'?1.25:1));surfaceMat.metalness=quality==='low'?.2:.65;previousQuality=quality;resize();}
      render();
    };
    renderScene=()=>{if(running&&renderer)render();};refreshScene();sceneTick(0);
    window.addEventListener('pagehide',()=>{running=false;observer.disconnect();scene.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material){if(o.material.map)o.material.map.dispose();o.material.dispose();}});if(renderer)renderer.dispose();},{once:true});
    text('render-badge','3D · THREE.JS LOCAL');
    Object.assign(api,{mode:'3D',scene,camera,renderer,fish,surface,waterBody,bubbles,flows});
  }
  if(data.force_fallback)fallback('selección manual');
  else{try{start3d();}catch(error){console.warn('AquaControl: alternativa 2.5D',error.message);fallback('WebGL no disponible');}}
  initCharts();schedule();
})();
