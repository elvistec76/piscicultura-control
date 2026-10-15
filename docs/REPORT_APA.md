# Diseño y simulación de un sistema de control automático de la calidad del agua para piscicultura mediante retroalimentación

Versión 0.5.0 · 14 de octubre de 2026 · Capítulos I a V aprobados; capítulos VI y VII como diseño y plan de pruebas

Autor: Elvis Erik Huaynoca Condori. Docente y paralelo: completar antes de entregar. Materia: Ingeniería de Sistemas. Fecha de portada: 14 de octubre de 2026. Contiene capítulos I a V aprobados, capítulos VI y VII de diseño y planificación, y referencias APA 7. Resultados y capítulo VIII pendientes de evidencias de Codex.

## Capítulo I Introducción

### 1.1 Antecedentes

El material de la asignatura define un sistema como un conjunto de elementos relacionados que participan en el cumplimiento de un objetivo común. Desde esta perspectiva, estudiar un proceso exige identificar sus componentes y comprender las relaciones que explican su comportamiento. El mismo documento describe el control como un conjunto de acciones que permite orientar un proceso ante perturbaciones y distingue las estrategias de lazo abierto y lazo cerrado (*Introducción a la Ingeniería de Sistemas*, s. f.).

Estos conceptos ofrecen una base para estudiar el mantenimiento de las condiciones del agua en piscicultura. Un estanque reúne componentes biológicos, físicos y operativos cuyos cambios se relacionan. La temperatura, por ejemplo, influye en la disponibilidad de oxígeno y en la respiración de los peces. El oxígeno también varía por procesos como la fotosíntesis, la respiración y el intercambio con la atmósfera (Organización de las Naciones Unidas para la Alimentación y la Agricultura [FAO], s. f.). Estas relaciones justifican abordar el proceso mediante un análisis del conjunto.

El presente proyecto adopta la simulación computacional como medio para representar esas relaciones y estudiar las decisiones de un controlador. No se parte de ensayos propios ni de datos de una instalación piscícola concreta. Se propone construir un entorno académico en el que sea posible observar cómo evolucionan las variables, introducir perturbaciones y comparar acciones programadas con acciones basadas en mediciones.

### 1.2 Contextualización de la piscicultura

Para este proyecto, la piscicultura se entiende como la crianza de peces en un ambiente acuático gestionado. Su estudio requiere considerar las características de la especie y las condiciones del medio. El manual de la FAO sobre calidad del agua explica que temperatura, oxígeno y pH se relacionan con procesos físicos y biológicos del estanque; por tanto, una condición apropiada para un escenario no debe trasladarse automáticamente a otro (FAO, s. f.).

El nivel de agua se incorpora como variable operativa vinculada con la cantidad disponible y los intercambios de agua. La turbidez se incluye para representar cambios en la condición óptica del agua. Su interpretación requiere distinguirla de la concentración de sólidos y de la transparencia medida con otros métodos. Las unidades, relaciones y límites de estas variables se justificarán en las etapas de investigación y modelado.

La aplicación contemplará perfiles iniciales de tilapia, trucha y carpa. Cada perfil deberá identificar la especie concreta, la etapa de cultivo considerada y la procedencia de sus valores. La denominación general de un pez no bastará para atribuirle un rango universal. Cuando no exista sustento suficiente para un valor, este se identificará como demostrativo y no como recomendación de manejo.

### 1.3 Descripción general del proyecto

Se propone diseñar una aplicación que simule el control automático de temperatura, oxígeno disuelto, pH, turbidez y nivel de agua. El usuario seleccionará un perfil de especie, configurará el estanque, establecerá condiciones iniciales y elegirá un escenario de operación. Un modelo dinámico calculará la evolución del proceso durante un intervalo de tiempo definido.

Los sensores virtuales producirán mediciones del estado simulado. En la estrategia de lazo cerrado, el controlador utilizará esas mediciones y las referencias para determinar acciones mediante actuadores virtuales. Las acciones modificarán la evolución del proceso y las nuevas mediciones permitirán revisar las decisiones. Esta secuencia representa la retroalimentación descrita en el material de la asignatura (*Introducción a la Ingeniería de Sistemas*, s. f.).

En la estrategia de lazo abierto, las acciones seguirán una programación temporal o por eventos definidos sin utilizar las mediciones para corregirlas. Será posible conservar sensores para visualizar y registrar datos: en ese caso, la medición tendrá una función de observación y no cerrará el lazo. La comparación utilizará condiciones iniciales y perturbaciones equivalentes para atribuir las diferencias al comportamiento de las estrategias.

La aplicación se desarrollará con Python, NumPy, SciPy, Streamlit, Pandas, Plotly y SQLite. Pytest se utilizará para verificar el comportamiento técnico. Los gráficos y registros permitirán examinar la relación entre perturbaciones, mediciones y decisiones. En esta etapa se documenta el diseño; todavía no existe evidencia de implementación o de desempeño.

### 1.4 Alcance y delimitación

El proyecto se delimita a un estanque virtual por ejecución y a las cinco variables indicadas. Se incluirán perfiles configurables, sensores y actuadores virtuales, estrategias de lazo abierto y cerrado, perturbaciones, alarmas, fallos simulados y registros temporales. La delimitación a un estanque facilita seguir el flujo de información y observar las interacciones entre sus variables.

La simulación será completamente digital. No comprenderá adquisición de sensores físicos, instalación de equipos, operación de una piscigranja ni certificación para uso productivo. Tampoco abarcará un modelo completo de crecimiento, enfermedades, nutrición, amoníaco, salinidad o ecosistema del estanque. Algunas de estas condiciones podrán intervenir como factores simplificados, siempre que se declaren sus supuestos.

El trabajo seguirá seis etapas: redacción inicial, investigación teórica, análisis y arquitectura, especificación matemática, implementación y revisión de evidencias. Los resultados y las conclusiones definitivas se redactarán después de ejecutar pruebas documentadas.

## Capítulo II Planteamiento del problema

### 2.1 Descripción del problema

La calidad del agua presenta variaciones a lo largo del tiempo. La FAO describe relaciones entre temperatura, oxígeno disuelto, actividad biológica y cambios diarios del pH (FAO, s. f.). Estas interacciones hacen necesario considerar la evolución del proceso al estudiar una estrategia de control.

Desde el punto de vista académico, representar el control únicamente mediante un diagrama o una tabla de umbrales resulta insuficiente para examinar cómo responde el sistema a una perturbación. Una aplicación que sustituya directamente un valor alterado por el valor deseado tampoco permitiría observar los efectos de la capacidad limitada de los actuadores, la incertidumbre de los sensores o el tiempo requerido para modificar el proceso.

El problema del proyecto consiste en construir una representación computacional coherente del proceso y de su control, de manera que las decisiones tengan efectos progresivos y verificables. La simulación deberá mostrar qué se mide, qué se desea mantener, qué se manipula y cómo se registran las respuestas. Asimismo, deberá permitir comparar estrategias bajo condiciones reproducibles, sin anticipar que el lazo cerrado será superior en todos los casos.

La propuesta no se sustenta en un diagnóstico de pérdidas de una piscigranja determinada. Su necesidad es educativa y técnica: integrar los conceptos de Ingeniería de Sistemas con una aplicación funcional y una evaluación documentada.

### 2.2 Formulación del problema

¿Cómo diseñar y simular un sistema de control con retroalimentación que represente la evolución de temperatura, oxígeno disuelto, pH, turbidez y nivel de agua en un estanque de piscicultura, y permita evaluar su respuesta frente a perturbaciones mediante una comparación reproducible con una estrategia de lazo abierto?

### 2.3 Objetivo general

Diseñar y desarrollar una simulación computacional de un sistema de control automático de la calidad del agua para piscicultura, basada en retroalimentación, que represente cinco variables del estanque y permita evaluar su respuesta ante perturbaciones mediante indicadores y escenarios reproducibles.

### 2.4 Objetivos específicos

