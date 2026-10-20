"""Figuras locales sin dependencias remotas."""
import plotly.graph_objects as go
from .config import VARIABLES,UNITS,ACTIONS

LABELS=['Temperatura','Oxígeno disuelto','pH','Turbidez','Nivel']
ACTION_LABELS=['Calentamiento','Enfriamiento','Aireación','Incremento pH','Disminución pH','Filtración','Entrada','Salida']


def time_label(seconds):
    hours,remainder=divmod(max(0,round(seconds)),3600)
    minutes,seconds=divmod(remainder,60)
    return f'{hours} h'+(f' {minutes} min' if minutes or seconds else '')+(f' {seconds} s' if seconds else '')


def figures(run,samples,actions):
    t=[s['time_s']/3600 for s in samples]; result=[]
    end=max((s['time_s'] for s in samples),default=0)
    tick_step=next(step for step in [1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,21600,43200,86400] if step>=end/5)
    ticks=list(range(0,int(end)+1,tick_step))
    time_axis=dict(title='Tiempo simulado',tickvals=[tick/3600 for tick in ticks],ticktext=[time_label(tick) for tick in ticks])
    for j,(name,unit) in enumerate(zip(LABELS,UNITS)):
        f=go.Figure()
        hover='%{customdata}<br>%{y:.2f}'+(' '+unit if unit!='1' else '')+'<extra>%{fullData.name}</extra>'
        times=[time_label(s['time_s']) for s in samples]
        f.add_trace(go.Scatter(x=t,y=[s['x'][j] for s in samples],name='Valor del agua simulada',line=dict(color='#67e8f9'),customdata=times,hovertemplate=hover))
        f.add_trace(go.Scatter(x=t,y=[s['values'][j] for s in samples],name='Lectura del sensor',connectgaps=False,opacity=.75,line=dict(color='#a78bfa'),customdata=times,hovertemplate=hover))
        lo,hi=run['config']['profile']['operating_bands'][j]
        if j==3: lo=run['config']['domain']['turbidity_NTU'][0]
        f.add_hrect(y0=lo,y1=hi,fillcolor='green',opacity=.12,line_width=0,annotation_text='Rango deseado')
        f.add_hline(y=run['config']['profile']['references'][j],line_dash='dash',line_color='#fbbf24',annotation_text='Objetivo')
        f.update_layout(title=name,xaxis=time_axis,yaxis_title=f'{name} ({unit})' if unit!='1' else name,height=320,margin=dict(l=40,r=20,t=45,b=40))
        result.append(f)
    f=go.Figure()
    for name,label in zip(ACTIONS,ACTION_LABELS):
        a=[a for a in actions if a['actuator_id']==name]
        f.add_trace(go.Scatter(x=[a['start_s']/3600 for a in a],y=[a['mean_effective'] for a in a],name=label,mode='lines',line_shape='hv',customdata=[time_label(a['start_s']) for a in a],hovertemplate='%{customdata}<br>Intensidad: %{y:.1%}<extra>%{fullData.name}</extra>'))
    f.update_layout(title='Funcionamiento de los equipos',xaxis=time_axis,yaxis_title='Intensidad del equipo',yaxis_tickformat='.0%',height=350)
    for plot in result+[f]: plot.update_layout(uirevision=run['run_id'])
    return result+[f]
