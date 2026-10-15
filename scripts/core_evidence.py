import json, math, numpy as np
from tests.test_core import isolated,solve,volume_usage
from piscicultura.model import saturation
from piscicultura.actuators import mean_actions
from pathlib import Path
r={}
r['AC02']=[dict(temperature_C=t,expected=e,observed=saturation(t),absolute_error=abs(e-saturation(t)),tolerance=1e-6,factors=saturation(t,factors=True)[1:]) for t,e in [(10,11.28794737),(20,9.09242604),(30,7.55879605)]]
c=isolated();c['parameters'].update(exchange_m3_s=.0002,inlet_max_m3_s=.0008,leak_base_m3_s=.0001,evaporation_m3_s=.00001);c['z0'][4]=1
result=solve(c,600,[0,0,0,0,1]);usage=volume_usage(c,result,600)
r['AC03']=dict(expected=1.0414,observed=float(result[4]),tolerance=1e-7,inlet_m3=usage['inlet_m3'],outlet_m3=usage['outlet_m3'],test_config=c)
c=isolated();c['parameters']['heater_max_W']=10000;c['z0'][0]=1
r['AC04']=dict(expected=20.8600095557,observed=float(solve(c,3600,[1,0,0,0,0])[0]),tolerance=1e-6,test_config=c)
c=isolated();c['parameters']['k_natural_s_inv']=1e-4
r['AC05']=dict(expected=saturation(20)+(2-saturation(20))*math.exp(-.36),observed=float(solve(c,3600)[1]),tolerance=1e-5,test_config=c)
c=isolated();c['parameters']['ph_relaxation_s_inv']=1/86400
r['AC06']=dict(expected=7.4+.6*math.exp(-1/24),observed=float(solve(c,3600)[2]),tolerance=1e-6,test_config=c)
c=isolated();c['parameters']['k_settle_s_inv']=2e-5
r['AC07']=dict(expected=40*math.exp(-.072),observed=float(solve(c,3600)[3]),tolerance=1e-4,test_config=c)
c=isolated();r['AC08']=dict(expected=1-math.exp(-1),observed=float(solve(c,30,[1]*5)[5]),tolerance=1e-7,signed_means=mean_actions([1,0,0,0,0],np.array([-1,0,0,0,0]),120,[30]*5,np.ones(8)).tolist(),test_config=c)
for k,v in r.items():
 if isinstance(v,dict):v['absolute_error']=abs(v['observed']-v['expected'])
Path('evidence/core_checks.json').write_text(json.dumps(r,ensure_ascii=False,indent=2))
