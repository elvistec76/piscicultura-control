# AquaControl — estanques seleccionables

Esta ampliación es una capa de presentación sobre `2160594afbf538a4541ad74079d32f2768f0b965`, en la rama `codex/estanques-3d-seleccionables`. Mantiene M-AGUA-DEMO-1, RunConfig, integración, control, sensores, SQLite, exportaciones y documentos académicos anteriores.

## Arquitectura

`app.py → tank_view.snapshot → JSON → st.iframe → Three.js / SVG 2.5D`

El adaptador recibe copias de registros confirmados. No llama a `advance`, `prepare`, `decide`, `conditions`, `effective` ni a operaciones de escritura. La nueva pestaña permite consultar cualquier corrida del historial, incluidas las dos integrantes de una comparación. Preparar una corrida selecciona esa nueva corrida en la vista; elegir otra corrida solo cambia la consulta. Los mandos existentes continúan en «Ejecución y evolución» y las exportaciones mantienen su formato.

`presentation_tank_shape`, `presentation_render_mode` y `presentation_run_id` son preferencias de `st.session_state`. No forman parte de RunConfig, parámetros, decisiones, métricas, comparaciones ni exportaciones.

## Contrato de datos y tiempos

- Geometría: radio `sqrt(A/π)`; largo `sqrt(2A)`; ancho `sqrt(A/2)`. Ambas áreas son A. H procede de la altura geométrica configurada. Una escala uniforme ajusta la escena a la cámara sin cambiar las proporciones físicas del tanque.
- Agua: usa h de `run.state[4]`, con tiempo `run.time_s`. Volumen mostrado `A*h`, sin recortes, límites añadidos ni correcciones de estado. La altura geométrica y las reglas de dominio del modelo se conservan. Un nivel negativo no se transforma en volumen positivo: no se crea un sólido de agua con altura negativa y se muestra la superficie en la coordenada h exacta y una advertencia. Un nivel superior al tanque se representa por encima de su borde.
- Tarjetas: última muestra y confirmada, con su propio tiempo. No sustituyen lecturas ausentes o inválidas por x, referencias ni última lectura válida. pH se presenta como adimensional.
- Estado exacto y lecturas pueden tener tiempos distintos: en un cruce parcial de dominio se utiliza el último estado exacto persistido, la muestra anterior y el intervalo parcial efectivo. Se muestran los tres tiempos sin prolongarlos.
- Actuadores: ocho registros del intervalo con mayor `end_s`. La orden de los cinco canales firmados se descompone en ocho órdenes físicas: calor/frío, aire, pH+/pH−, filtro, entrada/salida. Disponibilidad y `mean_effective` se muestran como campos separados. No se recomputa una acción a partir de una orden. La actividad visual equivale estrictamente a `mean_effective > 0`; valores positivos muy pequeños se indican como `<0,01%`.
- Alarmas: se reconstruye el conjunto activo reproduciendo las transiciones `activation`/`clear` de categoría `alarm`. No se deducen nuevas alarmas desde los umbrales. La ausencia de muestras se indica por separado.
- Sin intervalos: equipos sin datos, sin supuesta acción efectiva. Se puede mostrar el estado inicial confirmado de una corrida preparada.

## Renderizado y animación

Three.js 0.170.0 se distribuye como un IIFE local minificado en `piscicultura/tank_assets/vendor/three.min.js`. Se generó desde el paquete npm oficial mediante esbuild 0.25.10. Se incluye la licencia MIT de Three.js. Se eligió este empaquetado para evitar importaciones externas en el iframe y funcionar sin Internet después de instalar las dependencias Python. Node/npm/esbuild no son necesarios para ejecutar AquaControl.

El renderizador construye tanque circular o rectangular, estructura metálica, agua semitransparente con brillos de iluminación, peces con cuerpo/aletas/cola, cinco sondas y cableado, tuberías, válvulas, difusor, armario, seis equipos auxiliares y dos circuitos de entrada/salida. Los equipos y tuberías son esquemáticos y su disposición no es un proyecto de ingeniería de planta. El nivel y la geometría del tanque se expresan en metros.

La turbidez exacta solo modifica la apariencia óptica, mediante una interpolación ilustrativa acotada de color/opacidad; no modifica U, las ecuaciones ni las lecturas. No hay modelo óptico ni biológico validado. Los peces son decorativos.

Burbujas: acción de aireación. Partículas en tuberías: entrada/salida. Indicador y rotor: filtración. Aros térmicos: calefacción/enfriamiento. Señales de pH: canales pH+/pH− existentes; no representan una dosificación química real. Toda indicación procede del último intervalo confirmado.

