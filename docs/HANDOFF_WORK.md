# Entrega formal de especificación a Codex

SPC-AGUA-001 · Documentación 0.5.0 · Modelo M-AGUA-DEMO-1 1.0.0 · 14 de octubre de 2026 · Propietario Work.

## Estado y autorización

Etapas 1 a 4 aprobadas por el estudiante. La etapa 4 se aprobó mediante «aprobado», en respuesta al informe I–V y al paquete 0.4.0. La etapa 5 entrega esta base para iniciar la programación en el entorno de Codex elegido por el estudiante. El paquete está preparado; no se afirma recepción por Codex, sincronización con GitHub, implementación ni ejecución de pruebas. Capítulos VI y VII describen diseño y plan; se entregan para consulta y revisión. La etapa 6 continúa pendiente de evidencias.

La versión documental 0.5.0 registra la aprobación y organiza la entrega. El modelo cambia de etiqueta 1.0.0-proposed a 1.0.0 por su aprobación. No se modifican ecuaciones, valores de parámetros, perfiles ni tolerancias de 0.4.0. Esa aprobación es académica y no valida condiciones productivas.

## Cómo recibir el paquete

1. Abrir el repositorio o proyecto que el estudiante haya seleccionado. Leer las instrucciones locales aplicables y revisar archivos y cambios existentes antes de editar.
2. Extraer el ZIP e incorporar el contenido de piscicultura-control en la raíz correcta del proyecto. Comparar cada coincidencia y preservar el código o los cambios ajenos. No crear una carpeta de proyecto anidada por accidente.
3. Leer README, este archivo, PROJECT_SPEC, REQUIREMENTS, MATHEMATICAL_MODEL, MODEL_DEFAULTS.json y ACCEPTANCE_PLAN. Consultar REPORT_APA y SOURCE_MAP para contexto y procedencia. ANALYSIS_STAGE1 y RESEARCH_STAGE2 son antecedentes históricos; no sustituyen la especificación vigente.
4. Verificar concordancia del identificador, las versiones y el alcance. Ante diferencias entre este paquete y trabajo ya implementado, describirlas antes de cambiar el modelo. No mezclar documentos de distintas versiones sin registro.

No se ha proporcionado aquí URL ni acceso al repositorio; no existe sincronización automática con otro chat. Mantener la visibilidad elegida por el estudiante. No publicar, cambiar visibilidad ni desplegar por inferencia. Un repositorio existente puede contener una implementación previa: inspeccionarla y adaptarla sin destruir trabajo.

## Precedencia y propietarios

MATHEMATICAL_MODEL fija ecuaciones, unidades y secuencia; MODEL_DEFAULTS.json fija valores y metadatos; ACCEPTANCE_PLAN fija procedimientos y criterios. PROJECT_SPEC y REQUIREMENTS definen alcance, contratos y obligaciones. Si existe contradicción, reportarla para resolución documental antes de implementar el aspecto afectado. No escoger una variante silenciosamente. Avanzar en trabajo independiente del conflicto.

Work mantiene documentación académica, especificación, requisitos, fuentes, modelo, configuración de referencia, plan de aceptación y este archivo. Codex mantiene código, pruebas y docs/IMPLEMENTATION.md, docs/TEST_RESULTS.md y docs/HANDOFF_CODEX.md. Esos tres documentos no se incluyen con resultados supuestos. Codex registrará propuestas de cambio para Work; no reescribirá ecuaciones o criterios aprobados para ocultar un fallo.

## Invariantes que debe conservar la implementación