1. Identificar los elementos, atributos, relaciones, fronteras, entradas, salidas y subsistemas del proceso a partir del material de Ingeniería de Sistemas.
2. Definir perfiles configurables de tilapia, trucha y carpa, diferenciando valores sustentados en fuentes técnicas de valores demostrativos.
3. Especificar modelos dinámicos para las cinco variables, los sensores y los actuadores, declarando unidades, supuestos y limitaciones.
4. Diseñar estrategias de lazo abierto y cerrado con límites de actuación y reglas de decisión explícitas.
5. Implementar una interfaz que permita configurar, ejecutar y observar escenarios, junto con el historial de mediciones, acciones y alarmas.
6. Evaluar el comportamiento de ambas estrategias mediante pruebas reproducibles, registros e indicadores de desempeño previamente definidos.
7. Mantener trazabilidad entre los conceptos académicos, los requisitos, el diseño y las evidencias de implementación.

### 2.5 Justificación técnica

La simulación permitirá examinar la respuesta temporal del proceso y la influencia de las decisiones de control. La separación entre estado real simulado y medición virtual hará posible introducir ruido, sesgos o fallos sin alterar de forma arbitraria el modelo del estanque. La definición de capacidad y tiempos de respuesta de los actuadores permitirá evaluar situaciones en las que la corrección sea lenta o insuficiente.

Registrar la configuración y las perturbaciones permitirá repetir los experimentos. Además, la comparación entre estrategias utilizará el mismo modelo del proceso, con condiciones equivalentes. Estas decisiones metodológicas facilitarán revisar si las diferencias observadas se deben al controlador o a cambios no controlados en el experimento.

### 2.6 Justificación académica

El proyecto aplicará los conceptos de sistema, objetivo, elementos, atributos, estructura, organización y frontera a un caso concreto. También permitirá distinguir variables medidas, controladas y manipuladas, así como referencias y perturbaciones. La retroalimentación se observará como una relación funcional entre medición, comparación, decisión y actuación, conforme a la base de la asignatura (*Introducción a la Ingeniería de Sistemas*, s. f.).

La documentación y las pruebas facilitarán verificar que los conceptos tengan una representación en el software. De este modo, el trabajo integrará análisis sistémico, diseño y evaluación, en lugar de limitarse a la presentación visual de datos.

### 2.7 Justificación práctica

La aplicación ofrecerá un entorno de experimentación sin requerir equipos físicos. El estudiante podrá modificar condiciones, introducir fallos y revisar decisiones para comprender el funcionamiento del control. Su utilidad práctica inicial será didáctica: no se atribuirán mejoras productivas, ahorro real de agua o reducción de mortalidad sin evidencia de campo.

Los registros también permitirán preparar demostraciones y explicar resultados durante la exposición. La posibilidad de repetir un escenario contribuirá a revisar errores y contrastar decisiones entre el informe y el programa.

### 2.8 Alcances y limitaciones

El compromiso funcional comprende las cinco variables, tres perfiles iniciales, dos estrategias de control, perturbaciones programables, fallos, alarmas, gráficos e historial persistente. Los escenarios e indicadores se especificarán antes de la programación y servirán como base para las pruebas de aceptación.

La fidelidad dependerá de los modelos y de sus parámetros. Un estanque representado mediante valores agregados no describirá todas las diferencias espaciales del agua. El pH requerirá especial cuidado por su relación con procesos químicos; una aproximación empírica deberá declararse como tal. La turbidez tampoco se convertirá automáticamente a concentración de sólidos sin una relación sustentada.

Las pruebas con datos sintéticos permitirán verificar la consistencia numérica y el comportamiento del programa, pero no demostrarán precisión predictiva en una instalación real. El análisis de resultados señalará escenarios con corrección insuficiente, saturación, oscilaciones o fallos. Las conclusiones finales dependerán de las evidencias aportadas por Codex.

## Capítulo III Marco teórico

### 3.1 Ingeniería de Sistemas

El material de la asignatura establece que un sistema reúne elementos relacionados orientados a un objetivo. También diferencia las propiedades de esos elementos, sus relaciones y las reglas que condicionan su funcionamiento (*Introducción a la Ingeniería de Sistemas*, s. f.). En el proyecto, estas categorías permitirán describir el estanque virtual, el sistema de control y su coordinación.

Como complemento, el International Council on Systems Engineering (INCOSE, s. f.) presenta la Ingeniería de Sistemas como un enfoque integrador y transdisciplinario que considera la realización, el uso y el retiro de sistemas. Esta perspectiva amplía el análisis del objeto controlado hacia sus necesidades, diseño y evaluación. Para la simulación propuesta, implica mantener coherencia entre la finalidad educativa, los requisitos, los modelos y las pruebas.

La aplicación de este enfoque exige explicar las relaciones. Un sensor aporta información, pero no modifica por sí mismo el agua; el controlador decide y el actuador ejecuta una acción cuyo efecto depende del proceso. El historial conserva evidencia, mientras la interfaz permite observar y configurar. Ninguna de estas funciones, de manera aislada, representa el control completo del estanque.

### 3.2 Teoría General de Sistemas y enfoque sistémico

La Teoría General de Sistemas proporciona un marco para estudiar conjuntos organizados mediante conceptos aplicables a distintos dominios. En este trabajo, su aplicación se concentra en las relaciones entre elementos, el objetivo común, la delimitación y los intercambios. Estas categorías se sustentan en las definiciones del capítulo de la materia. No se pretende desarrollar toda la teoría ni atribuir al documento contenidos que aparecen solamente en su índice.

Adcock (s. f.), en el SEBoK, explica que el pensamiento sistémico utiliza conceptos, principios y patrones comunes para comprender situaciones, y que su aplicación puede apoyarse en modelos. Su artículo identifica la obra de Bertalanffy entre sus referencias principales. Aquí se cita el artículo consultado; no se presenta la obra original de Bertalanffy como si se hubiera revisado directamente.

Para este proyecto, el enfoque sistémico significa examinar si una decisión sobre una variable influye en las demás. Por ejemplo, la reposición de agua podría modificar el nivel y, según las características de la entrada, también la temperatura o la composición. Esta relación es una hipótesis de diseño que deberá especificarse en el modelo. El análisis posterior indicará cuáles interacciones se representan y cuáles se excluyen.

La frontera conceptual delimitará un estanque y los componentes que intervienen en su simulación. El ambiente aportará condiciones y perturbaciones. Estar dentro de esa frontera no implica que cada variable pueda imponerse libremente: el controlador solo dispondrá de las acciones y capacidades definidas.

### 3.3 Sistemas de control

El documento de la asignatura caracteriza un sistema de control por su influencia sobre un sistema controlado, orientada a alcanzar referencias mediante acciones. Sus elementos incluyen sensores, controlador, decisor y actuadores. En la descripción del lazo cerrado incorpora el comparador y la señal de referencia (*Introducción a la Ingeniería de Sistemas*, s. f.).

En la simulación, el sistema controlado será el modelo del agua. Las variables controladas serán las propiedades para las que se establezcan objetivos. Las variables medidas serán las lecturas de los sensores virtuales; las manipuladas serán las acciones efectivas, como una potencia o un caudal cuando estos se definan. Esta distinción evita confundir un resultado deseado con el mecanismo utilizado para obtenerlo.

Una referencia puede ser un valor o una condición de operación. La futura especificación diferenciará consigna, banda aceptable y umbral de alarma. También separará la orden calculada de la acción efectiva, puesto que un actuador puede tener capacidad limitada o presentar un fallo.

### 3.4 Control de lazo abierto y lazo cerrado

En el lazo abierto, las acciones siguen una programación sin corregirse con la medición de la salida. En el lazo cerrado, la información de salida interviene en la decisión posterior (*Introducción a la Ingeniería de Sistemas*, s. f.). Ambos modos podrán observarse mediante gráficos; la diferencia estará en el uso de las mediciones para actuar.

Como aplicación conceptual, un aireador programado por horario representaría una estrategia abierta. Si su acción se modifica a partir de la lectura de oxígeno y de una referencia, representaría una estrategia cerrada. Son ejemplos propuestos para comprender los modos, no algoritmos ya seleccionados ni equipos instalados.

