# Revisión de control y presentación — 19 de octubre de 2026

Se contrastaron la especificación SPC-AGUA-001 0.5.0, el modelo M-AGUA-DEMO-1 1.0.0, MODEL_DEFAULTS.json y ACCEPTANCE_PLAN.md con la implementación de esta carpeta. Se ejecutó la matriz numérica completa y las comprobaciones de interfaz, almacenamiento y presentación indicadas abajo.

## Resultado

**107 casos de prueba únicos aprobados, sin fallos finales.** Se cuentan una sola vez los casos repetidos entre ejecuciones.

| Ejecución | Casos | Fallos | Duración (s) |
|---|---:|---:|---:|
| numerical-tests.xml | 57 | 0 | 760.53 |
| interface-tests.xml | 47 | 0 | 63.81 |
| repository-integration-tests.xml | 14 | 0 | 14.55 |

La suite numérica comenzó antes de la corrección de detección de procesos de Windows y de los últimos ajustes visuales. Las ecuaciones, umbrales, escenarios y criterios de aceptación no cambiaron. Tras corregir el almacenamiento se volvió a ejecutar la integración con la interfaz y las pruebas específicas de propietario. El último ajuste de altura del marco del estanque se verificó visualmente en el navegador.

## Procedimientos contrastados

| Plan | Resultado observado |
|---|---|
| AC01–AC08 | Pasan la validación y las comprobaciones aisladas de saturación, caudales, calor, oxígeno, pH, turbidez y respuesta de equipos con las tolerancias originales. |
| AC09 | Pasan los umbrales exactos, las igualdades y la memoria de histéresis. El abierto conserva sus órdenes aunque cambien las lecturas. |
| AC10 | Equilibrio nominal aprobado en los tres perfiles. |
| AC11 | Ambas estrategias completan S1 para los tres perfiles con 2881 muestras y 2880 decisiones; las repeticiones cumplen la tolerancia de reproducción. |
| AC12 | Recuperación S2 aprobada en las tres especies; detalle debajo. |
| AC13 | Se registran efectos y alarmas de fuga S3 y carga térmica S4. El cerrado completa sin salir del dominio; el nivel se recupera dentro del plazo exigido tras S3. |
| AC14 | S5 cerrado se detiene exactamente a 7200 s por lectura ausente y no emite una decisión nueva en ese instante. El abierto continúa. S7 mantiene el sesgo plausible sin inventar su detección. |
| AC15 | La avería S6 deja la acción efectiva del aireador en cero durante el periodo programado. S9 termina por cruce del dominio del nivel, sin recortar el agua al objetivo. |
| AC16–AC17 | Pausa, continuación, consultas y reintentos preservan los datos. Se verifica reversión del lote ante fallo de escritura, exportación e identificación de procesos cerrados. |
| AC18–AC19 | Pasan el refinamiento numérico y las fórmulas de indicadores, incluida la comprobación energética aislada. |
| AC20 | Pasan la ejecución del núcleo sin Streamlit/Plotly y las comprobaciones con conexiones de red denegadas. El rendimiento se registra como medición descriptiva, sin acreditar el equipo de referencia. |

## Recuperación S2

Se conservó el mismo estado inicial, respuesta inicial de equipos y ruido en ambas estrategias. El indicador J es el promedio del error absoluto integrado, normalizado por variable y duración; no representa producción ni supervivencia.

| Perfil | J cerrado / J abierto | Inicio de recuperación de T, O₂, pH, turbidez y nivel (min) | Tiempo en banda entre horas 4 y 12 |
|---|---:|---|---|
| Tilapia | 0.1526 | 10, 5, 32, 46, 5 | 100%, 100%, 100%, 100%, 100% |
| Trucha | 0.1450 | 25, 5, 32, 46, 5 | 100%, 100%, 100%, 100%, 100% |
| Carpa | 0.1531 | 0, 4, 32, 46, 5 | 100%, 100%, 100%, 100%, 100% |

Recuperación significa la primera muestra en banda seguida de 30 minutos consecutivos dentro de ella. En la carpa, la temperatura inicial ya pertenece a la banda; por eso su inicio es 0 minutos.

## Correcciones y presentación

- Ejecución y evolución reúne el estanque, sus lecturas, alarmas, actividad de los equipos y seis gráficas. Se retiró la pestaña separada de vista del estanque. Los resultados y registros detallados permanecen en el historial.
- La demostración solicita un intervalo cada tres segundos de pantalla. El paso manual sigue disponible. Una prueba verifica inicio, avance, pausa sin cambios al consultar, reanudación y detención. La simulación no es un proceso en tiempo real.
- Los ejes temporales usan horas/minutos/segundos; el objetivo es una línea amarilla punteada. La intensidad de los equipos se expresa como porcentaje.
- La presentación de turbidez respeta el criterio unilateral del modelo: estar por debajo de la banda inferior no constituye una desviación penalizada. Se verificaron tarjetas y franja de la gráfica frente al criterio de aceptación.
- En Windows, la detección de propietarios usaba `/proc`, una ruta de Linux. Se cambió por una consulta de identidad y tiempos del proceso a Windows, sin enviar señales ni terminar procesos. Se probaron un propietario vivo, un segundo lector, una sesión pausada, un proceso cerrado, reutilización de identificador y falta de permisos de consulta.
- Se evitó enviar un valor nulo al visor JSON cuando aún no existe estado de terminación. La comprobación del navegador no registró errores nuevos después de corregirlo; se repitieron los tres recorridos de interfaz (`final-ui-tests.xml`).
- La configuración conserva sus campos y distribución previos a esta revisión.
- La revisión en navegador comprobó el estanque 3D, el avance automático, la pausa y las curvas de recuperación. La evidencia visual y el estado confirmado se guardan en el directorio de esta revisión.

## Rendimiento y límites

S8: 22.28, 26.05, 26.48 s; mediana **26.05 s**. La meta documental es 60 s. Esta ejecución no certifica RNF10: no se acreditaron el almacenamiento SSD y todas las condiciones de carga del equipo de referencia.

Las pruebas confirman el comportamiento del software dentro del modelo académico. No constituyen validación de campo. No se simulan crecimiento, reproducción, enfermedades, amoníaco ni química completa. La biomasa es fija y los parámetros son demostrativos. El controlador no recibe el estado exacto ni el calendario oculto de fallos: decide usando las lecturas y su memoria. Las animaciones ilustran registros guardados y no producen el control.

## Reproducción

Desde la raíz del proyecto en PowerShell:

```powershell
$env:PISCICULTURA_EVIDENCE_DIR='evidence/revision_control_2026-10-19'
.\.venv\Scripts\python.exe -m pytest tests/test_core.py tests/test_functional.py tests/test_acceptance.py -q --junitxml=evidence/revision_control_2026-10-19/numerical-tests.xml
.\.venv\Scripts\python.exe -m pytest tests/test_presentation_control.py tests/test_ui.py tests/test_tank_view.py tests/test_pr1_revision.py -q --junitxml=evidence/revision_control_2026-10-19/interface-tests.xml
.\.venv\Scripts\python.exe -m pytest tests/test_functional.py tests/test_repository_owner.py tests/test_ui.py -q --junitxml=evidence/revision_control_2026-10-19/repository-integration-tests.xml
```

Las bases de pruebas están aisladas de `work/piscicultura.sqlite`. Las exportaciones, la realización de ruido, los resultados por caso y el entorno están en `evidence/revision_control_2026-10-19/`. Se mantuvieron los informes históricos; este archivo registra la revisión actual.
