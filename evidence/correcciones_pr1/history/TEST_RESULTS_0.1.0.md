# Resultados de verificación

Responsable Codex. SPC-AGUA-001 0.5.0; M-AGUA-DEMO-1 1.0.0; software 0.1.0. Estos resultados verifican el simulador académico y no acreditan condiciones productivas. pH/turbidez son aproximaciones empíricas y los parámetros son demostrativos.

## Ejecución y criterio de lectura

Suite completa: **58 casos parametrizados, 0 fallos** según `evidence/pytest.xml`. AC01–AC19 se evalúan contra sus umbrales originales. AC20 acredita sus comprobaciones funcionales, pero la aceptación de rendimiento/RNF10 permanece **NO EVALUABLE** por hardware. Un test técnico que termina sin aserciones fallidas no subsana esa limitación.

Entorno: {"python": "3.12.14", "platform": "Linux-6.18.44-x86_64-with-glibc2.41", "sqlite": "3.53.1", "code": "0.1.0", "packages": {"numpy": "2.3.5", "scipy": "1.17.0", "pandas": "2.2.3", "plotly": "7.1.0", "streamlit": "1.66.0", "pytest": "9.1.1"}}

Comando ejecutado desde la raíz:

```bash
work/venv/bin/python -m pytest -q tests --junitxml=evidence/pytest.xml
work/clean-venv/bin/python -m pytest -q tests/test_core.py tests/test_functional.py tests/test_ui.py --junitxml=evidence/clean-environment-tests.xml
work/venv/bin/python -m scripts.core_evidence
```

La suite usa las funciones de producción, bases SQLite nuevas para aislamiento y una tabla de ruido persistida por corrida. La instalación limpia y `pip check` también se comprobaron. Los datos de máquina llevan UTC y corresponden al 14 de octubre de 2026 en America/La_Paz. El commit numérico evaluado y los hashes del código final se identifican en HANDOFF_CODEX y source_manifest. Las mejoras posteriores de presentación se volvieron a verificar mediante AppTest.

Orden de vectores y tolerancias: T (°C), C (mg/L), p (adimensional), U (NTU), h (m). En los casos aislados los términos anulados figuran en core_checks.json; no se cambiaron ecuaciones. AC03 representa entrada y descarga simultáneas mediante recambio explícito .0002 m³/s más entrada .0008 m³/s, respetando los grupos firmados.

## AC01 a AC20

