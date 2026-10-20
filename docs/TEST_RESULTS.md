# Resultados de verificación de la corrección R1

Software 0.1.1 · commit de producción `9568cc8` · contrato SPC-AGUA-001 0.5.0 · modelo M-AGUA-DEMO-1 1.0.0 · revisión académica Work 0.6.0. Consolidación: 15 de octubre de 2026, America/La_Paz. La revisión de integración sigue pendiente; estos resultados no son aprobación académica ni validación productiva.

## Estado de la ejecución recuperada

La ejecución anterior guardó el arreglo en Git y terminó la suite completa antes de interrumpirse la conversación. Se comprobaron el registro, XML, código y artefactos existentes y se completaron únicamente comparación, manifiestos, documentación y entrega. No se atribuye otra ejecución completa a la reanudación.

La suite completa comenzó el 15 de octubre a las 03:15:50 UTC, equivalente al **14 de octubre a las 23:15:50 en America/La_Paz**. Resultado XML: **85 casos, 0 fallos, 0 errores, 0 omitidos**, 354.998 s (registro redondeado: 355.00 s). Las sumas de tiempos individuales de los casos se identifican aparte en verification_summary.json. El paquete Python y las pruebas no cambiaron después del commit ensayado; los dos scripts nuevos consolidan datos y manifiestos.

| Etapa | Código / evidencia | Observado | Interpretación |
|---|---|---|---|
| Entrega inicial | 41ec9f2; evidence/pytest.xml | 58/58 pasados | Histórico 0.1.0, no se sustituye |
| Revisión de Work | evidencia_revision/work_review_pytest.xml | 58/58 pasados | Ejecución de Work, no atribuida a Codex |
| Reproducción previa de nuevos casos | regresiones_antes.xml, 24 casos | 22 fallidos, 2 pasados | Reproduce defectos anteriores; no son fallos de la versión corregida |
| Primer arreglo | regresiones_despues.xml | 24/24 pasados | Mismos casos anteriores tras el arreglo |
| Suite corta ampliada | pruebas_cortas.xml | 44/44 pasados en 11.211 s | 27 casos nuevos más el subconjunto de 17 originales |
| Regresión completa 0.1.1 | pytest.xml | 85/85 pasados | 58 originales y 27 nuevos; incluye AC01–AC20 |

Los 17, 24 y 44 casos son subconjuntos o etapas de verificación, no requisitos adicionales ni pruebas que deban sumarse a 85. Las evidencias de corrección están bajo `evidence/correcciones_pr1/`; las anteriores y las de Work permanecen intactas.

## OBS01–OBS05: esperado y observado

| Observación | Esperado / criterio | Observado | Pruebas y estado técnico |
|---|---|---|---|
| OBS01: bandas y métricas | Rechazar ancho T/C <=0 antes de preparar; no crear corrida. Un fallo derivado debe tener causa y conservar el lote confirmado, sin NaN inventado ni excepción de interfaz sin gestionar. | Errores identifican temperature_C/oxygen_mg_L y profile.operating_bands; cero corridas creadas. Fallos de generación, finitud y persistencia quedan en metrics_status=FAILED; COMPLETED/STOPPED/FAILED físicos y datos confirmados permanecen. | 18 regresiones, AC01/12/17/19, AppTest, comparación, reapertura y compatibilidad de base anterior: pasados. Corrección verificada; revisión Work pendiente. |
| OBS02: turbidez medida | Con U=[5,20], r=10, x=y=2 y [0,1800], fuera=0, fracción=1 y recuperación=0 para x e y; IAE sigue siendo 14400 NTU·s. | Se obtiene exactamente lo esperado. Para U=25, fuera=1800 s, fracción=0, recuperación=null e IAE=27000 NTU·s. Ausencia intermedia: cobertura 2/3, sin integral completa de y. | 4 regresiones, AC19 y comparación/ventana: pasados. Corrección verificada; no se cambió el modelo óptico. |
| OBS03: ventana | dt=135 aceptado; [14400,43200] tiene duración 28800 s; muestra exterior a 14310 aporta 45 s por convención izquierda. | Duración=28800 s, fuera=45 s, fracción=0.9984375. IAE de ese fragmento=26.25 °C·s con interpolación del error absoluto. Coincidencia de extremos conserva el resultado. | 5 regresiones, AC12/19, seis S2 con dt=135 y contraste dt=60: pasados. Corrección verificada. |
| OBS04: documentación Work | Incorporar revisión, README, prompt e informe sin cambiar contrato ejecutable ni contenido académico ajeno. | Archivos recibidos de 6ac325a incorporados exactamente; Word disponible en la raíz. La edición 0.6.0 no se usó como spec_version. Equivalencia de 12 documentos y 4 diagramas confirmada por Work; las antiguas diferencias se explican como históricas. | Manifiesto byte por byte y revisión de diferencias: verificados. No implica aprobación del informe propuesto. |
| OBS05 / RNF10 | S8 en el equipo local con CPU/RAM/SSD y protocolo acreditados, mediana <=60 s. | Solo hay máquina virtual; tiempos descriptivos nuevos y originales conservados. No se acredita SSD local ni contexto del plan. | AC20 funcional pasado; aceptación de rendimiento contextual pendiente/no evaluable. Sin excepción de integración otorgada. |