La comparación exigirá mantener equivalentes las condiciones iniciales y las perturbaciones. Si el modo denominado abierto modifica sus acciones por alarmas basadas en mediciones, esa protección introducirá retroalimentación. Por ello, las reglas de comparación deberán declarar cualquier intervención que altere el tipo de estrategia.

### 3.5 Retroalimentación y respuesta dinámica

La retroalimentación negativa orienta las acciones hacia la reducción de desviaciones. El material de la materia también advierte que un ajuste inadecuado puede producir oscilaciones (*Introducción a la Ingeniería de Sistemas*, s. f.). En consecuencia, el cierre del lazo no bastará para declarar que el diseño es estable o preciso.

Åström y Murray (s. f.-a) presentan la atenuación de perturbaciones, el seguimiento de referencias y la robustez frente a incertidumbres como propiedades que se estudian en sistemas con retroalimentación. Su tratamiento incluye modelos dinámicos y análisis de estabilidad. Este complemento fundamenta la necesidad de evaluar la respuesta del controlador, en lugar de atribuirle ventajas universales.

En el proyecto se observarán la evolución temporal, las desviaciones, la recuperación y la actividad de los actuadores. Si una acción no logra corregir una perturbación, el registro deberá mostrarlo. El programa no sustituirá el estado alterado por la referencia para aparentar una respuesta satisfactoria.

### 3.6 Principios de piscicultura y perfiles de especies

El entorno acuático es el medio en el que se desarrolla el cultivo de peces. Su representación exige identificar la especie y las condiciones de producción. Se propone trabajar con tilapia del Nilo, trucha arcoíris y carpa común. Las fichas de FAO permiten distinguir Oreochromis niloticus y Cyprinus carpio, mientras el manual de Woynarovich et al. (2011) aborda Oncorhynchus mykiss (FAO, 2009a, 2009b).

Los perfiles no deben confundirse con tres estanques simultáneos. La aplicación ejecutará un estanque por corrida y utilizará el perfil seleccionado. Para mantener un alcance manejable, se propone representar una fase de crecimiento o engorde y dejar incubación y reproducción fuera del modelo inicial. La etapa de cultivo deberá figurar en la configuración aprobada.

Las fuentes utilizan criterios diferentes para describir las temperaturas: preferencia, crecimiento, reproducción o tolerancia. Por ejemplo, la ficha de tilapia indica una preferencia de 31 a 36 °C, mientras la tabla térmica de adultos del manual de estanques informa 27 a 30 °C (FAO, 2009b, s. f.). Estos intervalos se conservarán con su contexto y no se combinarán mediante un promedio.

### 3.7 Calidad del agua

#### 3.7.1 Temperatura

La temperatura se representará en grados Celsius. Su referencia deberá relacionarse con especie y fase de cultivo. Woynarovich et al. (2011) señalan 13 a 15 °C en relación con aprovechamiento del alimento y crecimiento de trucha. La ficha de carpa informa 23 a 30 °C para mejor crecimiento (FAO, 2009a). Estos antecedentes orientan la selección posterior; no establecen por sí solos límites de alarma o capacidad de un equipo.

#### 3.7.2 Oxígeno disuelto

El oxígeno se expresará en mg/L y podrá examinarse también como porcentaje de saturación. DOTABLES considera temperatura, presión barométrica y salinidad para calcular solubilidad (U.S. Geological Survey [USGS], 2022). Por tanto, una saturación expresada en porcentaje no equivale a una concentración única para todos los escenarios.

Para trucha, Woynarovich et al. (2011) distinguen condiciones próximas a saturación de concentraciones bajas aceptables para determinadas edades. De manera semejante, la tolerancia de carpa a poco oxígeno descrita por FAO (2009a) no se adoptará como objetivo de operación. El perfil del programa deberá identificar qué significado tiene cada valor.

#### 3.7.3 pH

La International Union of Pure and Applied Chemistry (IUPAC, s. f.) define el pH mediante el logaritmo negativo de la actividad de los iones hidrógeno. Es una magnitud adimensional. Esta definición impide interpretarlo como una cantidad que se mezcla linealmente por simple promedio de los valores de pH.

Para la simulación, se deberá elegir entre una aproximación empírica explícita y un modelo que represente la química necesaria. La primera opción puede ser útil para la demostración de control, pero no permitirá deducir dosificaciones reales. Esta restricción es una decisión metodológica del proyecto.

#### 3.7.4 Turbidez

La turbidez describe una condición óptica influida por materiales presentes en el agua. Anderson (2005) aborda la selección de equipos y el reporte de esta medición. La explicación del USGS (2026) identifica las unidades nefelométricas NTU en la medición descrita.

El proyecto conservará NTU como unidad de su variable virtual. No supondrá que corresponde a mg/L de sólidos ni a centímetros de transparencia. Tampoco atribuirá un límite a cada especie sin una fuente aplicable. Un umbral adoptado únicamente para un ejercicio deberá identificarse como demostrativo.

#### 3.7.5 Nivel del agua

El nivel se representará como altura en metros respecto del fondo definido. Su intervalo operativo dependerá de la geometría y del volumen útil propuesto. No se tratará como un límite fisiológico propio de la especie.

Como decisión de modelado posterior, su evolución deberá relacionarse con entradas y salidas de agua. Los efectos de fugas, reposición o evaporación se especificarán cuando se definan los balances. No se atribuyen a la literatura valores de profundidad que todavía no se han seleccionado.

### 3.8 Simulación computacional

Åström y Murray (s. f.-b) explican que la elección de un modelo depende de las preguntas de análisis y del nivel de detalle requerido. Presentan estados que evolucionan mediante ecuaciones diferenciales o de diferencias. Para el proyecto, esto permite distinguir el proceso representado de su medición y de las decisiones de control.

La documentación de SciPy describe solve_ivp como una función para resolver numéricamente problemas de valor inicial de ecuaciones diferenciales ordinarias (SciPy, s. f.). Su disponibilidad respalda la herramienta elegida; no determina las ecuaciones del agua ni demuestra que el modelo sea fiel a un estanque real.

Se diferenciarán el tiempo simulado, el intervalo de medición y los pasos internos de integración. La animación en pantalla no definirá el comportamiento matemático. La configuración y los eventos se conservarán para repetir escenarios y comparar estrategias.

### 3.9 Verificación y límites de validez

En este proyecto, verificar el software significará comprobar que calcula y registra conforme a la especificación. La consistencia del modelo se examinará mediante unidades, balances aplicables, comportamientos esperados y sensibilidad numérica. Validar su precisión frente a un estanque real requeriría datos empíricos, que no están disponibles en esta etapa.

Por ello, las conclusiones se limitarán al alcance de las evidencias. Una simulación puede mostrar un comportamiento coherente con sus supuestos sin predecir una piscigranja particular. La formulación matemática y los criterios de aceptación se completarán antes del traspaso a Codex.

## Capítulo IV Análisis y diseño del sistema

### 4.1 Objetivo del sistema

El sistema propuesto tendrá como objetivo regular las condiciones representadas del agua mediante acciones limitadas y evaluar su respuesta ante perturbaciones. La finalidad académica será observar las relaciones entre medición, comparación, decisión y actuación. El cumplimiento se determinará con registros y pruebas; no se presume que toda perturbación pueda corregirse.

El análisis utiliza las categorías de objetivo, elementos, atributos, estructura, organización y frontera del material de la asignatura (*Introducción a la Ingeniería de Sistemas*, s. f.). Las decisiones de arquitectura de este capítulo constituyen propuestas de diseño del proyecto y no definiciones extraídas de esa fuente.

### 4.2 Elementos y atributos

Se identifica un estanque virtual por ejecución. Su perfil corresponderá a tilapia del Nilo, trucha arcoíris o carpa común en crecimiento o engorde. Los peces se representarán mediante parámetros de carga biológica; no se simulará su crecimiento individual ni todo su ciclo de vida. La hipótesis inicial de agua bien mezclada deberá declararse en el modelo y limita la representación de diferencias entre superficie y fondo.

Tabla 1

*Elementos del sistema y atributos previstos*