| Caso | Esperado / configuración | Observado | Tolerancia / criterio | Estado |
|---|---|---|---|---|
| AC01 | Tres perfiles; rechazos por finitud, geometría, malla, unidad y O2 inviable | Tres configuraciones aceptadas; casos negativos rechazados. Ver test_AC01 y pruebas de perfiles | Sin tolerancia numérica; excepción explícita | APROBADO |
| AC02 | Csat a 10,20,30 °C; FS=FP=1 | (11.288, 9.0924, 7.5588) mg/L; máximo error 3.101862e-09 | ≤1e−6 mg/L | APROBADO |
| AC03 | Nivel aislado y volúmenes; esperado 1.0414 | 1.0414 m; error 4.662937e-15 | ≤1e−7 m; entradas 0.6 y descarga 0.12 m³ | APROBADO |
| AC04 | Calor aislado; esperado 20.86001 | 20.86001 °C; error 3.793943e-11 | ≤1e−6 °C | APROBADO |
| AC05 | Oxígeno aislado; esperado 4.144208 | 4.144208 mg/L; error 1.776357e-15 | ≤1e−5 mg/L | APROBADO |
| AC06 | pH aislado; esperado 7.975514 | 7.975514 adimensional; error 2.664535e-15 | ≤1e−6 | APROBADO |
| AC07 | Turbidez aislada; esperado 37.22124 | 37.22124 NTU; error 1.421085e-14 | ≤1e−4 NTU | APROBADO |
| AC08 | Respuesta auxiliar a 30 s, cambio firmado e integrales; esperado 0.6321206 | 0.6321206 adimensional; error 6.116696e-09 | ≤1e−7; integral por raíz ≤1e−10 | APROBADO |
| AC09 | Igualdades, memoria y no inversión inmediata; abierto independiente de y | Umbrales de los cinco grupos y frontera de argumentos comprobados por test_AC09 | Reglas exactas de sección 10 | APROBADO |
| AC10 | S0, 6 h, abierto, tres perfiles | Máximo error por perfil: (0, 0, 0, 0, 0); (0, 0, 0, 0, 0); (0, 0, 0, 0, 0) | (1e−5,1e−5,1e−6,1e−4,1e−7) | APROBADO |
| AC11 | S1, 48 h, ambas estrategias, tres perfiles, repetición | Seis pares COMPLETED; 2881 muestras y 2880 decisiones por corrida; error máximo (0, 0, 0, 0, 0) | Tolerancias de reproducción por variable | APROBADO |
| AC12 | S2, 12 h, tres perfiles; recuperar ≤4 h, fracción ≥.95, Jc/Ja ≤.8 | Jc/Ja por perfil: (0.15257, 0.14498, 0.15314); ver tabla S2 | Criterios originales, sin cambios | APROBADO |
| AC13 | S3/S4, ambas estrategias, tres perfiles; cerrado sin cruce de dominio | 12 corridas conservadas; retorno del nivel tras fin de S3 (s): (0, 0, 0) | Retorno <3600 s; alarmas, saturación y uso conservados | APROBADO |
| AC14 | S5 y S7, ambas estrategias, tres perfiles | S5 cerrado FAILED a 7200 s con 120 decisiones; abierto COMPLETED; S7 conserva GOOD y sesgo −.5 mg/L sin diagnóstico inventado | Tiempo exacto; sesgo/ruido error ≤1e−12 | APROBADO |
| AC15 | S6 y S9, ambas estrategias, tres perfiles | S6: aire efectivo cero en [7200,21600); S9: seis FAILED con estado/instante irregular, sin muestra inventada | Cruce h=.25 m, error <1e−9 m | APROBADO |
| AC16 | Pausa/continuación, consultas y recibo repetido | Error frente a S1 sin pausa: (0, 0, 0, 0, 0); 2881 muestras al terminar | Reproducción; ninguna fila duplicada | APROBADO |
| AC17 | Fallo a mitad de lote, FK, historial, exportación y huérfanas | Lote revertido; tiempo confirmado 60.0 s, FAILED; sin recibo fallido; huérfana INTERRUPTED | Integridad exacta y causa explícita | APROBADO |
| AC18 | S2, tres perfiles y dos estrategias, solver refinado | Máxima diferencia por variable: (6.1718e-10, 1.6282e-09, 6.5005e-11, 8.9747e-09, 1.3147e-10) | (0.002,0.002,0.0002,0.02,0.00002) | APROBADO |
| AC19 | Serie sintética, convención izquierda y energía parcial | IAE=(2); fuera=(1) s; energía=10 kWh | IAE=2; fuera=1 s; energía 10±1e−6 kWh | APROBADO |
| AC20 | S8, tres bases nuevas, sin red/presentación; meta mediana ≤60 s | (8.9939, 8.7344, 8.9811) s; mediana 8.981134 s. Núcleo, consulta y exportación con socket bloqueado | Hardware local con SSD no acreditado | PARCIAL: funciones aprobadas; rendimiento NO EVALUABLE para aceptación contextual |

Para reproducir un caso aislado: `work/venv/bin/python -m pytest -q tests/test_core.py::test_AC04` (sustituir el ID). Para los casos parametrizados: `work/venv/bin/python -m pytest -q tests/test_acceptance.py -k AC12`; para toda la matriz usar el comando completo. Las exportaciones originales se conservan en evidence/runs, con sus configuraciones y realizaciones. `observations.json` aporta los detalles por perfil y estrategia; `core_checks.json` registra esperados/observados sin redondeo de los ensayos aislados.

## Recuperación S2 y refinamiento

