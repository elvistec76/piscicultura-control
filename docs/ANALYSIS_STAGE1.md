# Análisis inicial y estructura del informe

Versión 0.1.0 · 14 de octubre de 2026 · Aprobada por el estudiante el 14 de octubre de 2026; conservada como base de etapa 1

## Lectura del documento de la asignatura

El texto desarrolla definiciones de sistema, objetivo, elementos, atributos, estructura, organización, frontera, entradas, salidas, variables y parámetros; posteriormente presenta control, sensores, controlador, decisor, actuador, perturbaciones y estrategias de lazo abierto y cerrado. El índice inicial enumera otros temas de la materia, pero su enumeración no equivale a un desarrollo teórico. No se atribuirán al capítulo explicaciones completas de construcción de modelos o fundamentos históricos de la TGS que no contiene.

El proyecto aplicará estas definiciones al conjunto estanque virtual y sistema de control. La planta representa el proceso del agua y el controlador representa las decisiones. Su relación, junto con sensores y actuadores, conforma el sistema de control.

## Precisiones para evitar contradicciones

- El documento utiliza Vc para variables controladas y variables de control. La especificación usará x para estado, y para medición, r para referencia, u para acción manipulada y d para perturbación.
- Su explicación de parámetros se conservará como base académica, pero en el modelo se distinguirán estados que evolucionan y parámetros fijos durante una corrida.
- La frontera del modelo delimita lo representado; no significa que el controlador pueda imponer cualquier estado interno. Solo actúa mediante capacidades limitadas.
- Una perturbación puede programarse y conocerse por el simulador, sin que el controlador tenga acceso a ella. Esto evita darle información perfecta no disponible en el escenario.
- La medición para gráficos en lazo abierto no constituye retroalimentación si no influye en las acciones. Los escenarios de comparación no activarán correcciones por alarmas en ese modo.
- La retroalimentación negativa busca reducir desviaciones, pero no garantiza estabilidad, rapidez o precisión. Estos atributos se evaluarán después de ajustar y probar el controlador.
- No se identificará turbidez con sólidos suspendidos ni se asignarán límites universales a especies diferentes.

## Matriz de trazabilidad conceptual

| ID | Concepto del capítulo | Aplicación propuesta | Componente de software | Evidencia prevista |
|---|---|---|---|---|
| C01 | Sistema y enfoque sistémico | Estanque y control como conjunto interrelacionado | Orquestador y modelo del proceso | Ejecución integrada y relaciones documentadas |
| C02 | Objetivo | Mantener condiciones definidas y evaluar respuesta | Configuración y métricas | Referencias visibles y métricas por variable |
| C03 | Elementos | Agua, peces representados, sensores, actuadores, controlador | Modelo y módulos virtuales | Inventario y estado de cada elemento |
| C04 | Atributos | Volumen, capacidad, precisión, tiempos de respuesta | Configuración de componentes | Valores, unidades y procedencia |
| C05 | Estructura | Relaciones entre proceso, medición y actuación | Interfaces entre módulos | Flujo completo y efectos de actuación |
| C06 | Organización | Reglas de decisión, prioridad e interbloqueo | Controlador y gestión de fallos | Registro de regla aplicada |
| C07 | Frontera y ambiente | Un estanque virtual; condiciones externas | Configuración y perturbaciones | Límites del modelo y escenarios |
| C08 | Entradas de materia | Agua de reposición y carga de alimento representadas | Modelo de entradas | Balance y eventos registrados |
| C09 | Entradas de energía | Calor y energía asociada a equipos virtuales | Modelo térmico y actuadores | Flujo y unidades declarados |
| C10 | Entradas de información | Especie, referencias, escenario | Interfaz y configuración | Configuración guardada |
| C11 | Salidas | Agua descargada, intercambio de calor, datos y alarmas | Modelo, historial e interfaz | Registros y salidas representadas |
| C12 | Variables | T, oxígeno, pH, turbidez y nivel | Estado del proceso | Series temporales diferenciadas |
| C13 | Parámetros | Geometría y coeficientes fijos por corrida | Configuración versionada | Manifiesto de ejecución |
| C14 | Sistema controlado | Dinámica del estanque | Modelo matemático | Evolución sin controlador |
| C15 | Variables controladas | Propiedades del agua con objetivos | Configuración y métricas | Comparación con referencias o bandas |
| C16 | Variables de medida | Lecturas virtuales distintas del estado | Sensores | Estado y lectura trazados por separado |
| C17 | Variables de control | Potencias, caudales y dosificaciones | Actuadores | Orden y acción efectiva registradas |
| C18 | Perturbaciones | Clima, alimentación, fugas y fallos | Generador de escenarios | Eventos con instante y magnitud |
| C19 | Sensor | Medición con ruido o fallo configurable | Sensores virtuales | Pruebas de ruido, sesgo y pérdida |
| C20 | Comparador | Error respecto a referencia o banda | Comparación | Error registrado por variable |
| C21 | Controlador y decisor | Selección de acción según reglas | Control automático | Razón de la decisión |
| C22 | Actuador | Modificación progresiva del proceso | Dinámica de actuadores | Capacidad y respuesta limitada |
| C23 | Lazo abierto | Programa temporal sin corrección medida | Estrategia programada | Acciones independientes de y |
| C24 | Lazo cerrado | Medir, comparar, actuar y volver a medir | Estrategia con retroalimentación | Cambio de acción según medición |
| C25 | Retroalimentación negativa | Acción orientada a reducir desviación | Controlador y evaluación | Respuesta observada, sin garantía anticipada |

Las entradas y salidas físicas anteriores son representaciones numéricas dentro del modelo; los intercambios reales de la aplicación son datos. Las métricas y la reproducibilidad son decisiones de diseño complementarias, no definiciones atribuidas al capítulo.

## Estructura propuesta para revisión

1. Capítulo I Introducción: antecedentes, contextualización, descripción del proyecto y delimitación.
2. Capítulo II Planteamiento del problema: descripción, formulación, objetivos, justificación y limitaciones.
3. Capítulo III Marco teórico: Ingeniería de Sistemas, TGS, control, retroalimentación, piscicultura, calidad del agua y simulación. Distinguir el capítulo proporcionado de las fuentes complementarias.
4. Capítulo IV Análisis y diseño del sistema: elementos y atributos, estructura, organización, frontera, flujos, variables, parámetros, perturbaciones, subsistemas, requisitos y diagramas.
5. Capítulo V Modelado matemático: estados, unidades, ecuaciones, referencias, sensores, actuadores, algoritmos, supuestos y validación.
6. Capítulo VI Diseño de la implementación: herramientas, arquitectura, responsabilidades, interfaces, persistencia e integración.
7. Capítulo VII Pruebas y validación: escenarios, indicadores, criterios y resultados verificables.
8. Capítulo VIII Conclusiones y recomendaciones: redactar definitivamente después de las pruebas.
9. Referencias: fuentes verificadas y citas coherentes en APA 7.
10. Anexos: trazabilidad, configuraciones, diagramas, capturas, evidencia y guía de reproducción.

El índice podrá consolidarse tras la aprobación. No se añaden capítulos desarrollados de etapas posteriores.
