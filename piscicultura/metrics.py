"""Indicadores con origen y unidades; sin integrales ocultas sobre ausencias."""
import numpy as np
from .config import VARIABLES,UNITS,ACTIONS


def assert_finite_metrics(value,path='metrics'):
    """Nulos expresan indisponibilidad; un número no finito siempre es un error."""
    import math
    from numbers import Real
    if isinstance(value,dict):
        for key,item in value.items(): assert_finite_metrics(item,path+'.'+key)
    elif isinstance(value,(list,tuple)):
        for j,item in enumerate(value): assert_finite_metrics(item,f'{path}[{j}]')
    elif isinstance(value,Real) and not math.isfinite(value):
        raise ValueError(path+': resultado derivado no finito')


def series_metrics(t,x,reference,bands,start=0.,*,variables=None,window=None):
    """Banda por identidad; ventana exacta sobre intervalos, sin muestras ficticias.

    Tiempo fuera: estado de la muestra izquierda original e intersección temporal.
    IAE: trapecios de error absoluto, interpolado linealmente en los extremos.
    Recuperación: primera muestra real seguida de 1800 s dentro de la ventana.
    """
    t=np.asarray(t,dtype=float);x=np.asarray(x,dtype=float)
    if len(t)<2: return None
    if x.ndim!=2 or len(x)!=len(t) or not np.isfinite(t).all() or not np.isfinite(x).all() or np.any(np.diff(t)<=0):
        raise ValueError('Series de métricas no finitas, dimensiones o tiempos inválidos')
    names=list(variables) if variables is not None else [None]*x.shape[1]
    if len(names)!=x.shape[1]: raise ValueError('Identidad de variables incompatible con las columnas')
    a,b=(float(t[0]),float(t[-1])) if window is None else map(float,window)
    if not np.isfinite([a,b]).all() or not t[0]<=a<b<=t[-1]:
        raise ValueError('Ventana sin cobertura temporal completa o extremos inválidos')
    duration=b-a;dt=np.diff(t)
    error=np.abs(x-np.asarray(reference))
    inside=(x>=np.array(bands)[:,0]) & (x<=np.array(bands)[:,1])
    for j,name in enumerate(names):
        if name==VARIABLES[3]: inside[:,j]=x[:,j]<=bands[j][1]
    if window is None:
        widths=dt
        iae=np.sum((error[1:]+error[:-1])*.5*dt[:,None],axis=0)
    else:
        left=np.maximum(t[:-1],a);right=np.minimum(t[1:],b)
        mask=right>left;widths=np.where(mask,right-left,0.)
        e0=error[:-1][mask];slope=(error[1:]-error[:-1])[mask]/dt[mask,None]
        e_left=e0+slope*(left[mask]-t[:-1][mask])[:,None]
        e_right=e0+slope*(right[mask]-t[:-1][mask])[:,None]
        iae=np.sum((e_left+e_right)*.5*widths[mask,None],axis=0)
    outside=np.sum((~inside[:-1])*widths[:,None],axis=0)
    recovery=[];origin=max(a,start) if window is not None else start
    for j in range(x.shape[1]):
        recovered=None
        for i in range(len(t)):
            if t[i]<max(a,start) or t[i]>b or not inside[i,j]: continue
            end=int(np.searchsorted(t,t[i]+1800))
            if end<len(t) and t[end]<=b and np.all(inside[i:end+1,j]):
                recovered=float(t[i]-origin);break
        recovery.append(recovered)
    result=dict(iae=iae.tolist(),outside_s=outside.tolist(),in_band_fraction=(1-outside/duration).tolist(),recovery_s=recovery,duration_s=duration,interval_s=[a,b],variables=names,iae_boundary_rule='Interpolación lineal del error absoluto entre muestras; trapecios recortados',outside_rule='Estado izquierdo original por duración de intersección')
    assert_finite_metrics(result)
    return result


