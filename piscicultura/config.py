"""Configuración congelada, procedencia y validación antes de integrar."""
from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULTS = json.loads((ROOT / 'docs/MODEL_DEFAULTS.json').read_text())
VARIABLES = DEFAULTS['variable_order']
UNITS = ['°C', 'mg/L', '1', 'NTU', 'm']
ACTIONS = DEFAULTS['availability_order']
EVENT_UNITS = {'environment': '°C', 'feed': '1', 'leak': 'm³/s', 'rain': 'm³/s',
               'ph_rate': 's⁻¹', 'turbidity_rate': 'NTU/s', 'availability': '1',
               'missing': '1', 'freeze': '1'}

@dataclass(frozen=True)
class RunConfig:
    document: str

    @property
    def data(self):
        return json.loads(self.document)

    @classmethod
    def freeze(cls, draft):
        try:
            validate(draft)
        except (TypeError,KeyError,IndexError,AttributeError,ZeroDivisionError) as exc:
            raise ValueError('Estructura o campo de configuración inválido: '+str(exc)) from exc
        return cls(json.dumps(draft, ensure_ascii=False, allow_nan=False, sort_keys=True))


def duplicate_profile(profile, name):
    p = deepcopy(profile)
    p['parent_profile_id'] = p['id']
    p['id'] = p['id'] + '_copia'
    p['name'] = name
    return p


def calibrate(c):
    from .model import saturation
    p, r, prof = c['parameters'], np.array(c['profile']['references']), c['profile']
    V = p['area_m2'] * r[4]
    cs = saturation(r[0], p['pressure_Pa'], p['salinity_per_mille'])
    demand = (p['fish_consumption_mg_kg_s_at20'] * p['biomass_kg'] *
              p['temperature_Q10']**((r[0]-20)/10)/(1000*V) +
              p['water_consumption_mg_L_s_at20']*p['temperature_Q10']**((r[0]-20)/10))*r[1]/(p['oxygen_half_saturation_mg_L']+r[1])
    return [p['heat_exchange_W_K']*2/p['heater_max_W'],
            ((demand-p['evaporation_m3_s']/V*prof['inlet_oxygen_mg_L'])/(cs-r[1])-p['k_natural_s_inv'])/p['k_air_s_inv'],
            p['ph_relaxation_s_inv']*(r[2]-p['ph_background'])/p['ph_actuation_per_s'],
            ((p['turbidity_source_NTU_s']+p['evaporation_m3_s']/V*(p['inlet_turbidity_NTU']-r[3]))/r[3]-p['k_settle_s_inv'])/p['k_filter_s_inv'],
            p['evaporation_m3_s']/p['inlet_max_m3_s']]


def make_config(profile_index=0, scenario='S1', strategy='closed'):
    c = deepcopy(DEFAULTS)
    c.pop('profiles')
    c['schema_version'] = '1.0.0'
    c['code_version'] = '0.1.0'
    c['profile'] = deepcopy(DEFAULTS['profiles'][profile_index])
    c['units'] = dict(zip(VARIABLES, UNITS))
    c['strategy'] = strategy
    c['scenario'] = scenario
    c['events'] = []
    c['environment_amplitude_C'] = 2.0
    c['x0'] = c['profile']['references'].copy()
    c['origin_registry'] = [
        {'classification':'bibliographic', 'value':'Csat coefficients', 'unit':'mg/L', 'source':DEFAULTS['solubility_source']},
        {'classification':'derived', 'value':'temperature reference', 'unit':'°C', 'source':c['profile']['temperature_origin']['antecedent']},
        {'classification':'demonstrative', 'value':'other references, bands, alarms, parameters', 'unit':'canonical per field', 'source':'MODEL_DEFAULTS.json 0.5.0'}]
    horizons = {'S0':6,'S1':48,'S2':12,'S3':12,'S4':24,'S5':6,'S6':12,'S7':6,'S8':48,'S9':8}
    if scenario not in horizons:
        raise ValueError('Escenario desconocido')
    c['time']['horizon_s'] = horizons[scenario]*3600
    if scenario in ('S0','S2'):
        c['sensor']['sigma'] = [0.0]*5
        c['environment_amplitude_C'] = 0.0
    else:
        for day in range(3):
            for start in [28800,72000]:
                a = day*86400+start
                b = a+1800
                if b <= c['time']['horizon_s']:
                    c['events'].append(event('feed', 'water', a,b,1,'1'))
    if scenario == 'S2':
        r=c['profile']['references']
        c['x0']=[r[0]-2,r[1]-1.5,6.8,40,0.85]
    specials = {'S3':('leak','water',21600,25200,.0008,'m³/s'),
                'S4':('environment','water',21600,43200,20,'°C'),
                'S5':('missing',1,7200,7800,1,'1'),
                'S6':('availability',2,7200,21600,0,'1'),
                'S7':('bias',1,7200,14400,-.5,'mg/L'),
                'S9':('leak','water',7200,28800,.003,'m³/s')}
    if scenario in specials:
        c['events'].append(event(*specials[scenario]))
    c['open_commands'] = calibrate(c)
    c['z0'] = c['open_commands'].copy()
    return c