| Elemento | Atributos principales | Función en la simulación |
|---|---|---|
| Estanque y agua | Geometría, volumen, cinco variables y condiciones iniciales | Representar el proceso controlado |
| Población de peces | Especie, fase y biomasa parametrizada | Representar demanda biológica simplificada |
| Perfil de cultivo | Fuentes, referencias, bandas y origen de valores | Configurar un escenario identificable |
| Sensores virtuales | Variable, unidad, muestreo, ruido, sesgo y calidad | Producir lecturas del proceso |
| Comparador y decisor | Referencias, reglas, errores y prioridades | Determinar órdenes justificadas |
| Actuadores virtuales | Capacidad, acción efectiva, respuesta y fallo | Modificar la evolución del agua |
| Ambiente simulado | Clima, aportes y perturbaciones programadas | Introducir condiciones externas |
| Registro e interfaz | Identificadores, tiempo simulado y versión | Conservar evidencias y permitir observación |

Nota. Elaboración propia a partir de las categorías del material de la asignatura. Las capacidades y los coeficientes siguen pendientes de especificación matemática.

### 4.3 Estructura y organización

La estructura se define por las relaciones entre proceso, sensores, controlador y actuadores. Los sensores observan el proceso; el controlador recibe lecturas y referencias; los actuadores transforman las órdenes en acciones efectivas. El orquestador coordina la secuencia, mientras el registro conserva evidencia para evaluar el conjunto.

La organización estará determinada por reglas: validar antes de iniciar, conservar la configuración de cada ejecución, respetar capacidades, registrar decisiones y distinguir estados de ejecución. La simulación tendrá estados preparada, en ejecución, pausada, completada, detenida, fallida e interrumpida. Una detención solicitada por el usuario conservará los resultados parciales. Una interrupción del proceso informático no se presentará como una ejecución completada.

La configuración quedará congelada al iniciar. Cambiar especie, referencias o estrategia exigirá crear otra ejecución. Las perturbaciones se definirán antes de comenzar para garantizar repetibilidad. Durante una corrida se permitirá pausar, continuar, avanzar un intervalo o detener; no se modificarán valores del agua mediante controles de la interfaz.

### 4.4 Frontera y ambiente

La frontera del sistema representado incluirá el estanque y los componentes virtuales de control. El ambiente aportará condiciones climáticas, características del agua de entrada y eventos externos. El generador de escenarios conocerá estos eventos para reproducirlos, pero el controlador no recibirá su calendario oculto.

Debe distinguirse esa frontera conceptual de la del programa. La aplicación intercambiará datos con el usuario y archivos locales; las entradas y salidas de agua, calor o energía serán cantidades calculadas. Tampoco se confundirá la aplicación con una piscigranja física: el diseño no comprende conexión con equipos reales.

### 4.5 Entradas y salidas

Tabla 2

*Flujos representados en la frontera del estanque y del control*

| Tipo | Entradas representadas | Salidas representadas |
|---|---|---|
| Materia | Agua de reposición, oxígeno transferido y carga de alimento simplificada | Agua descargada y material retirado según el modelo |
| Energía | Intercambio térmico y energía asociada a equipos virtuales | Pérdidas térmicas y energía transferida al ambiente |
| Información | Perfil, referencias, lecturas y programación | Mediciones, decisiones, alarmas y resultados |

Nota. Las fronteras elegidas determinan qué se considera intercambio. El capítulo V deberá establecer los balances y evitar contar dos veces un mismo flujo. Un filtro recirculante, por ejemplo, no reduce por sí mismo el volumen si el modelo no representa una descarga.

### 4.6 Variables y parámetros

Las cinco variables del alcance serán temperatura en °C, oxígeno disuelto en mg/L, pH adimensional, turbidez en NTU y nivel en m. El modelo podrá usar estados internos auxiliares si la formulación química o los actuadores los requieren; ello no incorporará automáticamente otra variable controlada a la interfaz.

Se utilizará x para estado, y para medición, r para referencia, u para acción manipulada y d para perturbación. Una lectura puede diferir del estado por ruido o sesgo. El controlador tendrá acceso a y y r, pero no al estado exacto del simulador. Los evaluadores podrán consultar x para examinar los efectos del error de medición.

Los parámetros fijos de una corrida comprenderán geometría, biomasa representada, coeficientes, capacidades y condiciones declaradas. El nivel será una variable; la geometría que permite relacionarlo con volumen será un parámetro. Presión y salinidad se tratarán como condiciones parametrizadas del escenario del oxígeno. Los valores numéricos se fijarán en la etapa siguiente.

### 4.7 Perturbaciones y fallos

Se proponen cambios de temperatura ambiental, aportes de agua, cargas de alimentación, fugas e interrupciones del suministro. Cada evento tendrá tipo, instante, duración, magnitud, unidad y componente afectado. El modelo deberá especificar sus efectos; no bastará con mostrar una etiqueta en pantalla.

Los fallos de sensor incluirán pérdida de lectura, sesgo y lectura congelada. Los de actuador incluirán indisponibilidad y reducción de capacidad. La pérdida de una lectura podrá identificarse como dato inválido. Un sesgo plausible o una lectura congelada no se considerarán detectados automáticamente si no existe una regla que los identifique. El historial de inyección de fallos será accesible para evaluación, sin dar esa información oculta al controlador.

Como política inicial propuesta, si una lectura requerida resulta inválida, el coordinador registrará la alarma y finalizará la corrida como fallida antes de calcular nuevas acciones con ella. Esta regla describe una detención del experimento digital. Las políticas alternativas de operación degradada deberán justificarse en la especificación matemática si se incorporan.

### 4.8 Subsistemas y arquitectura conceptual

Se propone una arquitectura modular local. La presentación utilizará Streamlit y Plotly; los servicios de aplicación coordinarán las corridas; el dominio contendrá modelos, sensores y estrategias; la infraestructura gestionará SQLite y los formatos de intercambio. El núcleo de simulación deberá poder ejecutarse sin abrir la interfaz.

La documentación de Streamlit describe la reevaluación del script y el uso de Session State para conservar datos entre esas reevaluaciones (Streamlit, s. f.). Por ello, la interfaz mantendrá el identificador de la corrida y enviará comandos explícitos. Dibujar un gráfico o cambiar una pestaña no deberá avanzar el reloj ni repetir la integración.

Tabla 3

*Módulos propuestos y responsabilidades*

| Módulo | Responsabilidad | Resultado principal |
|---|---|---|
| Configuración y perfiles | Validar especie, unidades y procedencia | Configuración congelada |
| Modelo del agua | Calcular cambios de las variables | Estado actualizado |
| Sensores | Aplicar muestreo y errores de medición | Lecturas con calidad |
| Control | Comparar y decidir según la estrategia | Órdenes y motivos |
| Actuadores | Limitar y transformar órdenes | Acciones efectivas |
| Escenarios | Proveer perturbaciones y fallos repetibles | Eventos del escenario |
| Orquestación | Coordinar reloj, pasos y estados | Resultado de cada avance |
| Alarmas | Clasificar condiciones y fallos detectados | Eventos informativos |
| Persistencia | Guardar ejecuciones y series relacionadas | Historial íntegro |
| Evaluación | Calcular métricas y comparar | Indicadores por variable |
| Interfaz y exportación | Mostrar resultados y generar archivos | Panel y datos exportables |

Nota. Elaboración propia. La clasificación funcional del capítulo I se conserva y se detalla; la exportación y las alarmas quedan identificadas como responsabilidades explícitas.

Figura 1

*Lazo cerrado de la simulación*

[[FIGURE:control_loop.png]]

Nota. Elaboración propia. El observador puede registrar el estado exacto, pero esa conexión no entrega información adicional al controlador. En lazo abierto, el programa temporal sustituye la decisión basada en mediciones.

Figura 2

*Arquitectura modular propuesta*

[[FIGURE:architecture.png]]

Nota. Elaboración propia. Las flechas representan dependencias y coordinación lógica; no añaden relaciones físicas al estanque. Los contratos y estructuras de datos se detallan en PROJECT_SPEC.

