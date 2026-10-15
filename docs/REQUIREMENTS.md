# Requisitos del sistema

SPC-AGUA-001 · Versión 0.5.0 · 2026-10-14 · Etapas 1 a 4 aprobadas; entrega documental de etapa 5 preparada.
Se conservan RF01 a RF11. Los sufijos detallan cada familia y no sustituyen su identidad. Ningún requisito tiene evidencia de implementación. Las comprobaciones siguientes son criterios funcionales; las tolerancias y los casos numéricos se concretan en ACCEPTANCE_PLAN 0.5.0.

## Requisitos funcionales y comprobación prevista

| ID | Requisito | Comprobación de aceptación |
|---|---|---|
| RF01.1 | Ofrecer perfiles de O. niloticus, O. mykiss y C. carpio en crecimiento o engorde | Las tres identidades y la fase figuran en selección y configuración guardada |
| RF01.2 | Etiquetar cada valor como bibliográfico, derivado o demostrativo, con unidad y procedencia | Inspeccionar un perfil con las tres clases; un valor bibliográfico sin fuente se rechaza |
| RF01.3 | Permitir duplicar un perfil para editarlo sin cambiar las corridas históricas | Editar la copia y comprobar que la configuración histórica conserva su valor original |
| RF02.1 | Configurar geometría, estado inicial, biomasa, presión, salinidad y tiempo de simulación | La configuración aceptada contiene todos los campos exigidos por el modelo |
| RF02.2 | Distinguir referencias, bandas operativas y umbrales de alarma | Un cambio de umbral no altera silenciosamente la referencia; la relación permitida se valida según MATHEMATICAL_MODEL |
| RF02.3 | Validar tipos, unidades, límites y coherencia antes de iniciar; congelar la configuración | Rechazar geometría inválida o campos no finitos y exigir nueva corrida para cambiar un dato tras iniciar |
| RF03.1 | Calcular evolución progresiva de las cinco variables mediante el modelo aprobado | Una orden produce tasas de cambio y respuesta temporal; no asigna directamente estado igual a referencia |
| RF03.2 | Iniciar, avanzar un intervalo, pausar, continuar y detener dentro de una sesión | Pausar conserva tiempo y estado; continuar avanza desde ese punto; detener conserva datos parciales |
| RF03.3 | Usar un reloj simulado independiente de los refrescos y de la velocidad de visualización | Visualizar varias veces la misma corrida no añade pasos ni modifica sus series |
| RF04.1 | Separar estado exacto del proceso y medición por variable | Un sesgo configurado altera la lectura y no modifica directamente el estado de la planta |
| RF04.2 | Representar muestreo, ruido, sesgo, pérdida y lectura congelada | El escenario reproduce cada efecto; la detección solo se afirma cuando existe regla o señal de diagnóstico |
| RF04.3 | Entregar al controlador lecturas con calidad y sin acceso al estado exacto | Un controlador de prueba recibe únicamente el contrato permitido; no recibe el calendario oculto de fallos |
| RF05.1 | Registrar por separado orden y acción efectiva de cada actuador | Una orden superior a capacidad genera limitación y una acción efectiva distinta |
| RF05.2 | Representar capacidad, respuesta y disponibilidad | Un fallo o reducción de capacidad modifica la acción efectiva; respuesta y límites se especifican en MATHEMATICAL_MODEL 0.5.0 |
| RF05.3 | Coordinar acciones incompatibles y documentar prioridades | La configuración no permite dosificaciones opuestas simultáneas ni llenado y vaciado incompatibles; recambio explícito es un modo distinto |
| RF06.1 | Ejecutar lazo abierto con programa por tiempo o eventos predefinidos sin corrección de y | Con tiempo y programa iguales, variar y no cambia las órdenes abiertas |
| RF06.2 | Ejecutar lazo cerrado con comparación y decisiones justificadas | En un caso definido para ello, variar una lectura válida cambia el error o la decisión según la regla |
| RF06.3 | Identificar estrategia, parámetros y motivo de cada decisión | El registro permite reconstruir la regla y los datos utilizados; no se cambia estrategia a mitad de corrida |
| RF07.1 | Definir perturbaciones por tipo, tiempo, magnitud, duración, unidad y objetivo | Un evento fuera del horizonte o con unidad incompatible se rechaza; uno válido afecta al modelo |
| RF07.2 | Inyectar fallos de sensores y actuadores y conservar su calendario para auditoría | La inyección aparece en historial; el controlador solo conoce síntomas o diagnósticos permitidos |
| RF07.3 | Aplicar una política explícita ante lecturas requeridas inválidas y errores numéricos | En cerrado, una lectura requerida inválida registra causa y termina antes de una nueva decisión; en abierto una lectura observacional inválida se registra sin alterar u |
| RF08.1 | Mostrar series de las cinco variables, referencias o bandas y acciones efectivas | Cada gráfico muestra tiempo simulado, unidad, variable y leyenda; distingue x e y cuando se muestran ambos |
| RF08.2 | Registrar activación y cese de alarmas con origen y severidad | Una condición definida genera un evento de activación y otro de cese, sin duplicarlos por cada refresco |
| RF08.3 | Mostrar calidad y estado de corrida; no representar datos ausentes como normales | Una pérdida de sensor aparece como dato ausente o inválido; una corrida parcial no figura como completada |
| RF09.1 | Guardar configuración inmutable, muestras, decisiones, acciones y eventos vinculados | Consultar una corrida permite recuperar sus series y metadatos asociados |
| RF09.2 | Persistir cada lote aceptado de registros de forma atómica y sin duplicados | Una escritura fallida no deja un lote parcialmente guardado; reenviar un identificador ya confirmado no duplica datos |
| RF09.3 | Consultar historial y exportar configuración JSON y series CSV con metadatos | Reabrir la aplicación permite consultar una corrida guardada; los archivos identifican corrida, unidad y tiempo |
| RF10.1 | Comparar abierto y cerrado bajo la misma base y realización exógena | Verificar igualdad de estado inicial, horizonte, perturbaciones y ruido; la estrategia es una diferencia declarada |
| RF10.2 | Calcular indicadores por variable y uso de actuadores según fórmulas aprobadas | Un caso de cálculo manual coincide dentro de tolerancia; no se suman errores dimensionalmente incompatibles |
| RF10.3 | Identificar duración común, terminaciones y límites de comparabilidad | Si una corrida termina antes, se separa la comparación del tramo común de los resultados completos y se informa la causa |
| RF11.1 | Versionar especificación, modelo, perfiles, controlador y entorno de ejecución | Una corrida guardada registra los identificadores y versiones que efectivamente utilizó |
| RF11.2 | Conservar semilla, estructura de generadores y realización exógena | Una repetición usa las mismas entradas externas; los generadores internos del controlador no desplazan el ruido del escenario |
| RF11.3 | Asociar pruebas y documentación con su versión sin inventar evidencias | Cada resultado futuro identificará caso, versión y artefacto; el estado pendiente permanece visible hasta recibir evidencia de Codex |

