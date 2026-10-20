from copy import deepcopy
import inspect
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import zipfile
import io
import numpy as np
import pytest
from piscicultura.config import make_config,RunConfig,DEFAULTS,duplicate_profile,event,VARIABLES
from piscicultura.control import Measurement,decide
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService
from piscicultura.export import export_bytes
from piscicultura.metrics import series_metrics
from piscicultura.scenarios import noise_table,conditions
from piscicultura.sensors import measure


def frame(values,qualities=None): return Measurement(0,0,tuple(values),tuple(qualities or ['GOOD']*5),('',)*5)


def test_AC09():
    c=make_config();r=c['profile']['references'];s=c['controller'];op=c['open_commands']
    def call(y,m=None,strategy='closed'): return decide(strategy,r,s,op,frame(y),m or [0]*5)
    for j,delta in [(0,.3),(2,.15),(4,.03)]:
        for sign in [-1,1]:
            y=r.copy();y[j]=r[j]+sign*delta; assert call(y)[0][j]==0
            y[j]+=sign*1e-8; assert call(y)[0][j]==-sign
            memory=[0]*5;memory[j]=-sign
            y[j]=r[j]-sign*2*delta
            assert call(y,memory)[0][j]==0  # apagar, sin invertir
            assert call(y)[0][j]==sign
    y=r.copy();y[1]-=.2;assert call(y)[0][1]==1
    y[1]=r[1]+.2;assert call(y,[0,1,0,0,0])[0][1]==0
    y[1]=r[1];assert call(y,[0,1,0,0,0])[0][1]==1
    y=r.copy();y[3]=15;assert call(y)[0][3]==1
    y[3]=10;assert call(y,[0,0,0,1,0])[0][3]==0
    assert np.array_equal(call(r,strategy='open')[0],call([None]*5,strategy='open')[0])
    assert list(inspect.signature(decide).parameters)==['strategy','reference','settings','open_commands','frame','memory']

@pytest.mark.parametrize('profile',range(3))
def test_AC10(laboratory,profile):
    run,obs,_=laboratory;a=run(profile,'S0','open')
    diff=np.max(abs(np.array([s['x'] for s in a['samples']])-a['run']['config']['x0']),axis=0)
    obs[f'AC10_p{profile}']=dict(max_error=diff.tolist(),status=a['run']['status'])
    assert a['run']['status']=='COMPLETED';assert np.all(diff<=DEFAULTS['acceptance']['replay_abs_tolerances'])

@pytest.mark.parametrize('profile',range(3))
@pytest.mark.parametrize('strategy',['open','closed'])
def test_AC11(laboratory,profile,strategy):
    run,obs,service=laboratory;a=run(profile,'S1',strategy)
    rid=service.prepare(a['run']['config'],a['run']['noise']);repeat=service.run_all(rid)
    b=service.repo.records(rid,'samples')
    diff=np.max(abs(np.array([s['x'] for s in a['samples']])-np.array([s['x'] for s in b])),axis=0)
    obs[f'AC11_p{profile}_{strategy}']=dict(max_error=diff.tolist(),samples=len(b),decisions=len(service.repo.records(rid,'decisions')),status=repeat['status'])
    assert len(a['samples'])==len(b)==2881
    assert len(a['decisions'])==len(service.repo.records(rid,'decisions'))==2880
    assert a['run']['status']==repeat['status']=='COMPLETED'
    assert np.all(diff<=DEFAULTS['acceptance']['replay_abs_tolerances'])
    assert np.array_equal(a['run']['noise'],repeat['noise'])