### 4.9 Requisitos funcionales

Los identificadores RF01 a RF11 se mantienen desde el inventario inicial. Su detalle se organiza en subrequisitos verificables para evitar que un cambio de versión rompa la trazabilidad.

RF01 comprenderá perfiles configurables y procedencia de valores. RF02 cubrirá estanque, condiciones iniciales, referencias y validación. RF03 exigirá evolución progresiva y control del avance. RF04 distinguirá estado y medición. RF05 representará órdenes, límites y acciones efectivas. RF06 incluirá las estrategias abierta y cerrada.

RF07 incorporará perturbaciones y fallos con efectos registrados. RF08 cubrirá gráficos, alarmas y calidad de los datos. RF09 guardará configuraciones, mediciones, decisiones y eventos. RF10 permitirá comparar corridas equivalentes y calcular indicadores. RF11 identificará versiones y evidencias de reproducción.

La especificación detallada de REQUIREMENTS contiene 33 subrequisitos funcionales, sus condiciones de comprobación y la relación con los módulos. No se marcan como implementados. Los criterios que dependen de ecuaciones o tolerancias tendrán una condición explícita de cierre en la etapa 4.

### 4.10 Requisitos no funcionales

Se establecen requisitos sobre reproducibilidad, consistencia de unidades, integridad de registros, independencia del núcleo, prevención de avances duplicados, claridad de la interfaz, manejo de errores, ejecución local y trazabilidad. Las pruebas deberán distinguir la repetición dentro de un entorno fijado de la comparación entre entornos distintos.

La persistencia se organizará mediante transacciones y relaciones verificables. La documentación de SQLite explica las transacciones y la activación de restricciones de claves foráneas (SQLite, s. f.-a, s. f.-b). Su empleo en este proyecto será una decisión de implementación que Codex deberá demostrar mediante pruebas.

No se fijará una promesa de velocidad sin hardware de referencia ni una carga de datos determinada. El caso de rendimiento, su entorno y el umbral se cerrarán antes del inicio de programación. Esto evita presentar un requisito imposible de comprobar.

### 4.11 Flujo de operación y persistencia

El usuario configurará el escenario y solicitará su validación. Si existen errores, se indicarán los campos afectados y no se creará una corrida ejecutable. Si la configuración es válida, se generará un identificador y se conservará una copia de sus parámetros y versiones.

Durante cada avance autorizado, el coordinador obtendrá mediciones, solicitará decisiones, aplicará la dinámica de los actuadores e integrará el proceso. Se registrarán muestras, órdenes, acciones y eventos con tiempo simulado. El capítulo V fijará el orden temporal exacto y el tratamiento de eventos coincidentes.

La base de datos contendrá ejecuciones, muestras, decisiones, acciones, eventos, métricas y grupos de comparación. El diseño diferenciará el estado guardado para estudiar una corrida de la información necesaria para continuar una pausa dentro de la sesión. La recuperación tras un cierre inesperado permitirá consultar datos parciales, pero no implicará reanudar automáticamente la integración.

La comparación creará dos corridas vinculadas a una misma configuración base y realización exógena. Se identificarán la estrategia y sus parámetros como diferencias autorizadas. El sistema no declarará equivalencia únicamente porque se utilice la misma semilla aleatoria.

### 4.12 Trazabilidad y cierre del diseño

Cada familia de requisitos se vincula con objetivos, conceptos de la asignatura, módulos y evidencias previstas. Por ejemplo, RF04 materializa sensores y variables de medida; RF05 representa actuadores y variables manipuladas; RF06 y RF10 permiten examinar las estrategias y sus respuestas. La matriz completa se conserva en REQUIREMENTS y se complementa con el análisis conceptual de la etapa 1.

La etapa 3 deja definidos los límites funcionales y los contratos de coordinación. Permanecen pendientes las ecuaciones, referencias numéricas, capacidades, tiempos de respuesta, ganancias y criterios cuantitativos. Esas decisiones corresponderán a la etapa 4 y deberán ser coherentes con este diseño antes de entregar la especificación a Codex.

## Capítulo V Modelado matemático

### 5.1 Naturaleza y procedencia del modelo

Se propone el modelo M-AGUA-DEMO-1, orientado a estudiar la evolución de las cinco variables y las decisiones de control. La formulación combina balances simplificados con aproximaciones empíricas. La ecuación de saturación del oxígeno procede del memorando técnico del U.S. Geological Survey (USGS, 2011); los coeficientes de respuesta, las cargas y los umbrales operativos se seleccionan para la demostración académica.

Cada valor se clasifica como bibliográfico, derivado o demostrativo. Un valor derivado puede seleccionarse dentro de un antecedente técnico sin constituir un óptimo universal. Un valor demostrativo permite definir un experimento reproducible, pero no representa una medición de campo ni una recomendación productiva. Las cifras completas y sus metadatos se conservan en MODEL_DEFAULTS.json.

### 5.2 Variables de estado y supuestos

El estado del agua comprende temperatura T, oxígeno disuelto C, pH p, turbidez U y nivel h. Se usan grados Celsius, mg/L, magnitud adimensional, NTU y metros. El tiempo se expresa en segundos. Se añaden cinco estados auxiliares z para representar la respuesta térmica, de aireación, de pH, de filtración y de nivel. Estos auxiliares no amplían las cinco variables de calidad comprometidas.

El estanque se supone rectangular y bien mezclado. El área es constante y el volumen depende del nivel. La biomasa se mantiene fija durante cada corrida. La formulación excluye estratificación, crecimiento individual, enfermedades y química completa del ecosistema. Estas simplificaciones permiten concentrar el análisis en las relaciones de control, aunque limitan la fidelidad de los resultados.

### 5.3 Modelo del volumen y del nivel

Se representan caudales de entrada qin, salida qout, lluvia qr, fuga ql y evaporación qe, en m³/s. Para un área A, el volumen y el nivel se relacionan mediante:

$$
V = A h
$$

$$
dh/dt = (qin + qr − qout − ql − qe)/A
$$

El caso nominal utiliza A=10 m², h=1 m y V=10 m³. La altura geométrica máxima es 1.5 m. El programa finalizará con un fallo explícito si el nivel cruza el dominio matemático adoptado; no reemplazará el valor calculado por el nivel de referencia. La filtración recirculante no implica una descarga de agua por sí misma.

### 5.4 Modelo térmico

El intercambio térmico simplificado depende de la temperatura ambiental Te, del coeficiente H, de las potencias máximas PH y PK y de las intensidades efectivas aH y aK. Se define:

$$
Qnet = H(Te − T) + PH aH − PK aK
$$

$$
dT/dt = Qnet/(ρ cp V) + Jin
$$

$$
Jin = [qin(Tin − T) + qr(Tr − T)]/V
$$

Se adoptan densidad constante de 1000 kg/m³ y calor específico de 4186 J/(kg K) como aproximaciones. Se omiten el calor latente de evaporación, la radiación separada y el calor de equipos auxiliares. Por tanto, esta formulación representa un balance térmico simplificado y no una predicción completa del ambiente piscícola.

### 5.5 Modelo del oxígeno disuelto

El oxígeno cambia por intercambio con el aire, aireación, demanda biológica e intercambio de agua. Se usa Csat para la saturación calculada según temperatura, presión y salinidad. Los términos del modelo son:

$$
dC/dt = (k0 + kA aA)(Csat − C) − R + JC
$$

$$
JC = [qin(Cin − C) + qr(Cr − C) + qe C]/V
$$

La demanda R depende de biomasa, temperatura, alimentación y disponibilidad de oxígeno. Se adopta un factor demostrativo Q10=2 y una función C/(KC+C), con KC=0.5 mg/L, para que la demanda tienda a cero cuando se agota el oxígeno. Su expresión completa y las unidades de sus coeficientes se especifican en MATHEMATICAL_MODEL.

La saturación utiliza las ecuaciones de Benson y Krause recogidas por USGS (2011), con factores de temperatura, salinidad y presión. Se revisaron los coeficientes en la página correspondiente del memorando. Como referencia calculada, a 20 °C, una atmósfera y salinidad cero, la fórmula produce aproximadamente 9.092426 mg/L. Ese valor es un cálculo bibliográfico de referencia y no una medición del proyecto.

