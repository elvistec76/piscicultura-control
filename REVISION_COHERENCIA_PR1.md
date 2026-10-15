# Revisión de coherencia del PR 1

**Dictamen: solicitar cambios. No recomendar integración de la versión revisada.**

Fecha local: 14 de octubre de 2026, America/La_Paz. Revisión Work R1; edición académica 0.6.0 para revisión. Especificación evaluada SPC-AGUA-001 0.5.0, modelo M-AGUA-DEMO-1 1.0.0 y software 0.1.0. Head verificado: 41ec9f2d21edb21499c14437b3d00dd9e135e0d2.

[PR 1](https://github.com/elvistec76/piscicultura-control/pull/1) abierto, borrador, no integrado en la consulta realizada. El ZIP adjunto coincide con ese head. La condición mergeable de GitHub solo indica posibilidad técnica de integración, no aceptación de requisitos. No se publicó revisión, se modificó el PR ni se ejecutó merge.

## Alcance y método

Se inspeccionaron los tres documentos de Codex, los 14 archivos del paquete Python, app.py, las pruebas, los datos de referencia y la documentación académica. Se conservaron las evidencias originales; las nuevas ejecuciones ocurrieron en una copia aislada. El análisis combina inspección estática, contraste de manifiestos, reejecución de la suite, AppTest y recálculo independiente desde CSV. Los resultados no se generalizan fuera de las configuraciones verificadas.

## Evidencia comprobada

- XML original: 58 casos, 0 fallos, 0 errores, 0 omitidos, 381.534 s. XML de entorno limpio: 17 casos, 0 fallos, 0 errores, 5.615 s. Los 17 son un subconjunto reejecutado y no 17 requisitos adicionales. El XML de interfaz aporta una ejecución de un caso.
- Manifiestos: 29 archivos de código y soporte, 60 exportaciones y 17 archivos documentales de la base remota cotejados sin discrepancias respecto de sus hashes declarados. Esto acredita integridad respecto de esos manifiestos, no validación de campo.
- Cotejo con el ZIP 0.5.0 creado por Work: 12 documentos en docs y 4 diagramas idénticos. README distinto; prompt y Word ausentes del árbol remoto. Se resuelve la equivalencia técnica de especificación/modelo/requisitos; no se afirma equivalencia completa de todo el paquete.
- S1: las seis corridas exportadas completan y contienen 2881 muestras y 2880 decisiones.
- S2: J, IAE, recuperación y fracción de banda se recalcularon desde los CSV sin llamar al módulo de métricas de producción. J coincide con el almacenado. Las condiciones iniciales y la tabla de ruido se comparten entre estrategias.

Reejecución Work: **58 casos, 0 fallos, 0 errores**, 238.568 s. Comando: `python -m pytest -q tests --junitxml=evidence/work_review_pytest.xml`. Se ejecutó sobre código sin modificar, en copia separada.

Las versiones principales coinciden con la entrega: Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, Pandas 2.2.3, Plotly 7.1.0, Streamlit 1.66.0 y Pytest 9.1.1. La revisión usó un entorno virtual con paquetes base heredados; no afirma otra instalación limpia. El SQLite y la plataforma de revisión se registran en las evidencias. Los 17 casos de entorno limpio y Chromium corresponden a Codex; Work reejecutó AppTest dentro de la suite, sin repetir la inspección Chromium.

## Coherencia de modelos y control

| Aspecto | Conclusión y límite |
|---|---|
| Variables y estado | Cinco salidas T,C,p,U,h; diez estados ordenados según el contrato. Biomasa fija y mezcla perfecta. |
| Temperatura y nivel | Se preservan balances, volumen A·h, unidades y términos de caudal. AC03 usa recambio explícito, compatible con evitar acciones firmadas opuestas. |
| Oxígeno | Saturación USGS, demanda con temperatura/biomasa/alimentación y términos de mezcla/evaporación corresponden a la especificación. No hay calibración biológica por especie ni validación de campo. |
| pH | Relajación directa, acción firmada, alimentación y tasa externa empíricas; sin balance de H+, alcalinidad, mezclas químicas ni dosis físicas. AC06 verifica la ODE simplificada. |
| Turbidez | Índice empírico con aporte y remoción; mezcla lineal de NTU es un supuesto virtual. Sin conversión a sólidos, Secchi, resuspensión o concentración por evaporación. AC07 verifica la ODE; OBS02 corrige una métrica, no la ecuación. |
| Actuadores | Cinco respuestas auxiliares y ocho acciones, con capacidades y disponibilidad; integrales separadas en cruces de cero. No se observó asignación x=r ni recorte correctivo del agua. |
| Control | Histéresis con igualdades/memoria aprobadas; abierto constante calibrado. Interfaz del controlador sin x ni calendario oculto. |
| Ruido y tiempo | PCG64, tabla persistida y reutilización por índice; ruido fuera de RK45, eventos [inicio,fin), muestra terminal reutilizada. |
| Persistencia | Lotes transaccionales, FK y recibos; AC16/AC17 verifican reintento y reversión. Fallo de métricas derivadas requiere OBS01. |
| Comparaciones truncadas | Se distinguen tramo común y horizonte observado. La interpolación x y los consumos comunes solo por intervalos completos se declaran como aproximaciones; no usar para afirmar ventaja de una corrida fallida. |

Los coeficientes empíricos no deben cambiarse a un modelo químico/óptico más complejo para responder a esta revisión. Hacerlo sería otro alcance y requeriría especificación y validación nuevas.

## Resultados respaldados

| Perfil S2 | J abierto | J cerrado | Jc/Ja | Recuperación T,C,p,U,h (s) | Banda [4,12] h |
|---|---|---|---|---|---|
| Tilapia | 0.8982199533 | 0.1370391219 | 0.1525674435 | 600,300,1920,2760,300 | 100 % cada variable |
| Trucha | 1.0274654531 | 0.1489662171 | 0.1449841614 | 1500,300,1920,2760,300 | 100 % cada variable |
| Carpa | 0.9013714138 | 0.1380336065 | 0.1531373243 | 0,240,1920,2760,300 | 100 % cada variable |

Carpa inicia T=23 °C, dentro de la banda en el límite inferior; recuperación 0 no significa salto artificial. Las razones son para S2 y dt=60 s, no superioridad universal. S4 muestra que el cerrado puede emplear más energía parcial que el abierto; no concluir ahorro general a partir de J.

S5 cerrado falla a 7200 s por la política prevista y no decide en ese instante; el abierto completa. S6 anula acción de aireación durante la avería y S7 no inventa detección del sesgo. S9 termina por dominio en aproximadamente 9700 s abierto y 14397.126575 s cerrado. Estos FAILED son resultados esperados de los escenarios, no evidencia de que el test de detección falle.

AC01–AC19 tienen evidencia favorable en las configuraciones originales y reejecutadas. AC20 verifica funciones sin red y desacoplamiento de presentación; no acredita la condición local de RNF10. Mediana S8 original: 8.981134 s, con tiempos 8.993926, 8.734400, 8.981134 s. Hardware virtual/SSD no acreditado: conservar pendiente, sin alterar el umbral de 60 s.

## Defectos adicionales reproducidos

| ID | Prioridad | Hallazgo y efecto | Corrección exigida |
|---|---|---|---|
| OBS01 | Alta | Banda T [28.5,28.5] aceptada; S0 termina a 3600 s como COMPLETED sin métricas por J no finito y ValueError. También falla al detener a 60 s. | Rechazar anchos T/C nulos y comunicar fallos de métricas conservando datos. |
| OBS02 | Media | U=[5,20], x=y=2, tiempos [0,1800]: x fuera=0 y recuperación=0; y fuera=1800 y recuperación=null. | Mantener identidad de variable y regla unilateral en métricas individuales de y. |
| OBS03 | Media | dt=135 admitido: ventana [4,12] h se recorta a [14445,43200], duración 28755. Serie sintética informa 1 en lugar de .9984375 por convención izquierda. | Ponderar intersecciones con extremos exactos, denominador 28800 y pruebas de ventana. |

Los tres casos están fuera de la cobertura original. No contradicen el hecho de que sus 58 pruebas pasan; muestran que esa suite aún no basta para todas las configuraciones aceptadas. OBS02/03 no alteran las cifras S2 originales con bandas default y dt=60. OBS01–03 se detallan con ubicaciones y evidencias exigidas en OBSERVACIONES_CODEX_PR1.md.

## Matriz de los 33 subrequisitos

«Favorable» significa respaldado en el alcance probado e inspeccionado, sin afirmar verificación exhaustiva. «Parcial» requiere corrección antes de cierre. La matriz revisa los estados de Codex y no copia su aprobación global.

| ID | Obligación resumida | Estado Work | Evidencia o corrección |
|---|---|---|---|
| RF01.1 | Ofrecer perfiles de O. niloticus, O. mykiss y C. carpio en crecimiento o engorde | Favorable | AC01; catálogo y recorrido AppTest. |
| RF01.2 | Etiquetar cada valor como bibliográfico, derivado o demostrativo, con unidad y procedencia | Favorable | Registro de procedencia, unidades, AC01 y fuentes. Mantener etiquetas demostrativas al editar. |
| RF01.3 | Permitir duplicar un perfil para editarlo sin cambiar las corridas históricas | Favorable | Copia/serialización congelada; prueba funcional y AppTest. |
| RF02.1 | Configurar geometría, estado inicial, biomasa, presión, salinidad y tiempo de simulación | Favorable | Contratos y formulario; AppTest adicional conserva área20, biomasa70, P95000 y S0.1. |
| RF02.2 | Distinguir referencias, bandas operativas y umbrales de alarma | Parcial | OBS01: se admiten bandas degeneradas que anulan J. |
| RF02.3 | Validar tipos, unidades, límites y coherencia antes de iniciar; congelar la configuración | Parcial | OBS01: falta rechazo previo de anchos T/C nulos. |
| RF03.1 | Calcular evolución progresiva de las cinco variables mediante el modelo aprobado | Favorable | AC02–08 y corridas con estados progresivos; modelo inspeccionado. |
| RF03.2 | Iniciar, avanzar un intervalo, pausar, continuar y detener dentro de una sesión | Favorable | AC16; AppTest; pausa, continuación y detención. |
| RF03.3 | Usar un reloj simulado independiente de los refrescos y de la velocidad de visualización | Favorable | AC16 y renderizados AppTest sin avance adicional. |
| RF04.1 | Separar estado exacto del proceso y medición por variable | Favorable | AC14; x/y separados en datos y sensor. |
| RF04.2 | Representar muestreo, ruido, sesgo, pérdida y lectura congelada | Favorable | AC14 y pruebas de ruido/sesgo/missing/freeze. |
| RF04.3 | Entregar al controlador lecturas con calidad y sin acceso al estado exacto | Favorable | Contrato decide inspeccionado; AC09. |
| RF05.1 | Registrar por separado orden y acción efectiva de cada actuador | Favorable | AC08 y registros de comandos/medias efectivas. |
| RF05.2 | Representar capacidad, respuesta y disponibilidad | Favorable | AC08/15; respuesta30s y disponibilidad. |
| RF05.3 | Coordinar acciones incompatibles y documentar prioridades | Favorable | Estados firmados, AC08; recambio explícito en AC03. |
| RF06.1 | Ejecutar lazo abierto con programa por tiempo o eventos predefinidos sin corrección de y | Favorable | AC09/10/14; abierto constante independiente de y. |
| RF06.2 | Ejecutar lazo cerrado con comparación y decisiones justificadas | Favorable | AC09/12; histéresis, error y memoria. |
| RF06.3 | Identificar estrategia, parámetros y motivo de cada decisión | Favorable | Configuración y decisions.csv identifican motivos y estrategia. |
| RF07.1 | Definir perturbaciones por tipo, tiempo, magnitud, duración, unidad y objetivo | Favorable | AC01/13; validación de malla/unidad y combinación de eventos. |
| RF07.2 | Inyectar fallos de sensores y actuadores y conservar su calendario para auditoría | Favorable | AC14/15; auditoría separada de alarma observable. |
| RF07.3 | Aplicar una política explícita ante lecturas requeridas inválidas y errores numéricos | Favorable | AC14/15; terminación sin decisión inválida y raíz de dominio. |
| RF08.1 | Mostrar series de las cinco variables, referencias o bandas y acciones efectivas | Favorable | charts.py, test_charts_offline y AppTest; seis gráficos. |
| RF08.2 | Registrar activación y cese de alarmas con origen y severidad | Favorable | Prueba de transiciones y reconocimiento; engine/repository. |
| RF08.3 | Mostrar calidad y estado de corrida; no representar datos ausentes como normales | Favorable | AC14/15 y presentación de calidad/causa/estado. |
| RF09.1 | Guardar configuración inmutable, muestras, decisiones, acciones y eventos vinculados | Favorable | Repository con FK y series asociadas; AC11/17. |
| RF09.2 | Persistir cada lote aceptado de registros de forma atómica y sin duplicados | Favorable | AC16/17; recibo y rollback. |
| RF09.3 | Consultar historial y exportar configuración JSON y series CSV con metadatos | Favorable | AC17, AppTest y ZIP autónomos; historial/CSV/JSON. |
| RF10.1 | Comparar abierto y cerrado bajo la misma base y realización exógena | Favorable | Configs y ruido idénticos por estrategia; AC12. |
| RF10.2 | Calcular indicadores por variable y uso de actuadores según fórmulas aprobadas | Parcial | OBS01–03: finitud de J, turbidez y ventana temporal. |
| RF10.3 | Identificar duración común, terminaciones y límites de comparabilidad | Favorable | Prueba funcional de comparación truncada y S5/S9; aproximación declarada. |
| RF11.1 | Versionar especificación, modelo, perfiles, controlador y entorno de ejecución | Favorable | Manifiestos, config, metadata, entorno y versiones. |
| RF11.2 | Conservar semilla, estructura de generadores y realización exógena | Favorable | noise.csv PCG64 persistido; AC11; sin ruido en RK45. |
| RF11.3 | Asociar pruebas y documentación con su versión sin inventar evidencias | Favorable | XML/manifiestos vinculados; esta revisión conserva alcance y nuevos pendientes. |

Resultado: 30 RF favorables en el alcance probado y 3 parciales. Ninguna funcionalidad se marca ausente íntegramente por estos defectos; tampoco se aprueba toda la familia a partir de una sola prueba.

## Matriz de los 10 requisitos no funcionales

| ID | Estado Work | Evidencia y límite |
|---|---|---|
| RNF01 | Favorable | AC11/16/18, tolerancias originales y reproducción; limitado al entorno fijado. |
| RNF02 | Parcial | Balances/unidades verificados; OBS01 admite J no finito con banda degenerada. |
| RNF03 | Favorable | AC17, FK, unicidad y reversión real de lote. |
| RNF04 | Favorable | AC20 impide importar presentación en subproceso; dominio independiente. |
| RNF05 | Favorable | AC16/17 y recibos; reintento no duplica. |
| RNF06 | Favorable | AppTest en español, etiquetas/unidades/estados. Recorrido indicado, no revisión exhaustiva de toda edición JSON. |
| RNF07 | Parcial | Historial/fallos previstos verificados; OBS01 propaga ValueError y deja métricas ausentes sin diagnóstico de resultado derivado. |
| RNF08 | Favorable | Casos sin socket, gráficos locales y consulta/exportación; instalación requiere dependencias y no se acredita Windows. |
| RNF09 | Favorable | Configuración congelada por corrida, exportaciones/manifiestos y pruebas de copia. |
| RNF10 | Pendiente | Medición descriptiva virtual; falta equipo local/SSD y protocolo contextual de aceptación. |

Resultado: 7 RNF favorables, 2 parciales y 1 pendiente. Esos conteos describen esta revisión, no una certificación del programa.

## Correcciones académicas preparadas

Se actualiza REPORT_APA: estado de implementación y cronología en I–VI; capítulo VII con pruebas reales, recálculo S2, defectos y alcance; capítulo VIII con conclusiones sustentadas y recomendaciones. Se añaden referencias internas identificables a los documentos de Codex y un anexo de trazabilidad. Se conserva el modelo y se elimina la afirmación obsoleta de que todas las pruebas están pendientes.

En REQUIREMENTS se corrige el error de Work «pendientes de aprobación» para RNF01/RNF10: criterios aprobados en etapa 4; RNF01 probado en su alcance y RNF10 pendiente contextual. PROJECT_SPEC, modelo, plan y handoff reciben notas de estado, sin alterar ecuaciones ni tolerancias. MODEL_DEFAULTS.json permanece idéntico al original.

Se distingue edición académica 0.6.0 del contrato ejecutable 0.5.0. Cambiar spec_version en la aplicación solo por esta revisión rompería la validación actual y no está solicitado. La documentación corregida es propuesta de revisión y no queda aprobada por el solo hecho de generarla.

No se modificaron código ni IMPLEMENTATION, TEST_RESULTS o HANDOFF_CODEX propiedad de Codex. No se fabricaron pruebas de campo, plataforma Windows, rendimiento local ni resolución de los defectos. Docente/paralelo siguen por completar.

## Condiciones de integración

Ahora: **solicitar cambios y conservar borrador**. Corregir OBS01–03, añadir pruebas que reproduzcan sus fallos previos, reejecutar regresión y devolver commit, XML y exportaciones afectadas. Cerrar diferencias documentales OBS04 y revisar nuevamente la coherencia. RNF10/OBS05 permanece abierto hasta medir el equipo de referencia.

Después de las correcciones podrá reconsiderarse integración técnica; aceptar una primera versión con RNF10 abierto requeriría una decisión explícita y no equivaldría al cumplimiento integral. Esta revisión no otorga esa excepción ni ejecuta merge.

Las conclusiones de campo y la aceptación completa quedan fuera de la evidencia actual. Los datos de referencia apoyan la simulación académica en su alcance, con los tres defectos y el rendimiento contextual aún por cerrar.
