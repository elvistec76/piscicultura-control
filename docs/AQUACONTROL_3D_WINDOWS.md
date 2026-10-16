# AQUACONTROL 3D: reproducción y demostración en Windows

Esta mejora se desarrolla sobre `codex/reproduccion-animada-aquacontrol`, derivada de `codex/estanques-3d-seleccionables` en `c43f444151006461fb1ed3ec960a878a2349a549`. No modifica main ni integra PR #1.

## Conservar el proyecto local

Detenga Streamlit con Ctrl+C antes de cambiar archivos. Haga una copia de la carpeta del proyecto y de la base SQLite, conservando su entorno virtual existente. No reemplace ni borre `work/` o su base de datos al actualizar el código.

Si tiene Git, consulte primero `git status` y preserve sus cambios locales antes de cambiar de rama. Después de obtener la rama de esta entrega:

```powershell
git fetch origin codex/reproduccion-animada-aquacontrol
git switch --track origin/codex/reproduccion-animada-aquacontrol
```

Si ya tiene esa rama local, use `git switch codex/reproduccion-animada-aquacontrol`. No ejecute reset, checkout o merge sobre main.

Si la carpeta procede de un ZIP y no tiene `.git`, no queda conectada a una rama remota. Extraiga el ZIP de la nueva rama en otra carpeta, mantenga la copia original y registre el commit/base de esta entrega. Reutilice el Python del entorno virtual existente y una copia de la base con el servidor detenido. Conserve los archivos modificados y el informe para una revisión posterior; no afirme que un ZIP constituye un checkout remoto. Si luego crea un clon Git, traslade únicamente los cambios de código revisados, sin agregar la base ni el entorno virtual.

## Ejecutar desde Visual Studio Code

En la terminal integrada, desde la raíz del proyecto, use el ejecutable de su entorno existente. Si se llama `.venv`:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502
```

Si su entorno se llama `venv`, sustituya `.venv` por `venv`. También puede usar la ruta absoluta al Python que ya tiene seleccionado en Visual Studio Code. No necesita activar PowerShell ni cambiar su política de ejecución para usar esa ruta.

Abra `http://localhost:8502` en Brave. No reinstale dependencias si la aplicación arranca: `requirements.txt` y `requirements-lock.txt` no cambian en esta mejora. Three.js se conserva en el repositorio; Plotly se incorpora desde el paquete Python instalado. El renderizador y las gráficas no descargan bibliotecas, texturas ni modelos de Internet.

Por defecto se usa `work/piscicultura.sqlite`. Para consultar una copia específica, antes de iniciar:

```powershell
$env:PISCICULTURA_DB = 'C:\ruta\copia\piscicultura.sqlite'
```

El servicio de ejecución conserva su comportamiento existente de inicialización y recuperación de corridas al abrir la aplicación. El módulo de reproducción abre su propia conexión SQLite `mode=ro`, con `query_only=ON`; sus controles no llaman al servicio, no reconocen alarmas ni escriben resultados.

## Recorrido funcional

1. Abra **Vista del estanque** y seleccione una corrida existente, su representación circular o rectangular y el renderizado. Si no hay corridas, prepare y ejecute una desde las pestañas originales. La vista no crea datos automáticamente.
2. Active **Modo ambiente**. Debe percibir natación, movimiento de colas, ondas y brillos, incluso en COMPLETED, PAUSED o STOPPED. El nivel exacto y su tiempo permanecen fijos. Los peces son decorativos, sin simulación biológica.
3. Pulse **Reiniciar**, seleccione una velocidad y pulse **Reproducir**. La velocidad significa segundos simulados por segundo de reproducción: 60× recorre 60 s simulados por segundo real. **Pausar reproducción** detiene el cursor; no pausa ni reanuda el simulador.
4. Arrastre la línea de tiempo, escriba un instante en segundos o use las flechas para saltar entre tiempos registrados. También puede hacer clic en una muestra o evento de la gráfica.
5. Compare **Tiempo simulado**, **Tiempo de reproducción**, **Estado x**, **Medición y** e **intervalo de acción efectiva**. Entre registros se retiene el último estado exacto, sin interpolación. El instante terminal puede tener un estado exacto posterior a la última medición en una terminación parcial.
6. Las tarjetas muestran la medición guardada y su calidad. Una lectura ausente o inválida no se sustituye por el estado exacto, una referencia ni una lectura anterior válida.
7. Los ocho canales muestran orden, disponibilidad y media efectiva registrada. Burbujas, indicadores de regulación, filtración y flujos solo aparecen con acción efectiva positiva en el intervalo representado. Una orden positiva con disponibilidad cero no produce burbujas. La media de un intervalo no es un caudal instantáneo; su animación no reconstruye la dinámica interna del actuador.
8. Consulte **Trazabilidad de la última decisión registrada**, desde el enlace del panel derecho. Se conserva el vínculo `input_sample_index`, referencias, errores, códigos, órdenes y la primera muestra posterior disponible hasta el cursor. Esa observación no demuestra causalidad. En lazo abierto se identifica el programa constante sin corrección por retroalimentación.
9. Active el interruptor superior **Modo presentación académica** para ocultar formularios, comparación e historial. Desactívelo para regresar a las cinco pestañas. **Ampliar estanque**, dentro del dashboard, ajusta su tamaño sin ocultar datos. La demostración guiada es opcional y omite las etapas sin registros; no inyecta eventos.

