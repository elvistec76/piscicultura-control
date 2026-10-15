# Evidencias para Work

Datos producidos por el software 0.1.0 sobre SPC-AGUA-001 0.5.0 / M-AGUA-DEMO-1 1.0.0. Ver `../docs/TEST_RESULTS.md` y `../docs/HANDOFF_CODEX.md` para interpretación, versión e incidencias. Son simulaciones demostrativas, no observaciones de campo.

- `pytest.xml`: resultado individual de la suite completa y parametrizada.
- `clean-environment-tests.xml`: verificación corta en entorno virtual sin paquetes heredados.
- `core_checks.json`: valores esperados, observados, errores y configuraciones declaradas de aislamiento AC02–AC08.
- `observations.json`: datos observados por caso/perfil/estrategia de AC10–AC20.
- `run_index.json`: corridas de referencia, métricas, estado, identificador y nombre del archivo.
- `runs/`: ZIP autónomo por corrida; ver IMPLEMENTATION para esquema y unidades.
- `comparisons/`: 24 comparaciones vinculadas, con base, ruido, tramos, terminaciones y métricas. Los fallos se conservan.
- `document_manifest.json`: hashes de documentos y diagramas académicos preservados.
- `source_manifest.json`: hashes del código y pruebas entregados.
- `hardware.json`, `environment.json`: entorno observado, con limitación del hardware para RNF10.
- `ui_review.json`, `ui/`: recorrido de Streamlit y capturas reales de Chromium con solicitudes externas bloqueadas. Las imágenes no sustituyen las series.

Desde la raíz, después de instalar las dependencias:

```bash
work/venv/bin/python -m scripts.replay_export evidence/runs/S2_p0_closed.zip --db work/replay.sqlite --output work/replay
work/venv/bin/python -m pytest -q tests --junitxml=evidence/pytest.xml
work/venv/bin/python -m scripts.core_evidence
work/venv/bin/python -m scripts.reference_comparisons
```

La reproducción usa `noise.csv` completo, no vuelve a generar ruido a partir de la semilla. La suite genera sus propias bases y las exportaciones. `reference_comparisons` se ejecuta después de la suite y utiliza su base `work/acceptance.sqlite`. Los identificadores nuevos son distintos; los estados y realizaciones se comparan con tolerancias aprobadas. Repetir la suite crea nuevas corridas, sin alterar las anteriores.

Para revisar una corrida sin ejecutar código: extraer su ZIP, abrir `metadata.json`, `config.json`, `manifest.json` y `metrics.json`, y consultar los CSV. `sample_index` y `time_s` vinculan las mediciones; `decision_index` referencia la muestra de entrada; las acciones declaran sus intervalos. Los datos nulos o ausentes llevan calidad. Las terminaciones fuera de malla figuran en metadatos y eventos.
