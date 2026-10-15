# Devolución de Codex a Work

SPC-AGUA-001 0.5.0 · M-AGUA-DEMO-1 1.0.0 · Software 0.1.0 · 14 de octubre de 2026, America/La_Paz.

## Resultado entregado

Se implementó una aplicación local con Python, NumPy, SciPy, Streamlit, Pandas, Plotly, SQLite y Pytest. Incluye cinco variables del agua, diez estados internos, tres perfiles, sensores virtuales con calidad, ocho acciones efectivas, histéresis, abierto calibrado, perturbaciones, fallos, alarmas, gráficos, historial, exportación y comparación reproducible.

H1–H5 están completados en su trabajo de implementación y evidencia. La suite completa tuvo 58 pruebas parametrizadas pasadas en 381.54 s. AC01–AC19 cumplieron los criterios en las configuraciones evaluadas. AC20 verificó núcleo, persistencia, consulta y exportación sin red; sus tres duraciones fueron 8.993926, 8.734400 y 8.981134 s (mediana 8.981134 s). **La aceptación contextual de RNF10 no es evaluable**: el entorno es una máquina virtual y no se puede acreditar el SSD/equipo local del plan. No se presenta ese dato como aceptación completa de AC20.

Se revisaron los 33 RF y los 10 RNF individualmente en TEST_RESULTS. Los RF y nueve RNF tienen evidencia dentro del alcance probado; RNF10 conserva la limitación anterior. Además, 17 pruebas de núcleo, contratos e interfaz pasaron en un entorno virtual limpio; la interfaz final se comprobó con AppTest y Chromium. La revisión académica posterior de Work sigue pendiente.

En S2, J cerrado/abierto fue 0.152567 (tilapia), 0.144984 (trucha) y 0.153137 (carpa). Las cinco variables cumplieron la recuperación y la permanencia en banda exigidas. Estos resultados corresponden a los escenarios demostrativos, no a desempeño productivo ni superioridad universal. En carpa T ya comienza dentro de su banda operativa, por eso su recuperación térmica es 0 s según la definición aprobada.

S5 cerrado termina FAILED a 7200 s antes de otra decisión; el abierto conserva su programa y completa. S6 tiene aireación efectiva nula durante la avería. S7 mantiene el sesgo plausible sin detección inventada. S9 termina en la raíz del cruce exterior de nivel, conservando tiempo y estado: 9700 s en abierto y 14397.126574685 s en cerrado para los tres perfiles. Las corridas fallidas conservan datos y no se etiquetan como completadas.

## Código y acceso

Repositorio: https://github.com/elvistec76/piscicultura-control

Rama: `codex/implementacion-spc-agua-0.5.0`. No se integró a main, no se desplegó y se mantuvo la visibilidad pública previamente existente. La Pull Request se entrega como borrador para revisión.

Base documental: `f69f4d8`. Commits incrementales: `01f765c` (núcleo), `b200a5c` (servicios/persistencia/aplicación), `155ea6725393816d14eead4b24b343df60bd993d` (núcleo numérico y transaccional de la matriz completa), `6cd7b08c5b82e73826885af6833cfbbb7084fc7b` (presentación final, reproducción y evidencia). Las ecuaciones y el motor numérico no cambiaron después de `155ea67`. Los hashes del código entregado constan en `evidence/source_manifest.json`; la entrega posterior agrega documentos y datos de evidencia. Los XML identifican cada prueba efectiva; las ampliaciones de interfaz y comprobación de volúmenes se volvieron a ejecutar en la suite corta limpia.

Documentos para revisar:

- [IMPLEMENTATION.md](IMPLEMENTATION.md): arquitectura real, instalación, versiones, secuencia, persistencia, límites y comandos.
- [TEST_RESULTS.md](TEST_RESULTS.md): AC01–AC20, esperados/observados/errores/tolerancias, 33 RF y 10 RNF, incidencias y contexto.
- [Índice de evidencias](../evidence/README.md): acceso a datos y reproducción.
- [Índice de corridas](../evidence/run_index.json): 57 exportaciones, incluidas seis de refinamiento.
- [Comparaciones](../evidence/comparisons): 24 grupos de referencias comunes, con terminaciones y limitaciones.
- [Rendimiento](../evidence/benchmark/index.json): tres exportaciones adicionales S8 y sus duraciones reales.
- [Reproducción desde ruido persistido](../evidence/replay_result.json): S2 tilapia cerrado, error máximo de x=(0,0,0,0,0).

