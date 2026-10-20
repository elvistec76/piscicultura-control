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
from piscicultura.tank_view import show_tank,SHAPES

st.set_page_config(page_title='AquaControl · Piscicultura',page_icon='💧',layout='wide')
st.title('AquaControl · Calidad del agua')
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
    with st.expander('Detalles del perfil'):
        st.write(f"**{profile['scientific_name']}** · Crecimiento o engorde")
        if st.button('Duplicar perfil para editar'):
            st.session_state.profiles.append(duplicate_profile(profile,profile['name']+' · copia'))
            st.rerun()
    c=make_config(min(choice,2),scenario,STRATEGY[mode]);c['profile']=deepcopy(profile)
    with st.form('configuration'):
        cols=st.columns(4)
        c['parameters']['area_m2']=cols[0].number_input('Área (m²)',value=10.)
        c['parameters']['height_max_m']=cols[1].number_input('Altura geométrica (m)',value=1.5)
        c['parameters']['biomass_kg']=cols[2].number_input('Biomasa fija (kg)',value=50.)
        c['time']['horizon_s']=cols[3].number_input('Horizonte (h)',value=float(c['time']['horizon_s']/3600))*3600
        st.write('**Condiciones iniciales del agua**')
        cols=st.columns(5)
        for j,(name,unit) in enumerate(zip(LABELS,UNITS)):
            c['x0'][j]=cols[j].number_input(f'{name}: inicial ({unit})',value=float(c['x0'][j]))
        with st.expander('Referencias, bandas y alarmas'):
            st.caption('Se cargan según la especie. Las bandas evalúan la operación; los límites críticos generan alarmas. En turbidez solo se usa la alarma superior.')
            for j,(name,unit) in enumerate(zip(LABELS,UNITS)):
                cols=st.columns(5)
                c['profile']['references'][j]=cols[0].number_input(f'{name}: referencia ({unit})',value=float(profile['references'][j]))
                for col,key,idx,label in [(cols[1],'operating_bands',0,'banda inferior'),(cols[2],'operating_bands',1,'banda superior'),(cols[3],'critical_limits',0,'alarma inferior'),(cols[4],'critical_limits',1,'alarma superior')]:
                    if j==3 and key=='critical_limits' and idx==0:
                        continue
                    c['profile'][key][j][idx]=col.number_input(f'{name}: {label} ({unit})',value=float(profile[key][j][idx]))
        with st.expander('Sensores y parámetros del modelo'):
            cols=st.columns(3)
            c['parameters']['pressure_Pa']=cols[0].number_input('Presión (Pa)',value=101325.)
            c['parameters']['salinity_per_mille']=cols[1].number_input('Salinidad (‰)',value=0.)
            c['time']['control_interval_s']=cols[2].number_input('Intervalo de control (s)',value=60)
            c['time']['max_step_s']=min(10,c['time']['control_interval_s']/6)
            for j,(name,unit) in enumerate(zip(LABELS,UNITS)):
                a,b=st.columns(2)
                c['sensor']['sigma'][j]=a.number_input(f'Ruido σ · {name} ({unit})',value=float(c['sensor']['sigma'][j]))
                c['sensor']['bias'][j]=b.number_input(f'Sesgo base · {name} ({unit})',value=0.)
            dedicated_parameters={'area_m2','height_max_m','biomass_kg','pressure_Pa','salinity_per_mille'}
            model_parameters={key:value for key,value in c['parameters'].items() if key not in dedicated_parameters}
            st.caption('Otros parámetros del modelo. Área, altura, biomasa, presión y salinidad se editan únicamente en sus campos.')
            parameter_text=st.text_area('Parámetros demostrativos (JSON, unidades indicadas en los nombres)',json.dumps(model_parameters,ensure_ascii=False,indent=2),height=220)
        with st.expander('Perturbaciones y fallos programados'):
            st.caption('El escenario ya incluye su calendario. Modifíquelo solo para personalizar el experimento. Intervalos [inicio, fin) en segundos, múltiplos del intervalo de control.')
            event_text=st.text_area('Calendario del escenario (JSON)',json.dumps(c['events'],ensure_ascii=False,indent=2),height=180)
            st.caption('Tipos: environment °C, feed adimensional, leak/rain m³/s, ph_rate s⁻¹, turbidity_rate NTU/s; bias usa unidad del sensor, missing/freeze adimensional; availability factor [0,1]. Sensores 0–4: T,C,p,U,h. Actuadores 0–7: calor, frío, aire, pH+, pH−, filtro, entrada, salida.')
        submit=st.form_submit_button('Validar y preparar corrida')
    if submit:
        try:
            current=st.session_state.get('run_id')
            if current in service.active and service.active[current][2].status in ['PREPARED','RUNNING','PAUSED']: raise ValueError('Detenga la corrida activa antes de preparar otra.')
            extra_parameters=json.loads(parameter_text)
            if not isinstance(extra_parameters,dict): raise ValueError('Los parámetros del modelo deben ser un objeto JSON.')
            if dedicated_parameters.intersection(extra_parameters): raise ValueError('Edite área, altura, biomasa, presión y salinidad en sus campos, no en el JSON.')
            c['parameters'].update(extra_parameters);c['events']=json.loads(event_text)
            pr=c['profile'];r=pr['references'];p=c['parameters']
            pr.update(inlet_temperature_C=r[0],rain_temperature_C=r[0],baseline_environment_C=r[0]-2,inlet_oxygen_mg_L=.95*saturation(r[0],p['pressure_Pa'],p['salinity_per_mille']),rain_oxygen_mg_L=.95*saturation(r[0],p['pressure_Pa'],p['salinity_per_mille']))
            c['open_commands']=calibrate(c);c['z0']=c['open_commands'].copy()
            cfg=RunConfig.freeze(c)
            st.session_state.draft=cfg.data
            st.session_state.run_id=service.prepare(cfg.data)
            st.session_state.presentation_run_id=st.session_state.run_id
            st.success('Configuración válida y congelada. Corrida preparada sin avanzar el tiempo.')
        except (ValueError,TypeError,KeyError,ZeroDivisionError) as exc: st.error('Configuración rechazada: '+str(exc))
    origins=pd.DataFrame(c['origin_registry']).replace({'bibliographic':'Bibliográfico','derived':'Derivado','demonstrative':'Demostrativo','Csat coefficients':'Coeficientes de saturación de oxígeno','temperature reference':'Referencia térmica','other references, bands, alarms, parameters':'Otras referencias, bandas, alarmas y parámetros','canonical per field':'Unidad indicada en cada campo'})
    with st.expander('Procedencia de los valores'):
        st.dataframe(origins.rename(columns={'classification':'Clase de origen','value':'Valor o grupo','unit':'Unidad','source':'Procedencia'}),hide_index=True)