| Perfil | J abierto | J cerrado | J cerrado/abierto | Recuperaciones T,C,p,U,h (s) | Fracción en banda [4,12] h |
|---|---|---|---|---|---|
| Tilapia | 0.89822 | 0.1370391 | 0.1525674 | (600, 300, 1920, 2760, 300) | (1, 1, 1, 1, 1) |
| Trucha | 1.027465 | 0.1489662 | 0.1449842 | (1500, 300, 1920, 2760, 300) | (1, 1, 1, 1, 1) |
| Carpa | 0.9013714 | 0.1380336 | 0.1531373 | (0, 240, 1920, 2760, 300) | (1, 1, 1, 1, 1) |

AC18 conserva la misma malla de control y ruido al refinar solo RK45. Se registraron las seis diferencias por variable y no se ampliaron tolerancias.

## Fallos previstos y persistencia

S5 cerrado termina a 7200 s con la muestra 120 MISSING, 120 decisiones previas y ninguna decisión a 7200 s. El abierto completa y mantiene la orden. S7 mantiene el sesgo plausible y calidad GOOD; sus eventos de inyección no son diagnósticos del controlador. S6 conserva la respuesta auxiliar aunque gA=0 y recupera disponibilidad exactamente a 21600 s.

| S9 | Estrategia | Tiempo de cruce (s) | Nivel terminal (m) | Estado |
|---|---|---|---|---|
| Tilapia | open | 9700.0000000000 | 0.250000000000 | FAILED |
| Tilapia | closed | 14397.1265746850 | 0.250000000000 | FAILED |
| Trucha | open | 9700.0000000000 | 0.250000000000 | FAILED |
| Trucha | closed | 14397.1265746850 | 0.250000000000 | FAILED |
| Carpa | open | 9700.0000000000 | 0.250000000000 | FAILED |
| Carpa | closed | 14397.1265746850 | 0.250000000000 | FAILED |

El valor del límite en termination_state identifica la raíz del cruce exterior, no un recorte del agua. No se añade una muestra de malla allí. Los intervalos parciales y las decisiones ya aplicadas quedan conservados. AC17 fuerza una excepción de SQLite después de la tercera inserción del lote; se verifica que no sobrevivan filas parciales, avance ni recibo fallido. El último tiempo confirmado y los datos anteriores se mantienen; la causa queda explícita. Una prueba en subproceso termina al propietario y la reapertura marca INTERRUPTED; otro lector con propietario vivo no lo hace.

## Interfaz, entorno local y rendimiento

AppTest recorre las cuatro pestañas, duplica/edita un perfil, valida/prepara, avanza, pausa, continúa, detiene y compara. La configuración histórica permanece congelada. Los renderizados repetidos no avanzan. Chromium 154.0.8037.57 muestra seis gráficos en historial sin errores de página; solo se permiten solicitudes a loopback. Los gráficos también se generan con conexiones de socket bloqueadas. Las capturas se inspeccionaron visualmente. Las claves de JSON/códigos de auditoría conservan nombres técnicos canónicos; los textos de uso, unidades, calidad y estados se presentan en español.

S8: duraciones (8.9939, 8.7344, 8.9811) s, mediana 8.981134 s; meta original 60 s. CPU virtual Intel Xeon Platinum 8573C, 3 vCPU; RAM visible 9.7 GiB; Debian 13.6 x86_64; filesystem overlay y vda ROTA=1, sin modelo físico verificable. **RNF10 no evaluable**: ni el SSD físico ni el contexto del equipo local del plan se pueden acreditar. Se mantiene la medición descriptiva y no se generaliza a otros equipos.

## Revisión de los 33 subrequisitos funcionales

Las evidencias de UI se identifican en ui_review.json, ui-tests.xml y ui/. Las pruebas citadas están en tests/test_functional.py salvo prefijo AC. Cada fila acredita únicamente la comprobación descrita.