La presión inicial de 101325 Pa define un escenario demostrativo a una atmósfera. No equivale a asumir que un estanque real de La Paz tenga esa presión. Antes de aceptar un perfil modificado, se verificará que la referencia de oxígeno y su umbral de apagado sean compatibles con la saturación prevista.

### 5.6 Aproximaciones de pH y turbidez

El pH se representará mediante una ecuación empírica de relajación y acción virtual:

$$
dp/dt = kp(pbg − p) + gp(aB − aD) + dp_ext − gf F
$$

pbg representa una condición de fondo, aB y aD son intensidades normalizadas para incrementar o disminuir pH, F representa alimentación y dp_ext una perturbación externa. Esta ecuación no calcula actividad de hidrógeno, alcalinidad ni mezcla química. Tampoco permite convertir una acción virtual en una dosis real de reactivo. Su utilidad se limita a estudiar cómo un controlador responde a una señal dinámica declarada como aproximada.

La turbidez se describe con un índice empírico que incluye aporte, recambio y reducción por filtración:

$$
dU/dt = JU + sU(1 + F) − (ks + kF aF)U + dU_ext
$$

$$
JU = [qin(Uin − U) + qr(Ur − U)]/V
$$

La mezcla lineal del índice es un supuesto de la simulación. No se presenta como ley general de turbidez real ni se convierte a concentración de sólidos. Se omiten concentración por evaporación y resuspensión. Estas limitaciones permiten interpretar correctamente lo que muestran los gráficos.

### 5.7 Parámetros y referencias de demostración

Tabla 4

*Referencias y bandas operativas seleccionadas para la simulación*

| Perfil | Temperatura objetivo y banda °C | Oxígeno objetivo y banda mg/L |
|---|---|---|
| Tilapia del Nilo | 28.5; 27 a 30 | 6; 5 a 8.5 |
| Trucha arcoíris | 14; 13 a 15 | 9; 8 a 11.5 |
| Carpa común | 25; 23 a 26 | 6; 5 a 8.5 |

Nota. Las temperaturas se seleccionan dentro de antecedentes documentados en la etapa 2. Las referencias de oxígeno y todas las bandas se adoptan como configuración demostrativa, no como límites certificados para cualquier condición de cultivo.

Los tres perfiles utilizan pH objetivo 7.5 y banda de 7 a 8; turbidez objetivo 10 NTU y límite operativo superior de 20 NTU; nivel objetivo 1 m y banda de 0.9 a 1.1 m. El catálogo también distingue límites críticos de alarma y dominios matemáticos. Una alarma crítica no provoca una corrección escondida del agua.

Tabla 5

*Parámetros principales del caso demostrativo*

| Parámetro | Valor | Interpretación |
|---|---|---|
| Área y biomasa | 10 m² y 50 kg | Geometría y carga constantes |
| Potencias térmicas máximas | 20000 W por sentido | Capacidad virtual de calentamiento y enfriamiento |
| Caudales máximos | 0.002 m³/s por sentido | Entrada y salida reguladas |
| Respuesta de actuadores | 30 s | Constante de tiempo de cada grupo |
| Muestreo de control | 60 s | Intervalo entre decisiones |
| Horizonte nominal | 48 h | Duración del escenario principal |
| Presión y salinidad | 101325 Pa y 0 ‰ | Condiciones del caso nominal |

Nota. Elaboración propia. Son valores de configuración y aproximaciones declaradas; no especificaciones de equipos adquiridos ni resultados experimentales.

### 5.8 Sensores y actuadores virtuales

La medición de cada variable se obtiene mediante estado, sesgo y ruido:

$$
y(j,k) = xj(tk) + bj(k) + σj ε(j,k)
$$

Las desviaciones estándar propuestas son 0.03 °C, 0.02 mg/L, 0.01 de pH, 0.1 NTU y 0.002 m. El ruido estándar se limita a tres desviaciones antes de escalarlo. Se guarda la tabla completa de ruido para reutilizarla entre estrategias. Esta limitación afecta a la señal virtual de medición, no al estado del agua.

La pérdida de lectura produce un dato ausente. Un sesgo o una congelación plausibles no se declaran detectados automáticamente. En lazo cerrado, una lectura requerida inválida termina el experimento antes de otra decisión; en lazo abierto, una lectura meramente observacional inválida no modifica la orden programada.

La respuesta de los actuadores se define mediante:

$$
dzj/dt = (vj − zj)/τj
$$

Un estado firmado permite pasar progresivamente entre dos sentidos sin activar acciones opuestas al mismo tiempo. Las disponibilidades de los equipos virtuales multiplican la acción efectiva y permiten representar fallos. Las acciones se registran con límites y tiempos de respuesta; no se asigna directamente la referencia a la variable controlada.

### 5.9 Estrategias de control

Se adopta control cerrado por histéresis. La documentación de MathWorks (s. f.) describe el uso de umbrales diferentes de activación y desactivación para representar este comportamiento. La fuente se utiliza como apoyo conceptual; la aplicación conserva el conjunto tecnológico Python aprobado.

Tabla 6

*Reglas principales del controlador cerrado*

| Grupo | Activación desde reposo | Desactivación |
|---|---|---|
| Temperatura | Desviación superior a 0.3 °C en el sentido correspondiente | Al alcanzar la referencia |
| pH | Desviación superior a 0.15 | Al alcanzar la referencia |
| Nivel | Desviación superior a 0.03 m | Al alcanzar la referencia |
| Aireación | Lectura menor o igual a referencia menos 0.2 mg/L | Lectura mayor o igual a referencia más 0.2 mg/L |
| Filtración | Lectura mayor o igual a 15 NTU | Lectura menor o igual a 10 NTU |

Nota. Se conserva el modo entre umbrales. Las reglas exactas de igualdad, inicialización y cambio de sentido se encuentran en la especificación matemática. No se incorpora acción integral ni se requieren ganancias PID para esta versión.

El lazo abierto de comparación se calibra para el equilibrio nominal, sin ciclo ambiental ni alimentación. Sus comandos constantes compensan las pérdidas y demandas del caso base. Ambos modos reciben el mismo estado inicial y la misma realización externa; la diferencia autorizada reside en la estrategia y sus parámetros. Así, la comparación examina la capacidad de corrección frente a condiciones que cambian, sin partir de una estrategia abierta arbitrariamente inactiva.

### 5.10 Integración y orden temporal

La evolución se resolverá mediante RK45, con tolerancia relativa de 1e−7 y tolerancias absolutas por estado. El paso interno máximo será de 10 s o un sexto del intervalo de control, el menor. La documentación de SciPy explica el uso de tolerancias y métodos para problemas de valor inicial (SciPy, s. f.); sus valores concretos corresponden al diseño propuesto.

Las perturbaciones y los fallos se alinearán con la malla de control y usarán intervalos con inicio incluido y fin excluido. La temperatura ambiental podrá variar de forma continua dentro de cada integración. No se generará nuevo ruido en los pasos internos del integrador.

Al completar 48 h con decisiones cada 60 s, se esperan 2880 intervalos y 2881 muestras, incluida la final. Una muestra se produce una sola vez y se reutiliza al comenzar el siguiente avance. Los registros se confirman mediante transacción; un refresco o un comando repetido no añade integración. Las salidas del dominio se conservarán como fallos con causa y estado de terminación.

### 5.11 Indicadores y criterios de aceptación

La evaluación distinguirá error integrado, tiempo fuera de banda, recuperación, uso de agua, actividad virtual de pH y energía parcial estimada. Los indicadores basados en el estado exacto se separarán de los basados en mediciones. La suma comparativa de errores se normalizará antes de combinar unidades diferentes.

La recuperación se define como la primera muestra en banda seguida de 1800 s consecutivos dentro de ella. Para el escenario S2, se propone que las cinco variables recuperen su banda antes de cuatro horas, permanezcan dentro al menos el 95 % del tramo posterior evaluado y que el error normalizado conjunto del cerrado sea al menos 20 % menor que el del abierto. Son metas de aceptación pendientes de prueba, no resultados de la simulación.

