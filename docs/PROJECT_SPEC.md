# Especificación maestra del proyecto

ID: SPC-AGUA-001
Versión: 0.5.0
Fecha local: 2026-10-14
Propietario: Work documentación
Estado: etapas 1 a 4 aprobadas; paquete de etapa 5 preparado para entrega a Codex; sin implementación acreditada.

## 1 Propósito y alcance

Simular un estanque de piscicultura y su sistema de control automático para estudiar retroalimentación, perturbaciones y desempeño. Cinco variables: temperatura °C, oxígeno mg/L, pH adimensional, turbidez NTU y nivel m. Un estanque por corrida; perfiles de Oreochromis niloticus, Oncorhynchus mykiss y Cyprinus carpio en crecimiento o engorde, aprobados por el estudiante. No hay incubación, reproducción, crecimiento individual, sensores físicos ni operación productiva.

La biomasa puede permanecer fija durante la corrida según el supuesto aprobado en etapa 4. Los perfiles guardan fuentes y condiciones; seleccionar una especie no valida automáticamente los coeficientes ni los rangos. RESEARCH_STAGE2 conserva los antecedentes y las discrepancias.

Tecnologías: Python, NumPy, SciPy, Streamlit, Pandas, Plotly, SQLite y Pytest. No cambiar sin aprobación del estudiante. No se fijan aquí versiones no comprobadas de bibliotecas ni compatibilidad con un equipo concreto.

## 2 Convenciones y fronteras

x = estado exacto simulado; y = medición virtual; r = referencia; u_cmd = orden; u_eff = acción efectiva; d = perturbación; theta = parámetros. Tiempo canónico en segundos. Mantener unidades explícitas y convertir solo en límites documentados.

El estado interno puede contener auxiliares químicos o de actuadores, manteniendo las cinco variables de salida del alcance. El controlador no recibe x, theta internos del proceso ni el calendario oculto de fallos. Puede recibir su configuración, r, y y sus propios estados internos. El evaluador sí utiliza x, con origen de indicador explícito.

Distinguir la frontera física representada del estanque y la frontera informática de la aplicación. Los flujos de materia y energía son cantidades del modelo, no transferencias físicas reales.

## 3 Reglas de organización

- Configuración inmutable desde inicio; cambios crean nueva corrida.
- Un comando autorizado produce como máximo un avance confirmado.
- Dibujar, consultar o cambiar pestaña no integra el proceso.
- La pausa conserva estado del proceso, sensores, actuadores, controlador y generadores dentro de la sesión.
- La detención conserva datos parciales; una corrida fallida o interrumpida no se etiqueta como completada.
- No asignar x = r como sustituto de integración; no ocultar saturación mediante recortes que aparenten éxito.
- No usar mediciones inválidas para calcular una orden cerrada.
- No atribuir detección automática a un sesgo o fallo plausible sin un detector definido.
- No modificar una estrategia durante la corrida.

## 4 Arquitectura de software

| Capa | Módulos propuestos | Responsabilidad |
|---|---|---|
| Presentación | ui, charts | Formularios, panel de ejecución, historial y gráficos |
| Aplicación | simulation_service, comparison_service, export_service | Casos de uso, comandos y coordinación |
| Dominio | configuration, profiles, water_model, sensors, controllers, actuators, scenarios, alarms, metrics | Reglas y dinámica independientes de la interfaz |
| Infraestructura | repository, sqlite_store, serialization | Persistencia, transacciones y formatos de intercambio |
| Verificación posterior | tests | Casos de dominio, integración, persistencia y comparación a cargo de Codex |

Los nombres son un mapa de responsabilidades para revisión; Codex podrá proponer rutas equivalentes mediante HANDOFF_CODEX. No son archivos ya implementados. El dominio no importa Streamlit, Plotly ni repositorios concretos. Los servicios reciben contratos de repositorio y de modelo.

### Módulos del dominio