def readable_duration(seconds):
    hours,remainder=divmod(max(0,round(seconds)),3600)
    minutes,seconds=divmod(remainder,60)
    parts=[f'{hours} h']
    if minutes or seconds: parts.append(f'{minutes} min')
    if seconds: parts.append(f'{seconds} s')
    return ' '.join(parts)


def show_run(rid,key):
    run=repo.get(rid);samples=repo.records(rid,'samples');actions=repo.records(rid,'actuator_records')
    summary=st.columns(3)
    state_label='Lista para iniciar' if run['status']=='PREPARED' else STATUS[run['status']]
    summary[0].write(f"**Estado:** {state_label}")
    summary[1].write(f"**Tiempo simulado:** {readable_duration(run['time_s'])} de {readable_duration(run['config']['time']['horizon_s'])}")
    summary[2].write(f"**Especie:** {run['config']['profile']['name']}")
    st.progress(min(1.,max(0.,run['time_s']/run['config']['time']['horizon_s'])))
    if run['cause']: st.error('Causa: '+run['cause'])
    if run['metrics_status']=='FAILED': st.error('No se pudieron calcular los resultados: '+run['metrics_cause']+'. Los datos de la simulación están guardados.')
    elif run['metrics_status']=='UNAVAILABLE': st.warning('Los resultados de esta simulación no están disponibles.')
    if run['status']=='PREPARED':
        st.info('La configuración está lista. Use «Avanzar un intervalo» para revisar paso a paso o «Ejecutar hasta terminar» para calcular toda la simulación.')
    if samples:
        st.write('**Últimas lecturas del agua**')
        last=samples[-1];cols=st.columns(5)
        for j,(name,unit) in enumerate(zip(LABELS,UNITS)):
            v=last['values'][j];display_unit='' if unit=='1' else ' '+unit
            cols[j].metric(name,f'{v:.2f}{display_unit}' if v is not None else 'Sin lectura')
            lo,hi=run['config']['profile']['operating_bands'][j]
            if last['qualities'][j]!='GOOD':
                cols[j].caption({'MISSING':'Lectura ausente','INVALID':'Lectura inválida'}.get(last['qualities'][j],'Lectura no disponible'))
            else:
                cols[j].caption('Dentro del rango deseado' if v<=hi and (j==3 or v>=lo) else 'Fuera del rango deseado')
        st.write('**Evolución del agua**')
        st.caption('La franja verde muestra el rango deseado y la línea punteada, el valor objetivo.')
        for f in figures(run,samples,actions): st.plotly_chart(f,width="stretch",key=key+f.layout.title.text)
    events=repo.records(rid,'events')
    st.write('**Alarmas**')
    alarms=[e for e in events if e['category']=='alarm']
    if alarms:
        alarm_labels={'LIMITE_CRITICO':'Fuera de los límites de alarma','FUERA_DE_BANDA':'Fuera del rango deseado','LECTURA_MISSING':'Lectura ausente','LECTURA_INVALID':'Lectura inválida'}
        st.dataframe([{'Momento':readable_duration(e['time_s']),'Variable':dict(zip(VARIABLES,LABELS)).get(e['target'],e['target']),'Estado':{'activation':'Activada','clear':'Finalizada'}.get(e['transition'],e['transition']),'Aviso':alarm_labels.get(e['code'],e['code'])} for e in alarms],hide_index=True)
        alarm_ids=[e['event_seq'] for e in events if e['category']=='alarm' and e['transition']=='activation']
        if alarm_ids:
            st.caption('Reconocer una alarma registra que la revisó; no corrige las condiciones del agua.')
            seq=st.selectbox('Alarma para reconocer',alarm_ids,key=key+'ack')
            if st.button('Reconocer alarma',key=key+'ackbutton'): repo.acknowledge(rid,seq);st.success('Reconocimiento registrado.')
    else:
        st.caption('Todavía no hay lecturas para evaluar alarmas.' if not samples else 'No se han registrado alarmas.')
    stored_metrics=repo.records(rid,'metrics')
    if run['metrics_status']=='READY' and stored_metrics and stored_metrics[0]['x']:
        m=stored_metrics[0];st.write('**Resultados de la simulación**')
        st.dataframe([{'Variable':name,'Tiempo fuera del rango deseado':readable_duration(m['x']['outside_s'][j]),'Tiempo hasta estabilizarse':readable_duration(m['x']['recovery_s'][j]) if m['x']['recovery_s'][j] is not None else 'No se estabilizó'} for j,name in enumerate(LABELS)],hide_index=True)
        usage=m['usage'];st.write(f"Agua repuesta: {usage['inlet_m3']:.4f} m³ · Agua descargada: {usage['outlet_m3']:.4f} m³ · Energía parcial estimada: {usage['partial_energy_kWh']:.4f} kWh")
        st.caption('Se considera estable después de permanecer 30 minutos seguidos dentro del rango deseado. Resultados calculados con los valores del agua simulada.')
    with st.expander('Detalles técnicos de la simulación'):
        st.caption('Identificador: '+rid+' · '+('Lazo cerrado' if run['config']['strategy']=='closed' else 'Lazo abierto'))
        if events: st.dataframe(pd.DataFrame(events),hide_index=True)
        st.json(run['config']);st.json(repo.records(rid,'metrics'))
        if run['termination_state'] is not None: st.json(run['termination_state'])
    st.download_button('Descargar corrida (ZIP: JSON y CSV)',export_bytes(repo,rid),file_name=rid+'.zip',mime='application/zip',key=key+'download')