def evaluate(run,samples,actions,end_s=None):
    c=run['config']; r=c['profile']['references'];bands=c['profile']['operating_bands']
    pairs=[(s['time_s'],s['x']) for s in samples]
    term=run['termination_state']
    if term and (not pairs or term['time_s']>pairs[-1][0]): pairs.append((term['time_s'],term['state'][:5]))
    if end_s is not None and pairs and end_s<pairs[-1][0]:
        times=np.array([p[0] for p in pairs]);values=np.array([p[1] for p in pairs]);endpoint=[float(np.interp(end_s,times,values[:,j])) for j in range(5)]
        pairs=[p for p in pairs if p[0]<end_s]+[(end_s,endpoint)]
    t=[p[0] for p in pairs];x=[p[1] for p in pairs]
    xm=series_metrics(t,x,r,bands,variables=VARIABLES) if len(t)>1 else None
    scales=[(bands[0][1]-bands[0][0])/2,(bands[1][1]-bands[1][0])/2,.5,20,.1]
    if not np.isfinite(scales).all() or min(scales)<=0:
        raise ValueError('profile.operating_bands T/C: escalas de J deben ser positivas y finitas')
    J=float(np.mean(np.array(xm['iae'])/(np.array(scales)*xm['duration_s']))) if xm and xm['duration_s']>0 else None
    window=None
    if t and t[-1]>=43200:
        window=series_metrics(t,x,r,bands,variables=VARIABLES,window=(14400,43200))
    valid=np.array([[v is not None for v in s['values']] for s in samples],dtype=bool)
    coverage=valid.mean(axis=0).tolist() if samples else [0]*5
    ym=[]
    for j in range(5):
        if samples and all(valid[:,j]) and end_s is None:
            result=series_metrics([s['time_s'] for s in samples],[[s['values'][j]] for s in samples],[r[j]],[bands[j]],variables=[VARIABLES[j]])
        else: result=None
        ym.append(result)
    p=c['parameters'];integrals=np.zeros(8);flows=dict(rain_m3=0.,leak_m3=0.,evaporation_m3=0.,exchange_m3=0.)
    for a in actions:
        duration=a['end_s']-a['start_s']
        if end_s is not None:
            # Comparación común de consumos solo usa intervalos completos; se declara cobertura.
            if a['end_s']>end_s: continue
        j=ACTIONS.index(a['actuator_id']);integrals[j]+=a['mean_effective']*duration
        if j==0:
            flows['rain_m3']+=(p['rain_base_m3_s']+a['disturbances']['rain'])*duration
            flows['leak_m3']+=(p['leak_base_m3_s']+a['disturbances']['leak'])*duration
            flows['evaporation_m3']+=p['evaporation_m3_s']*duration
            flows['exchange_m3']+=p['exchange_m3_s']*duration
    energy=float(np.dot(integrals,[p['heater_max_W'],p['cooler_max_W']/p['cooling_COP'],p['air_power_W'],0,0,p['filter_power_W'],p['inlet_power_W'],p['outlet_power_W']])/3.6e6)
    return dict(formula_version='M-AGUA-DEMO-1/section14-v1',origin='x',variables=VARIABLES,units=UNITS,interval_s=[t[0],t[-1]] if t else [],x=xm,J=J,window_4_12h=window,y=dict(coverage=coverage,per_variable=ym,rule='IAE solo con cobertura completa; sin interpolación de ausencias'),joint_recovery_s=max(xm['recovery_s']) if xm and all(v is not None for v in xm['recovery_s']) else None,usage=dict(inlet_m3=float(integrals[6]*p['inlet_max_m3_s']+flows['exchange_m3']),outlet_m3=float(integrals[7]*p['outlet_max_m3_s']+flows['exchange_m3']),ph_base_normalized_s=float(integrals[3]),ph_acid_normalized_s=float(integrals[4]),partial_energy_kWh=energy,**flows),common_endpoint_policy='x interpolado linealmente si necesario; consumos comunes solo intervalos completos' if end_s is not None else 'termination_state irregular incluido solo en x')