Las pruebas numéricas usan las tolerancias originales de ACCEPTANCE_PLAN. Los ejemplos sintéticos anteriores son aritmética exacta o comprobaciones con error absoluto <=1e−12; no amplían umbrales de aceptación. Cerca de .95 se verificaron .9515625 y .946875: el primero satisface la permanencia y el segundo no. No se cambió el umbral para aprobar ambos.

El contrato de `metrics_status`, `metrics_cause` y `metrics_stage` se describe en IMPLEMENTATION. El estado del resultado derivado no reemplaza al de integración. Un resultado anterior se conserva para auditoría cuando falla un recálculo; no se presenta como el último cálculo disponible. Si la base tampoco admite guardar el diagnóstico, se comunica ese error sin fingir persistencia.

## Reejecución de aceptación

AC01–AC19 tienen resultado favorable en sus configuraciones de referencia nuevamente ensayadas. AC20 mantiene resultado funcional favorable y rendimiento contextual pendiente. La tabla siguiente destaca el impacto de la revisión; los casos aislados restantes y sus tolerancias se conservan en ACCEPTANCE_PLAN y en el XML nuevo.

| Casos | Esperado | Observado / evidencia nueva |
|---|---|---|
| AC01 | Configuración válida y rechazo previo de inválidos | Tres perfiles válidos; finitud/unidades/malla/referencia O2 comprobadas; T/C degeneradas rechazadas sin run_id |
| AC02–AC08 | Soluciones analíticas y respuesta auxiliar con tolerancias aprobadas | Ocho pruebas core, incluida AC01, pasan; ecuaciones/actuadores sin cambios; tolerancias sin ampliar |
| AC09–AC11 | Histéresis, equilibrio y reproducción | Pasados; S1 ambas estrategias/tres perfiles completan con 2881 muestras y 2880 decisiones |
| AC12 | Recuperación <=14400 s, fracción >=.95 en [4,12] h y Jc/Ja <=.8 | Pasado en las tres especies; tabla cuantitativa inferior. Se añadió ventana exacta para dt=135 sin restringirlo |
| AC13–AC16 | Perturbaciones, fallos previstos, pausa e idempotencia | Pasados; S5/S9 conservan FAILED exigido; la repetición de un comando no añade filas |
| AC17 | Reversión atómica, historial/exportación y huérfanas | Pasado; además se comprueban fallos de métricas tras el lote, datos intactos, diagnóstico persistido y reapertura |
| AC18 | Refinamiento con tolerancias originales | Seis repeticiones S2, tres perfiles/dos estrategias, pasadas |
| AC19 | IAE=2, tiempo fuera=1 s, energía parcial 10 kWh | Pasado; se añadieron IAE de turbidez unilateral y ventanas con extremos dentro de intervalos |
| AC20 | Desacoplamiento, funciones sin red y medición S8 contextual | Funciones pasadas; tres bases nuevas y duraciones registradas; RNF10 pendiente |

## Referencias y comparación con 0.1.0

Se compararon las 57 exportaciones nuevas de referencia, incluidas seis refinadas, con las originales. Diferencia máxima observada de x=(0,0,0,0,0), de J=0 y de IAE de la ventana original=0. Las tolerancias de reproducción de x siguen siendo (1e−5 °C,1e−5 mg/L,1e−6,1e−4 NTU,1e−7 m). No se alteraron estados para obtener esa igualdad; model.py, actuators.py, control.py, sensors.py, scenarios.py, engine.py y MODEL_DEFAULTS.json son idénticos al head revisado.

