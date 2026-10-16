"""Visual contract exercised against real confirmed simulation and Streamlit."""
import json
import math
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest
from streamlit.testing.v1 import AppTest

from piscicultura.config import ACTIONS, RunConfig, event, make_config
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService
from piscicultura.tank_view import SHAPES, geometry, render_html, snapshot
from tests.test_ui import by_label


def view(repo, rid, shape='Circular', **kwargs):
    return snapshot(repo.get(rid), repo.records(rid, 'samples'),
                    repo.records(rid, 'actuator_records'), repo.records(rid, 'events'),
                    shape, **kwargs)


@pytest.mark.parametrize('profile', range(3))
@pytest.mark.parametrize('strategy', ['open', 'closed'])
def test_visual_switch_preserves_x_y_actions_alarms_J_and_decisions(tmp_path, profile, strategy):
    repo = SQLiteRepository(tmp_path / 'view.sqlite')
    service = SimulationService(repo)
    c = make_config(profile, 'S1', strategy)
    c['time']['horizon_s'] = 3600
    c['events'] = [event('feed', 'water', 600, 1200, 1.5, '1')]
    baseline = service.prepare(c)
    service.run_all(baseline)
    displayed = service.prepare(c)
    for step in range(60):
        service.advance(displayed, f'view-{step}', step)
        before = '\n'.join(repo.db.iterdump())
        changes = repo.db.total_changes
        for shape in SHAPES:
            snap = view(repo, displayed, shape)
            render_html(snap)
            assert snap['geometry']['shape'] == shape
        assert repo.db.total_changes == changes
        assert '\n'.join(repo.db.iterdump()) == before
    for table in ['samples', 'decisions', 'actuator_records', 'events', 'metrics']:
        assert repo.records(displayed, table) == repo.records(baseline, table)
    assert repo.get(displayed)['state'] == repo.get(baseline)['state']
    assert repo.get(displayed)['config'] == RunConfig.freeze(c).data
    assert len(repo.list()) == 2
    assert repo.records(displayed, 'metrics')[0]['J'] == repo.records(baseline, 'metrics')[0]['J']
    repo.close()


@pytest.mark.parametrize('shape', SHAPES)
def test_same_area_volume_and_unclipped_level(tmp_path, shape):
    repo = SQLiteRepository(tmp_path / 'geometry.sqlite')
    service = SimulationService(repo)
    rid = service.prepare(make_config())
    run = repo.get(rid)
    original = deepcopy(run)
    for h in [-.25, .8, 2.1]:
        run['state'][4] = h  # presentation edge case; never written to SQLite
        snap = snapshot(run, [], [], [], shape)
        g = snap['geometry']
        assert math.pi * g['radius_m'] ** 2 == pytest.approx(g['area_m2'])
        assert g['length_m'] / g['width_m'] == pytest.approx(2)
        assert g['length_m'] * g['width_m'] == pytest.approx(g['area_m2'])
        assert snap['volume_m3'] == g['area_m2'] * h
        assert snap['state'][4] == h
        assert bool(snap['warnings']) == (h < 0 or h > g['height_m'])
    assert repo.get(rid) == original
    with pytest.raises(ValueError):
        geometry(10, 1.5, 'otra')
    repo.close()


@pytest.mark.parametrize('fault', ['missing', 'invalid'])
def test_missing_invalid_samples_are_not_replaced_with_exact_or_reference(tmp_path, fault):
    repo = SQLiteRepository(tmp_path / 'sensors.sqlite')
    service = SimulationService(repo)
    c = make_config(0, 'S0', 'closed')
    c['events'] = [event('missing' if fault == 'missing' else 'bias', 1, 60, 120,
                         1 if fault == 'missing' else 100, '1' if fault == 'missing' else 'mg/L')]
    rid = service.prepare(c)
    service.advance(rid, 'first', 0)
    snap = view(repo, rid)
    assert snap['status'] == 'FAILED' and not snap['animate']
    assert snap['sensors'][1]['value'] is None
    assert snap['sensors'][1]['quality'] == ('MISSING' if fault == 'missing' else 'INVALID')
    assert snap['sensors'][1]['exact'] is not None
    assert any(a['code'] == 'LECTURA_' + snap['sensors'][1]['quality'] for a in snap['alarms'])
    assert snap['sample_time_s'] == 60 and snap['interval_s'] == [0, 60]
    # Adapter is defensive even for nonfinite data supplied outside SQLite.
    samples = repo.records(rid, 'samples')
    samples[-1]['values'][0] = float('nan')
    samples[-1]['qualities'][0] = 'GOOD'
    defensive = snapshot(repo.get(rid), samples, [], [])
    assert defensive['sensors'][0]['quality'] == 'INVALID'
    json.dumps(defensive, allow_nan=False)
    repo.close()