Solo `RUNNING` permite animación decorativa del último intervalo; x, y, h y t permanecen constantes hasta el siguiente comando del simulador. Una pausa o estado terminal no crea bucle de animación. Se respeta `prefers-reduced-motion`; las señales estáticas siguen visibles. La animación se limita a aproximadamente 30 imágenes/s y deja de renderizar si el documento está oculto. Es una decisión de implementación, no una acreditación de RNF10.

Arrastre: giro y elevación. Rueda o botones: zoom. Botones de giro y restablecimiento permiten manejar la cámara sin arrastrar. Three.js 0.170.0 requiere WebGL2 para la escena 3D. La escena 2.5D SVG se selecciona automáticamente si falla la creación de WebGL2 o se pierde su contexto; también puede elegirse manualmente. 2.5D mantiene los datos y la altura de agua, pero es una proyección fija sin rotación, zoom ni animación continua.

Los valores de presentación se insertan como JSON escapado y como `textContent`; un nombre de perfil no se interpreta como HTML. No hay recursos de red, fuentes externas ni CDN en la escena.

## Ejecución local en Windows

Recomendado Python 3.12 de 64 bits, el mismo minor utilizado en esta verificación. Desde PowerShell, en la raíz del repositorio o del ZIP de código:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Abrir `http://localhost:8501`, validar y preparar una corrida y avanzar un intervalo en «Ejecución y evolución». En «Vista del estanque», cambiar «Representación» entre Circular/Rectangular. Pausar desde la pestaña de ejecución y volver a la vista para comprobar la escena estática. Seleccionar 2.5D si el navegador no ofrece WebGL.

La instalación inicial requiere acceso a los paquetes Python, o un repositorio de ruedas descargadas previamente. Tras instalar, la aplicación y sus gráficos funcionan en localhost sin red externa. La base predeterminada se guarda en `work/piscicultura.sqlite`. Una pestaña abierta conserva su preferencia visual; una sesión nueva puede recuperar el valor inicial. No se guarda la forma en SQLite.

Pruebas Python:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Verificación opcional en navegador, sin añadir dependencias de producción:

```powershell
.\.venv\Scripts\python.exe -m pip install playwright
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe scripts/verify_tank_browser.py
```

El script crea registros con el servicio real, genera las dos escenas, bloquea la red, prueba WebGL y su alternativa, arranca Streamlit con base aislada, cambia los selectores y guarda PNG y `browser-results.json` en `work/tank-browser/`. En Linux se puede indicar `--browser /usr/bin/chromium`. Los artefactos de trabajo no alteran los resultados históricos del repositorio.

Para regenerar el vendor, solo en desarrollo:

```powershell
npm install --prefix work/three-build three@0.170.0 esbuild@0.25.10
.\work\three-build\node_modules\.bin\esbuild work/three-build/node_modules/three/build/three.module.js --bundle --format=iife --global-name=THREE --minify --outfile=piscicultura/tank_assets/vendor/three.min.js
```

Conservar `THREE-LICENSE.txt`; comprobar el hash del archivo y repetir las pruebas de navegador después de regenerarlo.

## Archivos y revisión

- `.streamlit/config.toml`: paleta oscura.
- `app.py`: nombre AquaControl, pestaña y selectores de presentación, descarga de los datos existentes.
- `piscicultura/tank_view.py`: adaptador y frontera con `st.iframe`, disponible en Streamlit 1.66.0 fijado en el proyecto.
- `piscicultura/tank_assets/scene.html`, `scene.css`, `scene.js`: panel industrial, Three.js y SVG.
- `piscicultura/tank_assets/vendor/three.min.js`, `THREE-LICENSE.txt`, `README.md`: dependencia local y procedencia.
- `tests/test_tank_view.py`: invariancia, geometría, tiempos, alarmas, canales y Streamlit.
- `tests/test_ui.py`: conserva el recorrido anterior y actualiza únicamente la lista esperada de pestañas.
- `scripts/verify_tank_browser.py`: comprobaciones y capturas reproducibles en Chromium.
- `docs/TANK_VIEW.md` y `evidence/estanques_3d/`: instrucciones y evidencia nueva de esta ampliación.

Revisar el diff contra `codex/implementacion-spc-agua-0.5.0`. La mejora puede proponerse en un PR separado con esa rama como base, o incorporarse allí después de su revisión. Eso no integra PR #1 en `main` ni concede aceptación de RNF10. No se modificaron `main`, PR #1 ni los documentos académicos anteriores.

## Límites de verificación

Las cifras de la ejecución nueva, capturas y trazabilidad se consignan en `evidence/estanques_3d/README.md`. No se reutiliza la aprobación histórica 85/85 como resultado de esta versión.

La comprobación de navegador usa Chromium en Linux con renderizado por software; no acredita una GPU, Windows, Safari/Firefox, la apariencia en un proyector ni el equipo/protocolo establecidos para RNF10. No se declara validación de campo ni idoneidad productiva. pH y turbidez conservan las limitaciones empíricas del modelo.