| Perfil S2 con dt=60 | J abierto | J cerrado | Jc/Ja | Recuperación T,C,p,U,h (s) | Fracción [4,12] h |
|---|---|---|---|---|---|
| Tilapia | 0.8982199533 | 0.1370391219 | 0.1525674435 | (600, 300, 1920, 2760, 300) | (1, 1, 1, 1, 1) |
| Trucha | 1.0274654531 | 0.1489662171 | 0.1449841614 | (1500, 300, 1920, 2760, 300) | (1, 1, 1, 1, 1) |
| Carpa | 0.9013714138 | 0.1380336065 | 0.1531373243 | (0, 240, 1920, 2760, 300) | (1, 1, 1, 1, 1) |

Las seis integraciones adicionales dt=135 completan 12 h con 321 muestras, 320 decisiones y métricas READY. Sus ventanas registran exactamente [14400,43200] y 28800 s. Se distinguen de las series sintéticas de OBS03: estas últimas prueban casos cercanos a los bordes que no son una corrida integrada del estanque.

Se entregan **72 ZIP nuevos**: 57 referencias, 3 repeticiones S8, 6 casos dt=135 y 6 fallos deliberados de métricas. Hay 24 comparaciones nuevas, aparte de las 24 originales. En los seis fallos derivados exportados: las tres finalizaciones COMPLETED conservan 61 muestras y 60 decisiones; las tres STOPPED a 60 s conservan 2 muestras y 1 decisión. Los datos nulos se mantienen como ausencias con calidad.

## Trazabilidad de los 33 RF y 10 RNF

La matriz académica de Work R1 es una revisión del head anterior y no fue reescrita por Codex. Las siguientes filas describen la evidencia posterior y proponen reconsiderar los requisitos parciales. «Favorable» se limita al alcance ensayado; no acredita toda configuración ni aceptación integral.

