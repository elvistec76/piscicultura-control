"""Regresiones de OBS01–03; las evidencias R1 de Work se conservan intactas."""
import io
import json
import sqlite3
import zipfile
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from piscicultura.config import VARIABLES, RunConfig, make_config
from piscicultura.export import export_bytes
from piscicultura.metrics import evaluate
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService
from tests.test_ui import by_label


def synthetic(config, times, variable=None, value=None):
    samples=[]
    for t in times:
        x=config['profile']['references'].copy()
        if variable is not None: x[variable]=value
        samples.append(dict(time_s=t,x=x,values=x.copy()))
    return samples


def evaluate_samples(config,samples,**kwargs):
    return evaluate(dict(config=config,termination_state=None),samples,[],**kwargs)


@pytest.mark.parametrize('variable',[0,1],ids=['T','C'])
def test_OBS01_zero_width_rejected_before_prepare(tmp_path,variable):
    c=make_config(0,'S0','open');r=c['profile']['references'][variable]
    c['profile']['operating_bands'][variable]=[r,r]
    repo=SQLiteRepository(tmp_path/'invalid.sqlite');s=SimulationService(repo)
    with pytest.raises(ValueError,match=VARIABLES[variable]+'.*operating_bands'):
        s.prepare(c)
    assert repo.list()==[] and not s.active
    repo.close()


@pytest.mark.parametrize('phase',['completion','stop','sensor_failure'])
@pytest.mark.parametrize('fault',['generation','nonfinite','persistence'])
def test_OBS01_metrics_failure_preserves_confirmed_run(tmp_path,monkeypatch,phase,fault):
    c=make_config(0,'S0','open');c['time']['horizon_s']=3600
    if phase=='sensor_failure':
        c['strategy']='closed'
        c['events']=[dict(kind='missing',target=1,start_s=60,end_s=120,magnitude=1,unit='1')]
    repo=SQLiteRepository(tmp_path/'metrics.sqlite');s=SimulationService(repo);rid=s.prepare(c)
    if fault=='generation':
        def broken(*args,**kwargs): raise ValueError('GENERACION_INYECTADA')
        monkeypatch.setattr('piscicultura.service.evaluate',broken)
    elif fault=='nonfinite':
        def nonfinite(*args,**kwargs): return dict(J=float('nan'))
        monkeypatch.setattr('piscicultura.service.evaluate',nonfinite)
    else:
        repo.db.execute("CREATE TRIGGER metrics_failure BEFORE INSERT ON metrics BEGIN SELECT RAISE(ABORT,'PERSISTENCIA_INYECTADA'); END")
    if phase=='stop':
        s.advance(rid,'first',0);before=repo.get(rid);s.stop(rid)
        expected='STOPPED'
        assert repo.get(rid)['state']==before['state']
    else:
        s.run_all(rid);expected='FAILED' if phase=='sensor_failure' else 'COMPLETED'
    run=repo.get(rid);samples=repo.records(rid,'samples');decisions=repo.records(rid,'decisions')
    assert run['status']==expected and run['metrics_status']=='FAILED'
    assert fault.upper() in run['metrics_cause']
    assert run['time_s']==(3600 if phase=='completion' else 60)
    assert len(samples)==(61 if phase=='completion' else 2)
    assert len(decisions)==(60 if phase=='completion' else 1)
    receipt=repo.receipt(rid,'first' if phase=='stop' else 'interval-0')
    assert receipt and s.advance(rid,receipt['command_id'],0)==receipt
    assert repo.records(rid,'metrics')==[]
    with zipfile.ZipFile(io.BytesIO(export_bytes(repo,rid))) as z:
        assert json.loads(z.read('metadata.json'))['metrics_status']=='FAILED'
        assert json.loads(z.read('manifest.json'))['metrics_cause']==run['metrics_cause']
    reopened=SQLiteRepository(repo.path)
    assert reopened.get(rid)['metrics_cause']==run['metrics_cause']
    assert reopened.records(rid,'samples')==samples
    reopened.close();repo.close()


