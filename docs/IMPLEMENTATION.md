# Implementación técnica

Responsable: Codex. Especificación SPC-AGUA-001 0.5.0; modelo M-AGUA-DEMO-1 1.0.0; software 0.1.0. Fecha local de ejecución: 14 de octubre de 2026 (America/La_Paz; los registros de máquina usan UTC). Los resultados de pruebas se detallan en TEST_RESULTS.md.

## Recepción y alcance

Se inspeccionó `/workspace/piscicultura-control` antes de escribir. No había AGENTS.md aplicable, código previo ni cambios locales pendientes. El checkout inicial `1e1747a` contenía solo README y una especificación preliminar. `git fetch origin` encontró `f69f4d8`, que incorpora la documentación 0.5.0 y los diagramas. Se creó `codex/implementacion-spc-agua-0.5.0` directamente desde esa revisión, sin carpetas anidadas ni sobrescritura de trabajo ajeno. README, todos los documentos académicos y diagrams se preservaron íntegros.

El ZIP mencionado en el encargo no estaba accesible en los adjuntos ni en las carpetas del entorno. La fuente efectiva fue el commit remoto indicado. No se afirma equivalencia binaria con un ZIP que no se pudo inspeccionar. `evidence/document_manifest.json` permite verificar lo recibido de GitHub.

Se revisaron README, HANDOFF_WORK, PROJECT_SPEC, REQUIREMENTS, MATHEMATICAL_MODEL, MODEL_DEFAULTS, ACCEPTANCE_PLAN, antecedentes, revisión del modelo, fuentes, changelog, informe y diagramas SVG. No se cambiaron ecuaciones, coeficientes de referencia, umbrales ni tecnologías. La referencia documental a PROMPT_INICIO_CODEX.txt apunta a un archivo ausente en el árbol remoto; el encargo de esta sesión y HANDOFF_WORK aportan las instrucciones de implementación.

La aplicación representa un estanque bien mezclado con biomasa fija. Es una simulación académica; no acredita operación productiva. pH y turbidez son aproximaciones empíricas; las acciones de pH no son dosis químicas.

## Arquitectura real

| Archivo | Responsabilidad |
|---|---|
| `piscicultura/config.py` | Catálogo aprobado, copia de perfiles, unidades, validación y RunConfig congelada como JSON canónico |
| `model.py` | Saturación USGS, diez tasas y RK45 con eventos terminales |
| `actuators.py` | Límite de órdenes, respuesta auxiliar, ocho capacidades e integrales separadas en cruces de cero |
| `control.py` | Measurement y decisión pura por histéresis o programa constante |
| `scenarios.py`, `sensors.py` | Tabla PCG64 por índice; perturbaciones y disponibilidad por tiempo; ruido, sesgo, ausencia y congelación |
| `engine.py` | Un avance provisional, cursor de eventos, muestreo reutilizado, transiciones de alarma y terminación |
| `service.py` | Preparar, avanzar, pausar, continuar, detener y comparar; publicación después de COMMIT |
| `repository.py` | SQLite, claves foráneas, unicidad, transacciones, recibos, propietario y reconocimiento de alarmas |
| `metrics.py` | IAE, bandas, recuperación, J, cobertura de y y consumos con unidades |
| `export.py` | ZIP autónomo con JSON, CSV y manifiesto |
| `charts.py`, `app.py` | Plotly y Streamlit en español |
| `__main__.py` | Ejecución y comparación desde la terminal sin presentación |
| `tests/` | Pruebas analíticas, aceptación, contratos funcionales e interfaz real mediante AppTest |

El dominio no importa Streamlit, Plotly ni SQLite. Los módulos de presentación no calculan ecuaciones ni decisiones. El servicio recibe un repositorio por inyección; las pruebas usan SQLite temporal real y funciones de producción. No se usan servicios externos al ejecutar.

## Entorno e instalación comprobada

Python 3.12.14, SQLite 3.53.1; NumPy 2.3.5, SciPy 1.17.0, Streamlit 1.66.0, Pandas 2.2.3, Plotly 7.1.0 y Pytest 9.1.1. SQLite pertenece al intérprete, no es un paquete pip. SO observado: Debian GNU/Linux 13.6, x86_64.

`requirements.txt` fija las seis dependencias directas verificadas. `requirements-lock.txt` registra todas las dependencias de un entorno virtual limpio instalado desde esas versiones. No se declara compatibilidad probada con otros sistemas operativos o intérpretes.