| Módulo | Recibe | Entrega | Conceptos de la materia |
|---|---|---|---|
| configuration y profiles | Borrador de configuración y catálogo | Configuración válida y congelada | Objetivo, atributos y parámetros |
| water_model | Tiempo, x, u_eff, d y theta | Tasas de cambio y variables de salida | Sistema controlado, entradas y salidas |
| sensors | Tiempo, estado observable y configuración del sensor | y y calidad | Sensor y variable de medida |
| controllers | Tiempo, r, y y estado propio | u_cmd, errores y motivos | Comparador, decisor y estrategias |
| actuators | u_cmd, estado propio y disponibilidad | u_eff y restricciones aplicadas | Variable manipulada y actuador |
| scenarios | Tiempo, semilla y realización exógena | d y efectos de fallos dirigidos | Ambiente y perturbaciones |
| alarms | Mediciones, calidad, acciones y reglas | Activación y cese de condiciones | Salidas de información |
| metrics | Series, base de comparación y fórmulas | Indicadores con unidad y origen | Evaluación del objetivo |

El orquestador no contendrá las ecuaciones ni las reglas particulares de los controladores. Coordinará reloj, muestreo, decisiones e integración. Las ecuaciones y la secuencia aprobadas se encuentran en MATHEMATICAL_MODEL.

## 5 Catálogo funcional de actuadores propuesto

| Variable principal | Acción propuesta | Otros efectos que deben evaluarse |
|---|---|---|
| Temperatura | Calentamiento y enfriamiento virtuales | Energía y dependencia del volumen |
| Oxígeno | Aireación regulable | Transferencia limitada por condiciones del agua |
| pH | Acciones de incremento y disminución | Química o aproximación empírica declarada |
| Turbidez | Filtración recirculante | Retiro de material; sin descarga de volumen por defecto |
| Nivel | Caudal de entrada y caudal de salida | Temperatura y composición del agua intercambiada |

Son categorías de diseño; sus capacidades virtuales aprobadas constan en MODEL_DEFAULTS.json y no son fichas de equipos físicos. Las acciones opuestas no operarán simultáneamente, salvo un modo de recambio de agua explícito que coordine entrada y salida. Filtración recirculante y recambio no son el mismo proceso. No se presume independencia de las cinco variables.

## 6 Contratos de datos propuestos

| Contrato | Campos mínimos e invariantes |
|---|---|
| RunConfig | schema_version, spec_version, model_version, profile_snapshot, phase, geometry, biomass, x0, references, bands, alarm_limits, sensor_config, actuator_config, controller_config, horizon_s, control_interval_s, pressure, salinity, scenario, random_manifest y solver_config |
| ProcessState | time_s y estado interno; permite obtener las cinco variables con unidades canónicas; auxiliares separados |
| MeasurementFrame | sample_index, time_s y lecturas por variable con value, unit, quality y diagnóstico observable; sin valor numérico inventado ante ausencia |
| ControlDecision | decision_index, time_s, strategy, input_sample_index, reference_snapshot, error_or_band_distance, commands y reason_codes |
| ActuatorTrace | actuator_id, intervalo temporal, u_cmd, u_eff representado, límites, disponibilidad y motivo de limitación; la resolución se fija en MATHEMATICAL_MODEL |
| ScenarioRealization | realization_id, ejes temporales, series o función determinista por tiempo, eventos, unidades, semillas independientes y versión del generador |
| SimulationEvent | event_seq, time_s, category, target, severity, activation_or_clear, code y datos; separar inyección oculta de detección observable |
| StepResult | Estado final, avance temporal realizado, muestras, decisiones, acciones, eventos y estado de corrida; correspondencia temporal verificable |
| RunResult | run_id, configuración congelada, versiones, estado final, causa de terminación, último tiempo confirmado y series disponibles |
| MetricResult | run_id, variable, origen x o y, métrica, valor, unidad, intervalo evaluado, fórmula/version y condición de validez |
| ComparisonResult | comparison_id, corridas, base común, diferencias autorizadas, intervalos evaluados y limitaciones |

