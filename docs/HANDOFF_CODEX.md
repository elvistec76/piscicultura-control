# Devolución de correcciones de Codex a Work — PR 1

Software 0.1.1 · SPC-AGUA-001 0.5.0 · M-AGUA-DEMO-1 1.0.0 · edición de revisión académica Work 0.6.0. Cierre documental: 15 de octubre de 2026, America/La_Paz.

## Estado entregado

Se atendieron OBS01–OBS03 y se conserva el mismo [PR #1 en borrador](https://github.com/elvistec76/piscicultura-control/pull/1), rama `codex/implementacion-spc-agua-0.5.0`. No se creó otro PR, no se integró a main, no se desplegó ni se cambió la visibilidad pública existente. Se solicita una nueva revisión con las evidencias; no se interpreta el resultado de pruebas como aprobación académica o permiso de integración.

La reanudación comprobó Git y los registros de la ejecución interrumpida. El arreglo estaba comprometido en `9568cc8` y la suite ya había terminado: **85/85 casos pasados, 0 errores/omitidos, 354.998 s**. No se volvió a ejecutar trabajo terminado. Se completaron comparación de datos, manifiestos, los tres documentos técnicos y entrega de la rama. Los 44 casos cortos, incluidos los 27 nuevos, son un subconjunto y no se suman al total de 85.

## Observaciones y resultado

| ID | Corrección o atención realizada | Evidencia | Estado |
|---|---|---|---|
| OBS01 | Rechazo previo de bandas T/C degeneradas; finitud de métricas y diagnóstico separado de integración; conserva datos y recibos, y permite historial/descarga sin excepción de interfaz | 18 regresiones nuevas, AC01/12/17/19, AppTest, reapertura y seis exportaciones de fallo deliberado | Corrección verificada por Codex; pendiente revisión Work |
| OBS02 | Identidad explícita de turbidez para x e y, regla solo superior; conserva IAE respecto a referencia y cobertura sin rellenar ausencias | 4 regresiones, AC19, fixtures de U=2/U=25/ausencia y ventanas/comparación | Corrección verificada por Codex |
| OBS03 | Ventana exacta [14400,43200], 28800 s, ponderación por intersección con estado izquierdo original; IAE por trapecio recortado de error absoluto | 5 regresiones, AC12/19, seis S2 dt=135 y contraste de las 57 referencias | Corrección verificada por Codex; dt=135 sigue admitido |
| OBS04 | Incorporados README, prompt, informe Word, revisión y propuestas de Work desde 6ac325a, sin edición de contenido ajeno | Manifiesto byte por byte; Word y fuentes accesibles en GitHub | Resuelto como incorporación documental; el dictamen académico sigue pendiente |
| OBS05 / RNF10 | Conservados tiempos originales y nuevos, sin declarar acreditación por hardware virtual | AC20 funcional y tres repeticiones S8 nuevas | Pendiente/no evaluable: falta equipo local/SSD y contexto del plan |

Reproducción del caso principal: OBS01 ahora rechaza la banda con variable/campo antes de crear corrida; OBS02 obtiene fuera=0 s y recuperación=0 para x e y; OBS03 obtiene duración=28800 s y fracción=0.9984375. Los valores esperados y observados, tolerancias y comandos están en TEST_RESULTS.

## Contrato y coherencia preservados

La edición académica 0.6.0 no cambió `spec_version=0.5.0`, `model_version=1.0.0`, ecuaciones, parámetros, tolerancias ni el catálogo tecnológico. El paquete se identifica como software 0.1.1. `model.py`, `actuators.py`, `control.py`, `sensors.py`, `scenarios.py`, `engine.py` y MODEL_DEFAULTS.json son idénticos al head 41ec9f2 revisado. Las cinco variables, diez estados, biomasa fija, control por histéresis y abierto calibrado conservan su comportamiento. No se asigna x=r ni se recorta el agua ni se da información oculta al controlador.

OBS01 incorpora `metrics_status`, `metrics_cause` y `metrics_stage`, descritos en IMPLEMENTATION. Son diagnósticos derivados, no nuevos estados de integración. Una corrida puede ser COMPLETED o STOPPED con métricas FAILED; ese diagnóstico conserva su causa y los datos confirmados. READY requiere resultados finitos y guardado correcto. Las bases anteriores se consultan sin inventar causas históricas. Si falla todo el almacenamiento, se comunica la imposibilidad de guardar el diagnóstico; no se afirma persistencia inexistente.

OBS02 conserva la regla unilateral de banda de U y el IAE respecto a rU. OBS03 no cambia el criterio .95, no rechaza dt=135 ni consume nuevas filas de ruido en extremos interpolados. Solo calcula la intersección temporal correcta y declara la regla de IAE. La recuperación usa muestras reales y la permanencia de 1800 s aprobada.

Los 57 archivos de referencia nuevos coinciden con los originales: máximo error x=(0,0,0,0,0), diferencia J=0 e IAE de ventana original=0. Esa igualdad corresponde a las configuraciones comparadas, no a validación de campo ni a todas las configuraciones posibles.

## Código, documentos y datos accesibles

- Producción y pruebas: `9568cc8` (OBS01–03). Incorporación de Work hacia la rama de desarrollo: `f3fadeb`, desde `6ac325a`. Base de revisión: `41ec9f2`.
- [IMPLEMENTATION](IMPLEMENTATION.md): arquitectura, contrato de diagnóstico, ventanas, esquema SQLite y comandos.
- [TEST_RESULTS](TEST_RESULTS.md): antes/después, suite de 85, aceptación afectada y trazabilidad de 33 RF/10 RNF.
- [Evidencia nueva](../evidence/correcciones_pr1/README.md), [resumen verificable](../evidence/correcciones_pr1/verification_summary.json) e [índice de referencias](../evidence/correcciones_pr1/regression/run_index.json).
- [24 comparaciones nuevas](../evidence/correcciones_pr1/regression/comparisons), [S2 dt=135](../evidence/correcciones_pr1/dt135/index.json) y [fallos derivados exportados](../evidence/correcciones_pr1/failure_exports/index.json).
- [Informe Word de Work](../Informe_Piscicultura_Revision_PR1_APA7.docx), [revisión de coherencia](../REVISION_COHERENCIA_PR1.md) y [observaciones](../OBSERVACIONES_CODEX_PR1.md).

Hay 72 ZIP nuevos autónomos: 57 referencias, 3 S8, 6 dt=135 y 6 fallos de métricas. Se preservaron las 60 exportaciones iniciales y toda la evidencia de Work. Los datos sintéticos están rotulados como fixtures de métricas y no como integración física. El manifiesto nuevo identifica código, fuentes recibidas y hashes de exportaciones. Los manifiestos y documentos iniciales son históricos del head 0.1.0; no se reetiquetan como evidencia del código actual. Los tres documentos iniciales se conservan en `evidence/correcciones_pr1/history/`.

Los documentos de revisión se encontraron en la raíz de GitHub, no en la ruta `docs/revision_pr1/` mencionada. Se informó esa diferencia antes de corregir. Work confirmó la equivalencia técnica de los 12 documentos y 4 diagramas con el paquete original; README/prompt/Word recibidos en R1 se incorporaron íntegros. La antigua frase de requisitos pendiente de aprobación fue corregida por Work, sin atribuirla a cambios de ecuaciones por Codex. Las propuestas académicas se mantienen con su estado de revisión; Codex no las convierte en aprobadas.

## Reproducción

Usar Python 3.12.14 y `requirements-lock.txt`, según IMPLEMENTATION. Desde la raíz:

```bash
PISCICULTURA_EVIDENCE_DIR=evidence/correcciones_pr1/regression PISCICULTURA_ACCEPTANCE_DB=work/revision_pr1/acceptance.sqlite work/clean-venv/bin/python -m pytest -q tests --junitxml=evidence/correcciones_pr1/pytest.xml
work/clean-venv/bin/python evidencia_revision/reproducir_observaciones.py --project .
work/clean-venv/bin/python -m scripts.pr1_revision_evidence
work/clean-venv/bin/python -m scripts.reference_comparisons --evidence-dir evidence/correcciones_pr1/regression --db work/revision_pr1/acceptance.sqlite
work/clean-venv/bin/python -m scripts.pr1_review_report
```

La ruta `work/clean-venv` identifica el entorno usado; un entorno nuevo instalado como `work/venv` puede sustituirla. El informe de comparación usa commits históricos y requiere clon Git. La aplicación se ejecuta con `python -m streamlit run app.py`, escucha en loopback y conserva funcionamiento local sin red tras instalar. La pausa solo reanuda dentro de la sesión; no se promete recuperación automática del estado físico al cerrar el proceso.

## Atención pendiente de Work y del estudiante

1. Reconsiderar OBS01–OBS03 con los XML, datos y el contrato de diagnóstico propuesto; actualizar el dictamen académico si corresponde. Las filas parciales de la revisión R1 describen el head anterior y no fueron sobrescritas por Codex.
2. Mantener RNF10 abierto: S8 0.1.1 midió (8.400498001,8.502229281,8.400134212) s, mediana 8.400498001 s; los originales y la mediana 8.981133522 s se conservan. Ninguna medición virtual ni la reejecución de Work acredita el SSD/equipo local. La meta sigue en 60 s.
3. No integrar ni otorgar aceptación integral con RNF10 abierto sin la decisión explícita que exige Work. Esta entrega solicita revisión; no concede esa excepción.
4. Resolver los pendientes administrativos del informe (docente/paralelo y fecha si corresponde), bajo propiedad académica de Work.

pH y turbidez continúan siendo aproximaciones empíricas; no hay química completa, dosificación física, conversión de NTU a sólidos ni validación de campo. Los parámetros demostrativos, límites y capacidades no son recomendaciones productivas. No se redactan conclusiones de ahorro universal ni desempeño de una piscigranja a partir de esta simulación.