Comandos desde la raíz del repositorio:

```bash
python -m venv work/venv
work/venv/bin/python -m pip install -r requirements-lock.txt
work/venv/bin/python -m pip check
work/venv/bin/python -m streamlit run app.py
```

Abrir `http://127.0.0.1:8501`. En Windows la ruta del ejecutable sería `work\venv\Scripts\python.exe`; esa plataforma no fue evaluada. La instalación original exploratoria utilizó un entorno con paquetes del sistema; adicionalmente se creó `work/clean-venv` sin paquetes heredados, se instaló `requirements.txt`, se congelaron las dependencias y se ejecutaron las pruebas cortas. No confundir instalación inicial con prueba de funcionamiento sin red posterior.

La base predeterminada es `work/piscicultura.sqlite`; se puede seleccionar otra mediante `PISCICULTURA_DB`. La aplicación desactiva telemetría en `.streamlit/config.toml` y escucha en loopback. No se desplegó ni se cambió la visibilidad del repositorio.

## Uso

1. Seleccionar especie, escenario y estrategia en Configuración. Para una variante, duplicar el perfil y editar los campos de la nueva corrida. Las tres especies están en crecimiento o engorde.
2. Revisar unidades, procedencia, geometría, presión, salinidad, biomasa, condiciones iniciales, referencias, bandas y alarmas. El calendario editable usa intervalos en segundos sobre la malla. El bloque avanzado permite revisar coeficientes y sensores.
3. Validar y preparar: esto guarda la configuración y tabla de ruido, sin medir ni integrar. Una corrida activa debe detenerse antes de preparar otra desde el formulario.
4. Avanzar por intervalo o ejecutar hasta terminar. Pausar y continuar conserva estado dentro de la sesión. Detener conserva datos parciales. Cambiar de pestaña o consultar nunca avanza.
5. Revisar cinco lecturas con calidad, curvas x/y, bandas, referencias, ocho acciones efectivas, alarmas y métricas. Reconocer una alarma solo registra el reconocimiento.
6. Comparar crea dos corridas vinculadas bajo la base validada y una tabla de ruido común. La pantalla separa horizonte observado, solicitado y tramo común. Los archivos completos pueden descargarse desde Historial.

Las copias editables del catálogo viven en la sesión. Las configuraciones de las corridas y sus exportaciones son persistentes. Tras cerrar la aplicación se consulta el historial; no se promete reanudar automáticamente el proceso físico simulado.

## Contratos y tiempo

RunConfig conserva esquema, especificación, modelo, software, perfil completo, referencias/bandas/alarma, parámetros, x0/z0, sensores, controlador, solver, escenario y calendario. La validación comprueba finitud, tipos, unidades, dominios, geometría, horizonte 1–72 h, intervalo 30–300 s, divisibilidad y eventos sobre la malla; también procedencia, saturación de O2 y calibración abierta realizable. Rechaza dominios distintos de los aprobados y tolerancias menos estrictas que las aprobadas.

Estado interno: `[T,C,p,U,h,zT,zC,zp,zU,zh]`. Tiempo canónico en segundos. RK45 usa rtol=1e−7 y atol aprobadas; max_step=min(10,Δ/6). En refinamiento se usa 5 s, rtol=1e−9 y atol/100. No se generan números aleatorios en RK45.

Cada intervalo es provisional hasta la transacción. En el primer comando se procesan eventos y muestra 0. Se evalúan alarmas medidas y calidad; una lectura requerida inválida en cerrado termina antes de decidir. Luego se mantiene la orden e integra el intervalo; al extremo se procesan eventos, una muestra terminal y sus alarmas. Esa muestra y los cursores se reutilizan en el siguiente comando. Un terminal inválido deja FAILED sin decisión adicional. Una corrida nominal completa tiene 2881 muestras y 2880 decisiones.

Los eventos se aplican en `[inicio,fin)`. Tasas y sesgos se suman; disponibilidades coincidentes usan el mínimo. Se rechazan congelaciones/pérdidas ambiguas. Congelación conserva la última lectura GOOD anterior, sin ruido nuevo; una congelación plausible sigue GOOD. La inyección solo figura como auditoría. El controlador recibe explícitamente estrategia, referencias, configuración propia, comandos abiertos, Measurement y memoria. No recibe x, parámetros de la planta ni el calendario.

