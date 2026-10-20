import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {randomUUID} from 'node:crypto';
import test from 'node:test';
import vm from 'node:vm';

const wrapper=readFileSync(new URL('../../piscicultura/tank_assets/live.js',import.meta.url),'utf8');
const template='<script id="snapshot" type="application/json">__SNAPSHOT_JSON__</script>';
const {default:mount}=await import('data:text/javascript;base64,'+Buffer.from(wrapper.replace('/*__DOCUMENT__*/',JSON.stringify(template))).toString('base64'));

test('repeated snapshots reuse the iframe and load its document only once',()=>{
  const frames=[],messages=[];
  globalThis.crypto??={randomUUID};
  globalThis.document={createElement(){
    let documentValue='';
    return {dataset:{},style:{},loads:0,setAttribute(){},contentWindow:{postMessage(message){messages.push(message);}},
      set srcdoc(value){this.loads++;documentValue=value;},get srcdoc(){return documentValue;}};
  }};
  const host={querySelector(){return frames[0];},appendChild(frame){frames.push(frame);}};
  mount({parentElement:host,data:{state_time_s:0,profile:'</script><img onerror=bad>'}});
  const frame=frames[0],identity=frame.dataset.instance;
  for(let time=60;time<=1200;time+=60)mount({parentElement:host,data:{state_time_s:time}});
  assert.equal(frames.length,1);
  assert.equal(frame.loads,1);
  assert.equal(frame.dataset.instance,identity);
  assert.equal(messages.at(-1).snapshot.state_time_s,1200);
  assert.ok(frame.srcdoc.includes('\\u003c/script\\u003e'));
  assert.ok(!frame.srcdoc.includes('<img'));
  // A delayed iframe load receives the latest data, rather than the first step.
  frame.onload();
  assert.equal(messages.at(-1).snapshot.state_time_s,1200);
});

test('scene updates replace the readings without duplicating cards or alarms',()=>{
  const ids=[...readFileSync(new URL('../../piscicultura/tank_assets/scene.html',import.meta.url),'utf8').matchAll(/id="([^"]+)"/g)].map(m=>m[1]);
  function element(){return {style:{},children:[],classList:{add(){},remove(){}},append(...items){this.children.push(...items);},replaceChildren(){this.children=[];}};}
  const elements=Object.fromEntries(ids.map(id=>[id,element()]));
  const initial={run_id:'run',status:'PREPARED',profile:'Tilapia',geometry:{shape:'Circular',area_m2:10,radius_m:1.78,height_m:1.5},state:[28.5,6,7.5,10,1],state_time_s:0,horizon_s:3600,sample_time_s:null,interval_s:null,
    sensors:Array.from({length:5},(_,j)=>({label:'Sensor '+j,key:String(j),value:null,quality:'MISSING',unit:'m',reference:1,in_band:null})),
    actuators:Array.from({length:8},()=>({label:'Equipo',effective:null,availability:null})),alarms:[],warnings:[],cause:'',force_fallback:true};
  elements.snapshot.textContent=JSON.stringify(initial);
  const handlers={},parent={};
  const window={parent,addEventListener(type,fn){handlers[type]=fn;}};
  vm.runInNewContext(readFileSync(new URL('../../piscicultura/tank_assets/scene.js',import.meta.url),'utf8'),{
    document:{getElementById:id=>elements[id],createElement:element,querySelectorAll:()=>[]},window,console});
  const next={...initial,status:'RUNNING',state_time_s:60,sample_time_s:60};
  handlers.message({source:{},data:{type:'aquacontrol:snapshot',snapshot:next}});
  assert.equal(window.__aquacontrol.snapshot.state_time_s,0,'foreign senders must be ignored');
  for(let time=60;time<=600;time+=60)handlers.message({source:parent,data:{type:'aquacontrol:snapshot',snapshot:{...next,state_time_s:time}}});
  assert.equal(window.__aquacontrol.snapshot.state_time_s,600);
  assert.equal(elements.sensors.children.length,5);
  assert.equal(elements.actuators.children.length,8);
  assert.equal(elements.alarms.children.length,1);
  assert.equal(elements['state-time'].textContent,'0 h 10 min de 1 h');
});