@pytest.mark.parametrize('profile',range(3))
def test_AC12(laboratory,profile):
    run,obs,_=laboratory;a=run(profile,'S2','open');b=run(profile,'S2','closed')
    m=b['metrics'];ratio=m['J']/a['metrics']['J']
    obs[f'AC12_p{profile}']=dict(J_open=a['metrics']['J'],J_closed=m['J'],ratio=ratio,recovery_s=m['x']['recovery_s'],in_band_4_12h=m['window_4_12h']['in_band_fraction'])
    assert a['run']['status']==b['run']['status']=='COMPLETED'
    assert all(v is not None and v<=14400 for v in m['x']['recovery_s'])
    assert min(m['window_4_12h']['in_band_fraction'])>=.95 and ratio<=.8
    # Diferencias autorizadas: solo estrategia; tabla de ruido y estados iguales.
    ca=deepcopy(a['run']['config']);cb=deepcopy(b['run']['config']);ca.pop('strategy');cb.pop('strategy');assert ca==cb
    assert a['run']['noise']==b['run']['noise']

@pytest.mark.parametrize('profile',range(3))
@pytest.mark.parametrize('scenario',['S3','S4'])
def test_AC13(laboratory,profile,scenario):
    run,obs,_=laboratory
    a=run(profile,scenario,'open');b=run(profile,scenario,'closed')
    obs[f'AC13_{scenario}_p{profile}']={s:dict(status=v['run']['status'],cause=v['run']['cause'],alarm_transitions=sum(e['category']=='alarm' for e in v['events']),usage=v['metrics']['usage']) for s,v in [('open',a),('closed',b)]}
    assert b['run']['status']=='COMPLETED'
    if scenario=='S3':
        eligible=[s for s in b['samples'] if 25200<=s['time_s']<28800 and .9<=s['x'][4]<=1.1]
        assert eligible
        obs[f'AC13_{scenario}_p{profile}']['return_level_s']=eligible[0]['time_s']-25200
    assert any(e['category']=='injection' for e in b['events'])

@pytest.mark.parametrize('profile',range(3))
@pytest.mark.parametrize('scenario',['S5','S7'])
def test_AC14(laboratory,profile,scenario):
    run,obs,_=laboratory;a=run(profile,scenario,'open');b=run(profile,scenario,'closed')
    obs[f'AC14_{scenario}_p{profile}']=dict(open_status=a['run']['status'],closed_status=b['run']['status'],closed_time=b['run']['time_s'],closed_decisions=len(b['decisions']),quality_7200=next(s['qualities'][1] for s in b['samples'] if s['time_s']==7200))
    if scenario=='S5':
        assert b['run']['status']=='FAILED' and b['run']['time_s']==7200
        assert all(d['time_s']<7200 for d in b['decisions'])
        assert a['run']['status']=='COMPLETED'
        assert all(d['commands']==a['run']['config']['open_commands'] for d in a['decisions'])
        assert any(s['values'][1] is None and s['qualities'][1]=='MISSING' for s in a['samples'])
    else:
        for result in [a,b]:
            assert result['run']['status']=='COMPLETED'
            for sample in result['samples']:
                if 7200<=sample['time_s']<14400:
                    k=sample['sample_index'];expected=sample['x'][1]-.5+.02*result['run']['noise'][k][1]
                    assert abs(sample['values'][1]-expected)<1e-12 and sample['qualities'][1]=='GOOD'
            assert not any(e['category']=='alarm' and 'SESGO' in e['code'] for e in result['events'])

@pytest.mark.parametrize('profile',range(3))
@pytest.mark.parametrize('scenario',['S6','S9'])
def test_AC15(laboratory,profile,scenario):
    run,obs,_=laboratory;items={s:run(profile,scenario,s) for s in ['open','closed']}
    obs[f'AC15_{scenario}_p{profile}']={s:dict(status=v['run']['status'],time_s=v['run']['time_s'],cause=v['run']['cause'],termination=v['run']['termination_state']) for s,v in items.items()}
    for a in items.values():
        if scenario=='S6':
            assert a['run']['status']=='COMPLETED'
            actions=[r for r in a['actions'] if r['actuator_id']=='air' and 7200<=r['start_s']<21600]
            assert actions and all(r['availability']==0 and r['mean_effective']==0 for r in actions)
            assert any(r['actuator_id']=='air' and r['start_s']==21600 and r['availability']==1 for r in a['actions'])
        else:
            assert a['run']['status']=='FAILED' and a['run']['cause']=='CRUCE_DOMINIO'
            t=a['run']['termination_state'];assert abs(t['state'][4]-.25)<1e-9
            assert t['time_s']%60!=0 and a['samples'][-1]['time_s']<t['time_s']