El abierto usa la calibración de la sección 11, sin recortes de comandos inviables; z0 es la misma calibración en la comparación aprobada. El cerrado comienza con memoria cero. Acciones opuestas se obtienen de un solo estado firmado. Las integrales de acciones se separan en la raíz del cruce; nunca se reemplazan por la parte positiva del promedio firmado.

Un cruce exterior de dominio termina la integración y conserva instante/estado irregular en `termination_state`, sin inventar muestras fuera de malla. Los residuos negativos de C/U menores que 1e−7 se conservan y auditan; no son lecturas válidas. No se asigna x=r ni se recorta el agua.

## Persistencia y concurrencia

Tablas: runs, samples, decisions, actuator_records (ocho filas por intervalo), events, metrics, comparisons, comparison_members, command_receipts y acknowledgments. Las tablas de series contienen claves e índices explícitos y payload JSON. FK está activado por conexión. Las claves compuestas impiden duplicación.

Un lote de muestras, decisión, acciones, eventos, estado final y recibo se confirma en una transacción. Un command_id confirmado devuelve su recibo; usarlo con otro expected_step genera conflicto. Un fallo revierte el lote y conserva el estado confirmado anterior, marcando FAILED con causa cuando la base permite esa escritura. Las métricas son datos derivados y se guardan en una transacción aparte; pueden recalcularse desde registros confirmados.

La conexión permite cambio de hilo y un RLock serializa sus operaciones; otro RLock serializa el servicio por sesión. Esta decisión responde a las reevaluaciones de Streamlit y se probó en AppTest. La versión inicial admite una corrida activa por sesión local; no es una aplicación colaborativa distribuida.

El propietario combina host, PID e instante de inicio del proceso Linux. Se marca INTERRUPTED únicamente una corrida RUNNING/PAUSED cuyo proceso local ya no existe. Otro lector o pestaña con propietario vivo no provoca esa marca. Los registros históricos no son checkpoints completos para reanudar después del cierre.

## Métricas, comparación y formatos

Las métricas principales usan x, trapezoides para IAE y extremo izquierdo para tiempo fuera; los límites son inclusivos y U solo penaliza exceso superior. Recuperación exige 1800 s consecutivos dentro. J usa escalas por variable antes de promediar. Agua, actividad pH y energía parcial usan integrales de acciones; se guardan lluvia/fuga/evaporación y recambio aparte. No se suman errores con unidades incompatibles.

Las métricas sobre y informan cobertura por variable. Solo calculan IAE con cobertura completa; no se rellenan ausencias. En comparación truncada se informa tramo común y resultado completo observado con su causa; no se declara ganador al fallar antes. Para un extremo común irregular se interpola x linealmente en el tramo final; los consumos comunes se informan solo sobre intervalos completos, limitación explícita en el resultado. Los estados terminales de dominio sí se incorporan a las métricas x del horizonte observado.

Cada ZIP incluye `config.json`, `noise.csv` (epsilon estándar recortado, autoridad de reproducción), `samples.csv`, `decisions.csv`, `actions.csv`, `events.csv`, `metrics.json`, `metadata.json` y `manifest.json`. Valores ausentes: JSON null / celda CSV vacía junto con calidad; nunca cero inventado. El manifiesto incluye unidades, versiones, identificador y SHA-256 del CSV de ruido. Las muestras CSV distinguen x, y y calidad por variable. Las acciones incluyen orden, z inicial/final, disponibilidad y media efectiva por intervalo.

## Reproducción y pruebas

```bash
work/venv/bin/python -m pytest -q tests --junitxml=evidence/pytest.xml
work/venv/bin/python -m scripts.core_evidence
work/venv/bin/python -m piscicultura --scenario S2 --profile 0 --compare --db work/demo.sqlite --output work/exports
work/venv/bin/python -m piscicultura --config work/config.json --compare --db work/replay.sqlite --output work/replay
```

El último comando requiere extraer `config.json` de una exportación. Para reproducir literalmente la tabla persistida, usar el script de reproducción descrito en evidence/README.md; no depender únicamente de la semilla. La suite genera el índice y exportaciones de referencia. Usar una base nueva evita mezclar ensayos, aunque las claves únicas impiden duplicados entre corridas.

Los detalles observados, los casos fallidos de desarrollo corregidos, el rendimiento contextual y la matriz RF/RNF están en TEST_RESULTS.md. HANDOFF_CODEX.md identifica entregables y asuntos que Work debe resolver documentalmente.