Las 60 exportaciones autónomas incluyen configuración, ruido completo, muestras, decisiones, acciones, eventos, métricas, metadatos y manifiesto de unidades. No se requiere que Work vea el disco de Codex: los archivos están en la rama de GitHub y se entrega también un ZIP descargable con código, documentos y evidencias. Work debe abrir esa entrega o revisar la PR expresamente; no se asume sincronización entre chats.

## Preservación y diferencias

No se modificaron archivos propiedad de Work. `evidence/document_manifest.json` compara byte por byte README, docs y diagrams recibidos con f69f4d8. Se añadieron únicamente código, pruebas, dependencias, evidencias y los tres documentos de Codex. No se anidó otro proyecto ni había código ajeno pendiente que sobrescribir.

Se aplicó la arquitectura aprobada con rutas equivalentes descritas en IMPLEMENTATION. Se eligió JSON canónico dentro de contratos congelados y payloads SQLite con claves relacionales, sin cambiar ecuaciones, tecnologías o alcance. La conexión y el servicio se serializan entre reevaluaciones de Streamlit. La configuración inicial y la tabla de ruido quedan guardadas antes de medir; la muestra de extremo se reutiliza. No hay asignación x=r, recorte correctivo del agua ni acceso del controlador al estado exacto/calendario oculto.

Para AC03 se usó el modo de recambio explícito ya aprobado, evitando activar simultáneamente el grupo firmado de llenado y vaciado. Se declararon en core_checks.json todos los términos anulados de los ensayos aislados.

Las métricas de terminación incorporan el estado irregular solo a x. En un tramo común con extremo irregular, x se interpola linealmente en el último segmento y los consumos comunes se restringen a intervalos completos; esa limitación figura expresamente en el resultado. Las métricas completas de cada corrida conservan sus intervalos parciales reales.

## Reproducción mínima

Desde la raíz extraída o clonada, con Python 3.12.14:

```bash
python -m venv work/venv
work/venv/bin/python -m pip install -r requirements-lock.txt
work/venv/bin/python -m pip check
work/venv/bin/python -m streamlit run app.py
```

Abrir `http://127.0.0.1:8501`. La aplicación funciona sin red tras la instalación; guarda en `work/piscicultura.sqlite`. El historial puede consultarse después de reiniciar. La pausa permite continuar dentro de la sesión; los registros históricos no prometen reanudación automática tras cerrar el proceso.

```bash
work/venv/bin/python -m pytest -q tests --junitxml=evidence/pytest.xml
work/venv/bin/python -m scripts.replay_export evidence/runs/S2_p0_closed.zip --db work/replay.sqlite --output work/replay
```

El segundo comando usa la tabla persistida, no solo la semilla. Repite el experimento con nuevos identificadores y compara x con las tolerancias aprobadas. La suite completa genera nuevas corridas de aceptación; conservar la entrega original para contrastarla con una nueva ejecución.

## Puntos para resolución documental y continuidad de Work

1. El ZIP Piscicultura_Documentacion_v0.5.0.zip no fue accesible en esta sesión. La fuente efectiva fue el árbol GitHub f69f4d8 con documentos que declaran 0.5.0/1.0.0. Work debe confirmar que corresponde al paquete entregado; no se certifica una equivalencia binaria no comprobada.
2. REQUIREMENTS conserva una frase sobre RNF01/RNF10 pendientes de aprobación; HANDOFF_WORK y el encargo declaran aprobada la etapa 4. Se mantuvieron criterios originales y se dejó la contradicción para Work. No se reescribieron documentos académicos.
3. PROJECT_SPEC cita PROMPT_INICIO_CODEX.txt, ausente del árbol remoto. No bloqueó la implementación porque el encargo y HANDOFF_WORK aportaron sus instrucciones.
4. RNF10 necesita medición en el equipo local con SSD y contexto del plan. No se requiere cambiar su umbral a partir de los resultados de esta máquina virtual.
5. Work debe contrastar TEST_RESULTS y las exportaciones con el informe, completar conclusiones y capítulo VIII, y resolver docente/paralelo/fecha si corresponde. Codex no editó esas partes.

El simulador queda entregado para revisión técnica y académica. Los resultados de software no constituyen validación de campo: pH y turbidez son aproximaciones empíricas y los parámetros demostrativos no deben convertirse en recomendaciones, capacidades de equipos reales ni dosificación productiva.
