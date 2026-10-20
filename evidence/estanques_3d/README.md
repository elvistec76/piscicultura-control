# Evidencia nueva de estanques 3D

Base: `2160594afbf538a4541ad74079d32f2768f0b965`.

Implementación verificada: `add95134eb106f009119fb010c4bfb7968761423`. El commit posterior añade únicamente esta evidencia y precisión documental sobre WebGL2. Los hashes de `browser-results.json` identifican exactamente los archivos de aplicación y renderizado usados en las capturas. `integrity.json` conserva los hashes del núcleo y de los documentos anteriores, y comprueba que coinciden con la base.

## Resultados

**101/101 pruebas aprobadas, cero fallos, errores o casos omitidos.** La ejecución final de pytest informó 299,82 s. El XML conserva los tiempos por caso y el tiempo de suite.

La ejecución completa final se registra en `pytest.log` y `pytest.xml`. Contiene los 85 casos existentes, con la lista de pestañas actualizada, y los 16 casos nuevos de visualización. No se suma la ejecución corta como casos adicionales ni se utiliza la aprobación histórica 85/85 como evidencia de esta versión.

Las pruebas nuevas cubren:

- Las tres especies y ambas estrategias, con una corrida base y otra que cambia la vista entre intervalos: igualdad exacta de x, y, acciones efectivas, decisiones, alarmas y métricas, incluido J.
- 360 intervalos y 720 construcciones de vistas en ese contraste. Cada cambio conserva el volcado SQL completo y el contador de escrituras.
- Geometrías de igual área y volumen A*h, y niveles ilustrativos fuera de la geometría sin recortar el estado ni transformar un volumen negativo en positivo.
- Lecturas ausentes e inválidas generadas por el servicio real; tratamiento defensivo de una lectura no finita fuera de SQLite.
- Separación de orden, disponibilidad y acción efectiva; mapeo de los ocho canales; cese de alarmas; tiempos distintos en un intervalo terminal parcial.
- Preparada, en ejecución, pausada y estados terminales; ausencia de actividad inferida antes del primer intervalo.
- Renderizado sin red, escape de nombres de perfiles, cambios repetidos en Streamlit para los tres perfiles y selección automática de una nueva corrida conservando las preferencias visuales.

## Navegador y capturas

`browser-results.json` y `browser.log`: **23 comprobaciones correctas**, cero excepciones JavaScript y ninguna solicitud HTTP/HTTPS en las escenas sin red. El script usa Chromium en Linux con ANGLE/SwiftShader y luego arranca una instancia real de Streamlit con SQLite aislado.

Se comprobaron las dos formas en WebGL2, cinco sensores y ocho actuadores, rotación, zoom, conservación del snapshot, animación sin avance de t, pérdida real de contexto WebGL, ausencia de WebGL desde el inicio y falta de bucle de animación en pausa. En Streamlit se cambiaron los selectores varias veces y se pausó la corrida sin excepciones. Las 23 comprobaciones incluyen las repeticiones de selección; no son 23 requisitos académicos distintos.

Capturas generadas por el renderizador de producción, usando el escenario S2 de Tilapia y un intervalo confirmado [0,60] s:

| Archivo | Contenido |
| --- | --- |
| [Circular-3D.png](Circular-3D.png) | Circular, agua exacta, sensores, equipos e indicadores efectivos. |
| [Rectangular-3D.png](Rectangular-3D.png) | Rectangular de la misma área, proporción 2:1. |
| [Circular-2.5D.png](Circular-2.5D.png) | Alternativa automática sin WebGL, circular. |
| [Rectangular-2.5D.png](Rectangular-2.5D.png) | Alternativa automática sin WebGL, rectangular. |
| [Streamlit-Rectangular.png](Streamlit-Rectangular.png) | Iframe real de Streamlit después de cambios de forma y pausa. |

Se inspeccionaron visualmente las capturas para revisar estructura, geometría, peces, sondas, agua, legibilidad de las cinco métricas y sus unidades, ocho canales, tiempos, alarmas y estado pausado. Esto es revisión de capturas, no una sesión manual en Windows ni una medición de rendimiento gráfico. Las pruebas de interacción se automatizaron con Playwright. Las alarmas activas se consultan en un panel con desplazamiento, manteniendo el contador visible.

Lista completa de archivos del diff: [changed-files.txt](changed-files.txt).

## Reproducir y límites

Véase [la guía de ejecución en Windows y arquitectura](../../docs/TANK_VIEW.md), que incluye la lista de archivos cambiados y los comandos de pytest y Playwright. Las dependencias Python permanecen en sus versiones fijadas; Node.js no es necesario para ejecutar la aplicación. La versión efectiva de cada paquete, Python, SQLite, sistema y Chromium se registra en `browser-results.json`.

La evidencia previa y sus bases/exportaciones no se sustituyeron. Todos los archivos originales salvo `app.py`, `.streamlit/config.toml` y la expectativa de pestañas de `tests/test_ui.py` coinciden con la base. La nueva forma solo existe en el estado de presentación de la sesión, y la vista lee los registros confirmados.

No se comprobó manualmente Windows, GPU física, Safari/Firefox ni una presentación en proyector. No se acredita fluidez o tasa de imágenes por segundo en el equipo de exposición. **RNF10 sigue pendiente/no acreditado**: pasar la suite no sustituye el equipo y protocolo exigidos. pH y turbidez siguen siendo aproximaciones empíricas, los peces son decorativos y la interfaz no implica validación de campo ni idoneidad productiva.

La rama se entrega para revisión separada contra `codex/implementacion-spc-agua-0.5.0`. Se puede incorporar mediante un PR con esa rama como base después de revisar el diff; esto no integra PR #1 en `main` ni otorga aprobación de RNF10.
