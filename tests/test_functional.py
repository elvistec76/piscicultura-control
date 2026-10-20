"""Cobertura complementaria de RF/RNF que la matriz numérica no sustituye."""
from copy import deepcopy
import io
import json
import socket
import zipfile
import numpy as np
import pytest
from piscicultura import __version__
from piscicultura.config import make_config,RunConfig,duplicate_profile,event
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService
from piscicultura.scenarios import noise_table,conditions
from piscicultura.sensors import measure
from piscicultura.engine import initial,advance
from piscicultura.export import export_bytes
from tests.test_core import isolated,solve


def test_profile_copy_immutable_and_versions(tmp_path):
    repo=SQLiteRepository(tmp_path/'profiles.sqlite');s=SimulationService(repo);draft=make_config(0,'S0','open');rid=s.prepare(draft)
    draft['profile']['references'][0]=29
    assert repo.get(rid)['config']['profile']['references'][0]==28.5
    copied=duplicate_profile(repo.get(rid)['config']['profile'],'Copia editable');copied['references'][0]=29
    assert repo.get(rid)['config']['profile']['references'][0]==28.5
    env=repo.get(rid)['environment'];assert env['packages']['scipy'] and env['sqlite']
    assert repo.get(rid)['config']['model_version']=='1.0.0'
    repo.close()


def test_freeze_missing_invalid_noise_bias_and_event_boundaries():
    c=make_config(0,'S5');c['events']=[event('freeze',1,60,120,1,'1')];table=noise_table(c)
    d,g,f=conditions(c,0);a,last=measure(0,0,[28.5,6,7.5,10,1],table[0],c,f,[None]*5)
    _,_,f=conditions(c,60);b,last2=measure(1,60,[28.5,7,7.5,10,1],table[1],c,f,last)
    assert b.values[1]==a.values[1] and b.qualities[1]=='GOOD' and b.diagnostics[1]==''
    _,_,f=conditions(c,120);e,_=measure(2,120,[28.5,7,7.5,10,1],table[2],c,f,last2)
    assert e.values[1]==7+.02*table[2,1]
    _,_,f=conditions(c,60);m,_=measure(1,60,[28.5,7,7.5,10,1],table[1],c,f,[None]*5);assert m.values[1] is None and m.qualities[1]=='MISSING'
    c['sensor']['bias'][1]=100
    m,_=measure(0,0,[28.5,6,7.5,10,1],table[0],c,[],[None]*5);assert m.values[1] is None and m.qualities[1]=='INVALID'
    c['events']=[event('freeze',1,60,180,1,'1'),event('missing',1,120,240,1,'1')]
    with pytest.raises(ValueError): RunConfig.freeze(c)
    assert table.shape==(361,5) and np.max(abs(table))<=3


def test_event_combination_and_actuator_availability():
    c=make_config(0,'S0','open');c['events']=[event('leak','water',0,60,.001,'m³/s'),event('leak','water',0,120,.002,'m³/s'),event('availability',0,0,60,.5,'1'),event('availability',0,0,120,.3,'1')]
    RunConfig.freeze(c);d,g,_=conditions(c,0);assert d['leak']==.003 and g[0]==.3
    d,g,_=conditions(c,60);assert d['leak']==.002 and g[0]==.3


def test_terminal_invalid_no_decision_and_domain_crossing_receipt(tmp_path):
    repo=SQLiteRepository(tmp_path/'terminal.sqlite');s=SimulationService(repo)
    c=make_config(0,'S0','closed');c['events']=[event('missing',1,60,120,1,'1')]
    rid=s.prepare(c);receipt=s.advance(rid,'terminal',0)
    assert receipt['status']=='FAILED' and receipt['time_s']==60
    assert len(repo.records(rid,'samples'))==2 and len(repo.records(rid,'decisions'))==1
    assert s.advance(rid,'terminal',0)==receipt
    # Cruce parcial en el primer intervalo: empieza cerca del límite inferior.
    c=make_config(0,'S0','open');c['x0'][4]=.251;c['parameters']['leak_base_m3_s']=.01
    rid=s.prepare(c);receipt=s.advance(rid,'cross',0)
    assert receipt['status']=='FAILED' and 0<receipt['time_s']<60
    assert len(repo.records(rid,'samples'))==1 and len(repo.records(rid,'decisions'))==1
    assert s.advance(rid,'cross',0)==receipt
    repo.close()