def test_action_mapping_availability_alarm_clear_and_partial_times(tmp_path):
    repo = SQLiteRepository(tmp_path / 'records.sqlite')
    service = SimulationService(repo)
    c = make_config(0, 'S0', 'open')
    c['events'] = [event('availability', 2, 0, 120, 0, '1'), event('bias', 0, 0, 60, 4, '°C')]
    rid = service.prepare(c)
    service.advance(rid, 'one', 0)
    snap = view(repo, rid)
    air = snap['actuators'][2]
    assert [a['key'] for a in snap['actuators']] == ACTIONS
    assert air['command'] > 0 and air['availability'] == 0 and air['effective'] == 0 and not air['active']
    assert not any(a['target'] == 'temperature_C' for a in snap['alarms'])  # clear at t=60
    record = repo.records(rid, 'actuator_records')[0]
    synthetic = []
    for j, key in enumerate(ACTIONS):
        row = deepcopy(record)
        row.update(actuator_id=key, command=[-.5, .4, -.3, .2, -.8], mean_effective=j / 10, availability=.5)
        synthetic.append(row)
    mapped = snapshot(repo.get(rid), [], synthetic, [])
    assert [a['command'] for a in mapped['actuators']] == [0, .5, .4, 0, .3, .2, 0, .8]
    assert [a['effective'] for a in mapped['actuators']] == [j / 10 for j in range(8)]
    c = make_config(0, 'S0', 'open')
    c['x0'][4] = .251
    c['parameters']['leak_base_m3_s'] = .01
    partial = service.prepare(c)
    service.advance(partial, 'partial', 0)
    snap = view(repo, partial)
    assert 0 < snap['state_time_s'] < 60 and snap['sample_time_s'] == 0
    assert snap['interval_s'] == [0, snap['state_time_s']]
    assert snap['state'][4] == repo.get(partial)['state'][4]
    assert snap['state'][4] != repo.records(partial, 'samples')[-1]['x'][4]
    repo.close()


def test_prepared_paused_stopped_completed_and_interrupted_are_static(tmp_path):
    repo = SQLiteRepository(tmp_path / 'status.sqlite')
    service = SimulationService(repo)
    rid = service.prepare(make_config(0, 'S0', 'open'))
    snap = view(repo, rid)
    assert not snap['animate'] and snap['sample_time_s'] is None
    assert all(a['effective'] is None for a in snap['actuators'])
    service.advance(rid, 'one', 0)
    assert view(repo, rid)['animate']
    service.pause(rid)
    assert not view(repo, rid)['animate']
    service.resume(rid)
    assert view(repo, rid)['animate']
    service.stop(rid)
    for status in ['STOPPED', 'COMPLETED', 'FAILED', 'INTERRUPTED']:
        run = repo.get(rid)
        run['status'] = status
        assert not snapshot(run, repo.records(rid, 'samples'), repo.records(rid, 'actuator_records'), [])['animate']
    repo.close()


def test_render_is_offline_and_profile_cannot_inject_scripts(tmp_path, monkeypatch):
    import socket
    repo = SQLiteRepository(tmp_path / 'offline.sqlite')
    service = SimulationService(repo)
    rid = service.prepare(make_config())
    snap = view(repo, rid, 'Rectangular', force_fallback=True)
    snap['profile'] = '</script><img src=x onerror=alert(1)>'
    def deny(*args, **kwargs):
        raise AssertionError('Network forbidden')
    monkeypatch.setattr(socket.socket, 'connect', deny)
    html = render_html(snap)
    assert '<script src=' not in html and '<link ' not in html
    assert '</script><img' not in html
    assert '/*__' not in html and '__SNAPSHOT_JSON__' not in html
    assert 'webglcontextlost' in html and 'VISTA 2.5D' in html
    repo.close()


@pytest.mark.parametrize('profile', range(3))
def test_streamlit_repeated_switch_does_not_create_run_or_decision(tmp_path, monkeypatch, profile):
    monkeypatch.setenv('PISCICULTURA_DB', str(tmp_path / 'ui.sqlite'))
    at = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()
    by_label(at.selectbox, 'Perfil de especie').select(profile).run()
    by_label(at.selectbox, 'Escenario').select('S0').run()
    by_label(at.button, 'Validar y preparar corrida').click().run()
    assert not at.exception
    rid = at.session_state['run_id']
    service = at.session_state['service']
    for status in ['PREPARED', 'RUNNING', 'PAUSED', 'STOPPED']:
        if status == 'RUNNING': by_label(at.button, 'Avanzar un intervalo').click().run()
        if status == 'PAUSED': by_label(at.button, 'Pausar').click().run()
        if status == 'STOPPED': by_label(at.button, 'Detener').click().run()
        before = '\n'.join(service.repo.db.iterdump())
        for shape in ['Rectangular', 'Circular', 'Rectangular', 'Circular']:
            by_label(at.selectbox, 'Representación').select(shape).run()
            assert not at.exception
            assert at.session_state['presentation_tank_shape'] == shape
            assert '\n'.join(service.repo.db.iterdump()) == before
        assert service.repo.get(rid)['status'] == status
        assert len(service.repo.list()) == 1
    by_label(at.selectbox, 'Renderizado').select('2.5D (sin WebGL)').run()
    assert not at.exception
    assert 'presentation_tank_shape' not in service.repo.get(rid)['config']
    # A second prepared run becomes the viewed run, retaining visual preferences.
    by_label(at.selectbox, 'Representación').select('Rectangular').run()
    previous = service.repo.get(rid)
    by_label(at.button, 'Validar y preparar corrida').click().run()
    assert not at.exception
    assert at.session_state['run_id'] != rid
    assert at.session_state['presentation_run_id'] == at.session_state['run_id']
    assert at.session_state['presentation_tank_shape'] == 'Rectangular'
    assert service.repo.get(rid) == previous
