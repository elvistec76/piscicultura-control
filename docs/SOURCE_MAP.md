# Fuentes y trazabilidad académica

Versión 0.5.0 · Consulta web 14 de octubre de 2026

| ID | Fuente | Localizador revisado | Aporte y límites |
|---|---|---|---|
| F01 | Documento adjunto Introducción a la Ingeniería de Sistemas | Capítulo 1, Control del Sistema y Estrategia de Control | Definiciones; autor y año pendientes; sin rangos piscícolas |
| F02 | FAO, Improving Pond Water Quality | Secciones 2.0 a 2.4, tabla 1 | Calidad y rangos térmicos de adultos; Secchi no equivale a NTU |
| F03 | FAO, Aeration and Oxygenation in Aquaculture | Secciones 1.1 y 1.2.6 | Consulta de apoyo; sin extracción de coeficientes; metadatos completos pendientes |
| F04 | FAO, 2009b, Oreochromis niloticus | Cabecera y Habitat and biology | Especie y preferencia; texto de J. E. Rakocy |
| F05 | Woynarovich, Hoitsy y Moth-Poulsen, 2011 | Portada y secciones 4.1 a 4.3, pp. impresas 13 y 14 | Trucha y etapas; no extrapolar embriones a engorde |
| F06 | FAO, 2009a, Cyprinus carpio | Cabecera y Habitat and biology | Crecimiento, pH y tolerancia; texto de A. Peteri |
| F07 | USGS, 2022, DOTABLES | Descripción y dominios | Solubilidad, temperatura, presión y salinidad |
| F08 | Anderson, 2005, Turbidity | Registro oficial, DOI y resumen | Medición y reporte; sin límites piscícolas |
| F09 | USGS, 2026, Turbidity and Water | Descripción y NTU | Unidad de turbidez; fecha 24 de agosto de 2026 verificada |
| F10 | Åström y Murray, Feedback Principles | Introducción e índice | Propiedades de retroalimentación; no desempeño del proyecto |
| F11 | Åström y Murray, System Modeling | Introducción y Chapter Summary | Estados y elección del modelo |
| F12 | Adcock, Systems Thinking, SEBoK | Autor, introducción y referencias | Pensamiento sistémico; no citar libros no consultados |
| F13 | IUPAC, pH | Definición indexada y DOI | Escala logarítmica y actividad; acceso directo bloqueado |
| F14 | SciPy, solve_ivp | Descripción, parámetros y tolerancias | Integración; no valida ecuaciones ni fija versión instalada |
| F15 | INCOSE, About Systems Engineering | Definición formal | Integración y ciclo de vida |

## Direcciones

- F02: https://www.fao.org/fishery/docs/CDrom/FAO_Training/FAO_Training/General/x6709e/x6709e02.htm
- F03: https://www.fao.org/4/x5744e/x5744e0m.htm
- F04: https://www.fao.org/fishery/docs/CDrom/aquaculture/I1129m/file/en/en_niletilapia.htm
- F05: https://www.fao.org/4/i2125e/i2125e.pdf
- F06: https://www.fao.org/fishery/docs/CDrom/aquaculture/I1129m/file/en/en_commoncarp.htm
- F07: https://www.usgs.gov/tools/dotables
- F08: https://www.usgs.gov/publications/chapter-a6-section-67-turbidity y https://doi.org/10.3133/twri09A6.7
- F09: https://www.usgs.gov/water-science-school/science/turbidity-and-water
- F10: https://www.fbswiki.org/wiki/index.php/Feedback_Principles
- F11: https://www.fbswiki.org/wiki/index.php/System_Modeling
- F12: https://sebokwiki.org/wiki/Systems_Thinking
- F13: https://goldbook.iupac.org/terms/view/P04524 y https://goldbook.iupac.org/terms/view/P04524/plain
- F14: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
- F15: https://www.incose.org/About%20Systems%20Engineering/

## Evidencia y metadatos

F04 y F06 se citan con autor corporativo y año de su identificación bibliográfica; se conserva la autoría individual como metadato. F05 confirma autores y año en la portada. F08 y F07 tienen fecha en registros oficiales. F10 y F11 se citan como páginas de autores sin fecha, no como una edición completa cuyo PDF no se logró consultar.

F02 conserva fecha pendiente; no se inventa año de la obra contenedora. F13 solo se utiliza para la definición indexada verificada; su lectura directa fue bloqueada.

Cada valor futuro deberá registrar fuente, localizador, especie, etapa, condiciones, unidad y uso. RESEARCH_STAGE2 no es configuración aprobada. Los valores demostrativos y las aproximaciones se etiquetarán.

## Fuentes de arquitectura añadidas en etapa 3

- F16: Streamlit, Add statefulness to apps. https://docs.streamlit.io/develop/concepts/architecture/session-state. Apartados What is State e inicialización. Aporta reevaluación y estado de sesión; no demuestra idempotencia del programa propuesto.
- F17: SQLite, SQLite Foreign Key Support. https://www.sqlite.org/foreignkeys.html. Apartado Enabling Foreign Key Support. Aporta activación por conexión; no implica que ya esté implementada.
- F18: SQLite, Transaction. https://www.sqlite.org/lang_transaction.html. Descripción de transacciones y COMMIT/ROLLBACK. Aporta base técnica para persistencia; los contratos y tablas son diseño propio.

Las tablas y figuras del capítulo IV son elaboración propia. No se reutilizan imágenes de terceros ni se presentan capturas de una implementación. Las reglas, contratos y requisitos corresponden al diseño aprobado en etapas 3 y 4.

## Fuentes matemáticas añadidas en etapa 4

- F19: U.S. Geological Survey, 13 de julio de 2011, Change to solubility equations for oxygen in water, Office of Water Quality Technical Memorandum 2011.03. https://water.usgs.gov/water-resources/memos/documents/WQ.2011.03.pdf. Portada con fecha verificada y anexo, ecuaciones 1 y 7 a 11. Se revisó visualmente la página PDF 6 para coeficientes y factores. Respalda únicamente la saturación y sus factores, no todo el modelo piscícola.
- F20: MathWorks, Relay. https://www.mathworks.com/help/simulink/slref/relay.html. Apartados Description y Switch on/off point. Respalda el principio de histéresis; los valores y las igualdades de esta simulación son propios. No supone adoptar Simulink ni cambiar tecnologías.
- F14, SciPy solve_ivp: se revisó nuevamente el manual para integración RK45 y tolerancias; los valores concretos son decisiones del proyecto.

La especificación matemática usa balances simplificados de elaboración propia y aproximaciones empíricas declaradas para pH y turbidez. Los parámetros numéricos se clasifican en MODEL_DEFAULTS; las referencias térmicas derivan de antecedentes B01, B03 y B09. Los límites de oxígeno, pH, turbidez y nivel y todos los umbrales de alarma se etiquetan como demostrativos. No se presenta una dosificación química real ni una ecuación calibrada de turbidez.

## Evidencias de implementación incorporadas en revisión R1

La edición académica 0.6.0 cita la devolución, implementación y resultados de Codex de la entrega 0.1.0, commit 41ec9f2d21edb21499c14437b3d00dd9e135e0d2. Se verifican frente a XML, código y exportaciones del ZIP recibido. No son bibliografía de validación física ni mediciones de una piscigranja. Las nuevas comprobaciones de Work se conservan separadas en el paquete de revisión.
