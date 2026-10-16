"""Production JavaScript projection exercised with real SQLite records."""
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess

import pytest

from piscicultura.config import event, make_config
from piscicultura.replay import load_history
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService
from piscicultura.tank_view import snapshot

ROOT = Path(__file__).resolve().parents[1]


def javascript(base, history, assertions):
    if not shutil.which('node'):
        pytest.skip('Node requerido para verificar el código real del reproductor')
    program = "require('./piscicultura/tank_assets/replay.js'); const assert=require('node:assert/strict'); const fs=require('node:fs'); const {base,history}=JSON.parse(fs.readFileSync(0,'utf8')); const replay=AquaReplay.create(base,history);\n" + assertions
    result = subprocess.run(['node', '-e', program], cwd=ROOT, input=json.dumps(dict(base=base, history=history)), text=True, capture_output=True)
    assert result.returncode == 0, result.stderr


@pytest.fixture
def stored(tmp_path):
    repo = SQLiteRepository(tmp_path / 'replay.sqlite')
    service = SimulationService(repo)
    c = make_config(0, 'S0', 'open')
    c['time']['horizon_s'] = 3600
    c['events'] = [event('missing', 1, 60, 120, 1, '1'),
                   event('availability', 2, 60, 120, 0, '1'),
                   event('bias', 0, 0, 60, 4, '°C')]
    rid = service.prepare(c)
    for k in range(3):
        service.advance(rid, f'fixture-{k}', k)
    service.stop(rid)
    history = load_history(repo.path, rid)
    base = snapshot(history['run'], history['samples'], history['actuator_records'], history['events'])
    yield repo, rid, base, history
    repo.close()


def test_real_projection_boundaries_quality_and_alarms(stored):
    _, _, base, history = stored
    javascript(base, history, """
      let s=replay.project(30);
      assert.equal(s.selected_time_s,30); assert.equal(s.state_time_s,0); assert.equal(s.sample_time_s,0);
      assert.deepEqual(s.state,history.samples[0].x); assert.match(s.state_policy,/sin interpolación/);
      assert.deepEqual(s.interval_s,[0,60]); assert.equal(s.controller_input.sample_index,s.decision.input_sample_index);
      assert(s.alarms.some(a=>a.target==='temperature_C'));
      s=replay.project(60);
      assert.equal(s.state_time_s,60); assert.equal(s.sample_time_s,60);
      assert.equal(s.sensors[1].value,null); assert.equal(s.sensors[1].quality,'MISSING');
      assert.deepEqual(s.interval_s,[60,120]); assert.equal(s.actuators[2].availability,0);
      assert.equal(s.actuators[2].effective,0); assert.equal(s.actuators[2].active,false);
      assert(!s.alarms.some(a=>a.target==='temperature_C'));
      assert(s.alarms.some(a=>a.code==='LECTURA_MISSING'));
      assert.equal(s.decision.strategy,'open'); assert(s.decision.errors.every(e=>e===null));
      assert.equal(s.observed_sample,null);
      s=replay.project(120); assert.equal(s.sensors[1].quality,'GOOD');
      assert(!s.alarms.some(a=>a.code==='LECTURA_MISSING'));
      s=replay.project(180); assert.deepEqual(s.state,history.run.state.slice(0,5));
      assert.deepEqual(s.interval_s,[120,180]); assert.equal(s.observed_sample.time_s,180);
      // Rewind must clear alarms and outcomes accumulated while playing forward.
      assert.equal(replay.project(30).observed_sample,null);
      assert.equal(replay.project(-10).selected_time_s,0); assert.equal(replay.project(1000).selected_time_s,180);
      assert(replay.hasPerturbation); assert(replay.guide.every(g=>replay.times.includes(g.time_s)));
    """)


def test_no_writes_and_consistent_read_transaction(stored, monkeypatch):
    repo, rid, base, history = stored
    before = '\n'.join(repo.db.iterdump())
    changes = repo.db.total_changes
    original_connect = sqlite3.connect
    seen = []

    def connect(database, **kwargs):
        assert database.endswith('?mode=ro') and kwargs['uri'] is True
        db = original_connect(database, **kwargs)
        db.set_trace_callback(seen.append)
        # SQLite enforces mode=ro even if a future edit accidentally attempts DML.
        with pytest.raises(sqlite3.OperationalError, match='readonly'):
            db.execute('UPDATE runs SET status=status')
        db.rollback()
        seen.clear()
        return db

    monkeypatch.setattr(sqlite3, 'connect', connect)
    for _ in range(2):
        assert load_history(repo.path, rid) == history
        javascript(base, history, 'for(const t of [0,90,180,60,0])replay.project(t);')
    assert seen.count('BEGIN') == 1
    assert repo.db.total_changes == changes
    assert '\n'.join(repo.db.iterdump()) == before