Los nombres de campo son conceptuales; las clases y tipos finales se acordarán con Codex. Se exige definir la representación de valores ausentes y no finitos antes de exportar. Un pH no llevará unidad mg/L. La ausencia de lectura se representará con valor nulo y calidad, no con cero.

### Servicios y operaciones conceptuales

| Operación | Entrada | Salida y regla |
|---|---|---|
| validate_config | Borrador | Configuración validada o errores por campo; sin iniciar integración |
| prepare_run | Configuración validada | run_id y copia congelada con estado PREPARED |
| advance_run | run_id, command_id y expected_step | Un StepResult confirmado o conflicto explícito; reintento no duplica |
| pause_run / continue_run | Corrida activa de la sesión | Estado preservado o retomado sin reiniciar |
| stop_run | Corrida y causa | Resultado parcial con estado STOPPED |
| get_run / list_runs | Identificador o filtros | Lectura del historial sin avanzar simulación |
| compare_strategies | Base validada y realización fija | Dos corridas vinculadas e indicadores comparables |
| export_run | Corrida guardada | Configuración JSON, series CSV y metadatos |

## 7 Ciclo de una corrida

1. Editar perfil y escenario en borrador.
2. Validar campos, procedencia, dominios y coherencia.
3. Congelar configuración y preparar realización exógena.
4. Inicializar proceso, sensores, actuadores, controlador y reloj.
5. Atender un comando de avance con identificador único.
6. Obtener lecturas, decidir según estrategia e integrar la respuesta.
7. Evaluar condiciones y guardar el lote de registros de forma atómica.
8. Publicar el resultado confirmado y permitir el siguiente comando.
9. Completar, pausar, detener o fallar según la condición correspondiente.

La secuencia anterior es funcional. La sección 13 de MATHEMATICAL_MODEL fija el orden exacto de eventos, el muestreo terminal y la integración. Esta versión incluye diez estados internos y cinco salidas; las acciones dobles usan estados firmados para evitar oposición simultánea. No se reconstruirá el estado del controlador a partir de los gráficos.

Un error de persistencia impedirá confirmar el avance: se preservará el último paso confirmado y se marcará el fallo. No se continuará desde un estado parcial no guardado. Una repetición no ejecutará otra vez un comando ya confirmado.

## 8 Estados de ejecución

PREPARED -> RUNNING.
RUNNING -> PAUSED, COMPLETED, STOPPED o FAILED.
PAUSED -> RUNNING o STOPPED.
La pérdida del proceso o del propietario activo permite clasificar RUNNING o PAUSED como INTERRUPTED cuando se compruebe que no existe una ejecución viva correspondiente.
COMPLETED, STOPPED, FAILED e INTERRUPTED son terminales para esa corrida.

No marcar corridas ajenas como interrumpidas solo por abrir otra pestaña. La primera versión admite una corrida activa por sesión y ejecución local, sin prometer colaboración simultánea. Reabrir historial es obligatorio; recuperar automáticamente una corrida tras cerrar el proceso queda fuera del alcance inicial.

## 9 Fallos y alarmas

- Lectura ausente o inválida: quality debe expresarlo. En cerrado, si es necesaria para decidir, registrar causa y terminar el experimento antes de calcular una nueva orden. En abierto, una lectura meramente observacional inválida se registra y no modifica u.
- Sesgo o congelación plausible: solo detectar mediante una regla prevista o diagnóstico observable. El calendario de inyección no es un diagnóstico permitido.
- Actuador averiado: modificar su acción efectiva y registrar disponibilidad; el controlador solo recibe diagnóstico si ese canal se define expresamente.
- Estado numérico no finito o salida del dominio matemático admitido: finalizar el experimento como FAILED, sin alterar x para aparentar corrección.
- Las alarmas operativas utilizan lecturas y diagnósticos permitidos; las evaluaciones basadas en x se etiquetan como auditoría y no generan acciones escondidas.
- Reconocer una alarma en la interfaz no la resuelve ni altera el agua. La activación y el cese se registran una vez por transición.