def event(kind,target,start,end,magnitude,unit):
    return dict(kind=kind,target=target,start_s=start,end_s=end,magnitude=magnitude,unit=unit)


def validate(c):
    def finite(obj, path='config'):
        if isinstance(obj, dict):
            for k,v in obj.items(): finite(v,path+'.'+k)
        elif isinstance(obj,list):
            for i,v in enumerate(obj): finite(v,f'{path}[{i}]')
        elif isinstance(obj,(int,float)) and (isinstance(obj,bool) or not math.isfinite(obj)):
            raise ValueError(path+': valor numérico no finito o booleano')
    finite(c)
    def vec(value,n,name):
        if len(value)!=n or any(isinstance(x,bool) or not isinstance(x,(int,float)) for x in value):
            raise ValueError(name+': vector numérico inválido')
    if (c['spec_id'],c['spec_version'],c['model_id'],c['model_version']) != ('SPC-AGUA-001','0.5.0','M-AGUA-DEMO-1','1.0.0'):
        raise ValueError('Identificadores o versiones incompatibles')
    if c['domain']!=DEFAULTS['domain']: raise ValueError('Dominios matemáticos distintos del modelo aprobado')
    if c['units'] != dict(zip(VARIABLES,UNITS)): raise ValueError('Unidades incompatibles')
    if c['strategy'] not in ['open','closed']: raise ValueError('Estrategia inválida')
    if c['profile']['phase']!='crecimiento_engorde': raise ValueError('Fase fuera de alcance')
    for item in c['origin_registry']:
        if item['classification'] not in ['bibliographic','derived','demonstrative'] or not item.get('unit') or not item.get('source'):
            raise ValueError('Procedencia incompleta')
    p=c['parameters']
    signed=['ph_background','ph_external_base_per_s']
    for key,value in p.items():
        vals=value if isinstance(value,list) else [value]
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) for v in vals): raise ValueError(key+': tipo inválido')
        if key not in signed and any(v<0 for v in vals): raise ValueError(key+': debe ser no negativo')
    for key in ['area_m2','height_max_m','density_kg_m3','heat_capacity_J_kg_K','oxygen_half_saturation_mg_L','cooling_COP','temperature_Q10']:
        if p[key]<=0: raise ValueError(key+': debe ser positivo')
    vec(p['actuator_tau_s'],5,'tau')
    if min(p['actuator_tau_s'])<=0: raise ValueError('tau debe ser positivo')
    for key in ['pressure_Pa','salinity_per_mille']:
        a,b=DEFAULTS['domain'][key]
        if not a<=p[key]<=b: raise ValueError(key+': fuera de dominio')
    H,dt=c['time']['horizon_s'],c['time']['control_interval_s']
    if not 3600<=H<=259200 or not 30<=dt<=300 or H%dt!=0: raise ValueError('Horizonte o intervalo inválido')
    if c['time']['solver']!='RK45' or not 0<c['time']['max_step_s']<=min(10,dt/6): raise ValueError('Integrador o paso no aprobado')
    vec(c['time']['atol'],10,'atol')
    if min(c['time']['atol'])<=0 or not 0<c['time']['rtol']<=1e-7 or any(a>b for a,b in zip(c['time']['atol'],DEFAULTS['time']['atol'])): raise ValueError('Tolerancias inválidas o menos estrictas que el modelo aprobado')
    for key in ['x0','z0','open_commands']:
        vec(c[key],5,key)
    vec(c['profile']['references'],5,'referencias')
    domains=[DEFAULTS['domain'][v] for v in VARIABLES]
    for j,(a,b) in enumerate(domains):
        if not a<=c['x0'][j]<=b: raise ValueError(VARIABLES[j]+': estado inicial fuera de dominio')
        lo,hi=c['profile']['operating_bands'][j]
        cl,ch=c['profile']['critical_limits'][j]
        r=c['profile']['references'][j]
        if not a<=cl<=lo<=r<=hi<=ch<=b: raise ValueError(VARIABLES[j]+': bandas, referencia o límites incoherentes')
    if max(c['x0'][4],c['profile']['critical_limits'][4][1])>=p['height_max_m']: raise ValueError('Altura geométrica insuficiente')
    for key in ['z0','open_commands']:
        for j,v in enumerate(c[key]):
            if not (0 if j in (1,3) else -1)<=v<=1: raise ValueError(key+': calibración o respuesta no realizable')
    from .model import saturation
    if not np.allclose(c['open_commands'],calibrate(c),rtol=0,atol=1e-12): raise ValueError('Comandos abiertos distintos de la calibración nominal; recalcular explícitamente')
    pr=c['profile']; ctrl=c['controller']
    if ctrl['algorithm']!='sampled_hysteresis' or ctrl['initial_memory']!=[0]*5: raise ValueError('Algoritmo o memoria inicial no aprobados')
    if pr['references'][1]+ctrl['oxygen_delta_mg_L']>=.98*saturation(pr['operating_bands'][0][1],p['pressure_Pa'],p['salinity_per_mille']):
        raise ValueError('Referencia de oxígeno no realizable a saturación operativa')
    vec(c['sensor']['sigma'],5,'sigma'); vec(c['sensor']['bias'],5,'sesgo')
    if min(c['sensor']['sigma'])<0 or c['sensor']['noise_standard_clip']!=3: raise ValueError('Ruido inválido')
    for j in range(5):
        lo,hi=c['sensor']['measurement_ranges'][j]
        if lo>=hi: raise ValueError('Rango instrumental inválido')
    for key in ['thermal_delta_C','ph_delta','level_delta_m','oxygen_delta_mg_L']:
        if ctrl[key]<=0: raise ValueError('Histéresis inválida')
    if ctrl['filter_off_NTU']>=ctrl['filter_on_NTU']: raise ValueError('Umbrales de filtro invertidos')
    for e in c['events']:
        k=e['kind']; a,b=e['start_s'],e['end_s']; v=e['magnitude']; target=e['target']
        unit=UNITS[target] if k=='bias' and isinstance(target,int) and 0<=target<5 else EVENT_UNITS.get(k)
        if unit is None or e['unit']!=unit: raise ValueError('Unidad o tipo de evento incompatible')
        if not 0<=a<b<=H or a%dt or b%dt: raise ValueError('Evento fuera de horizonte o malla')
        if k in ['environment','feed','leak','rain','ph_rate','turbidity_rate'] and target!='water': raise ValueError('Objetivo de perturbación incompatible')
        if k in ['bias','missing','freeze'] and (not isinstance(target,int) or not 0<=target<5): raise ValueError('Sensor inválido')
        if k=='availability' and (not isinstance(target,int) or not 0<=target<8 or not 0<=v<=1): raise ValueError('Disponibilidad inválida')
        if k in ['feed','leak','rain','turbidity_rate'] and v<0: raise ValueError('Tasa negativa')
    for i,e in enumerate(c['events']):
        for f in c['events'][i+1:]:
            if e['target']==f['target'] and max(e['start_s'],f['start_s'])<min(e['end_s'],f['end_s']):
                kinds={e['kind'],f['kind']}
                if kinds<= {'missing','freeze','bias'} and ('freeze' in kinds or 'missing' in kinds):
                    raise ValueError('Fallos de sensor superpuestos ambiguos o redundantes')
