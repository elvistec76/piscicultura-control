"""Recorrido real de Streamlit mediante AppTest, con base aislada."""
import json
from pathlib import Path
from streamlit.testing.v1 import AppTest


def by_label(items,label): return next(i for i in items if i.label==label)


def test_demonstration_advances_and_pause_preserves_state(tmp_path,monkeypatch):
    monkeypatch.setenv('PISCICULTURA_DB',str(tmp_path/'demonstration.sqlite'))
    at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()
    by_label(at.selectbox,'Escenario').select('S2').run()
    by_label(at.button,'Validar y preparar corrida').click().run()
    service=at.session_state['service'];rid=at.session_state['run_id']
    execution=at.tabs[1]
    assert len(execution.get('bidi_component'))==1
    assert execution.get('bidi_component')[0].key=='live_tank_'+rid
    assert not execution.metric and not execution.dataframe and not execution.json
    by_label(at.button,'Iniciar demostración').click().run()
    assert not at.exception and at.session_state['demonstration_running']
    assert service.repo.get(rid)['time_s']==60
    at.run()
    assert service.repo.get(rid)['time_s']==120
    by_label(at.button,'Pausar').click().run()
    assert not at.exception and not at.session_state['demonstration_running']
    assert service.repo.get(rid)['status']=='PAUSED'
    before=service.repo.get(rid)
    at.run();at.run()
    assert service.repo.get(rid)==before
    assert len(at.tabs[1].get('plotly_chart'))==6
    by_label(at.button,'Iniciar demostración').click().run()
    assert not at.exception and service.repo.get(rid)['time_s']==before['time_s']+60
    by_label(at.button,'Detener').click().run()
    assert not at.exception and not at.session_state['demonstration_running']
    assert service.repo.get(rid)['status']=='STOPPED'


def test_dedicated_parameters_are_saved_without_json_override(tmp_path,monkeypatch):
    monkeypatch.setenv('PISCICULTURA_DB',str(tmp_path/'configuration.sqlite'))
    at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()
    by_label(at.selectbox,'Escenario').select('S0').run()
    by_label(at.number_input,'Horizonte (h)').set_value(1.)
    by_label(at.number_input,'Área (m²)').set_value(12.)
    by_label(at.number_input,'Altura geométrica (m)').set_value(1.8)
    by_label(at.number_input,'Biomasa fija (kg)').set_value(60.)
    by_label(at.number_input,'Presión (Pa)').set_value(100000.)
    by_label(at.number_input,'Salinidad (‰)').set_value(.3)
    by_label(at.button,'Validar y preparar corrida').click().run()
    assert not at.exception and not at.error, [error.value for error in at.error]
    service=at.session_state['service']
    run=service.repo.get(at.session_state['run_id'])
    parameters=run['config']['parameters']
    assert {key:parameters[key] for key in ['area_m2','height_max_m','biomass_kg','pressure_Pa','salinity_per_mille']}=={
        'area_m2':12.,'height_max_m':1.8,'biomass_kg':60.,'pressure_Pa':100000.,'salinity_per_mille':.3}
    by_label(at.button,'Avanzar un intervalo').click().run()
    assert not at.exception and service.repo.get(run['run_id'])['time_s']==60


def test_spanish_configuration_execution_history(tmp_path,monkeypatch,artifact_dir):
    monkeypatch.setenv('PISCICULTURA_DB',str(tmp_path/'ui.sqlite'))
    at=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()
    assert not at.exception
    assert [t.label for t in at.tabs]==['Configuración','Ejecución y evolución','Comparación','Historial y exportación']
    assert len(by_label(at.selectbox,'Perfil de especie').options)==3
    by_label(at.button,'Duplicar perfil para editar').click().run()
    assert not at.exception
    at.run();assert len(by_label(at.selectbox,'Perfil de especie').options)==4
    by_label(at.selectbox,'Perfil de especie').select(3).run()
    by_label(at.selectbox,'Escenario').select('S0').run()
    by_label(at.number_input,'Horizonte (h)').set_value(1.)
    by_label(at.number_input,'Temperatura: referencia (°C)').set_value(29.)
    by_label(at.number_input,'Temperatura: inicial (°C)').set_value(29.)
    by_label(at.button,'Validar y preparar corrida').click().run()
    assert not at.exception
    rid=at.session_state['run_id'];service=at.session_state['service'];before=service.repo.get(rid)
    assert before['time_s']==0 and service.repo.records(rid,'samples')==[]
    assert any('Tiempo simulado:** 0 h de 1 h' in item.value for item in at.markdown)
    assert any('Estado:** Lista para iniciar' in item.value for item in at.markdown)
    assert before['config']['profile']['references'][0]==29.
    assert at.session_state['profiles'][0]['references'][0]==28.5
    at.run();at.run();assert service.repo.get(rid)==before
    by_label(at.button,'Avanzar un intervalo').click().run();assert not at.exception
    assert service.repo.get(rid)['time_s']==60
    assert any('Tiempo simulado:** 0 h 1 min de 1 h' in item.value for item in at.markdown)
    by_label(at.button,'Pausar').click().run();assert service.repo.get(rid)['status']=='PAUSED'
    by_label(at.button,'Continuar').click().run();assert service.repo.get(rid)['status']=='RUNNING'
    by_label(at.button,'Detener').click().run();assert service.repo.get(rid)['status']=='STOPPED'
    by_label(at.button,'Comparar estrategias con la configuración validada').click().run()
    assert not at.exception and at.session_state['comparison']['common_duration_s']==3600
    assert service.repo.get(rid)['status']=='STOPPED'
    assert len(at.metric)==5  # ejecución usa las lecturas del estanque; historial conserva las tarjetas
    assert any(d.label=='Descargar corrida (ZIP: JSON y CSV)' for d in at.get('download_button'))
    assert any('aproximaciones empíricas' in w.value for w in at.warning)
    (artifact_dir/'ui_review.json').write_text(json.dumps(dict(method='Streamlit AppTest',tabs=[t.label for t in at.tabs],profiles=4,initial_time_s=0,after_command_time_s=60,status='STOPPED',render_does_not_advance=True,exceptions=0,comparison_common_s=3600,copy_reference_C=29.,original_reference_C=28.5,charts_per_view=6,metrics_per_view=5),ensure_ascii=False,indent=2))
