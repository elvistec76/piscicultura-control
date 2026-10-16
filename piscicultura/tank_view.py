"""Read-only presentation snapshots; no integration, control or persistence writes."""
import json
import math
from functools import lru_cache
from pathlib import Path

from .config import ACTIONS, VARIABLES, UNITS
from .charts import LABELS, ACTION_LABELS

ASSETS = Path(__file__).with_name('tank_assets')
SHAPES = ('Circular', 'Rectangular')


def finite(value):
    """Reject absent/nonfinite display data without substituting a physical value."""
    return float(value) if isinstance(value, (int, float)) and math.isfinite(value) else None


def geometry(area, height, shape):
    if shape not in SHAPES:
        raise ValueError('Representación desconocida')
    if not math.isfinite(area) or area <= 0 or not math.isfinite(height) or height <= 0:
        raise ValueError('Geometría no representable')
    return dict(shape=shape, area_m2=area, height_m=height,
                radius_m=math.sqrt(area / math.pi),
                length_m=math.sqrt(2 * area), width_m=math.sqrt(area / 2))


def snapshot(run, samples, actions, events, shape='Circular', force_fallback=False):
    """Adapt confirmed records only. x(t), y(t_k), and interval means keep their times.

    Water uses the persisted exact state, including a partial terminal interval.
    Sensor cards use the latest confirmed sample, never last_good or references.
    Command components are mapped to the eight physical channels without using
    actuator response/availability to invent a new effective action.
    """
    c = run['config']
    g = geometry(c['parameters']['area_m2'], c['parameters']['height_max_m'], shape)
    last = max(samples, key=lambda s: s['time_s']) if samples else None
    state = [finite(v) for v in run['state'][:5]]
    level = state[4]
    warnings = []
    if level is None or not 0 <= level <= g['height_m']:
        warnings.append('Nivel exacto fuera de la geometría o no finito; no se recorta ni se corrige.')
    sensors = []
    for j, (key, label, unit) in enumerate(zip(VARIABLES, LABELS, UNITS)):
        value = finite(last['values'][j]) if last else None
        quality = last['qualities'][j] if last else 'MISSING'
        if quality not in ('GOOD', 'MISSING', 'INVALID'):
            quality = 'INVALID'
        if quality == 'GOOD' and value is None:
            quality = 'INVALID'
        if quality != 'GOOD':
            value = None
        sensors.append(dict(key=key, label=label, unit='adim.' if unit == '1' else unit,
                            value=value, quality=quality, exact=state[j],
                            diagnosis=last['diagnostics'][j] if last else 'SIN_MUESTRA',
                            reference=c['profile']['references'][j],
                            band=c['profile']['operating_bands'][j]))
    # A failed partial integration may end after the latest measured sample.
    end = max((a['end_s'] for a in actions), default=None)
    latest = {a['actuator_id']: a for a in actions if a['end_s'] == end}
    channels = [(0, 1), (0, -1), (1, 1), (2, 1), (2, -1), (3, 1), (4, 1), (4, -1)]
    actuators = []
    for key, label, (index, sign) in zip(ACTIONS, ACTION_LABELS, channels):
        a = latest.get(key)
        raw = finite(a['command'][index]) if a else None
        command = max(0., sign * raw) if raw is not None else None
        effective = finite(a['mean_effective']) if a else None
        actuators.append(dict(key=key, label=label, command=command,
                              availability=finite(a['availability']) if a else None,
                              effective=effective, active=effective is not None and effective > 0,
                              reason=a['limit_reason'] if a else 'SIN_INTERVALO'))
    alarm_map = {}
    for e in sorted(events, key=lambda e: (e['time_s'], e['event_seq'])):
        if e['category'] != 'alarm':
            continue
        key = (e['target'], e['code'])
        if e['transition'] == 'activation':
            alarm_map[key] = dict(e)
        elif e['transition'] == 'clear':
            alarm_map.pop(key, None)
    interval = None
    if latest:
        row = next(iter(latest.values()))
        interval = [row['start_s'], row['end_s']]
    return dict(schema='aquacontrol-view-1', run_id=run['run_id'], status=run['status'],
                profile=c['profile']['name'], strategy=c['strategy'], cause=run['cause'],
                geometry=g, state=state, state_time_s=run['time_s'],
                sample_time_s=last['time_s'] if last else None, interval_s=interval,
                volume_m3=c['parameters']['area_m2'] * level if level is not None else None,
                sensors=sensors, actuators=actuators, alarms=list(alarm_map.values()),
                warnings=warnings, animate=run['status'] == 'RUNNING' and interval is not None,
                force_fallback=bool(force_fallback))


@lru_cache(maxsize=1)
def assets():
    return tuple((ASSETS / name).read_text(encoding='utf-8') for name in
                 ('scene.html', 'scene.css', 'vendor/three.min.js', 'replay.js', 'scene.js'))


@lru_cache(maxsize=1)
def plotly_asset():
    from plotly.offline import get_plotlyjs
    return get_plotlyjs()


def render_html(data):
    template, css, three, replay, js = assets()
    plotly = plotly_asset() if 'history' in data else ''
    # A profile name cannot terminate the JSON script or inject HTML.
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e')
    return template.replace('/*__CSS__*/', css).replace('/*__THREE__*/', three).replace('/*__REPLAY__*/', replay).replace('/*__PLOTLY__*/', plotly).replace('/*__JS__*/', js).replace('__SNAPSHOT_JSON__', payload)


def show_tank(repo, rid, shape, force_fallback=False):
    """Streamlit boundary: reads only; selection belongs to the caller's UI state."""
    import streamlit as st
    from .replay import load_history
    history = load_history(repo.path, rid)
    data = snapshot(history['run'], history['samples'], history['actuator_records'],
                    history['events'], shape, force_fallback)
    data['history'] = history
    # Fixed frame height avoids layout/scroll-anchor jumps while a GPU canvas
    # is animating. Narrow layouts keep their native iframe scroll bar.
    st.iframe(render_html(data), height=1950, alt='AquaControl: estanque, sensores y actuadores')
    return data
