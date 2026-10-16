/* Local renderer: consumes a snapshot, never sends commands or advances time. */
(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('snapshot').textContent);
  const el = id => document.getElementById(id);
  const text = (id, value) => { el(id).textContent = value; };
  const num = (v, digits = 3) => v === null ? '—' : Number(v).toLocaleString('es', {maximumFractionDigits: digits});
  const pct = v => v === null ? '—' : v > 0 && v < .0001 ? '<0,01%' : num(v * 100, 2) + '%';
  const clock = t => t === null ? 'Sin muestra' : `${num(t, 3)} s · ${num(t / 3600, 4)} h`;
  const statuses = {PREPARED:'Preparada',RUNNING:'En ejecución',PAUSED:'Pausada',STOPPED:'Detenida',COMPLETED:'Completada',FAILED:'Fallida',INTERRUPTED:'Interrumpida'};
  text('run-badge', (statuses[data.status] || data.status).toUpperCase());
  if (data.status !== 'RUNNING') el('run-badge').classList.add(data.status === 'FAILED' ? 'failed' : 'still');
  text('shape-label', data.geometry.shape + ' industrial');
  text('profile', `${data.profile} · ${data.strategy === 'closed' ? 'Lazo cerrado' : 'Lazo abierto'} · ${data.run_id.slice(0, 10)}`);
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
  const g = data.geometry, circular = g.shape === 'Circular';
  text('water-label', `NIVEL EXACTO h = ${num(data.state[4], 5)} m`);
  text('volume-label', `V = A × h = ${num(data.volume_m3, 5)} m³`);
  text('dimensions', circular ? `A ${num(g.area_m2)} m² · r ${num(g.radius_m)} m · H ${num(g.height_m)} m` : `A ${num(g.area_m2)} m² · ${num(g.length_m)} × ${num(g.width_m)} m · H ${num(g.height_m)} m`);
  text('exact-caption', `t = ${num(data.state_time_s)} s · volumen y nivel sin recorte`);
  text('interval', data.interval_s ? `Intervalo confirmado: [${num(data.interval_s[0])}, ${num(data.interval_s[1])}] s` : 'Sin intervalo confirmado. No se infiere actividad.');
  data.actuators.forEach(a => {
    const row = document.createElement('div'); row.className = 'actuator-row' + (a.active ? ' active' : '');
    const name = document.createElement('span'); const dot = document.createElement('i'); name.append(dot, a.label); row.append(name);
    [a.command, a.availability, a.effective].forEach((v, i) => {
      const span = document.createElement('span'); span.textContent = i === 1 ? num(v, 3) : pct(v);
      if (i === 2) span.className = 'effective';
      if (i === 1 && v !== null && v < 1) span.className = 'unavailable'; row.append(span);
    });
    row.title = a.reason || 'Registro confirmado'; el('actuators').append(row);
  });
  text('alarm-count', String(data.alarms.length));
  if (!data.alarms.length) { const p = document.createElement('div'); p.className = 'no-alarm'; p.textContent = data.sample_time_s === null ? '○ Aún no hay muestras para alarmas' : '✓ Sin alarmas activas registradas'; el('alarms').append(p); }
  data.alarms.forEach(a => {
    const row = document.createElement('div'); row.className = 'alarm' + (a.severity === 'CRITICA' ? ' critical' : '');
    const sensor = data.sensors.find(s => s.key === a.target);
    row.textContent = `${sensor ? sensor.label : a.target}: ${a.code.replaceAll('_', ' ')}`;
    const time = document.createElement('small'); time.textContent = `Activada en t = ${num(a.time_s)} s · ${a.severity}`; row.append(time); el('alarms').append(row);
  });
  text('motion-label', data.animate ? 'Animación ilustrativa del último intervalo confirmado' : 'Escena estática · ' + (statuses[data.status] || data.status));
  text('motion-caption', data.animate ? 'Las burbujas y los flujos indican acciones efectivas registradas. La animación no avanza el tiempo ni interpola el estado.' : 'El agua, los equipos y los peces conservan la última posición. Rotación y zoom disponibles en 3D.');
  text('warnings', [...data.warnings, data.cause ? 'Terminación: ' + data.cause : ''].filter(Boolean).join(' '));

  const viewport = el('viewport');
  let renderer, raf = null, running = false;
  function fallback(reason) {
    running = false; if (raf !== null) cancelAnimationFrame(raf);
    if (renderer) { renderer.domElement.remove(); renderer.dispose(); }
    text('render-badge', 'VISTA 2.5D · ' + reason);
    text('motion-label', 'Vista 2.5D estática · ' + (statuses[data.status] || data.status));
    text('motion-caption', 'Los símbolos indican acciones efectivas registradas. Proyección fija del estado confirmado, sin evolución ni animación continua.');
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
    window.__aquacontrol = {mode:'2.5D',snapshot:data,static:true,reason};
  }

  function start3d() {
    const T = THREE;
    renderer = new T.WebGLRenderer({antialias:true,alpha:true,powerPreference:'low-power'});
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.7));
    renderer.setClearColor(0x0b1c2a, 0); renderer.shadowMap.enabled = true; renderer.shadowMap.type=T.PCFSoftShadowMap;
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
    const statusMaterial=i=>new T.MeshStandardMaterial({color:activity(i)?0x69e9bc:0x566e80,emissive:activity(i)?0x2e9a70:0x000000,emissiveIntensity:.8});
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
    const h=data.state[4], turbidity=data.state[3];
    const visualTurbidity=turbidity===null?0:Math.min(1,Math.max(0,turbidity/100));
    const waterColor=new T.Color(0x16899c).lerp(new T.Color(0x7e8357),visualTurbidity);
    const waterMat=new T.MeshPhysicalMaterial({color:waterColor,transparent:true,opacity:.22+.38*visualTurbidity,roughness:.2,metalness:.25,side:T.DoubleSide,depthWrite:false});
    const surfaceMat=new T.MeshPhysicalMaterial({color:waterColor,transparent:true,opacity:.47+.3*visualTurbidity,roughness:.12,metalness:.65,side:T.DoubleSide,depthWrite:false});
    const fish=[];
    if(h!==null){
      if(h>0){if(circular)cyl(0,h/2,0,g.radius_m*.994,h,waterMat);else box(0,h/2,0,L*.994,h,W*.994,waterMat);}
      const surface=mesh(circular?new T.CircleGeometry(g.radius_m*.994,80):new T.PlaneGeometry(L*.994,W*.994),surfaceMat,0,h,0);surface.rotation.x=-Math.PI/2;
      if(h>0){
        const gleam=new T.MeshBasicMaterial({color:0xa5e6ec,transparent:true,opacity:.15,depthWrite:false});
        for(let i=0;i<5;i++){const ripple=ring((i-2)*L*.09,h+.006*u,Math.cos(i)*W*.18,(.12+i*.05)*u,gleam,.004*u);ripple.scale.z=.6;}
        const fishMat=new T.MeshStandardMaterial({color:0xa3c1b6,metalness:.35,roughness:.45});
        for(let i=0;i<13;i++){
          const f=new T.Group(),phase=i*2.399;f.position.set(Math.cos(phase)*L*.28,h*(.25+.4*(i%4)/4),Math.sin(phase)*W*.28);root.add(f);
          const body=mesh(new T.SphereGeometry(.095*u,16,10),fishMat,0,0,0,f);body.scale.set(1.9,.65,.65);
          const tail=mesh(new T.ConeGeometry(.085*u,.12*u,3),fishMat,-.19*u,0,0,f);tail.rotation.z=-Math.PI/2;tail.scale.z=.25;
          mesh(new T.SphereGeometry(.01*u,8,6),dark,.12*u,.022*u,.049*u,f);
          const fin=mesh(new T.ConeGeometry(.045*u,.09*u,3),fishMat,-.02*u,.07*u,0,f);fin.scale.z=.2;
          f.rotation.y=phase;fish.push({group:f,phase,origin:f.position.clone()});
        }
      }
    }
    // Five probes and their cables, with quality colours from y, not x.
    const sensorNames=['T','O₂','pH','U','h'];
    for(let i=0;i<5;i++){
      const x=(i-2)*L*.135,z=-W*.28,y=H*.44;
      const material=data.sensors[i].quality==='GOOD'?cyan:new T.MeshStandardMaterial({color:0xffad7d,emissive:0x8d241c});
      cyl(x,y,z,.027*u,.25*u,metal);cyl(x,y-.11*u,z,.028*u,.06*u,material);
      pipe([[x,y+.12*u,z],[x,H+.12*u,z],[x,H+.17*u,-W/2-.17*u]],dark,.01*u);
      label(sensorNames[i],x,H+.32*u,z,'#68dce9',.13*u);
    }
    // Cabinet and controller are illustrative; no extra simulated sensor/channel.
    box(-L/2-.49*u,.49*u,-W/2-.27*u,.45*u,.98*u,.32*u,dark);
    box(-L/2-.49*u,.61*u,-W/2-.1*u,.28*u,.25*u,.015*u,cyan);
    label('CONTROL',-L/2-.49*u,1.12*u,-W/2-.27*u);
    const equipment=[];
    const equipNames=['CALOR','FRÍO','AIREACIÓN','pH +','pH −','FILTRO'];
    for(let i=0;i<6;i++){
      const x=-L/2-.5*u+(i%3)*(L+u)/2,z=i<3?W/2+.48*u:-W/2-.52*u;
      const mat=statusMaterial(i);equipment.push({x,z});
      if(i===3||i===4){cyl(x,.24*u,z,.12*u,.44*u,dark);cyl(x,.48*u,z,.08*u,.05*u,metal);}
      else{box(x,.2*u,z,.36*u,.34*u,.32*u,dark);cyl(x,.45*u,z,.13*u,.21*u,metal);for(let k=0;k<4;k++)box(x,.4*u+k*.035*u,z,.29*u,.01*u,.25*u,dark);}
      cyl(x,.58*u,z,.03*u,.035*u,mat);label(equipNames[i],x,.85*u,z,activity(i)?'#80ecc4':'#9fb5c4',.13*u);
      const toZ=i<3?W*.3:-W*.3;
      pipe([[x,.14*u,z],[x,.14*u,z*.82],[x,H*.25,toZ]],metal,.025*u);
      if((i===0||i===1)&&activity(i)){const heat=new T.MeshBasicMaterial({color:i===0?0xff9064:0x5aaef5,transparent:true,opacity:.32,depthWrite:false});ring(x,.35*u,z,.27*u,heat,.035*u);}
    }
    // Inlet/outlet pipes with hand valves and effective flow markers.
    const flows=[];
    [6,7].forEach((index,k)=>{
      const x=(k===0?-1:1)*(L/2+.23*u),z=W*.12;
      const points=[[x,-.08*u,z+W*.38],[x,H+.18*u,z+W*.38],[x,H+.18*u,z],[x+(k===0?.4:-.4)*u,H+.18*u,z],[x+(k===0?.4:-.4)*u,H*.55,z]];
      pipe(points,metal,.055*u);
      const valve=ring(x,H*.65,z+W*.38,.11*u,statusMaterial(index),.018*u);valve.rotation.x=0;valve.rotation.y=Math.PI/2;
      label(k===0?'ENTRADA':'SALIDA',x,H+.47*u,z+W*.38,activity(index)?'#80ecc4':'#9fb5c4',.13*u);
      if(activity(index)){
        const curve=new T.CatmullRomCurve3((k===0?points:[...points].reverse()).map(p=>new T.Vector3(...p)),false,'catmullrom',.1);
        for(let i=0;i<6;i++){const bead=mesh(new T.SphereGeometry(.062*u,8,6),cyan);flows.push({mesh:bead,curve,phase:i/6});bead.position.copy(curve.getPoint(i/6));}
      }
    });
    // Submerged diffuser, bubbles driven exclusively by recorded mean air action.
    const diffuser=cyl(L*.12,.06*u,W*.08,.19*u,.07*u,dark);
    const bubbles=[];
    if(activity(2)&&h!==null&&h>0){
      const bubbleMat=new T.MeshPhysicalMaterial({color:0xb0f2fa,transparent:true,opacity:.6,roughness:.1,metalness:.3,depthWrite:false});
      for(let i=0;i<34;i++){const phase=i/34;const b=mesh(new T.SphereGeometry((.013+i%4*.005)*u,8,6),bubbleMat);const x=L*.12+Math.sin(i*4)*.15*u,z=W*.08+Math.cos(i*6)*.15*u;b.position.set(x,h*phase,z);bubbles.push({mesh:b,x,z,phase});}
    }
    // Filtration indication is an effective-action indicator, never an inferred order.
    let rotor;
    if(activity(5)){const {x,z}=equipment[5];rotor=box(x,.59*u,z,.22*u,.02*u,.03*u,statusMaterial(5));}
    // Level ruler shows physical geometry; camera motion does not alter it.
    for(let i=0;i<=4;i++){const y=H*i/4;line([[L/2+.09*u,y,-W/2],[L/2+.18*u,y,-W/2]],0x7eaabc);}
    let azimuth=.78,elevation=.49,distance=9.1,dragging=false,lastX=0,lastY=0,elapsed=0,lastStamp=null,lastTick=null;
    const target=new T.Vector3(0,H*root.scale.y*.45,0);
    function render(){camera.position.set(target.x+distance*Math.cos(elevation)*Math.sin(azimuth),target.y+distance*Math.sin(elevation),target.z+distance*Math.cos(elevation)*Math.cos(azimuth));camera.lookAt(target);renderer.render(scene,camera);}
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
    let frames=0;
    function animate(stamp){
      if(!running)return;
      // This clock only illustrates the last confirmed interval; x, y and t stay fixed.
      if(document.visibilityState==='visible'){
        const delta=lastTick===null?0:Math.min((stamp-lastTick)/1000,.05);elapsed+=delta;lastTick=stamp;
        if(lastStamp===null||stamp-lastStamp>=32){
          bubbles.forEach(b=>{b.mesh.position.y=((b.phase+elapsed*.25)%1)*h;});
          flows.forEach(f=>f.mesh.position.copy(f.curve.getPoint((f.phase+elapsed*.16)%1)));
          fish.forEach(f=>{f.group.position.x=f.origin.x+Math.sin(elapsed*.5+f.phase)*.04*u;f.group.rotation.z=Math.sin(elapsed*2+f.phase)*.035;});
          if(rotor)rotor.rotation.y=elapsed*2;
          render();frames++;lastStamp=stamp;
        }
      }else {lastStamp=null;lastTick=null;}
      raf=requestAnimationFrame(animate);
    }
    if(data.animate && !window.matchMedia('(prefers-reduced-motion: reduce)').matches)raf=requestAnimationFrame(animate);
    window.addEventListener('pagehide',()=>{running=false;if(raf!==null)cancelAnimationFrame(raf);observer.disconnect();scene.traverse(o=>{if(o.geometry)o.geometry.dispose();if(o.material){if(o.material.map)o.material.map.dispose();o.material.dispose();}});renderer.dispose();},{once:true});
    text('render-badge','3D · THREE.JS LOCAL');
    window.__aquacontrol={mode:'3D',snapshot:data,scene,camera,renderer,static:!data.animate,get frames(){return frames;}};
  }
  if(data.force_fallback)fallback('selección manual');
  else{try{start3d();}catch(error){console.warn('AquaControl: alternativa 2.5D',error.message);fallback('WebGL no disponible');}}
})();
