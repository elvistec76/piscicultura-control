"""Aplicación local: ejecutar con python -m streamlit run app.py."""
import json
import os
import uuid
from copy import deepcopy
import pandas as pd
import streamlit as st
from piscicultura.config import DEFAULTS,VARIABLES,UNITS,make_config,duplicate_profile,calibrate,RunConfig,event
from piscicultura.model import saturation
from piscicultura.repository import SQLiteRepository
from piscicultura.service import SimulationService
from piscicultura.export import export_bytes
from piscicultura.charts import figures,LABELS

st.set_page_config(page_title='Agua · Piscicultura',page_icon='💧',layout='wide')
st.title('Calidad del agua · Simulador de control')
st.caption('SPC-AGUA-001 0.5.0 · M-AGUA-DEMO-1 1.0.0 · Cinco variables, un estanque por corrida')
st.warning('Simulación académica sin validación de campo. pH y turbidez son aproximaciones empíricas; los parámetros demostrativos no son recomendaciones productivas.')
STATUS={'PREPARED':'Preparada','RUNNING':'En ejecución','PAUSED':'Pausada','COMPLETED':'Completada','STOPPED':'Detenida','FAILED':'Fallida','INTERRUPTED':'Interrumpida'}
STRATEGY={'Lazo cerrado · histéresis':'closed','Lazo abierto · constante calibrado':'open'}
SCENARIOS={'S0':'Equilibrio','S1':'Nominal','S2':'Recuperación','S3':'Fuga','S4':'Carga térmica','S5':'Lectura ausente','S6':'Aireación averiada','S7':'Sesgo plausible','S8':'Rendimiento','S9':'Capacidad insuficiente'}
if 'service' not in st.session_state:
    st.session_state.service=SimulationService(SQLiteRepository(os.environ.get('PISCICULTURA_DB','work/piscicultura.sqlite')))
