"""Reproducir con epsilon persistido; nunca regenerar el ruido desde la semilla."""
import argparse
import csv
import io
import json
from pathlib import Path
import zipfile
import numpy as np
from piscicultura.config import VARIABLES,DEFAULTS
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService
from piscicultura.export import export_bytes


def main():
    parser=argparse.ArgumentParser(description='Reproducir una exportación y comprobar sus tolerancias')
    parser.add_argument('archive',type=Path);parser.add_argument('--db',default='work/replay.sqlite');parser.add_argument('--output',type=Path,default=Path('work/replay'))
    a=parser.parse_args()
    with zipfile.ZipFile(a.archive) as z:
        config=json.loads(z.read('config.json'));meta=json.loads(z.read('metadata.json'))
        rows=list(csv.DictReader(io.StringIO(z.read('noise.csv').decode())))
        noise=np.array([[float(row[v]) for v in VARIABLES] for row in rows])
        expected=list(csv.DictReader(io.StringIO(z.read('samples.csv').decode())))
    repo=SQLiteRepository(a.db);service=SimulationService(repo);rid=service.prepare(config,noise)
    if meta['status']=='STOPPED':
        while service.active[rid][2].time_s<meta['time_s']: service.advance(rid,'replay-'+str(service.active[rid][2].k),service.active[rid][2].k)
        service.stop(rid)
    else: service.run_all(rid)
    samples=repo.records(rid,'samples');run=repo.get(rid)
    if len(samples)!=len(expected): raise AssertionError('Número de muestras distinto')
    dx=np.max(abs(np.array([s['x'] for s in samples])-np.array([[float(s['x_'+v]) for v in VARIABLES] for s in expected])),axis=0) if samples else np.zeros(5)
    assert np.all(dx<=DEFAULTS['acceptance']['replay_abs_tolerances'])
    assert run['status']==meta['status'] and abs(run['time_s']-meta['time_s'])<1e-7
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/(rid+'.zip')).write_bytes(export_bytes(repo,rid))
    result=dict(source=str(a.archive),run_id=rid,status=run['status'],time_s=run['time_s'],max_abs_error_x=dx.tolist(),tolerances=DEFAULTS['acceptance']['replay_abs_tolerances'],noise_source='CSV persistido; sin regeneración')
    (a.output/'replay_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False))
    repo.close()

if __name__=='__main__':main()
