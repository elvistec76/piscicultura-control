"""Muestreo con memoria de última lectura GOOD y congelación plausible."""
import math
from .control import Measurement


def measure(k,t,x,epsilon,c,faults,last_good):
    vals=[]; qualities=[]; diagnoses=[]; last=list(last_good)
    for j in range(5):
        active=[e for _,e in faults if e['target']==j]
        kinds={e['kind'] for e in active}
        # last_good se retiene al empezar el fallo; no se actualiza durante freeze.
        if 'missing' in kinds or ('freeze' in kinds and last[j] is None):
            v=None; q='MISSING'; diag='SIN_LECTURA'
        else:
            v=last[j] if 'freeze' in kinds else float(x[j]+c['sensor']['bias'][j]+sum(e['magnitude'] for e in active if e['kind']=='bias')+c['sensor']['sigma'][j]*epsilon[j])
            lo,hi=c['sensor']['measurement_ranges'][j]
            invalid=not math.isfinite(v) or not lo<=v<=hi or (j in (1,3) and x[j]<0)
            q='INVALID' if invalid else 'GOOD'; diag='FUERA_DE_RANGO_O_NO_FINITO' if invalid else ''
            if invalid: v=None
            elif 'freeze' not in kinds: last[j]=v
        vals.append(v); qualities.append(q); diagnoses.append(diag)
    return Measurement(k,t,tuple(vals),tuple(qualities),tuple(diagnoses)),last
