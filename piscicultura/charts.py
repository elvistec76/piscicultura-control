"""Figuras locales sin dependencias remotas."""
import plotly.graph_objects as go
from .config import VARIABLES,UNITS,ACTIONS

LABELS=['Temperatura','Oxígeno disuelto','pH','Turbidez','Nivel']
ACTION_LABELS=['Calentamiento','Enfriamiento','Aireación','Incremento pH','Disminución pH','Filtración','Entrada','Salida']

def figures(run,samples,actions):
    t=[s['time_s']/3600 for s in samples]; result=[]
    for j,(name,unit) in enumerate(zip(LABELS,UNITS)):
        f=go.Figure()
        f.add_trace(go.Scatter(x=t,y=[s['x'][j] for s in samples],name='Estado exacto x'))
        f.add_trace(go.Scatter(x=t,y=[s['values'][j] for s in samples],name='Lectura y',connectgaps=False,opacity=.65))
        lo,hi=run['config']['profile']['operating_bands'][j]
        f.add_hrect(y0=lo,y1=hi,fillcolor='green',opacity=.12,line_width=0,annotation_text='Banda operativa demostrativa')
        f.add_hline(y=run['config']['profile']['references'][j],line_dash='dash',annotation_text='Referencia')
        f.update_layout(title=name,xaxis_title='Tiempo simulado (h)',yaxis_title=f'{name} ({unit if unit!="1" else "adimensional"})',height=320,margin=dict(l=40,r=20,t=45,b=40))
        result.append(f)
    f=go.Figure()
    for name,label in zip(ACTIONS,ACTION_LABELS):
        a=[a for a in actions if a['actuator_id']==name]
        f.add_trace(go.Scatter(x=[a['start_s']/3600 for a in a],y=[a['mean_effective'] for a in a],name=label,mode='lines',line_shape='hv'))
    f.update_layout(title='Acciones efectivas medias por intervalo',xaxis_title='Tiempo simulado (h)',yaxis_title='Intensidad normalizada',height=350)
    return result+[f]