service=st.session_state.service;repo=service.repo
if 'profiles' not in st.session_state: st.session_state.profiles=deepcopy(DEFAULTS['profiles'])
config_tab,execution_tab,compare_tab,history_tab=st.tabs(['Configuración','Ejecución y evolución','Comparación','Historial y exportación'])
with config_tab:
    col1,col2,col3=st.columns(3)
    profiles=st.session_state.profiles
    choice=col1.selectbox('Perfil de especie',range(len(profiles)),format_func=lambda i:profiles[i]['name'])
    scenario=col2.selectbox('Escenario',list(SCENARIOS),format_func=lambda x:x+' · '+SCENARIOS[x],index=1)
    mode=col3.selectbox('Estrategia',list(STRATEGY))
    profile=st.session_state.profiles[choice]
    st.write(f"**{profile['scientific_name']}** · Crecimiento o engorde")
    if st.button('Duplicar perfil para editar'):
        st.session_state.profiles.append(duplicate_profile(profile,profile['name']+' · copia'))
        st.rerun()
    c=make_config(min(choice,2),scenario,STRATEGY[mode]);c['profile']=deepcopy(profile)
    st.caption('Referencias térmicas derivadas de antecedentes; bandas, alarmas y restantes consignas demostrativas. Unidades canónicas visibles en cada campo.')
    with st.form('configuration'):
        cols=st.columns(4)
        c['parameters']['area_m2']=cols[0].number_input('Área (m²)',value=10.)
        c['parameters']['height_max_m']=cols[1].number_input('Altura geométrica (m)',value=1.5)
        c['parameters']['biomass_kg']=cols[2].number_input('Biomasa fija (kg)',value=50.)
        c['parameters']['pressure_Pa']=cols[3].number_input('Presión (Pa)',value=101325.)
        cols=st.columns(3)
        c['parameters']['salinity_per_mille']=cols[0].number_input('Salinidad (‰)',value=0.)
        c['time']['horizon_s']=cols[1].number_input('Horizonte (h)',value=float(c['time']['horizon_s']/3600))*3600
        c['time']['control_interval_s']=cols[2].number_input('Intervalo de control (s)',value=60)
        c['time']['max_step_s']=min(10,c['time']['control_interval_s']/6)
        st.write('**Condiciones iniciales, referencias, bandas y alarmas**')
        for j,(name,unit) in enumerate(zip(LABELS,UNITS)):
            cols=st.columns(6)
            c['x0'][j]=cols[0].number_input(f'{name}: inicial ({unit})',value=float(c['x0'][j]))
            c['profile']['references'][j]=cols[1].number_input(f'{name}: referencia ({unit})',value=float(profile['references'][j]))
            for col,key,idx,label in [(cols[2],'operating_bands',0,'banda inferior'),(cols[3],'operating_bands',1,'banda superior'),(cols[4],'critical_limits',0,'alarma inferior'),(cols[5],'critical_limits',1,'alarma superior')]:
                c['profile'][key][j][idx]=col.number_input(f'{name}: {label} ({unit})',value=float(profile[key][j][idx]))
        st.caption('Turbidez: solo el límite superior genera alarma. El inferior se conserva como metadato.')
        with st.expander('Sensores y parámetros del modelo'):
            for j,(name,unit) in enumerate(zip(LABELS,UNITS)):
                a,b=st.columns(2)
                c['sensor']['sigma'][j]=a.number_input(f'Ruido σ · {name} ({unit})',value=float(c['sensor']['sigma'][j]))
                c['sensor']['bias'][j]=b.number_input(f'Sesgo base · {name} ({unit})',value=0.)
            parameter_text=st.text_area('Parámetros demostrativos (JSON, unidades indicadas en los nombres)',json.dumps(c['parameters'],ensure_ascii=False,indent=2),height=220)
        st.write('**Perturbaciones y fallos programados**')
        st.caption('Intervalos [inicio, fin) en segundos sobre la malla. El controlador solo recibe lecturas; este calendario sirve para inyección y auditoría.')
        event_text=st.text_area('Calendario del escenario (JSON)',json.dumps(c['events'],ensure_ascii=False,indent=2),height=180)
        st.caption('Tipos: environment °C, feed adimensional, leak/rain m³/s, ph_rate s⁻¹, turbidity_rate NTU/s; bias usa unidad del sensor, missing/freeze adimensional; availability factor [0,1]. Sensores 0–4: T,C,p,U,h. Actuadores 0–7: calor, frío, aire, pH+, pH−, filtro, entrada, salida.')
        submit=st.form_submit_button('Validar y preparar corrida')
    if submit:
        try:
            current=st.session_state.get('run_id')
            if current in service.active and service.active[current][2].status in ['PREPARED','RUNNING','PAUSED']: raise ValueError('Detenga la corrida activa antes de preparar otra.')
            c['parameters']=json.loads(parameter_text);c['events']=json.loads(event_text)
            pr=c['profile'];r=pr['references'];p=c['parameters']
            pr.update(inlet_temperature_C=r[0],rain_temperature_C=r[0],baseline_environment_C=r[0]-2,inlet_oxygen_mg_L=.95*saturation(r[0],p['pressure_Pa'],p['salinity_per_mille']),rain_oxygen_mg_L=.95*saturation(r[0],p['pressure_Pa'],p['salinity_per_mille']))
            c['open_commands']=calibrate(c);c['z0']=c['open_commands'].copy()
            cfg=RunConfig.freeze(c)
            st.session_state.draft=cfg.data
            st.session_state.run_id=service.prepare(cfg.data)
            st.success('Configuración válida y congelada. Corrida preparada sin avanzar el tiempo.')
        except (ValueError,TypeError,KeyError,ZeroDivisionError) as exc: st.error('Configuración rechazada: '+str(exc))
    st.dataframe(pd.DataFrame(c['origin_registry']).rename(columns={'classification':'Clase de origen','value':'Valor o grupo','unit':'Unidad','source':'Procedencia'}),hide_index=True)