def test_zero_stationary_not_domain_failure():
    c=isolated();c['x0'][1]=0;c['x0'][3]=0
    from piscicultura.model import integrate
    from piscicultura.scenarios import conditions
    d,g,_=conditions(c,0)
    result=integrate(0,np.r_[c['x0'],c['z0']],60,np.zeros(5),g,d,c)
    assert result.status==0 and result.y[1,-1]==result.y[3,-1]==0


def test_alarm_transitions_acknowledge_and_stop(tmp_path):
    repo=SQLiteRepository(tmp_path/'alarms.sqlite');s=SimulationService(repo)
    c=make_config(0,'S0','open');c['events']=[event('bias',0,0,60,4,'°C')]
    rid=s.prepare(c);s.advance(rid,'a',0);s.advance(rid,'b',1)
    alarms=[e for e in repo.records(rid,'events') if e['category']=='alarm' and e['target']=='temperature_C']
    assert [(a['transition'],a['code']) for a in alarms]==[('activation','LIMITE_CRITICO'),('clear','LIMITE_CRITICO')]
    before=repo.get(rid)['state'];repo.acknowledge(rid,alarms[0]['event_seq']);repo.acknowledge(rid,alarms[0]['event_seq'])
    assert repo.get(rid)['state']==before and repo.db.execute('SELECT COUNT(*) FROM acknowledgments').fetchone()[0]==1
    s.pause(rid);s.stop(rid);assert repo.get(rid)['status']=='STOPPED' and len(repo.records(rid,'samples'))==3
    repo.close()


def test_comparison_common_interval_and_exports(tmp_path):
    repo=SQLiteRepository(tmp_path/'comparison.sqlite');s=SimulationService(repo)
    c=make_config(0,'S0','closed');c['time']['horizon_s']=3600;c['events']=[event('missing',1,60,120,1,'1')]
    result=s.compare(c);assert result['common_duration_s']==60
    assert result['full']['closed']['status']=='FAILED' and result['full']['open']['status']=='COMPLETED'
    for strategy,rid in result['members'].items():
        assert result['common'][strategy]['interval_s']==[0,60]
        with zipfile.ZipFile(io.BytesIO(export_bytes(repo,rid))) as z:
            cfg=json.loads(z.read('config.json'));assert cfg['strategy']==strategy
            assert 'noise.csv' in z.namelist() and json.loads(z.read('metadata.json'))['environment']['code']==__version__
    assert repo.db.execute('SELECT COUNT(*) FROM comparison_members').fetchone()[0]==2
    repo.close()


def test_charts_offline(tmp_path,monkeypatch):
    from piscicultura.charts import figures
    def deny(*a,**k): raise AssertionError('Red no permitida')
    monkeypatch.setattr(socket.socket,'connect',deny)
    repo=SQLiteRepository(tmp_path/'graphs.sqlite');s=SimulationService(repo);rid=s.prepare(make_config(0,'S0','open'));s.advance(rid,'a',0)
    fs=figures(repo.get(rid),repo.records(rid,'samples'),repo.records(rid,'actuator_records'))
    assert len(fs)==6
    for f in fs:
        html=f.to_html(include_plotlyjs=True,full_html=True)
        assert 'cdn.plot.ly' not in html.split('<script src=')[0] or '<script src=' not in html
        assert f.layout.xaxis.title.text=='Tiempo simulado'
        assert f.layout.xaxis.ticktext and all('h' in label for label in f.layout.xaxis.ticktext)
    repo.close()
