# Correcciones PR 1: evidencia de Codex 0.1.1

Revisión académica Work R1 0.6.0, contrato ejecutable SPC-AGUA-001 0.5.0 y modelo M-AGUA-DEMO-1 1.0.0. Las fuentes están en la raíz del repositorio, no en `docs/revision_pr1/`. El PR sigue en borrador; estos datos permiten solicitar una nueva revisión, sin otorgar aprobación ni integrar a main.

- `observaciones_antes.json`: ejecución del reproductor de Work sobre el head 41ec9f2.
- `regresiones_antes.xml`: primera batería de 24 casos nuevos; 22 fallaron y 2 ya pasaban. Son fallos intencionalmente documentados de la versión anterior.
- `observaciones_despues.json`: mismo reproductor sobre 0.1.1.
- `regresiones_despues.xml`: los primeros 24 casos pasan tras el arreglo.
- `pruebas_cortas.xml`: 44 casos en entorno limpio, incluidos los 27 nuevos y los 17 casos cortos anteriores. Son subconjuntos, no requisitos adicionales.
- `pytest.xml`: regresión completa de la versión corregida, AC01–AC20 y casos nuevos.
- `regression/`: corridas y observaciones de aceptación nuevas. Sus ZIP conservan configuración, ruido, muestras, acciones, eventos, métricas y diagnóstico de disponibilidad.
- `regression/comparisons/`: comparaciones nuevas con tramo común y horizonte observado.
- `failure_exports/`: seis experimentos de fallo inyectado de generación, finitud o escritura de métricas, al completar o detener; los estados físicos y datos confirmados se conservan. No son fallos del agua ni corridas productivas.
- `synthetic_fixtures.json`: entradas y salidas sintéticas de métricas; no se presentan como integración del estanque.
- `dt135/`: seis integraciones S2 reales de 12 h, con intervalo de control 135 s, sin rechazar esa configuración aprobada.
- `verification_summary.json`: conteos, reproducción y comparación de las 57 referencias antiguas/nuevas.
- `preservation_manifest.json`: fuentes de Work incorporadas intactas y evidencia histórica preservada.
- `source_manifest.json`, `archive_manifest.json`, `environment.json`: identificación de código, archivos y versiones reales.
- `history/`: copias exactas de los tres documentos Codex 0.1.0, conservadas para distinguir la entrega inicial de su corrección.

Comandos desde un clon Git con las dependencias instaladas (en esta sesión se usó `work/clean-venv/bin/python`):

```bash
PISCICULTURA_EVIDENCE_DIR=evidence/correcciones_pr1/regression PISCICULTURA_ACCEPTANCE_DB=work/revision_pr1/acceptance.sqlite work/clean-venv/bin/python -m pytest -q tests --junitxml=evidence/correcciones_pr1/pytest.xml
work/clean-venv/bin/python evidencia_revision/reproducir_observaciones.py --project .
work/clean-venv/bin/python -m scripts.pr1_revision_evidence
work/clean-venv/bin/python -m scripts.reference_comparisons --evidence-dir evidence/correcciones_pr1/regression --db work/revision_pr1/acceptance.sqlite
work/clean-venv/bin/python -m scripts.pr1_review_report
```

`pr1_review_report` usa los commits históricos para comprobar integridad; debe ejecutarse en un clon que los contenga. Los scripts de esta revisión no sustituyen los archivos de `evidencia_revision/` ni las referencias iniciales de `evidence/`. RNF10/OBS05 sigue pendiente de equipo local/SSD acreditado; los tiempos virtuales son descriptivos. pH y turbidez son aproximaciones empíricas sin validación de campo ni conversión a dosificación o recomendaciones productivas.