def show_run(rid,key):
    run=repo.get(rid);samples=repo.records(rid,'samples');actions=repo.records(rid,'actuator_records')
    st.write(f"**{STATUS[run['status']]}** · {run['time_s']/3600:.3f} h simuladas · {run['config']['profile']['name']}")
    st.caption('Corrida '+rid+' · '+('Lazo cerrado' if run['config']['strategy']=='closed' else 'Lazo abierto'))
    if run['cause']: st.error('Causa: '+run['cause'])
    if samples:
        last=samples[-1];cols=st.columns(5)
        for j,(name,unit) in enumerate(zip(LABELS,UNITS)):
            v=last['values'][j];cols[j].metric(name,f'{v:.4f} {unit}' if v is not None else 'Sin lectura')
            cols[j].caption({'GOOD':'Válida','MISSING':'Ausente','INVALID':'Inválida'}[last['qualities'][j]])
        for f in figures(run,samples,actions): st.plotly_chart(f,use_container_width=True,key=key+f.layout.title.text)
    events=repo.records(rid,'events')
    st.write('**Alarmas y eventos**')
    st.caption('Inyección: auditoría del simulador. Alarma: condición observable en mediciones. Reconocer una alarma solo registra su lectura.')
    if events:
        st.dataframe(pd.DataFrame(events).rename(columns={'event_seq':'Secuencia','time_s':'Tiempo (s)','category':'Origen','target':'Objetivo','severity':'Severidad','transition':'Transición','code':'Código','data':'Detalle'}),hide_index=True)
        alarm_ids=[e['event_seq'] for e in events if e['category']=='alarm' and e['transition']=='activation']
        if alarm_ids:
            seq=st.selectbox('Alarma para reconocer',alarm_ids,key=key+'ack')
            if st.button('Reconocer alarma',key=key+'ackbutton'): repo.acknowledge(rid,seq);st.success('Reconocimiento registrado.')
    with st.expander('Configuración congelada, métricas y terminación'):
        st.json(run['config']);st.json(repo.records(rid,'metrics'));st.json(run['termination_state'])
    st.download_button('Descargar corrida (ZIP: JSON y CSV)',export_bytes(repo,rid),file_name=rid+'.zip',mime='application/zip',key=key+'download')

with execution_tab:
    rid=st.session_state.get('run_id')
    if rid:
        run=repo.get(rid);cols=st.columns(5)
        try:
            if cols[0].button('Avanzar un intervalo',disabled=run['status'] not in ['PREPARED','RUNNING']):
                service.advance(rid,uuid.uuid4().hex,run['step']);st.rerun()
            if cols[1].button('Pausar',disabled=run['status']!='RUNNING'):
                service.pause(rid);st.rerun()
            if cols[2].button('Continuar',disabled=run['status']!='PAUSED'):
                service.resume(rid);st.rerun()
            if cols[3].button('Detener',disabled=run['status'] not in ['PREPARED','RUNNING','PAUSED']):
                service.stop(rid);st.rerun()
            if cols[4].button('Ejecutar hasta terminar',disabled=run['status'] not in ['PREPARED','RUNNING']):
                with st.spinner('Calculando y guardando intervalos…'): service.run_all(rid)
                st.rerun()
        except (ValueError,RuntimeError) as exc: st.error(str(exc))
        show_run(rid,'active')
    else: st.info('Prepare una corrida en Configuración. Consultar esta pestaña no integra el proceso.')
with compare_tab:
    st.write('Ambas estrategias comparten agua inicial, respuesta inicial de actuadores, calendario y tabla completa de ruido. Solo cambia la estrategia.')
    if st.button('Comparar estrategias con la configuración validada',disabled='draft' not in st.session_state):
        try:
            with st.spinner('Ejecutando lazo abierto y cerrado…'): st.session_state.comparison=service.compare(st.session_state.draft)
        except (ValueError,RuntimeError) as exc: st.error(str(exc))
    if 'comparison' in st.session_state:
        comparison=st.session_state.comparison
        st.write(f"Tramo común: {comparison['common_duration_s']/3600:.3f} h. Horizonte solicitado: {comparison['requested_horizon_s']/3600:.1f} h.")
        rows=[]
        for strategy,data in comparison['full'].items():
            m=data['metrics'];rows.append({'Estrategia':'Abierto' if strategy=='open' else 'Cerrado','Estado':STATUS[data['status']],'Duración (h)':data['time_s']/3600,'J adimensional':m['J'],'Causa':data['cause']})
        st.dataframe(rows,hide_index=True)
        st.caption('Se muestran métricas del horizonte observado y del tramo común por separado. Una terminación anticipada impide declarar ventaja por observar menos tiempo.')
        st.json(comparison)
        st.download_button('Descargar comparación JSON',json.dumps(comparison,ensure_ascii=False,indent=2),file_name='comparison.json')
with history_tab:
    history=repo.list()
    if history:
        st.dataframe(pd.DataFrame(history).assign(status=lambda f:f.status.map(STATUS)).rename(columns={'run_id':'Corrida','status':'Estado','cause':'Causa','time_s':'Tiempo (s)','step':'Paso','created_at':'Fecha UTC'}),hide_index=True)
        selected=st.selectbox('Consultar corrida guardada',[r['run_id'] for r in history])
        show_run(selected,'history')
    else: st.info('Aún no hay corridas guardadas.')