@st.fragment(run_every=3 if st.session_state.get('demonstration_running',False) else None)
def execution_view():
    rid=st.session_state.get('run_id')
    if not rid:
        st.info('Complete la pestaña Configuración y pulse «Validar y preparar corrida» para empezar.')
        return
    run=repo.get(rid)
    if st.session_state.get('demonstration_running',False):
        if run['status'] in ['PREPARED','RUNNING']:
            try:
                service.advance(rid,uuid.uuid4().hex,run['step'])
            except (ValueError,RuntimeError) as exc:
                st.session_state.demonstration_running=False
                st.error(str(exc))
            run=repo.get(rid)
        if run['status'] not in ['PREPARED','RUNNING']:
            st.session_state.demonstration_running=False
            st.rerun()
    cols=st.columns(6)
    try:
        if cols[0].button('Iniciar demostración',disabled=run['status'] not in ['PREPARED','RUNNING','PAUSED'] or st.session_state.get('demonstration_running',False),help='Avanza un paso simulado cada tres segundos para observar el control del agua.'):
            if run['status']=='PAUSED': service.resume(rid)
            st.session_state.demonstration_running=True
            st.rerun()
        if cols[1].button('Avanzar un intervalo',help='Calcula '+readable_duration(run['config']['time']['control_interval_s'])+' para revisar un paso.',disabled=run['status'] not in ['PREPARED','RUNNING'] or st.session_state.get('demonstration_running',False)):
            service.advance(rid,uuid.uuid4().hex,run['step']);st.rerun()
        if cols[2].button('Pausar',disabled=run['status']!='RUNNING'):
            st.session_state.demonstration_running=False
            service.pause(rid);st.rerun()
        if cols[3].button('Continuar',disabled=run['status']!='PAUSED'):
            service.resume(rid);st.rerun()
        if cols[4].button('Detener',disabled=run['status'] not in ['PREPARED','RUNNING','PAUSED']):
            st.session_state.demonstration_running=False
            service.stop(rid);st.rerun()
        if cols[5].button('Ejecutar hasta terminar',disabled=run['status'] not in ['PREPARED','RUNNING'] or st.session_state.get('demonstration_running',False)):
            with st.spinner('Calculando la simulación…'): service.run_all(rid)
            st.rerun()
    except (ValueError,RuntimeError) as exc: st.error(str(exc))
    with st.popover('Vista del estanque'):
        shape=st.selectbox('Representación',SHAPES,key='presentation_tank_shape')
        view_mode=st.selectbox('Renderizado',['Automático (3D)','2.5D (sin WebGL)'],format_func=lambda mode:'Automático' if mode=='Automático (3D)' else 'Vista simplificada',key='presentation_render_mode')
    show_tank(repo,rid,shape,view_mode=='2.5D (sin WebGL)')
    samples=repo.records(rid,'samples')
    actions=repo.records(rid,'actuator_records')
    if samples:
        plots=figures(run,samples,actions)
        for start in range(0,4,2):
            columns=st.columns(2)
            for column,plot in zip(columns,plots[start:start+2]):
                column.plotly_chart(plot,width="stretch",key='execution_'+plot.layout.title.text)
        for plot in plots[4:]:
            st.plotly_chart(plot,width="stretch",key='execution_'+plot.layout.title.text)