## Requisitos no funcionales

| ID | Cualidad y obligación | Evidencia prevista |
|---|---|---|
| RNF01 | Reproducibilidad en un entorno fijado y comparación numérica con tolerancias declaradas | Repetir configuración y realización; usar tolerancias por variable de ACCEPTANCE_PLAN |
| RNF02 | Consistencia de unidades y valores finitos en contratos | Rechazar unidades incompatibles; conservar unidad canónica por campo |
| RNF03 | Integridad referencial y unicidad en SQLite | Claves foráneas activadas en cada conexión, índices únicos y prueba de reversión de lote |
| RNF04 | Núcleo desacoplado de Streamlit y Plotly | Ejecutar un escenario desde pruebas sin interfaz ni importaciones de presentación en el dominio |
| RNF05 | Comandos de avance idempotentes | Reintentar un comando confirmado no avanza dos veces; comprobar run_id, command_id y paso esperado |
| RNF06 | Interfaz en español con unidades y procedencia visibles | Recorrer configuración, ejecución, alarmas e historial sin campos críticos ambiguos |
| RNF07 | Errores explícitos y recuperación del historial | Un error termina con causa y conserva lo confirmado; reinicio marca corridas huérfanas como interrumpidas |
| RNF08 | Ejecución local sin servicios externos necesarios tras instalar dependencias | Ejecutar escenario, gráficos, guardado y consulta sin red; el entorno soportado lo documentará Codex |
| RNF09 | Configuración histórica inmutable y trazabilidad de exportaciones | Editar un perfil no altera corridas previas; cada exportación incluye identificadores y versiones |
| RNF10 | Rendimiento medible con carga y entorno acordados | Usar S8 y AC20: 48 h, intervalo 60 s, tres repeticiones y mediana <=60 s en el equipo declarado |