def test_gaps_missing_sources_and_partial_terminal(stored, tmp_path):
    _, _, base, history = stored
    javascript(base, history, """
      history.actuator_records=history.actuator_records.filter(a=>!(a.start_s===60&&a.actuator_id===base.actuators[2].key));
      let r=AquaReplay.create(base,history); assert.equal(r.project(90).actuators[2].effective,null);
      history.samples=history.samples.filter(s=>s.time_s!==60);
      r=AquaReplay.create(base,history); assert.equal(r.project(90).sample_time_s,0);
      assert.equal(r.project(90).controller_input,null); // input index missing, no substitution
      history.samples=[];history.decisions=[];history.events=[];history.actuator_records=[];
      r=AquaReplay.create(base,history); const s=r.project(30);
      assert.equal(s.sample_time_s,null); assert.equal(s.decision,null);
      assert(s.sensors.every(v=>v.value===null));assert(s.actuators.every(a=>!a.active));
      assert(!r.hasPerturbation);assert.equal(r.guide.length,2);
    """)
    repo = SQLiteRepository(tmp_path / 'partial-replay.sqlite')
    try:
        c = make_config(0, 'S0', 'open'); c['x0'][4] = .251; c['parameters']['leak_base_m3_s'] = .01
        service = SimulationService(repo); rid = service.prepare(c); service.advance(rid, 'partial', 0)
        h = load_history(repo.path, rid)
        b = snapshot(h['run'], h['samples'], h['actuator_records'], h['events'])
        javascript(b, h, """
          const end=replay.duration;assert(end>0&&end<60);
          assert.equal(replay.project(end/2).state_time_s,0);
          const s=replay.project(end);assert.equal(s.state_time_s,end);assert.equal(s.sample_time_s,0);
          assert.deepEqual(s.state,history.run.state.slice(0,5));assert.deepEqual(s.interval_s,[0,end]);
        """)
    finally:
        repo.close()


def test_clock_pause_speed_reset_and_hidden_tab(stored):
    _, _, base, history = stored
    javascript(base, history, """
      const c=new AquaReplay.Clock(180);c.speed=2;c.play();c.tick(1000);c.tick(2000);
      assert.equal(c.time,2);assert.equal(c.elapsed,1);c.pause();c.tick(9000);assert.equal(c.time,2);
      c.seek(60);c.play();c.tick(10000);c.tick(11000);assert.equal(c.time,62);
      c.tick(12000,false);c.tick(19000);assert.equal(c.time,62);c.tick(20000);assert.equal(c.time,64);
      c.speed=4;c.tick(21000);assert.equal(c.time,68);
      c.reset();assert.equal(c.time,0);assert.equal(c.elapsed,0);assert.equal(c.playing,false);
      c.seek(179);c.play();c.tick(0);c.tick(1000);assert.equal(c.time,180);assert(!c.playing);
    """)


@pytest.mark.parametrize('status', ['COMPLETED', 'PAUSED', 'STOPPED'])
def test_closed_decision_input_and_status_do_not_change_playback(tmp_path, status):
    repo = SQLiteRepository(tmp_path / 'closed.sqlite')
    try:
        service = SimulationService(repo)
        c = make_config(0, 'S2', 'closed'); c['time']['horizon_s'] = 3600
        rid = service.prepare(c)
        if status == 'COMPLETED':
            service.run_all(rid)
        else:
            for k in range(2):
                service.advance(rid, f'closed-{k}', k)
            service.pause(rid) if status == 'PAUSED' else service.stop(rid)
        before = '\n'.join(repo.db.iterdump())
        h = load_history(repo.path, rid)
        b = snapshot(h['run'], h['samples'], h['actuator_records'], h['events'])
        javascript(b, h, """
          const s=replay.project(90),d=s.decision,input=s.controller_input;
          assert.equal(d.time_s,60);assert.equal(input.sample_index,d.input_sample_index);
          assert.equal(input.time_s,60);assert.deepEqual(d.errors,d.references.map((r,j)=>r-input.values[j]));
          assert.equal(d.strategy,'closed');assert.equal(s.observed_sample,null);
          assert.deepEqual(d,history.decisions.find(row=>row.decision_index===d.decision_index));
        """)
        assert '\n'.join(repo.db.iterdump()) == before
    finally:
        repo.close()


def test_academic_mode_hides_forms_preserves_run_and_returns(tmp_path, monkeypatch):
    from streamlit.testing.v1 import AppTest
    from tests.test_ui import by_label
    monkeypatch.setenv('PISCICULTURA_DB', str(tmp_path / 'presentation.sqlite'))
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=30).run()
    by_label(at.button, 'Validar y preparar corrida').click().run()
    by_label(at.button, 'Avanzar un intervalo').click().run()
    repo = at.session_state['service'].repo
    before = '\n'.join(repo.db.iterdump())
    by_label(at.toggle, 'Modo presentación académica').set_value(True).run()
    assert not at.exception and len(at.tabs) == 0
    assert not any(b.label == 'Validar y preparar corrida' for b in at.button)
    assert '\n'.join(repo.db.iterdump()) == before
    by_label(at.toggle, 'Modo presentación académica').set_value(False).run()
    assert not at.exception and len(at.tabs) == 5
    assert any(b.label == 'Validar y preparar corrida' for b in at.button)
    assert '\n'.join(repo.db.iterdump()) == before