def test_AC16(laboratory):
    run,obs,s=laboratory;a=run(0,'S1','closed');rid=s.prepare(a['run']['config'],a['run']['noise'])
    first=s.advance(rid,'first',0);counts=[len(s.repo.records(rid,t)) for t in ['samples','decisions','events']]
    s.pause(rid); before=s.repo.get(rid)
    for _ in range(3): s.repo.get(rid);s.repo.records(rid,'samples')
    assert s.repo.get(rid)==before
    assert s.advance(rid,'first',0)==first
    assert counts==[len(s.repo.records(rid,t)) for t in ['samples','decisions','events']]
    with pytest.raises(ValueError): s.advance(rid,'bad',1)
    s.resume(rid);s.run_all(rid)
    b=s.repo.records(rid,'samples');diff=np.max(abs(np.array([v['x'] for v in a['samples']])-np.array([v['x'] for v in b])),axis=0)
    assert np.all(diff<=DEFAULTS['acceptance']['replay_abs_tolerances'])
    obs['AC16']=dict(max_error=diff.tolist(),first_batch_counts=counts,final_samples=len(b))


def test_AC17(tmp_path,laboratory):
    _,obs,_=laboratory;path=tmp_path/'atomic.sqlite';repo=SQLiteRepository(path);s=SimulationService(repo)
    rid=s.prepare(make_config(0,'S0','open'));s.advance(rid,'ok',0)
    prior=repo.get(rid);counts={t:len(repo.records(rid,t)) for t in ['samples','decisions','actuator_records','events']}
    repo.fail_after=3
    with pytest.raises(RuntimeError,match='ERROR_PERSISTENCIA'): s.advance(rid,'fail',1)
    assert counts=={t:len(repo.records(rid,t)) for t in counts}
    assert repo.receipt(rid,'fail') is None
    after=repo.get(rid);assert after['state']==prior['state'] and after['time_s']==prior['time_s'] and after['status']=='FAILED'
    reopened=SQLiteRepository(path);assert reopened.get(rid)['status']=='FAILED'
    with zipfile.ZipFile(io.BytesIO(export_bytes(reopened,rid))) as archive:
        manifest=json.loads(archive.read('manifest.json'));assert manifest['run_id']==rid and manifest['units']['ph']=='1'
        assert b'run_id' in archive.read('samples.csv') and 'noise.csv' in archive.namelist()
    assert reopened.db.execute('PRAGMA foreign_keys').fetchone()[0]==1
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError):
        with reopened.db: reopened.db.execute('INSERT INTO samples VALUES (?,?,?,?)',('absent',0,0,'{}'))
    orphan=tmp_path/'orphan.sqlite'
    code="from piscicultura.repository import SQLiteRepository; from piscicultura.service import SimulationService; from piscicultura.config import make_config; s=SimulationService(SQLiteRepository("+repr(str(orphan))+")); r=s.prepare(make_config(0,'S0','open')); s.advance(r,'a',0)"
    subprocess.run([sys.executable,'-c',code],check=True)
    repo2=SQLiteRepository(orphan);assert repo2.list()[0]['status']=='INTERRUPTED'
    obs['AC17']=dict(counts_before_and_after=counts,confirmed_time=after['time_s'],status=after['status'],cause=after['cause'],orphan_status=repo2.list()[0]['status'],export_manifest=manifest)
    repo.close();reopened.close();repo2.close()

