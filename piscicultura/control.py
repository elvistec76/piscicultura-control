"""Frontera del controlador: solo configuración propia, lecturas y memoria."""
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class Measurement:
    index: int
    time_s: float
    values: tuple
    qualities: tuple
    diagnostics: tuple


def decide(strategy,reference,settings,open_commands,frame,memory):
    if strategy=='open':
        return np.array(open_commands), list(memory), [None]*5, ['PROGRAMA_CONSTANTE']*5
    if any(q!='GOOD' for q in frame.qualities): raise ValueError('LECTURA_REQUERIDA_INVALIDA')
    y=frame.values; r=reference; m=list(memory); reasons=[]
    for j,delta in [(0,settings['thermal_delta_C']),(2,settings['ph_delta']),(4,settings['level_delta_m'])]:
        old=m[j]
        if old==0: m[j]=1 if y[j]<r[j]-delta else -1 if y[j]>r[j]+delta else 0
        elif old==1 and y[j]>=r[j]: m[j]=0
        elif old==-1 and y[j]<=r[j]: m[j]=0
    if m[1]==0 and y[1]<=r[1]-settings['oxygen_delta_mg_L']: m[1]=1
    elif m[1]==1 and y[1]>=r[1]+settings['oxygen_delta_mg_L']: m[1]=0
    if m[3]==0 and y[3]>=settings['filter_on_NTU']: m[3]=1
    elif m[3]==1 and y[3]<=settings['filter_off_NTU']: m[3]=0
    for old,new in zip(memory,m): reasons.append('MANTIENE_MODO' if old==new else 'CAMBIO_POR_UMBRAL')
    return np.array(m,dtype=float),m,[rj-yj for rj,yj in zip(r,y)],reasons