El plan contiene 20 casos, desde soluciones analíticas aisladas hasta fallos, persistencia, repetición y refinamiento numérico. Como ejemplo de comprobación algebraica, aplicar 10000 W durante una hora a 10 m³, sin otros términos, implica un aumento aproximado de 0.860010 °C. Codex deberá contrastar ese resultado con el programa implementado.

El requisito de rendimiento se concreta en una carga de 48 h, registro local y tres repeticiones, con mediana objetivo de hasta 60 s en el equipo de referencia definido. Se registrarán hardware y versiones. Esa meta no acredita velocidad observada ni se trasladará a cualquier computadora.

### 5.12 Limitaciones y validación posterior

La especificación permite construir casos reproducibles y comprobar su consistencia, pero todavía no acredita desempeño de una aplicación. Los límites demostrativos, los coeficientes compartidos entre especies y las aproximaciones de pH y turbidez impiden atribuir precisión productiva a los resultados.

Las pruebas de Codex permitirán verificar la implementación, la integración numérica y el cumplimiento de las metas. Validar el comportamiento frente a un estanque real requeriría datos de campo y calibración adicional. Si una prueba no cumple un criterio, se revisará la formulación o el diseño mediante una nueva versión documentada; no se presentará el fallo como un resultado satisfactorio.

## Capítulo VI Diseño de la implementación

### 6.1 Propósito y herramientas

El diseño de implementación convierte el modelo aprobado en responsabilidades de software verificables. La aplicación se desarrollará en Python; NumPy y SciPy resolverán el cálculo numérico, Streamlit presentará la interfaz, Pandas y Plotly organizarán y mostrarán los resultados, SQLite conservará el historial y Pytest permitirá automatizar las comprobaciones. Esta distribución responde al alcance digital del proyecto y mantiene las tecnologías acordadas.

Las versiones concretas del lenguaje y de las bibliotecas se registrarán cuando Codex prepare y compruebe el entorno. La instalación deberá acompañarse de instrucciones reproducibles y de un archivo de dependencias coherente con las versiones utilizadas. No se presupone compatibilidad con un sistema operativo o equipo que todavía no haya sido probado.

### 6.2 Organización del software

La arquitectura separará presentación, aplicación, dominio e infraestructura. El dominio contendrá las ecuaciones, los sensores virtuales, los actuadores, las estrategias de control y los indicadores. La aplicación coordinará las operaciones de preparar, avanzar, pausar, detener, comparar y exportar. La infraestructura implementará el almacenamiento y los formatos de intercambio. La presentación utilizará los resultados confirmados para mostrar información y recibir comandos.

La separación permitirá ejecutar el núcleo sin abrir la interfaz y probar las reglas de control con entradas conocidas. El modelo no dependerá de Streamlit ni de la base de datos. Los nombres de módulos son una propuesta de organización; Codex documentará las rutas efectivas y cualquier adaptación que conserve las responsabilidades e invariantes aprobadas.

Tabla 7

*Responsabilidades de los grupos de módulos*

| Grupo | Responsabilidad | Resultado verificable |
|---|---|---|
| Configuración y perfiles | Validar, identificar procedencia y congelar valores | Copia completa por corrida |
| Modelo y actuadores | Integrar los diez estados y obtener las ocho acciones efectivas | Evolución y límites registrados |
| Sensores y escenarios | Producir lecturas y aplicar eventos en su instante | Calidad y realización reproducibles |
| Controladores y alarmas | Decidir con información permitida y registrar transiciones | Órdenes y motivos identificables |
| Servicios de simulación y comparación | Coordinar reloj, comandos y base común | Avances únicos y comparación trazable |
| Persistencia y exportación | Guardar lotes atómicos y recuperar historial | Datos íntegros y archivos identificados |
| Interfaz y gráficos | Mostrar configuración, ejecución y resultados | Cinco variables con unidades y estado |

Nota. La tabla describe el diseño previsto. No constituye un inventario de archivos implementados.

### 6.3 Algoritmo de ejecución

La preparación validará el perfil, la geometría, las referencias, los eventos y las condiciones de integración. Después congelará la configuración, generará la tabla de ruido por índice de muestra y establecerá el estado inicial del agua, la respuesta de los actuadores y la memoria del controlador. La misma realización externa se reutilizará al comparar estrategias.

Cada comando de avance identificará la corrida y el paso esperado. El servicio comprobará primero si ya existe un recibo confirmado para ese comando. En tal caso devolverá el resultado guardado. Si el comando es nuevo y corresponde al paso actual, seguirá el orden temporal de la especificación matemática: eventos aplicables, medición disponible, decisión, integración y preparación de la muestra terminal, con reutilización de esa muestra en el siguiente intervalo. La secuencia exacta y el tratamiento de los extremos se fijan en la sección 13 de MATHEMATICAL_MODEL.

La integración mantendrá constante la orden del controlador durante el intervalo y resolverá la respuesta de los actuadores junto con el agua. Una lectura requerida inválida impedirá calcular una nueva decisión cerrada. Un cruce del dominio conservará el instante y el estado de terminación. El servicio confirmará los registros y el recibo mediante una transacción antes de publicar el avance. La consulta de gráficos o el refresco de la página no ejecutarán este algoritmo.

### 6.4 Diseño de la interfaz

La configuración mostrará especie, fase, procedencia de valores, geometría, condiciones iniciales y escenario. Los errores se asociarán al campo que impida iniciar la corrida. Una modificación posterior exigirá preparar otra corrida para conservar la identidad del experimento y su historial.

La ejecución mostrará el tiempo simulado, las cinco mediciones con sus unidades y calidades, el estado de la corrida y los controles de avance, pausa, continuación y detención. Los gráficos distinguirán el estado exacto y la medición cuando se presenten ambos; incluirán referencias, bandas y acciones efectivas. Las pérdidas de lectura aparecerán como ausencias identificadas y no como valores cero.

La comparación permitirá inspeccionar la base compartida, las diferencias autorizadas, los indicadores por variable y las causas de terminación. El historial permitirá reabrir resultados y exportar configuración y series. Las alarmas mostrarán activación y cese; reconocerlas no modificará el agua. Los textos estarán en español y permitirán interpretar el experimento sin conocer la organización interna del código.

### 6.5 Integración y persistencia

SQLite conservará corridas, muestras, decisiones, acciones, eventos, indicadores, comparaciones y recibos de comandos. Las claves foráneas y las restricciones de unicidad impedirán registros huérfanos o repetidos. Cada lote aceptado deberá guardarse completo o revertirse. Si falla la escritura, la aplicación conservará el último paso confirmado y comunicará la causa sin continuar desde un estado parcial.

La pausa conservará en la sesión el estado del proceso, los actuadores, el controlador y los cursores de muestreo y eventos. La primera versión permitirá consultar el historial tras reiniciar, pero no prometerá reanudar automáticamente una ejecución después de cerrar el proceso. Las corridas huérfanas se distinguirán de las completadas mediante la política de propiedad de ejecución definida en la especificación.

### 6.6 Secuencia de construcción y documentación

Codex comenzará por revisar el paquete y preparar el entorno; después implementará configuración, dinámica y pruebas analíticas. Continuará con sensores, actuadores, control y escenarios; incorporará orquestación y persistencia antes de completar la interfaz, las comparaciones y la exportación. Este orden permitirá comprobar el comportamiento del núcleo antes de atribuirlo a la aplicación completa.

El código, las pruebas y los documentos de implementación serán responsabilidad de Codex. La documentación académica conservará su trazabilidad mediante PROJECT_SPEC, REQUIREMENTS, SOURCE_MAP y HANDOFF_WORK. Las desviaciones que cambien ecuaciones, parámetros, criterios o tecnologías se comunicarán antes de aplicarlas. Los ajustes de organización que mantengan el contrato se describirán en la devolución técnica.

## Capítulo VII Pruebas y validación

### 7.1 Propósito y estado de la evaluación