- Cinco salidas T,C,p,U,h; diez estados internos con cinco respuestas auxiliares. Biomasa fija y un estanque por corrida. Tres especies en crecimiento o engorde.
- Python, NumPy, SciPy, Streamlit, Pandas, Plotly, SQLite y Pytest. Verificar entorno y dependencias antes de fijar versiones; registrar las efectivamente usadas. No copiar archivos de instalación de otro chat como si estuvieran comprobados.
- Histéresis muestreada y lazo abierto constante calibrado. Mismo estado inicial del agua y actuadores y misma realización externa para ambas estrategias. No usar todos los actuadores apagados como sustituto del abierto aprobado.
- Controladores reciben lecturas y calidad; no reciben el estado exacto ni el calendario oculto de fallos. Auditoría e inyección no equivalen a detección.
- No asignar x=r, recortar estados para aparentar control ni consumir ruido en el integrador. Preservar la tabla de ruido, eventos por intervalos, cursores y muestra terminal conforme a sección 13.
- Integración RK45, límites de dominio, umbrales, tolerancias y criterios según archivos aprobados. 48 h a 60 s completas: 2881 muestras y 2880 decisiones.
- Comandos idempotentes y transacciones: avanzar solo por comando; renderizar no avanza. Reintentar no duplica registros. Un fallo de escritura no confirma estado parcial.
- Resultados parciales y fallos identificables; historial consultable. Pausa dentro de sesión y lectura de historial tras reiniciar no implican recuperación automática de una corrida cerrada.
- pH, turbidez, capacidades y coeficientes demostrativos se rotulan correctamente. No convertir valores a dosificación real ni presentar rangos como certificados.

## Hitos de construcción y evidencia

| Hito | Trabajo | Evidencia para continuar |
|---|---|---|
| H1 Entorno y contratos | Revisar proyecto, definir instalación reproducible y tipos de datos | Versiones efectivas, comandos de instalación y configuración validada |
| H2 Núcleo matemático | Integrar modelo y respuestas; construir pruebas aisladas | AC01 a AC08 con errores y tolerancias registrados |
| H3 Control y tiempo | Sensores, escenarios, histéresis, abierto y orden de eventos | AC09 a AC15; S0, S1 y S2 en perfiles indicados; fallos explícitos |
| H4 Persistencia | Transacciones, comandos, historial y exportación | AC16 y AC17; duplicados y reversión comprobados |
| H5 Aplicación y evaluación | Interfaz en español, comparación, indicadores y rendimiento | AC18 a AC20 y revisión completa de RF/RNF; instrucciones de uso |

Los hitos son orden de desarrollo, no etapas que requieran confirmaciones rutinarias. Una vez que el estudiante entregue el paquete a Codex para implementar, avanzar dentro del alcance autorizado. Una dificultad en un criterio no obliga a abandonar todo el trabajo: conservar las evidencias, corregir implementación y reportar cualquier modificación sustantiva propuesta.

Los comandos de instalación, ejecución y pruebas definitivos se fijarán al conocer la estructura real; Codex debe proporcionarlos y ejecutarlos. No se presentan aquí comandos para un app.py ni una estructura de paquetes inexistentes como si funcionaran. Las pruebas deberán ejercitar el código de producción; no replicar una fórmula únicamente dentro del test y atribuir ese resultado a la aplicación.

## Devolución obligatoria para la etapa 6

- IMPLEMENTATION: estructura real y responsabilidades, esquema de datos, secuencia temporal, dependencias y comandos de instalación, ejecución, prueba y reproducción.
- TEST_RESULTS: AC01 a AC20 individualmente, 33 RF y 10 RNF vinculados a evidencia suficiente. Para cada comprobación: versión, configuración, esperado, observado, error o duración, comando o pasos y estado. Registrar también fallos, omisiones y casos no evaluables; la aprobación de un caso no acredita toda una familia.
- HANDOFF_CODEX: resumen del comportamiento implementado, diferencias frente a 0.5.0, problemas pendientes, propuestas para Work y ubicación de evidencias. Incluir commit si existe o identificación reproducible del código entregado.
- Corridas y exportaciones de referencia con configuración congelada, tabla de ruido, eventos y métricas. Entregar un medio accesible de consulta; no asumir que Work ve el disco o el chat de Codex. Las imágenes de interfaz pueden apoyar la revisión, pero no sustituyen datos y pruebas.

La revisión académica posterior completará resultados y capítulo VIII a partir de esas evidencias. No existe todavía fecha de finalización ni desempeño observado. Pendientes administrativos del informe: docente y paralelo; confirmar fecha de entrega si cambia. El nombre del autor figura en la portada consolidada.