| ID | Evidencia | Observado | Estado |
|---|---|---|---|
| RF01.1 | AC01; UI | Tres especies y fase visibles, guardadas por corrida | APROBADO en alcance probado |
| RF01.2 | AC01; UI; core_checks | Clases bibliográfica/derivada/demostrativa, unidades y fuentes; rechazo de fuente ausente | APROBADO en alcance probado |
| RF01.3 | test_profile_copy_immutable_and_versions; UI | Copia editable a 29 °C; original e historia conservan 28.5 °C | APROBADO en alcance probado |
| RF02.1 | AC01; UI; config.json | Geometría, biomasa, x0, presión, salinidad y tiempo guardados | APROBADO en alcance probado |
| RF02.2 | AC01; UI | Campos separados de referencia, banda y alarma; validación de orden | APROBADO en alcance probado |
| RF02.3 | AC01; test_profile_copy_immutable_and_versions | Rechazo previo y serialización congelada; editar borrador no modifica corrida | APROBADO en alcance probado |
| RF03.1 | AC02–AC08; AC10–AC15 | Cinco salidas integradas progresivamente; diez estados | APROBADO en alcance probado |
| RF03.2 | AC16; UI; test_alarm_transitions_acknowledge_and_stop | Iniciar/avanzar/pausar/continuar/detener conservando parcial | APROBADO en alcance probado |
| RF03.3 | AC16; UI | Tres consultas y renderizados sin avance ni filas extra | APROBADO en alcance probado |
| RF04.1 | AC14; samples.csv | Sesgo en y; x permanece independiente de inyección directa | APROBADO en alcance probado |
| RF04.2 | AC14; test_freeze_missing_invalid_noise_bias_and_event_boundaries | Muestreo, ruido, sesgo, pérdida, congelación con y nulo si no hay lectura previa | APROBADO en alcance probado |
| RF04.3 | AC09; firma de decide | Solo frame y configuración/memoria propias; sin x/calendario | APROBADO en alcance probado |
| RF05.1 | AC08; actions.csv | Orden limitada y respuesta distinta; medias efectivas separadas | APROBADO en alcance probado |
| RF05.2 | AC08; AC15 | Capacidades, respuesta de 30 s y disponibilidad cero/reducida | APROBADO en alcance probado |
| RF05.3 | AC08; AC03 | Estados firmados excluyen oposición; recambio explícito separado | APROBADO en alcance probado |
| RF06.1 | AC09; AC10; AC14 | Abierto calibrado independiente de lecturas, incluso MISSING | APROBADO en alcance probado |
| RF06.2 | AC09; AC12 | Cambios de modo por lectura con error y memoria; recuperación registrada | APROBADO en alcance probado |
| RF06.3 | AC11; decisions.csv; config.json | Estrategia, parámetros, muestra referida y motivos congelados | APROBADO en alcance probado |
| RF07.1 | AC01; AC13; test_event_combination_and_actuator_availability | Eventos con tiempo, tasa, unidad y objetivo; fuera de malla rechazado | APROBADO en alcance probado |
| RF07.2 | AC14–AC15; events.csv | Inyección y síntomas separados; sesgo plausible sin detección falsa | APROBADO en alcance probado |
| RF07.3 | AC14–AC15; test_terminal_invalid_no_decision_and_domain_crossing_receipt | Fallo explícito antes de nueva decisión inválida; dominio parcial conserva estado | APROBADO en alcance probado |
| RF08.1 | test_charts_offline; UI; Chromium | Cinco figuras x/y con banda, referencia y unidad; figura de ocho acciones | APROBADO en alcance probado |
| RF08.2 | test_alarm_transitions_acknowledge_and_stop; events.csv | Activación y cese únicos; origen y severidad; reconocimiento no altera agua | APROBADO en alcance probado |
| RF08.3 | AC14–AC15; UI | Ausencia nula con calidad; estados terminales y causas visibles | APROBADO en alcance probado |
| RF09.1 | AC11; AC17; esquemas SQLite | Configuración, series, decisiones, acciones y eventos vinculados por FK | APROBADO en alcance probado |
| RF09.2 | AC16–AC17 | Reintento idempotente y reversión de lote con error inyectado | APROBADO en alcance probado |
| RF09.3 | AC17; UI; ZIP de referencia | Consulta tras reapertura; JSON/CSV con unidades, versiones e identificadores | APROBADO en alcance probado |
| RF10.1 | AC12; comparisons/ | Mismo x0,z0, ruido y calendario; solo estrategia difiere | APROBADO en alcance probado |
| RF10.2 | AC03; AC08; AC19; metrics.json | IAE, bandas, recuperación, J y consumos por unidad; energía parcial de referencia | APROBADO en alcance probado |
| RF10.3 | test_comparison_common_interval_and_exports; comparisons/S5_* y S9_* | Tramo común separado; fallo y horizonte solicitado informados | APROBADO en alcance probado |
| RF11.1 | AC01; test_profile_copy_immutable_and_versions; environment.json | Spec/modelo/perfil v1/algoritmo y software 0.1.0/entorno identificados | APROBADO en alcance probado |
| RF11.2 | AC11; noise.csv; manifest.json | Tabla PCG64 persistida por muestra/variable; no ruido en RK45 | APROBADO en alcance probado |
| RF11.3 | pytest.xml; manifiestos; este informe | Resultados ligados a versión y archivos; RNF10 no se acredita por inferencia | APROBADO en alcance probado |