El plan de pruebas comprobará que la implementación reproduzca el modelo aprobado y cumpla los requisitos. La aceptación documental de las etapas anteriores autoriza su construcción, pero todavía no demuestra el funcionamiento del programa. En esta versión no se han recibido resultados de ejecución de Codex; todos los casos de aceptación permanecen pendientes.

La verificación del software distinguirá tres niveles: soluciones analíticas de componentes, integración de los servicios y revisión funcional de la aplicación. Una comprobación algebraica del diseño no sustituye la ejecución del código. La validación frente a un estanque real exigiría datos de campo y calibración adicionales, fuera de las evidencias disponibles.

### 7.2 Casos y escenarios

El plan ACCEPTANCE_PLAN define 20 casos identificados como AC01 a AC20. Incluye validación de configuración y saturación de oxígeno; balances aislados de nivel, temperatura, oxígeno, pH y turbidez; respuesta de actuadores; umbrales de control; equilibrio, repetición, recuperación, perturbaciones, fallos, persistencia, refinamiento e indicadores. Los resultados se evaluarán con las tolerancias específicas de cada caso.

Los escenarios S0 a S9 fijan condiciones comparables. S0 examinará equilibrio nominal; S1, operación variable; S2, recuperación desde condiciones iniciales desviadas; S3 y S4, fuga y carga térmica; S5 a S7, lectura ausente, avería de aireación y sesgo plausible; S8, rendimiento; y S9, capacidad de llenado insuficiente. Sus tiempos y magnitudes se conservarán según la configuración aprobada.

Tabla 8

*Grupos de comprobación y evidencia prevista*

| Casos | Aspecto evaluado | Evidencia requerida |
|---|---|---|
| AC01 a AC08 | Configuración, ecuaciones y actuadores | Entradas, solución esperada, salida y error |
| AC09 a AC13 | Control, repetición y recuperación | Series, decisiones, indicadores y estado final |
| AC14 a AC17 | Fallos, comandos y persistencia | Eventos, causas, recibos y estado de la base |
| AC18 y AC19 | Refinamiento e indicadores | Diferencias numéricas y cálculo de referencia |
| AC20 | Rendimiento y ejecución del núcleo | Entorno, tres duraciones y mediana |

Nota. Los grupos organizan el plan; cada caso conserva su identidad y su criterio. También se revisarán los requisitos de interfaz y exportación que requieran evidencia manual.

### 7.3 Indicadores y criterios de aceptación

La evaluación utilizará error absoluto integrado, tiempo fuera de banda, recuperación sostenida, error normalizado conjunto y uso de actuadores. Los consumos de agua y la energía parcial estimada se presentarán con unidades y alcance. La actividad virtual de pH no se convertirá en dosificación física. Los indicadores identificarán si proceden del estado exacto o de las mediciones.

En S2 se exigirá que cada variable del lazo cerrado comience su ventana de recuperación antes o al cumplirse cuatro horas, permanezca en banda al menos el 95 % del tramo de cuatro a doce horas y permita un error normalizado conjunto al menos 20 % menor que el abierto. Una terminación anticipada no acreditará mejora por reducir el intervalo de cálculo. El criterio de rendimiento se evaluará con el equipo y el protocolo indicados en el plan, sin trasladar automáticamente sus conclusiones a otros equipos.

### 7.4 Registro y revisión de resultados

Cada resultado deberá identificar versión de código, especificación, modelo, entorno, configuración, realización externa, comando de reproducción y evidencia. Se registrarán el valor esperado, el observado, el error o la duración y el estado de aceptación. Los casos no ejecutados, fallidos o no evaluables se distinguirán de los aprobados.

Codex entregará IMPLEMENTATION con los módulos reales, TEST_RESULTS con las comprobaciones y HANDOFF_CODEX con diferencias y limitaciones. La revisión académica contrastará esos archivos con los 33 subrequisitos funcionales y los 10 no funcionales. Si un criterio falla, se documentará la causa y la corrección o propuesta de revisión; no se alterará silenciosamente el criterio para aparentar cumplimiento.

### 7.5 Resultados pendientes y continuidad del informe

No se incorporan gráficas de resultados, tablas de desempeño observado ni conclusiones sobre superioridad del controlador, porque la implementación y sus pruebas todavía no están acreditadas. El capítulo VIII se elaborará después de revisar las evidencias. Las conclusiones finales deberán responder a los objetivos y distinguir cumplimiento del modelo académico, limitaciones numéricas y ausencia de validación de campo.


## Referencias

Adcock, R. (s. f.). *Systems thinking*. En *Guide to the Systems Engineering Body of Knowledge*. Recuperado el 14 de octubre de 2026, de https://sebokwiki.org/wiki/Systems_Thinking

Anderson, C. W. (2005). *Turbidity* (Techniques of Water-Resources Investigations, Book 9, Chapter A6, Section 6.7). U.S. Geological Survey. https://doi.org/10.3133/twri09A6.7

Åström, K. J., & Murray, R. M. (s. f.-a). *Feedback principles*. FBSwiki. Recuperado el 14 de octubre de 2026, de https://www.fbswiki.org/wiki/index.php/Feedback_Principles

Åström, K. J., & Murray, R. M. (s. f.-b). *System modeling*. FBSwiki. Recuperado el 14 de octubre de 2026, de https://www.fbswiki.org/wiki/index.php/System_Modeling

International Council on Systems Engineering. (s. f.). *About systems engineering*. https://www.incose.org/About%20Systems%20Engineering/

International Union of Pure and Applied Chemistry. (s. f.). pH. En *Compendium of Chemical Terminology*. Recuperado el 14 de octubre de 2026, de https://doi.org/10.1351/goldbook.P04524

*Introducción a la Ingeniería de Sistemas*. (s. f.). [Material de asignatura, capítulo 1]. Documento proporcionado por el estudiante.

MathWorks. (s. f.). *Relay*. Recuperado el 14 de octubre de 2026, de https://www.mathworks.com/help/simulink/slref/relay.html

Organización de las Naciones Unidas para la Alimentación y la Agricultura. (2009a). *Cyprinus carpio*. En *Cultured aquatic species fact sheets*. https://www.fao.org/fishery/docs/CDrom/aquaculture/I1129m/file/en/en_commoncarp.htm

Organización de las Naciones Unidas para la Alimentación y la Agricultura. (2009b). *Oreochromis niloticus*. En *Cultured aquatic species fact sheets*. https://www.fao.org/fishery/docs/CDrom/aquaculture/I1129m/file/en/en_niletilapia.htm

Organización de las Naciones Unidas para la Alimentación y la Agricultura. (s. f.). *Improving pond water quality*. https://www.fao.org/fishery/docs/CDrom/FAO_Training/FAO_Training/General/x6709e/x6709e02.htm

SciPy. (s. f.). *scipy.integrate.solve_ivp*. En *SciPy manual*. Recuperado el 14 de octubre de 2026, de https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html

SQLite. (s. f.-a). *SQLite foreign key support*. https://www.sqlite.org/foreignkeys.html

SQLite. (s. f.-b). *Transaction*. https://www.sqlite.org/lang_transaction.html

Streamlit. (s. f.). *Add statefulness to apps*. Recuperado el 14 de octubre de 2026, de https://docs.streamlit.io/develop/concepts/architecture/session-state

U.S. Geological Survey. (2011, 13 de julio). *Change to solubility equations for oxygen in water* (Office of Water Quality Technical Memorandum 2011.03). https://water.usgs.gov/water-resources/memos/documents/WQ.2011.03.pdf

U.S. Geological Survey. (2022, 7 de noviembre). *DOTABLES*. https://www.usgs.gov/tools/dotables

U.S. Geological Survey. (2026, 24 de agosto). *Turbidity and water*. https://www.usgs.gov/water-science-school/science/turbidity-and-water

Woynarovich, A., Hoitsy, G., & Moth-Poulsen, T. (2011). *Small-scale rainbow trout farming* (FAO Fisheries and Aquaculture Technical Paper No. 561). Food and Agriculture Organization of the United Nations. https://www.fao.org/4/i2125e/i2125e.pdf
