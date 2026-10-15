"""Ecuaciones M-AGUA-DEMO-1 1.0.0. Sin ruido ni corrección de estados."""
import math
import numpy as np
from scipy.integrate import solve_ivp
from .actuators import effective


def saturation(T,P=101325.,S=0.,factors=False):
    K=T+273.15; atm=P/101325
    ln=-139.34411+157570.1/K-66423080/K**2+12438000000/K**3-862194900000/K**4
    fs=math.exp(-S*(.017674-10.754/K+2140.7/K**2))
    w=math.exp(11.8571-3840.70/K-216961/K**2)
    theta=.000975-1.426e-5*T+6.436e-8*T*T
    fp=(atm-w)*(1-theta*atm)/((1-w)*(1-theta))
    value=math.exp(ln)*fs*fp
    return (value,fs,fp) if factors else value


def rates(t,state,v,g,d,c):
    p=c['parameters']; prof=c['profile']
    T,C,ph,U,h=state[:5]; z=state[5:]
    H,K,A,B,D,F,I,O=effective(z,g)
    V=p['area_m2']*h
    qi=p['inlet_max_m3_s']*I+p['exchange_m3_s']
    qo=p['outlet_max_m3_s']*O+p['exchange_m3_s']
    qr=p['rain_base_m3_s']+d['rain']; ql=p['leak_base_m3_s']+d['leak']; qe=p['evaporation_m3_s']
    Te=prof['baseline_environment_C']+c['environment_amplitude_C']*math.sin(2*math.pi*t/86400)+d['environment']
    temp=(p['heat_exchange_W_K']*(Te-T)+p['heater_max_W']*H-p['cooler_max_W']*K)/(p['density_kg_m3']*p['heat_capacity_J_kg_K']*V)+(qi*(prof['inlet_temperature_C']-T)+qr*(prof['rain_temperature_C']-T))/V
    ft=p['temperature_Q10']**((T-20)/10)
    R=(p['fish_consumption_mg_kg_s_at20']*p['biomass_kg']*ft*(1+p['feed_respiration_multiplier']*d['feed'])/(1000*V)+p['water_consumption_mg_L_s_at20']*ft)*C/(p['oxygen_half_saturation_mg_L']+C)
    oxygen=(p['k_natural_s_inv']+p['k_air_s_inv']*A)*(saturation(T,p['pressure_Pa'],p['salinity_per_mille'])-C)-R+(qi*(prof['inlet_oxygen_mg_L']-C)+qr*(prof['rain_oxygen_mg_L']-C)+qe*C)/V
    phdot=p['ph_relaxation_s_inv']*(p['ph_background']-ph)+p['ph_actuation_per_s']*(B-D)+p['ph_external_base_per_s']+d['ph_rate']-p['ph_feed_coefficient_per_s']*d['feed']
    udot=(qi*(p['inlet_turbidity_NTU']-U)+qr*(p['rain_turbidity_NTU']-U))/V+p['turbidity_source_NTU_s']*(1+d['feed'])-(p['k_settle_s_inv']+p['k_filter_s_inv']*F)*U+p['turbidity_external_base_NTU_s']+d['turbidity_rate']
    hdot=(qi+qr-qo-ql-qe)/p['area_m2']
    return np.r_[temp,oxygen,phdot,udot,hdot,(np.asarray(v)-z)/p['actuator_tau_s']]


def integrate(t,state,end,v,g,d,c,check_domain=True):
    events=[]
    if check_domain:
        for j,name in enumerate(c['variable_order']):
            lo,hi=c['domain'][name]
            # C y U toleran únicamente el residuo numérico aprobado, sin recorte.
            if j in (1,3): lo=-1e-7
            for bound,direction in [(lo,-1),(hi,1)]:
                def crossing(t,y,j=j,bound=bound,direction=direction):
                    distance=y[j]-bound
                    if distance==0 and direction*rates(t,y,v,g,d,c)[j]<=0:
                        return -direction*1e-14
                    return distance
                crossing.terminal=True; crossing.direction=direction
                events.append(crossing)
    tc=c['time']
    return solve_ivp(lambda s,x:rates(s,x,v,g,d,c),(t,end),state,method='RK45',rtol=tc['rtol'],atol=tc['atol'],max_step=min(tc['max_step_s'],tc['control_interval_s']/6),events=events or None)
