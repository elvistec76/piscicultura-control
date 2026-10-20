"""Realización por tiempo e índice, independiente de los pasos RK45."""
import numpy as np


def noise_table(c):
    n=int(c['time']['horizon_s']/c['time']['control_interval_s'])
    rng=np.random.Generator(np.random.PCG64(c['sensor']['seed']))
    return np.clip(rng.standard_normal((n+1,5)),-3,3)


def conditions(c,t):
    d=dict.fromkeys(['environment','feed','leak','rain','ph_rate','turbidity_rate'],0.)
    g=np.ones(8); faults=[]
    for i,e in enumerate(c['events']):
        if e['start_s']<=t<e['end_s']:
            kind=e['kind']
            if kind in d: d[kind]+=e['magnitude']
            elif kind=='availability': g[e['target']]=min(g[e['target']],e['magnitude'])
            else: faults.append((i,e))
    return d,g,faults