@pytest.mark.parametrize('profile',range(3))
@pytest.mark.parametrize('strategy',['open','closed'])
def test_AC18(laboratory,profile,strategy):
    run,obs,_=laboratory;a=run(profile,'S2',strategy);b=run(profile,'S2',strategy,True)
    diff=np.max(abs(np.array([s['x'] for s in a['samples']])-np.array([s['x'] for s in b['samples']])),axis=0)
    obs[f'AC18_p{profile}_{strategy}']=dict(max_error=diff.tolist(),tolerances=DEFAULTS['acceptance']['grid_refinement_abs_tolerances'])
    assert np.all(diff<=DEFAULTS['acceptance']['grid_refinement_abs_tolerances'])


def test_AC19(laboratory):
    _,obs,_=laboratory;m=series_metrics([0,1,2],[[0],[2],[0]],[0],[[-1,1]])
    assert m['iae']==[2.] and m['outside_s']==[1.]
    from piscicultura.metrics import evaluate
    from tests.test_core import isolated
    c=isolated();c['parameters']['heater_max_W']=10000
    r=dict(config=c,termination_state=None)
    samples=[dict(time_s=t,x=[20,2,8,40,1],values=[20,2,8,40,1]) for t in [0,3600]]
    action=dict(actuator_id='heater',start_s=0,end_s=3600,mean_effective=1,disturbances=dict(rain=0,leak=0))
    energy=evaluate(r,samples,[action])['usage']['partial_energy_kWh'];assert abs(energy-10)<=1e-6
    obs['AC19']=dict(iae=m['iae'],outside_s=m['outside_s'],energy_kWh=energy)


def test_AC20(tmp_path,laboratory,monkeypatch,artifact_dir):
    _,obs,_=laboratory
    # Prohibición efectiva de red en el núcleo durante preparación, integración, guardado y exportación.
    import socket
    def denied(*args,**kwargs): raise AssertionError('RED_PROHIBIDA')
    monkeypatch.setattr(socket.socket,'connect',denied);monkeypatch.setattr(socket,'create_connection',denied)
    durations=[];benchmark_index=[]
    benchmark_dir=artifact_dir/'benchmark';benchmark_dir.mkdir(exist_ok=True)
    for i in range(3):
        repo=SQLiteRepository(tmp_path/f'bench{i}.sqlite');s=SimulationService(repo)
        start=time.perf_counter();rid=s.prepare(make_config(0,'S8','closed'));result=s.run_all(rid);durations.append(time.perf_counter()-start)
        assert result['status']=='COMPLETED' and len(repo.records(rid,'samples'))==2881
        archive=export_bytes(repo,rid);assert repo.list() and archive
        (benchmark_dir/f'S8_rep{i}.zip').write_bytes(archive)
        benchmark_index.append(dict(repetition=i,run_id=rid,duration_s=durations[-1],archive=f'S8_rep{i}.zip'))
        repo.close()
    code="""
import sys
class Block:
 def find_spec(self,fullname,*args):
  if fullname.split('.')[0] in {'streamlit','plotly'}: raise AssertionError(fullname)
sys.meta_path.insert(0,Block())
from piscicultura.config import make_config
from piscicultura.engine import initial,advance
from piscicultura.scenarios import noise_table
c=make_config(0,'S0','open'); r,b=advance(initial(c),c,noise_table(c)); assert r.time_s==60
"""
    subprocess.run([sys.executable,'-c',code],check=True)
    (benchmark_dir/'index.json').write_text(json.dumps(benchmark_index,indent=2))
    obs['AC20']=dict(durations_s=durations,median_s=statistics.median(durations),threshold_s=60,network='socket connect denegado',hardware_eligibility='NO EVALUABLE hasta verificar almacenamiento SSD y equipo local de referencia')
    # El umbral se registra, pero no acredita RNF10 en hardware no verificable.
    assert all(d>0 for d in durations)
