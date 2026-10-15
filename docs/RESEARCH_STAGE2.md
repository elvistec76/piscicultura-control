# Investigación técnica de la calidad del agua

Versión 0.2.0 · 14 de octubre de 2026 · Etapa 2 aprobada; hallazgos conservados con su contexto

## Criterios de lectura

Se consultaron fuentes de FAO para piscicultura, USGS para mediciones y solubilidad, INCOSE y SEBoK para el enfoque sistémico, y páginas de los autores de Feedback Systems para control y modelado. Los valores siguientes son hallazgos bibliográficos, no parámetros aprobados del programa. Un intervalo de supervivencia, uno de crecimiento y uno de reproducción responden a preguntas diferentes.

Las especies propuestas son tilapia del Nilo, Oreochromis niloticus; trucha arcoíris, Oncorhynchus mykiss; y carpa común, Cyprinus carpio. Para la primera simulación se recomienda estudiar peces en crecimiento o engorde y excluir incubación y reproducción. Esta delimitación adicional es una propuesta para aprobación, no una decisión impuesta por las fuentes.

## Registro de valores y su contexto

| ID | Especie y variable | Hallazgo | Contexto y localizador | Uso permitido |
|---|---|---|---|---|
| B01 | Tilapia del Nilo, temperatura | 27 a 30 °C | F02, sección 2.4, tabla 1: intervalo térmico óptimo para adultos; nombre antiguo Tilapia nilotica | Candidato para orientar un perfil; no define alarma ni consigna |
| B02 | Tilapia del Nilo, temperatura | 31 a 36 °C | F04, Habitat and biology: preferencia térmica | Registrar por separado; no sustituye automáticamente B01 |
| B03 | Trucha arcoíris, temperatura | 13 a 15 °C | F05, sección 4.2, p. impresa 14: aprovechamiento del alimento y crecimiento | Candidato asociado al criterio de la fuente |
| B04 | Trucha arcoíris, temperatura | 15 a 17 °C | F02, sección 2.4, tabla 1: óptimo térmico para adultos | Alternativa contextual; no promediar con B03 |
| B05 | Trucha arcoíris, oxígeno | Cercano al 100 % de saturación | F05, sección 4.3, p. impresa 14 | Preferencia técnica; convertir a mg/L requiere condiciones del agua |
| B06 | Trucha arcoíris, oxígeno | Aproximadamente 4 a 5 mg/L como concentración baja aceptable para edades mayores | F05, sección 4.3, p. impresa 14 | No usar como objetivo óptimo |
| B07 | Trucha arcoíris, pH | 6.5 a 8 para embriones y alevines tempranos | F05, sección 4.1, p. impresa 13 | No transferir al perfil de engorde; pendiente valor apropiado a esa etapa |
| B08 | Carpa común, temperatura | 23 a 30 °C | F06, Habitat and biology: mejor crecimiento | Candidato condicionado al criterio de la fuente |
| B09 | Carpa común, temperatura | 23 a 26 °C | F02, sección 2.4, tabla 1: óptimo térmico para adultos | Alternativa contextual; conservar ambas fuentes |
| B10 | Carpa común, pH | 6.5 a 9.0 | F06, Habitat and biology: intervalo óptimo informado | Candidato bibliográfico; no obliga a usar todo el intervalo como banda de control |
| B11 | Carpa común, oxígeno | Supervivencia descrita a 0.3 a 0.5 mg/L | F06, Habitat and biology | Excluir de consignas de operación; dato de tolerancia |

Las páginas impresas 13 y 14 de F05 corresponden a las páginas 23 y 24 del archivo PDF al contar desde 1. Se verificaron mediante la extracción de texto con localizadores del documento; no se interpretaron gráficas para deducir nuevos límites.

## Cobertura de los cinco parámetros por especie

| Variable | Tilapia del Nilo | Trucha arcoíris | Carpa común |
|---|---|---|---|
| Temperatura | Datos B01 y B02 con criterios diferentes | Datos B03 y B04 con criterios diferentes | Datos B08 y B09 con criterios diferentes |
| Oxígeno | Consigna de engorde no fijada por las fuentes revisadas | Datos B05 y B06; falta traducir saturación a concentración del escenario | B11 no es objetivo productivo; consigna pendiente |
| pH | Perfil de engorde pendiente de fuente específica o valor demostrativo | B07 pertenece a otra etapa; perfil de engorde pendiente | B10 disponible como antecedente técnico |
| Turbidez | Sin umbral en NTU adoptable del corpus revisado | Sin umbral en NTU adoptable del corpus revisado | Sin umbral en NTU adoptable del corpus revisado |
| Nivel | Depende de geometría y operación del estanque | Depende de geometría y operación del estanque | Depende de geometría y operación del estanque |

Esta tabla expresa la cobertura de la investigación realizada; no demuestra inexistencia de otras publicaciones. La especificación deberá completar los pendientes o declarar expresamente valores demostrativos.

## Implicaciones para el diseño posterior

1. Separar cuatro tipos de dato: condición bibliográfica, referencia de control, banda de operación y umbral de alarma. No asignarles el mismo número por conveniencia.
2. Mantener un perfil con identidad de especie, fase de cultivo, sistema representado, fuentes y fecha de revisión. No afirmar que simula todo el ciclo de vida.
3. Incorporar presión atmosférica en la evaluación del oxígeno, o declarar una presión fija. F07 contempla temperatura, presión y salinidad. No asumir condiciones de nivel del mar si después se representa un escenario de altura.
4. Definir salinidad fija para agua dulce y documentar su valor; no agregarla como sexta variable controlada sin revisar el alcance.
5. Distinguir turbidez óptica de concentración de sólidos y profundidad de transparencia. F08 y F09 orientan la medición; no aportan un límite piscícola universal. No convertir centímetros de Secchi a NTU por una regla inventada.
6. Derivar la banda de nivel de geometría, volumen útil y límites operativos propuestos; no presentarla como un rango fisiológico propio del pez.
7. Evitar representar pH como concentración lineal. F13 lo define mediante actividad de iones hidrógeno; una ecuación empírica deberá declararse y no se usará para calcular dosificaciones reales.
8. Evaluar corrección y oscilación antes de afirmar superioridad del controlador. La consulta de F10 no sustituye pruebas del diseño particular.

Estas implicaciones son inferencias de ingeniería para este proyecto. Las ecuaciones, los algoritmos y los valores demostrativos se decidirán en la etapa 4.

## Límites de la investigación

No se obtuvieron datos de campo, coeficientes calibrados ni fichas de equipos físicos. La fuente F02 se mantiene sin fecha porque no se verificó la portada de la obra contenedora. F13 se verificó a través de su definición indexada y DOI; el acceso directo fue bloqueado. Se utiliza únicamente su definición de pH y no información adicional de la página.

El catálogo permite redactar el marco teórico e identificar decisiones. No es todavía una tabla de configuración ejecutable. Los intervalos distintos permanecen visibles para que la selección futura tenga una justificación.

Nota de avance: el estudiante aprobó las especies concretas y crecimiento o engorde; la aprobación no convierte los antecedentes del catálogo en consignas numéricas.
