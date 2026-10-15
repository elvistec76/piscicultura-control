"""Reproduce OBS01–03 sin modificar código ni evidencias del repositorio.

Uso: python reproducir_observaciones.py --project /ruta/piscicultura-control
Ejecutar con las dependencias del proyecto instaladas. Imprime hallazgos;
después del arreglo los observados deben cambiar según las condiciones OBS.
"""
from pathlib import Path
import argparse,json,sys,tempfile

parser=argparse.ArgumentParser()
parser.add_argument('--project',type=Path,required=True)
args=parser.parse_args()
sys.path.insert(0,str(args.project.resolve()))
from piscicultura.config import make_config,RunConfig
from piscicultura.metrics import evaluate
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService

out={}
c=make_config(0,'S0','open');c['profile']['operating_bands'][0]=[28.5,28.5];c['time']['horizon_s']=3600
try:
    RunConfig.freeze(c)
except ValueError as e:
    out['OBS01']={'rejected_before_run':True,'cause':str(e)}
else:
    with tempfile.TemporaryDirectory() as folder:
        repo=SQLiteRepository(Path(folder)/'run.sqlite');s=SimulationService(repo);rid=s.prepare(c)
        result={'rejected_before_run':False}
        try:
            s.run_all(rid);result['unhandled_exception']=None
        except Exception as e:
            result['unhandled_exception']=type(e).__name__+': '+str(e)
        result.update(status=repo.get(rid)['status'],metrics_count=len(repo.records(rid,'metrics')))
        repo.close();out['OBS01']=result

c=make_config(0,'S0','open');c['profile']['operating_bands'][3]=[5,20];RunConfig.freeze(c)
samples=[{'time_s':t,'x':[28.5,6,7.5,2,1],'values':[28.5,6,7.5,2,1]} for t in [0,1800]]
m=evaluate({'config':c,'termination_state':None},samples,[])
out['OBS02']={'x_outside_s':m['x']['outside_s'][3],'y_outside_s':m['y']['per_variable'][3]['outside_s'][0],'expected_both_outside_s':0,'x_recovery_s':m['x']['recovery_s'][3],'y_recovery_s':m['y']['per_variable'][3]['recovery_s'][0],'expected_both_recovery_s':0}

c=make_config(0,'S2','closed');c['time']['control_interval_s']=135;RunConfig.freeze(c)
samples=[]
for t in range(0,43201,135):
    x=c['profile']['references'].copy()
    if t==14310:x[0]=32
    samples.append({'time_s':t,'x':x,'values':x.copy()})
m=evaluate({'config':c,'termination_state':None},samples,[])
out['OBS03']={'duration_s':m['window_4_12h']['duration_s'],'expected_duration_s':28800,'in_band_fraction_temperature':m['window_4_12h']['in_band_fraction'][0],'expected_left_convention_fraction':1-45/28800}
print(json.dumps(out,ensure_ascii=False,indent=2))
