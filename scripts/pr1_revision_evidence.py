"""Evidencia reproducible de las correcciones OBS01–03; no sustituye datos previos."""
import argparse
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from piscicultura.config import RunConfig, make_config
from piscicultura.export import export_bytes
from piscicultura.metrics import evaluate
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService, environment


def write_json(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,allow_nan=False,indent=2))


def fixtures(out):
    results={}
    for value in [2.,25.,None]:
        c=make_config(0,'S0','open');c['profile']['operating_bands'][3]=[5,20]
        samples=[]
        for i,t in enumerate([0,900,1800]):
            x=c['profile']['references'].copy();x[3]=2. if value is None else value
            y=x.copy()
            if value is None and i==1: y[3]=None
            samples.append(dict(time_s=t,x=x,values=y))
        results['OBS02_'+str(value)]=dict(type='Serie sintética para métricas, sin integración física',config=c,samples=samples,observed=evaluate(dict(config=c,termination_state=None),samples,[]))
    for count in [0,10,11]:
        c=make_config(0,'S2','closed');c['time']['control_interval_s']=135
        samples=[]
        for i,t in enumerate(range(0,43201,135)):
            x=c['profile']['references'].copy()
            if 106<=i<=106+count:x[0]=32
            samples.append(dict(time_s=t,x=x,values=x.copy()))
        expected_out=45+count*135
        results['OBS03_'+str(count)]=dict(type='Serie sintética para ventana, sin integración física',config=c,samples=samples,expected=dict(interval_s=[14400,43200],duration_s=28800,outside_s=expected_out,in_band_fraction=1-expected_out/28800),observed=evaluate(dict(config=c,termination_state=None),samples,[])['window_4_12h'])
    write_json(out/'synthetic_fixtures.json',results)


def failure_exports(out):
    exports=out/'failure_exports';exports.mkdir(exist_ok=True)
    index=[]
    for phase in ['completion','stop']:
        for fault in ['generation','nonfinite','persistence']:
            with tempfile.TemporaryDirectory() as folder:
                repo=SQLiteRepository(Path(folder)/'failure.sqlite');service=SimulationService(repo)
                c=make_config(0,'S0','open');c['time']['horizon_s']=3600;rid=service.prepare(c)
                if fault=='persistence':
                    repo.db.execute("CREATE TRIGGER fault BEFORE INSERT ON metrics BEGIN SELECT RAISE(ABORT,'PERSISTENCIA_INYECTADA_R1'); END")
                def broken(*args,**kwargs):
                    if fault=='generation': raise ValueError('GENERACION_INYECTADA_R1')
                    return dict(J=float('nan'))
                def execute():
                    if phase=='stop':service.advance(rid,'first',0);service.stop(rid)
                    else:service.run_all(rid)
                if fault=='persistence':execute()
                else:
                    with patch('piscicultura.service.evaluate',broken):execute()
                run=repo.get(rid);name=f'OBS01_{phase}_{fault}.zip'
                assert run['metrics_status']=='FAILED' and run['status']==('STOPPED' if phase=='stop' else 'COMPLETED')
                (exports/name).write_bytes(export_bytes(repo,rid))
                index.append(dict(phase=phase,fault=fault,run_id=rid,status=run['status'],metrics_status=run['metrics_status'],cause=run['metrics_cause'],time_s=run['time_s'],samples=len(repo.records(rid,'samples')),decisions=len(repo.records(rid,'decisions')),archive=name))
                repo.close()
    write_json(exports/'index.json',index)


def additional_runs(out):
    exports=out/'dt135';exports.mkdir(exist_ok=True)
    results=[]
    for profile in range(3):
        for strategy in ['open','closed']:
            with tempfile.TemporaryDirectory() as folder:
                repo=SQLiteRepository(Path(folder)/'run.sqlite');service=SimulationService(repo)
                c=make_config(profile,'S2',strategy);c['time']['control_interval_s']=135;RunConfig.freeze(c)
                rid=service.prepare(c);run=service.run_all(rid);m=repo.records(rid,'metrics')[0]
                assert run['status']=='COMPLETED' and run['metrics_status']=='READY' and m['window_4_12h']['duration_s']==28800
                name=f'S2_p{profile}_{strategy}_dt135.zip';(exports/name).write_bytes(export_bytes(repo,rid))
                results.append(dict(run_id=rid,profile=profile,strategy=strategy,status=run['status'],samples=len(repo.records(rid,'samples')),decisions=len(repo.records(rid,'decisions')),archive=name,metrics=m))
                repo.close()
    write_json(exports/'index.json',results)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path('evidence/correcciones_pr1'));args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    write_json(args.output/'environment.json',environment())
    fixtures(args.output);failure_exports(args.output);additional_runs(args.output)


if __name__=='__main__':main()
