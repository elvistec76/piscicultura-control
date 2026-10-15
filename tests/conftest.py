import hashlib
import json
from pathlib import Path
import pytest
from piscicultura.config import make_config
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService,environment
from piscicultura.export import export_bytes

@pytest.fixture(scope='session')
def laboratory():
    out=Path('evidence');(out/'runs').mkdir(parents=True,exist_ok=True)
    repo=SQLiteRepository('work/acceptance.sqlite');service=SimulationService(repo)
    cache={};observed={}
    def run(profile,scenario,strategy,refine=False):
        key=f'{scenario}_p{profile}_{strategy}'+('_refined' if refine else '')
        if key not in cache:
            c=make_config(profile,scenario,strategy)
            if refine:
                c['time']['max_step_s']=5;c['time']['rtol']=1e-9;c['time']['atol']=[a/100 for a in c['time']['atol']]
            rid=service.prepare(c);result=service.run_all(rid)
            samples=repo.records(rid,'samples');actions=repo.records(rid,'actuator_records')
            cache[key]=dict(run=result,samples=samples,actions=actions,events=repo.records(rid,'events'),decisions=repo.records(rid,'decisions'),metrics=service.compute_metrics(rid))
            (out/'runs'/f'{key}.zip').write_bytes(export_bytes(repo,rid))
        return cache[key]
    yield run,observed,service
    (out/'observations.json').write_text(json.dumps(observed,ensure_ascii=False,allow_nan=False,indent=2))
    (out/'run_index.json').write_text(json.dumps({k:dict(run_id=v['run']['run_id'],scenario=v['run']['config']['scenario'],profile=v['run']['config']['profile']['id'],strategy=v['run']['config']['strategy'],status=v['run']['status'],time_s=v['run']['time_s'],cause=v['run']['cause'],metrics=v['metrics'],archive='runs/'+k+'.zip') for k,v in cache.items()},ensure_ascii=False,indent=2))
    (out/'environment.json').write_text(json.dumps(environment(),indent=2))
    repo.close()