RNF10 dispone de criterio propuesto en AC20: carga S8, tres repeticiones, mediana <=60 s y equipo de referencia declarado. RNF01 adopta las tolerancias del plan. Ambos siguen pendientes de aprobación y de ejecución. No se promete compatibilidad con un sistema operativo o versión de Python no comprobados.

## Trazabilidad por familia

OE1 a OE7 corresponden a los objetivos específicos del capítulo II. C01 a C25 se conservan en ANALYSIS_STAGE1.

| Familia | Objetivos | Conceptos | Módulos principales | Evidencia vinculada |
|---|---|---|---|---|
| RF01 | OE2 | C02, C04, C10, C13 | Perfiles y configuración | Perfiles versionados y fuentes |
| RF02 | OE2, OE3 | C02, C04, C07, C13 | Configuración y validación | Casos aceptados y rechazados |
| RF03 | OE3, OE5 | C01, C05, C12, C14 | Proceso y orquestación | Series y control del reloj |
| RF04 | OE3 | C16, C19 | Sensores | Lecturas y calidad frente a x |
| RF05 | OE3, OE4 | C17, C22 | Actuadores y coordinación | Orden, límites y acción efectiva |
| RF06 | OE4 | C20, C21, C23, C24, C25 | Control y comparación | Decisiones por estrategia |
| RF07 | OE5, OE6 | C07, C18 | Escenarios y fallos | Eventos y efectos reproducidos |
| RF08 | OE5 | C11, C15, C16 | Interfaz y alarmas | Gráficos y eventos sin duplicación |
| RF09 | OE5, OE7 | C06, C10, C11 | Persistencia y exportación | Integridad, historial y archivos |
| RF10 | OE6 | C02, C23, C24, C25 | Evaluación y comparación | Indicadores y base común |
| RF11 | OE7 | C01, C05, C06 | Configuración y evidencia | Versiones, realización y resultados |

## Criterio de cierre documental

La aprobación de etapa 4 cubre modelos, perfiles numéricos, capacidades, referencias, bandas, alarmas, intervalos, políticas de fallos, tolerancias e indicadores. Los 33 subrequisitos y los 10 RNF siguen sin evidencia de implementación. La aceptación documental permite el traspaso; la aceptación del software requiere resultados de Codex.

## Correspondencia con aceptación 0.5.0

RF01 y RF02: AC01. RF03: AC02 a AC07, AC10, AC11 y AC18. RF04: AC09 y AC14. RF05: AC05, AC07, AC08 y AC15. RF06: AC09, AC10 y AC12. RF07: AC13 a AC15. RF08: AC13 a AC15. RF09: AC11, AC16 y AC17. RF10: AC03, AC12, AC13, AC18 y AC19. RF11: AC01, AC11 y AC17. RNF01 a RNF10 conservan sus evidencias previstas y se concretan con AC11, AC16, AC17, AC18 y AC20, junto con la revisión de unidades y de interfaz. No se marca ningún caso como pasado.