Las reglas propuestas no representan garantías para hardware real. La acción ante fallos y límites de dominio está fijada en MATHEMATICAL_MODEL y ACCEPTANCE_PLAN. No se añade control manual del estado del agua.

## 10 Comparación reproducible

Las dos corridas comparten geometría, carga, x0, modelo, horizonte, muestreo, condiciones, perturbaciones y realización del ruido. Las diferencias autorizadas son la estrategia y sus parámetros de control, identificados.

El ruido se vinculará a variable e índice de muestra o se precomputará; las entradas externas se definirán por tiempo simulado y se conservarán con su versión. Los pasos adaptativos del integrador no consumirán secuencias de ruido que cambien entre estrategias. La semilla sola no demuestra equivalencia.

En abierto, u depende del programa y del tiempo o eventos predefinidos, sin y. En cerrado depende de r, y y estado propio. Las métricas se calcularán por variable con unidad, fórmula y origen. Si hay terminación anticipada, separar tramo común y horizonte completo; no atribuir ventaja a una corrida por ocultar su tramo fallido.

## 11 Persistencia conceptual en SQLite

| Entidad | Identidad y contenido |
|---|---|
| runs | run_id; configuración congelada y versiones; estado, causa, inicio real, tiempo simulado confirmado y propietario de ejecución |
| samples | run_id + sample_index; time_s, cinco salidas exactas, cinco lecturas y calidades |
| decisions | run_id + decision_index; instante, muestra referida, errores, órdenes y motivos |
| actuator_records | run_id + actuator_id + record_index; instante o intervalo y acción efectiva |
| events | run_id + event_seq; instante, tipo, objetivo, severidad, código y datos |
| metrics | run_id + metric_key; variable, origen, fórmula, valor, unidad e intervalo |
| comparisons | comparison_id; base común y realización utilizada |
| comparison_members | comparison_id + strategy; run_id y diferencias autorizadas |
| command_receipts | run_id + command_id; paso esperado, resultado confirmado y estado de confirmación |

Toda entidad dependiente debe vincularse con una corrida válida. Las restricciones de unicidad impedirán duplicados. Las claves foráneas se activarán en cada conexión. No se borrarán resultados históricos al editar perfiles.

Una transacción confirmará cada lote aceptado con su recibo de comando. La configuración contendrá el programa de eventos y la realización exógena o los datos suficientes para reproducirla exactamente en el entorno fijado. Un registro histórico de muestras no se presenta como un checkpoint completo de reanudación tras cierre.

Los esquemas SQL y la normalización definitiva corresponden al diseño técnico posterior de Codex, conservando estos invariantes.

## 12 Interfaz propuesta

- Configuración: perfil, origen de valores, estanque, escenario y validación.
- Ejecución: tiempo simulado, cinco lecturas, calidad, estado y comandos de avance.
- Evolución: gráficos de variables, bandas y acciones; distinguir estado exacto y lectura.
- Alarmas e historial de eventos: activación, cese, detección e inyección identificables.
- Comparación: base común, estrategias, métricas y terminaciones.
- Historial y exportación: selección de corrida, configuración y archivos.

Los textos de uso estarán en español. La interfaz presentará datos confirmados y no avanzará por renderizado. Los detalles de módulos internos solo aparecerán cuando sirvan para explicar una decisión o evidencia.

## 13 Trazabilidad y pruebas

REQUIREMENTS contiene 33 subrequisitos funcionales y 10 no funcionales. ANALYSIS_STAGE1 conserva la matriz de 25 conceptos. Los objetivos específicos del informe mantienen su numeración. Codex deberá referir estas identidades en sus pruebas y evidencias.