with execution_tab:
    execution_view()
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
            m=data['metrics'];rows.append({'Estrategia':'Abierto' if strategy=='open' else 'Cerrado','Estado':STATUS[data['status']],'Duración (h)':data['time_s']/3600,'J adimensional':m['J'] if m else None,'Causa':data['cause'],'Estado de métricas':data['metrics_status'],'Diagnóstico de métricas':data['metrics_cause']})
        st.dataframe(rows,hide_index=True)
        st.caption('Se muestran métricas del horizonte observado y del tramo común por separado. Una terminación anticipada impide declarar ventaja por observar menos tiempo.')
        comparison_rows=[]
        for strategy,m in comparison['common'].items():
            if m and m['x']:
                for j,(name,unit) in enumerate(zip(LABELS,UNITS)):
                    comparison_rows.append({'Estrategia':'Abierto' if strategy=='open' else 'Cerrado','Variable':name,'Unidad del error integrado':unit+'·s','Error integrado absoluto':m['x']['iae'][j],'Fracción en banda':m['x']['in_band_fraction'][j]})
        st.dataframe(comparison_rows,hide_index=True)
        for diagnostic in comparison['common_metrics_diagnostics'].values():
            if diagnostic['status']=='FAILED': st.error('Métricas comunes no disponibles: '+diagnostic['cause'])
        with st.expander('Base común y métricas completas de comparación'): st.json(comparison)
        st.download_button('Descargar comparación JSON',json.dumps(comparison,ensure_ascii=False,indent=2),file_name='comparison.json')
with history_tab:
    history=repo.list()
    if history:
        st.dataframe(pd.DataFrame(history).assign(status=lambda f:f.status.map(STATUS)).rename(columns={'run_id':'Corrida','status':'Estado','cause':'Causa','time_s':'Tiempo (s)','step':'Paso','created_at':'Fecha UTC'}),hide_index=True)
        selected=st.selectbox('Consultar corrida guardada',[r['run_id'] for r in history])
        show_run(selected,'history')
    else: st.info('Aún no hay corridas guardadas.')