def test_OBS01_metrics_retry_preserves_old_result_and_recovers(tmp_path,monkeypatch):
    repo=SQLiteRepository(tmp_path/'retry.sqlite');s=SimulationService(repo)
    c=make_config(0,'S0','open');rid=s.prepare(c);s.advance(rid,'a',0);s.stop(rid)
    before=repo.records(rid,'metrics');state=repo.get(rid)['state']
    with monkeypatch.context() as m:
        def broken(*args,**kwargs): raise ValueError('RECALCULO_INYECTADO')
        m.setattr('piscicultura.service.evaluate',broken)
        assert s.compute_metrics(rid) is None
    assert repo.get(rid)['metrics_status']=='FAILED' and repo.records(rid,'metrics')==before
    result=s.compute_metrics(rid)
    assert result==before[0] and repo.get(rid)['metrics_status']=='READY'
    assert repo.get(rid)['metrics_cause']=='' and repo.get(rid)['state']==state
    repo.close()


@pytest.mark.parametrize('value,expected_out,expected_recovery',[(2.,0.,0.),(25.,1800.,None)],ids=['below_lower','above_upper'])
def test_OBS02_turbidity_x_y_identity(value,expected_out,expected_recovery):
    c=make_config(0,'S0','open');c['profile']['operating_bands'][3]=[5,20];RunConfig.freeze(c)
    m=evaluate_samples(c,synthetic(c,[0,1800],3,value))
    for result,j in [(m['x'],3),(m['y']['per_variable'][3],0)]:
        assert result['outside_s'][j]==expected_out
        assert result['in_band_fraction'][j]==1-expected_out/1800
        assert result['recovery_s'][j]==expected_recovery
        assert result['iae'][j]==abs(value-10)*1800


def test_OBS02_missing_turbidity_keeps_coverage_and_no_integral():
    c=make_config(0,'S0','open');c['profile']['operating_bands'][3]=[5,20]
    samples=synthetic(c,[0,900,1800],3,2.);samples[1]['values'][3]=None
    m=evaluate_samples(c,samples)
    assert m['y']['coverage'][3]==pytest.approx(2/3) and m['y']['per_variable'][3] is None
    assert m['x']['outside_s'][3]==0 and m['x']['iae'][3]==14400


def test_OBS02_turbidity_in_window_and_common_comparison():
    c=make_config(0,'S2','closed');c['profile']['operating_bands'][3]=[5,20]
    samples=synthetic(c,range(0,43201,135),3,2.)
    full=evaluate_samples(c,samples);common=evaluate_samples(c,samples,end_s=43200)
    for m in [full,common]:
        assert m['x']['outside_s'][3]==m['window_4_12h']['outside_s'][3]==0
        assert m['window_4_12h']['in_band_fraction'][3]==1
        assert m['window_4_12h']['iae'][3]==8*28800


@pytest.mark.parametrize('dt',[60,135],ids=['aligned','unaligned'])
def test_OBS03_exact_window_left_interval(dt):
    c=make_config(0,'S2','closed');c['time']['control_interval_s']=dt;RunConfig.freeze(c)
    samples=synthetic(c,range(0,43201,dt))
    target=14310 if dt==135 else 14340
    next(s for s in samples if s['time_s']==target)['x'][0]=32.
    m=evaluate_samples(c,samples);w=m['window_4_12h']
    assert w['duration_s']==28800 and w['interval_s']==[14400,43200]
    assert w['outside_s'][0]==(45 if dt==135 else 0)
    assert w['in_band_fraction'][0]==1-(45 if dt==135 else 0)/28800
    # IAE recorta el trapecio de |x-r| con interpolación lineal del error absoluto.
    assert w['iae'][0]==pytest.approx(26.25 if dt==135 else 0,abs=1e-12)


@pytest.mark.parametrize('outside_count,expected_fraction',[(10,.9515625),(11,.946875)])
def test_OBS03_window_near_95_percent(outside_count,expected_fraction):
    c=make_config(0,'S2','closed');c['time']['control_interval_s']=135
    samples=synthetic(c,range(0,43201,135));samples[106]['x'][0]=32.  # t=14310: 45 s en ventana
    for sample in samples[107:107+outside_count]: sample['x'][0]=32.
    w=evaluate_samples(c,samples)['window_4_12h']
    assert w['duration_s']==28800 and w['in_band_fraction'][0]==pytest.approx(expected_fraction,abs=1e-12)
    assert (w['in_band_fraction'][0]>=.95)==(outside_count==10)


def test_OBS03_both_window_boundaries_and_iae():
    from piscicultura.metrics import series_metrics
    w=series_metrics([0,10,20],[[0],[2],[0]],[0],[[-1,1]],window=(5,15))
    assert w['duration_s']==10 and w['interval_s']==[5,15]
    assert w['outside_s']==[5] and w['in_band_fraction']==[.5]
    assert w['iae']==[15.]