## Revisión de los 10 RNF

| ID | Evidencia | Estado | Observado / límite |
|---|---|---|---|
| RNF01 | AC11, AC16, AC18; replay_result.json | APROBADO | Repetición y refinamiento con tolerancias originales |
| RNF02 | AC01–AC08, AC19 | APROBADO | Unidades canónicas, finitud y soluciones analíticas |
| RNF03 | AC17 | APROBADO | FK por conexión, unicidad y reversión transaccional |
| RNF04 | AC20 | APROBADO | Proceso nuevo bloquea importaciones Streamlit/Plotly; dominio ejecuta un paso |
| RNF05 | AC16, AC17 | APROBADO | Recibo, run_id y expected_step impiden reintento duplicado |
| RNF06 | UI; Chromium; ui/ | APROBADO en recorrido indicado | Configuración, ejecución, gráficos, alarmas, comparación e historial en español |
| RNF07 | AC14–AC17; test_alarm_transitions_acknowledge_and_stop | APROBADO | Causas, parciales, historial reabierto y proceso huérfano identificado |
| RNF08 | AC20; test_charts_offline; Chromium | APROBADO en Debian/Python declarados | Socket externo bloqueado, gráficos locales, consulta y exportación disponibles |
| RNF09 | AC17; prueba de copia; ZIP | APROBADO | Configuración histórica inmutable y trazabilidad por manifiesto |
| RNF10 | AC20; hardware.json | NO EVALUABLE | Se midieron tres repeticiones, pero no se acredita equipo local/SSD del plan |

## Incidencias reales de desarrollo y asuntos para Work

1. El primer arnés AppTest resolvía app.py respecto de tests/; se corrigió a ruta absoluta. Luego una función de formato consultaba Session State fuera del hilo de renderizado; se cambió a un catálogo capturado localmente. Son fallos de desarrollo corregidos, no resultados numéricos omitidos.
2. AppTest detectó afinidad de hilo de la conexión SQLite al reevaluar Streamlit. Se habilitó cambio de hilo y se serializaron repositorio/servicio con RLock; también se actualizaron botones tras confirmar comandos. La suite corta volvió a pasar y la matriz completa se reinició sobre el núcleo corregido. La ejecución exploratoria interrumpida tuvo 15 pruebas pasadas; no se contó como matriz completa.
3. Una prueba del entorno limpio se lanzó antes de finalizar la instalación y no pudo importar Streamlit. Se repitió después de finalizar, con dependencias comprobadas. Las pruebas finales son las de los XML entregados.
4. No hubo ZIP accesible para cotejar con GitHub. La revisión efectiva proviene de f69f4d8; Work debe confirmar equivalencia del paquete. El archivo PROMPT_INICIO_CODEX.txt citado en PROJECT_SPEC no aparece en ese árbol.
5. REQUIREMENTS conserva una frase de RNF01/RNF10 pendiente de aprobación que contradice el cierre aprobado de HANDOFF_WORK y el encargo. Se documenta para Work y se mantienen los criterios aprobados originales.
6. RNF10 requiere nueva medición en el equipo local/SSD indicado. No hay validación de campo ni certificación productiva. Las conclusiones académicas y capítulo VIII siguen siendo responsabilidad de Work.