| ID | Evidencia posterior | Observado / estado técnico |
|---|---|---|
| RF01.1 | Regresión 0.1.1; AC01; UI | Tres especies y fase visibles, guardadas por corrida; favorable en alcance probado. |
| RF01.2 | Regresión 0.1.1; AC01; UI; core_checks | Clases bibliográfica/derivada/demostrativa, unidades y fuentes; rechazo de fuente ausente; favorable en alcance probado. |
| RF01.3 | Regresión 0.1.1; test_profile_copy_immutable_and_versions; UI | Copia editable a 29 °C; original e historia conservan 28.5 °C; favorable en alcance probado. |
| RF02.1 | Regresión 0.1.1; AC01; UI; config.json | Geometría, biomasa, x0, presión, salinidad y tiempo guardados; favorable en alcance probado. |
| RF02.2 | OBS01, AC01, AppTest | T/C con ancho cero rechazadas; referencia/banda/alarma diferenciadas. Corrección verificada, pendiente revisión Work. |
| RF02.3 | OBS01, AC01, prueba sin creación de corrida | Validación antes de prepare, configuración congelada y error de campo. Corrección verificada, pendiente revisión Work. |
| RF03.1 | Regresión 0.1.1; AC02–AC08; AC10–AC15 | Cinco salidas integradas progresivamente; diez estados; favorable en alcance probado. |
| RF03.2 | Regresión 0.1.1; AC16; UI; test_alarm_transitions_acknowledge_and_stop | Iniciar/avanzar/pausar/continuar/detener conservando parcial; favorable en alcance probado. |
| RF03.3 | Regresión 0.1.1; AC16; UI | Tres consultas y renderizados sin avance ni filas extra; favorable en alcance probado. |
| RF04.1 | Regresión 0.1.1; AC14; samples.csv | Sesgo en y; x permanece independiente de inyección directa; favorable en alcance probado. |
| RF04.2 | Regresión 0.1.1; AC14; test_freeze_missing_invalid_noise_bias_and_event_boundaries | Muestreo, ruido, sesgo, pérdida, congelación con y nulo si no hay lectura previa; favorable en alcance probado. |
| RF04.3 | Regresión 0.1.1; AC09; firma de decide | Solo frame y configuración/memoria propias; sin x/calendario; favorable en alcance probado. |
| RF05.1 | Regresión 0.1.1; AC08; actions.csv | Orden limitada y respuesta distinta; medias efectivas separadas; favorable en alcance probado. |
| RF05.2 | Regresión 0.1.1; AC08; AC15 | Capacidades, respuesta de 30 s y disponibilidad cero/reducida; favorable en alcance probado. |
| RF05.3 | Regresión 0.1.1; AC08; AC03 | Estados firmados excluyen oposición; recambio explícito separado; favorable en alcance probado. |
| RF06.1 | Regresión 0.1.1; AC09; AC10; AC14 | Abierto calibrado independiente de lecturas, incluso MISSING; favorable en alcance probado. |
| RF06.2 | Regresión 0.1.1; AC09; AC12 | Cambios de modo por lectura con error y memoria; recuperación registrada; favorable en alcance probado. |
| RF06.3 | Regresión 0.1.1; AC11; decisions.csv; config.json | Estrategia, parámetros, muestra referida y motivos congelados; favorable en alcance probado. |
| RF07.1 | Regresión 0.1.1; AC01; AC13; test_event_combination_and_actuator_availability | Eventos con tiempo, tasa, unidad y objetivo; fuera de malla rechazado; favorable en alcance probado. |
| RF07.2 | Regresión 0.1.1; AC14–AC15; events.csv | Inyección y síntomas separados; sesgo plausible sin detección falsa; favorable en alcance probado. |
| RF07.3 | Regresión 0.1.1; AC14–AC15; test_terminal_invalid_no_decision_and_domain_crossing_receipt | Fallo explícito antes de nueva decisión inválida; dominio parcial conserva estado; favorable en alcance probado. |
| RF08.1 | test_charts_offline y AppTest; capturas Chromium 0.1.0 históricas | Cinco figuras x/y con banda, referencia y unidad; figura de ocho acciones; favorable en alcance probado. |
| RF08.2 | Regresión 0.1.1; test_alarm_transitions_acknowledge_and_stop; events.csv | Activación y cese únicos; origen y severidad; reconocimiento no altera agua; favorable en alcance probado. |
| RF08.3 | Regresión 0.1.1; AC14–AC15; UI | Ausencia nula con calidad; estados terminales y causas visibles; favorable en alcance probado. |
| RF09.1 | Regresión 0.1.1; AC11; AC17; esquemas SQLite | Configuración, series, decisiones, acciones y eventos vinculados por FK; favorable en alcance probado. |
| RF09.2 | Regresión 0.1.1; AC16–AC17 | Reintento idempotente y reversión de lote con error inyectado; favorable en alcance probado. |
| RF09.3 | Regresión 0.1.1; AC17; UI; ZIP de referencia | Consulta tras reapertura; JSON/CSV con unidades, versiones e identificadores; favorable en alcance probado. |
| RF10.1 | Regresión 0.1.1; AC12; comparisons/ | Mismo x0,z0, ruido y calendario; solo estrategia difiere; favorable en alcance probado. |
| RF10.2 | OBS01–03, AC12/19, 27 regresiones nuevas | Finitud, turbidez y ventana corregidas; IAE y consumos conservan fórmulas. Corrección verificada, pendiente revisión Work. |
| RF10.3 | Regresión 0.1.1; test_comparison_common_interval_and_exports; comparisons/S5_* y S9_* | Tramo común separado; fallo y horizonte solicitado informados; favorable en alcance probado. |
| RF11.1 | Regresión 0.1.1; AC01; test_profile_copy_immutable_and_versions; environment.json | Spec/modelo/perfil v1/algoritmo y software 0.1.1/entorno identificados; favorable en alcance probado. |
| RF11.2 | Regresión 0.1.1; AC11; noise.csv; manifest.json | Tabla PCG64 persistida por muestra/variable; no ruido en RK45; favorable en alcance probado. |
| RF11.3 | Regresión 0.1.1; pytest.xml; manifiestos; este informe | Resultados ligados a versión y archivos; RNF10 no se acredita por inferencia; favorable en alcance probado. |