Cambiar representación o renderizado mediante los selectores nativos reconstruye la vista en el extremo más reciente del tramo confirmado. Las preferencias de forma se conservan en la sesión; ambiente, calidad y posición de reproducción pertenecen al documento visual y se reinician cuando Streamlit reconstruye ese documento. Una reproducción ya cargada es una instantánea coherente de la base, sin seguimiento en vivo de nuevas escrituras; recargue la vista para consultar intervalos confirmados después de cargarla.

## Calidad y accesibilidad

Para el Intel Core i5-8365U con gráficos integrados, comience por **Baja** y pruebe **Media**. La calidad solo cambia características visuales:

| Opción | Peces decorativos | Burbujas máximas | Sombras | Escala máxima de píxel | Límite de renderizado |
| --- | ---: | ---: | --- | ---: | ---: |
| Baja | 5 | 10 | No | 1 | 20 fps |
| Media | 9 | 20 | No | 1,25 | 30 fps |
| Alta | 13 | 34 | Sí | 1,7 | 30 fps |

También se ajustan geometría de peces, partículas de flujo y brillos. Son límites solicitados al renderizador, no un rendimiento medido o garantizado. La frecuencia del controlador, ecuaciones, precisión e integración permanecen intactas.

La animación se suspende al ocultar la pestaña o el documento; el estanque deja de renderizarse cuando queda fuera de pantalla. El cursor de reproducción tampoco recupera de golpe el tiempo pasado en una pestaña oculta. Sin modo ambiente y con el reproductor pausado, no queda un bucle continuo de renderizado. Se respeta `prefers-reduced-motion`, incluido un cambio de preferencia durante la sesión. La reproducción y selección de estados siguen disponibles sin animación decorativa.

Si WebGL no está disponible o se pierde su contexto, se conserva la alternativa **2.5D**, que actualiza el estado seleccionado y admite la reproducción con una proyección fija. Es una alternativa sin ondas ni natación continua. Puede seleccionarla manualmente en **Renderizado**.

## Pruebas

Con el Python de su entorno:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=work\verificacion.xml
```

Las pruebas nuevas del código JavaScript de selección histórica requieren Node **solo para verificación**, no para ejecutar la aplicación. Si Node no está disponible, pytest informa explícitamente esos casos como omitidos. Para comprobar el navegador, use Playwright si ya está instalado y un Brave/Chromium local:

```powershell
.\.venv\Scripts\python.exe scripts\verify_replay_browser.py --browser 'C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe'
```

Esta comprobación usa una base aislada en `work/replay-browser`, genera corridas de prueba con el motor existente y abre un servidor temporal en el puerto 8504. No utiliza su base funcional. Guarda resultados y capturas. No instala dependencias ni descarga navegadores automáticamente.

## Límites de la evidencia

Las pruebas de software y las capturas de esta entrega se ejecutan en Linux/Chromium, con renderizado de software en el entorno de trabajo. No acreditan rendimiento en Windows 10, Brave o el i5-8365U. **RNF10 continúa pendiente** de medición en el equipo objetivo. pH y turbidez conservan sus aproximaciones empíricas y la aplicación sigue sin validación de campo. Ninguna animación añade evidencia científica o recomendaciones productivas.
