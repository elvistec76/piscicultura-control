"""Recorrido real de Streamlit mediante AppTest, con base aislada."""
import json
from pathlib import Path
from streamlit.testing.v1 import AppTest


def by_label(items,label): return next(i for i in items if i.label==label)


def test_spanish_configuration_execution_history(tmp_path,monkeypatch):
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
    assert before['config']['profile']['references'][0]==29.
    assert at.session_state['profiles'][0]['references'][0]==28.5
    at.run();at.run();assert service.repo.get(rid)==before
    by_label(at.button,'Avanzar un intervalo').click().run();assert not at.exception
    assert service.repo.get(rid)['time_s']==60
    by_label(at.button,'Pausar').click().run();assert service.repo.get(rid)['status']=='PAUSED'
    by_label(at.button,'Continuar').click().run();assert service.repo.get(rid)['status']=='RUNNING'
    by_label(at.button,'Detener').click().run();assert service.repo.get(rid)['status']=='STOPPED'
    by_label(at.button,'Comparar estrategias con la configuración validada').click().run()
    assert not at.exception and at.session_state['comparison']['common_duration_s']==3600
    assert service.repo.get(rid)['status']=='STOPPED'
    assert len(at.metric)==10  # ejecución e historial muestran cinco lecturas cada uno
    assert any(d.label=='Descargar corrida (ZIP: JSON y CSV)' for d in at.get('download_button'))
    assert any('aproximaciones empíricas' in w.value for w in at.warning)
    Path('evidence/ui_review.json').write_text(json.dumps(dict(method='Streamlit AppTest',tabs=[t.label for t in at.tabs],profiles=4,initial_time_s=0,after_command_time_s=60,status='STOPPED',render_does_not_advance=True,exceptions=0,comparison_common_s=3600,copy_reference_C=29.,original_reference_C=28.5,charts_per_view=6,metrics_per_view=5),ensure_ascii=False,indent=2))
