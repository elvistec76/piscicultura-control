from copy import deepcopy
import math
import numpy as np
import pytest
from piscicultura.config import make_config,RunConfig,DEFAULTS
from piscicultura.model import saturation,integrate
from piscicultura.actuators import effective,mean_actions,response,limit


def isolated():
    c=make_config(0,'S0','open'); p=c['parameters']
    for key in ['heat_exchange_W_K','k_natural_s_inv','k_air_s_inv','fish_consumption_mg_kg_s_at20','water_consumption_mg_L_s_at20','ph_relaxation_s_inv','ph_actuation_per_s','turbidity_source_NTU_s','k_settle_s_inv','k_filter_s_inv','inlet_max_m3_s','outlet_max_m3_s','evaporation_m3_s']:
        p[key]=0.
    c['x0']=[20,2,8,40,1];c['z0']=[0]*5
    return c


def solve(c,duration,v=None,g=None):
    from piscicultura.scenarios import conditions
    d,_,_=conditions(c,0)
    return integrate(0,np.r_[c['x0'],c['z0']],duration,np.zeros(5) if v is None else v,np.ones(8) if g is None else g,d,c,False).y[:,-1]


def test_AC01():
    for j in range(3): RunConfig.freeze(make_config(j))
    for path,value in [('area_m2',0),('biomass_kg',float('nan')),('area_m2','10')]:
        c=make_config();c['parameters'][path]=value
        with pytest.raises((ValueError,TypeError)): RunConfig.freeze(c)
    for mutate in [lambda c:c['events'].append(dict(kind='leak',target='water',start_s=1,end_s=60,magnitude=.001,unit='m³/s')),
                   lambda c:c['profile']['references'].__setitem__(1,8.4),
                   lambda c:c['units'].__setitem__('ph','mg/L'),
                   lambda c:c['origin_registry'][0].__setitem__('source','')]:
        c=make_config();mutate(c)
        with pytest.raises(ValueError): RunConfig.freeze(c)


def test_AC02():
    for t,expected in [(10,11.28794737),(20,9.09242604),(30,7.55879605)]:
        value,fs,fp=saturation(t,factors=True)
        assert abs(value-expected)<=1e-6 and fs==fp==1


def test_AC03():
    c=isolated();p=c['parameters']
    # Recambio coordinado .0002 más entrada .0008 evita acciones opuestas.
    p.update(exchange_m3_s=.0002,inlet_max_m3_s=.0008,leak_base_m3_s=.0001,evaporation_m3_s=.00001)
    c['z0'][4]=1
    result=solve(c,600,[0,0,0,0,1])
    assert abs(result[4]-1.0414)<=1e-7
    assert abs((p['exchange_m3_s']+p['inlet_max_m3_s'])*600-.6)<=1e-12
    assert abs(p['exchange_m3_s']*600-.12)<=1e-12


def test_AC04():
    c=isolated();c['parameters']['heater_max_W']=10000;c['z0'][0]=1
    assert abs(solve(c,3600,[1,0,0,0,0])[0]-20.8600095557)<=1e-6


def test_AC05():
    c=isolated();c['parameters']['k_natural_s_inv']=1e-4
    expected=saturation(20)+(2-saturation(20))*math.exp(-.36)
    assert abs(solve(c,3600)[1]-expected)<=1e-5


def test_AC06():
    c=isolated();c['parameters']['ph_relaxation_s_inv']=1/86400
    assert abs(solve(c,3600)[2]-(7.4+.6*math.exp(-1/24)))<=1e-6


def test_AC07():
    c=isolated();c['parameters']['k_settle_s_inv']=2e-5
    assert abs(solve(c,3600)[3]-40*math.exp(-.072))<=1e-4


def test_AC08():
    c=isolated();result=solve(c,30,[1]*5)
    assert np.max(abs(result[5:]-(1-math.exp(-1))))<=1e-7
    z=[1,0,0,0,0];v=np.array([-1,0,0,0,0]);tau=[30]*5
    for t in np.linspace(0,120,100):
        a=effective(response(z,v,t,tau),np.ones(8));assert a[0]*a[1]==0
    mean=mean_actions(z,v,120,tau,np.ones(8))
    from scipy.integrate import quad
    for j in [0,1]:
        expected=quad(lambda t:effective(response(z,v,t,tau),np.ones(8))[j],0,120,points=[30*math.log(2)])[0]/120
        assert abs(mean[j]-expected)<1e-10
    out,limited=limit([3,-1,-3,2,0]);assert limited and list(out)==[1,0,-1,1,0]