@pytest.mark.parametrize('fault',['generation','persistence'])
def test_OBS01_ui_metrics_failure_is_visible(tmp_path,monkeypatch,fault):
    monkeypatch.setenv('PISCICULTURA_DB',str(tmp_path/'ui.sqlite'))
    at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()
    by_label(at.selectbox,'Escenario').select('S0').run()
    by_label(at.button,'Validar y preparar corrida').click().run()
    by_label(at.button,'Avanzar un intervalo').click().run()
    service=at.session_state['service'];rid=at.session_state['run_id']
    if fault=='generation':
        def broken(*args,**kwargs): raise ValueError('UI_GENERACION_INYECTADA')
        monkeypatch.setattr('piscicultura.service.evaluate',broken)
    else:
        service.repo.db.execute("CREATE TRIGGER metrics_failure BEFORE INSERT ON metrics BEGIN SELECT RAISE(ABORT,'UI_PERSISTENCIA_INYECTADA'); END")
    by_label(at.button,'Detener').click().run()
    assert not at.exception
    assert service.repo.get(rid)['status']=='STOPPED'
    assert any('Métricas no disponibles' in e.value for e in at.error)
    assert len(service.repo.records(rid,'samples'))==2


def test_OBS01_ui_zero_width_creates_no_run(tmp_path,monkeypatch):
    monkeypatch.setenv('PISCICULTURA_DB',str(tmp_path/'ui_invalid.sqlite'))
    at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()
    by_label(at.number_input,'Temperatura: banda inferior (°C)').set_value(28.5)
    by_label(at.number_input,'Temperatura: banda superior (°C)').set_value(28.5)
    by_label(at.button,'Validar y preparar corrida').click().run()
    assert not at.exception and at.session_state['service'].repo.list()==[]
    assert any('operating_bands' in e.value for e in at.error)


def test_OBS01_comparison_preserves_metric_diagnostics(tmp_path):
    repo=SQLiteRepository(tmp_path/'compare.sqlite');s=SimulationService(repo)
    repo.db.execute("CREATE TRIGGER metrics_failure BEFORE INSERT ON metrics BEGIN SELECT RAISE(ABORT,'COMPARACION_INYECTADA'); END")
    c=make_config(0,'S0','open');c['time']['horizon_s']=3600
    comparison=s.compare(c)
    for strategy in ['open','closed']:
        full=comparison['full'][strategy]
        assert full['status']=='COMPLETED' and full['metrics_status']=='FAILED' and full['metrics'] is None
        assert 'PERSISTENCE' in full['metrics_cause']
        assert comparison['common_metrics_diagnostics'][strategy]['status']=='READY'
        assert comparison['common'][strategy]['interval_s']==[0,3600]
    repo.close()


def test_OBS01_legacy_database_readable_without_invented_diagnosis(tmp_path):
    path=tmp_path/'legacy.sqlite';repo=SQLiteRepository(path);s=SimulationService(repo)
    a=s.prepare(make_config(0,'S0','open'));s.advance(a,'a',0);s.stop(a)
    b=s.prepare(make_config(0,'S0','open'));s.advance(b,'b',0);repo.set_status(b,'COMPLETED')
    before=repo.records(a,'samples')
    with repo.db: repo.db.execute('DROP TABLE metric_diagnostics')
    repo.close();repo=SQLiteRepository(path)
    assert repo.get(a)['metrics_status']=='READY' and repo.records(a,'samples')==before
    assert repo.get(b)['metrics_status']=='UNAVAILABLE'
    assert repo.get(b)['metrics_cause']=='SIN_DIAGNOSTICO_HISTORICO'
    repo.close()


def test_OBS01_ui_comparison_without_metrics(tmp_path,monkeypatch):
    monkeypatch.setenv('PISCICULTURA_DB',str(tmp_path/'ui_compare.sqlite'))
    at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()
    by_label(at.selectbox,'Escenario').select('S0').run()
    by_label(at.number_input,'Horizonte (h)').set_value(1.)
    by_label(at.button,'Validar y preparar corrida').click().run()
    by_label(at.button,'Detener').click().run()
    service=at.session_state['service']
    service.repo.db.execute("CREATE TRIGGER metrics_failure BEFORE INSERT ON metrics BEGIN SELECT RAISE(ABORT,'UI_COMPARACION_INYECTADA'); END")
    by_label(at.button,'Comparar estrategias con la configuración validada').click().run()
    assert not at.exception
    comparison=at.session_state['comparison']
    assert all(v['metrics'] is None and v['metrics_status']=='FAILED' for v in comparison['full'].values())
