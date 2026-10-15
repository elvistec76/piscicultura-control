"""Capacidades, respuesta firmada e integrales exactas por intervalo."""
import math
import numpy as np

LOW=np.array([-1,0,-1,0,-1])

def limit(v):
    raw=np.asarray(v,dtype=float)
    if raw.shape!=(5,) or not np.isfinite(raw).all(): raise ValueError('Orden inválida')
    out=np.clip(raw,LOW,1)
    return out, bool(np.any(out!=raw))


def effective(z,g):
    T,C,p,U,h=z
    return np.array([max(T,0),max(-T,0),C,max(p,0),max(-p,0),U,max(h,0),max(-h,0)])*g


def response(z,v,t,tau):
    return np.asarray(v)+(np.asarray(z)-v)*np.exp(-t/np.asarray(tau))


def mean_actions(z,v,duration,tau,g):
    """Integración separada en cada raíz; nunca pos(promedio z)."""
    signed={0:(0,1),2:(3,4),4:(6,7)}
    out=np.zeros(8)
    for j,(a,b,q) in enumerate(zip(z,v,tau)):
        points=[0.,duration]
        if b!=0 and a!=b:
            ratio=-b/(a-b)
            if 0<ratio<1:
                root=-q*math.log(ratio)
                if 0<root<duration: points.insert(1,root)
        for l,r in zip(points,points[1:]):
            integ=b*(r-l)+(a-b)*q*(math.exp(-l/q)-math.exp(-r/q))
            if j in signed:
                plus,minus=signed[j]
                if b+(a-b)*math.exp(-(l+r)/2/q)>=0: out[plus]+=integ
                else: out[minus]-=integ
            else: out[2 if j==1 else 5]+=integ
    return out*np.asarray(g)/duration if duration>0 else out