| RNF | Evidencia y estado técnico |
|---|---|
| RNF01 | AC11/16/18 y 57 comparaciones de referencias: favorable con tolerancias originales |
| RNF02 | AC01–08/19 más rechazo de escala cero y comprobación finita: corrección de OBS01 verificada; revisión Work pendiente |
| RNF03 | AC17, FK, reversión de lote y compatibilidad de diagnóstico con bases anteriores: favorable |
| RNF04 | AC20 ejecuta núcleo sin importar Streamlit/Plotly: favorable |
| RNF05 | AC16/17 y reintento de recibos tras fallo derivado sin duplicación: favorable |
| RNF06 | AppTest de configuración, ejecución, detención/comparación con métricas fallidas e historial en español: favorable en recorrido indicado |
| RNF07 | AC17 y 18 regresiones OBS01: fallo derivado con causa, datos conservados y reapertura; corrección verificada, revisión Work pendiente |
| RNF08 | AC20 y pruebas locales con conexiones bloqueadas: favorable en Debian/Python declarados |
| RNF09 | Configuración inmutable, exportaciones y manifiestos históricos/nuevos: favorable |
| RNF10 | Pendiente/no evaluable en hardware virtual; falta equipo local con SSD y protocolo del plan |

## Entorno, tiempos y límites

Versiones efectivas: {"python": "3.12.14", "platform": "Linux-6.18.44-x86_64-with-glibc2.41", "sqlite": "3.53.1", "code": "0.1.1", "packages": {"numpy": "2.3.5", "scipy": "1.17.0", "pandas": "2.2.3", "plotly": "7.1.0", "streamlit": "1.66.0", "pytest": "9.1.1"}}. `pip check` no detectó dependencias rotas; no se modificaron requisitos de instalación. La suite completa usó `work/clean-venv`, creado sin paquetes heredados en la instalación inicial.

S8 nuevo 0.1.1: (8.400498001, 8.502229281, 8.400134212) s; mediana **8.400498001 s**. S8 original 0.1.0: (8.993926115, 8.734400068, 8.981133522) s; mediana 8.981133522 s. Se conservan ambos registros descriptivos. El entorno sigue siendo virtual; estos tiempos no acreditan SSD local ni sustituyen la meta de 60 s en el equipo de referencia. El recálculo de Work no se usa como medición local de Codex.

Las pruebas de Chromium pertenecen a la entrega 0.1.0 y no se presentan como repetidas en esta corrección. La interfaz corregida se verificó con AppTest. No se acreditan Windows, uso físico, dosificación real ni desempeño productivo. pH y turbidez son aproximaciones empíricas; los parámetros compartidos entre especies y las capacidades son demostrativos. Las comparaciones truncadas conservan la aproximación declarada de x y consumos por intervalos completos.

## Comandos y acceso a la evidencia

Desde la raíz del repositorio:

```bash
PISCICULTURA_EVIDENCE_DIR=evidence/correcciones_pr1/regression PISCICULTURA_ACCEPTANCE_DB=work/revision_pr1/acceptance.sqlite work/clean-venv/bin/python -m pytest -q tests --junitxml=evidence/correcciones_pr1/pytest.xml
work/clean-venv/bin/python evidencia_revision/reproducir_observaciones.py --project .
work/clean-venv/bin/python -m scripts.pr1_revision_evidence
work/clean-venv/bin/python -m scripts.reference_comparisons --evidence-dir evidence/correcciones_pr1/regression --db work/revision_pr1/acceptance.sqlite
work/clean-venv/bin/python -m scripts.pr1_review_report
```

La reanudación reutilizó el XML ya finalizado; ejecutó los dos últimos comandos para cerrar las comparaciones/manifiestos y verificó integridad, sin repetir la suite innecesariamente. El script de Work se ejecutó sin modificarlo antes y después; sus salidas se guardaron con nombres distintos. Las regresiones negativas iniciales son históricas y no deben esperarse al ejecutar el código corregido.

[Índice de evidencia nueva](../evidence/correcciones_pr1/README.md). [Resultados íntegros históricos 0.1.0](../evidence/correcciones_pr1/history/TEST_RESULTS_0.1.0.md). Los XML y las 60 exportaciones iniciales permanecen en sus rutas originales. La revisión Work está íntegra en `evidencia_revision/` y los dos documentos de la raíz. No existe sincronización automática entre chats.

Pendientes: nueva revisión académica/técnica de Work y evaluación local válida de RNF10. El PR continúa en borrador. No se concede aprobación global ni excepción de integración con RNF10 abierto.