Los pendientes cuantitativos de etapa 3 se concretan en MATHEMATICAL_MODEL, MODEL_DEFAULTS.json y ACCEPTANCE_PLAN, versión 0.5.0. La etapa 4 fue aprobada por el estudiante; la ejecución de pruebas permanece pendiente. No quedan ganancias PID por definir: la estrategia seleccionada es histéresis muestreada. Las pruebas siguen pendientes de ejecución por Codex.

## 14 Responsabilidades y avance

Work mantiene PROJECT_SPEC, REQUIREMENTS, SOURCE_MAP, MATHEMATICAL_MODEL, REPORT_APA, HANDOFF_WORK y CHANGELOG_DOCS, además de anexos de diseño identificados como propios. Codex mantiene código, pruebas, IMPLEMENTATION, TEST_RESULTS y HANDOFF_CODEX. No se modifican esos archivos de Codex ni se afirma haber recibido evidencia.

Etapa 1 aprobada el 14 de octubre de 2026 mediante «si aprobamos».
Etapa 2 aprobada el 14 de octubre de 2026 mediante «si», en respuesta a la revisión del capítulo III, especies concretas y crecimiento o engorde.
Etapa 3 aprobada el 14 de octubre de 2026 mediante «apruebo».
Etapa 4 aprobada el 14 de octubre de 2026 mediante «aprobado»: M-AGUA-DEMO-1, configuración numérica y 20 casos de aceptación.
Etapa 5 preparada: paquete de especificación aprobada y guía de inicio; recepción y ejecución por Codex todavía no acreditadas.
Etapa 6 pendiente: revisión de evidencias y resultados.

El estudiante dispone de un repositorio según el contexto compartido; todavía no se ha facilitado aquí su URL ni se han sincronizado estos archivos. Se conservará la visibilidad que el estudiante haya elegido. No hay sincronización automática entre Work y Codex.

## 15 Cierre matemático aprobado en etapa 4

Modelo M-AGUA-DEMO-1. Diez estados: cinco propiedades del agua y cinco respuestas auxiliares. Histéresis cerrada y lazo abierto constante calibrado. Los contratos de z y v son vectores de cinco componentes; las acciones efectivas se descomponen en ocho capacidades. Las corridas completas de 48 h a 60 s tienen 2881 muestras y 2880 decisiones. Guardar z inicial/final, comandos, disponibilidades y medias efectivas por intervalo.

La física se simplifica; pH y turbidez son aproximaciones empíricas declaradas. Los coeficientes biológicos comunes y umbrales son demostrativos. Solo la ecuación de saturación se transcribe como formulación bibliográfica específica. Las referencias térmicas se seleccionan dentro de antecedentes registrados; no se atribuyen como óptimos universales.

ACCEPTANCE_PLAN contiene AC01 a AC20; RNF01, RNF02, RNF10 y criterios numéricos se cierran mediante ese plan. Toda la evidencia observada permanece pendiente. La etapa 5 reúne el paquete de traspaso, el diseño de implementación del capítulo VI y el plan de pruebas del capítulo VII. Los capítulos VI y VII describen el diseño y la evaluación prevista; no acreditan código existente. La programación corresponde a Codex tras recibir el paquete.

Ante discrepancias prevalece MATHEMATICAL_MODEL 0.5.0 para ecuaciones y secuencia, MODEL_DEFAULTS.json para valores completos y ACCEPTANCE_PLAN para comprobaciones. Cualquier contradicción debe resolverse documentalmente antes de implementar; no autoriza escoger silenciosamente una variante.

## 16 Entrega para implementación

HANDOFF_WORK contiene el orden de lectura, hitos de desarrollo y devolución de evidencias. PROMPT_INICIO_CODEX.txt permite iniciar el trabajo en el otro entorno. El modelo se etiqueta 1.0.0 al aprobarse; las ecuaciones, capacidades, perfiles y tolerancias de 0.4.0 no cambian. La versión documental 0.5.0 incorpora aprobación y diseño de entrega. Codex comprobará las dependencias disponibles y documentará sus versiones efectivas; no se presenta un archivo de dependencias no probado como entorno reproducido.
