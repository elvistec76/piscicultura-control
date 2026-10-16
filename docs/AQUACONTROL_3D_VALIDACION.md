# AQUACONTROL 3D: implementación y validación

Se trabajó en `codex/reproduccion-animada-aquacontrol`, derivada del commit `c43f444151006461fb1ed3ec960a878a2349a549` de `codex/estanques-3d-seleccionables`. Main conserva su referencia original y no se integra PR #1. El espacio disponible tenía Git y remoto; no tenía un entorno virtual del proyecto ni acceso al entorno Windows de Visual Studio Code. Se preparó un entorno de verificación aislado en `work/.venv`, sin cambiar los archivos de dependencias ni el entorno local del usuario.

## Implementación incremental

1. `f0b6b45`: lectura histórica de solo lectura, selección de tiempos, reloj de reproducción, animación ambiente independiente y comprobación de movimiento antes del rediseño. Siete pruebas específicas y 53 comprobaciones de navegador pasaron en esta etapa.
2. `d8e4d8a`: dashboard industrial 65/35, cinco variables a la derecha, controlador, ocho actuadores, alarmas, reproductor inferior, gráficas sincronizadas y presentación académica. Se conservan las cinco pestañas y las representaciones circular, rectangular y 2.5D.
3. `1986829`: la guía exige una diferencia real posterior en valores o calidad para ofrecer la etapa de cambio observado. La ausencia de cambio o de evento no se sustituye por una explicación inventada.

## Separación de datos y presentación

`piscicultura/replay.py` abre SQLite mediante URI `mode=ro`, activa `query_only` y reúne run, samples, decisions, actuator_records y events en una sola transacción de lectura. No importa ni llama al motor, sensores, controlador o servicio. Los controles de reproducción se ejecutan dentro del documento visual: no integran, no deciden, no reconocen alarmas y no envían órdenes al servidor.

`replay.js` selecciona el estado exacto anterior o coincidente, la última muestra y su calidad, la decisión vinculada por `input_sample_index`, los intervalos efectivos y las transiciones de alarma. Conserva por separado cursor, tiempo del estado, tiempo de medición, intervalo de acción y tiempo real de reproducción. No interpola valores. Un estado terminal parcial usa el estado exacto guardado y mantiene la hora anterior de la última medición.

Las acciones son medias registradas del intervalo [inicio, fin); el extremo final de la corrida muestra su último intervalo y se identifica como tal. No se reconstruye una acción instantánea. Si falta el registro de un canal o hay un hueco entre intervalos, no se prolonga artificialmente una actividad anterior. La lectura inválida/ausente no se sustituye por referencia, estado exacto o `last_good`.

El panel muestra errores, referencias, motivos y órdenes guardados. En lazo abierto se identifica el programa constante sin corrección por retroalimentación. Una muestra posterior se muestra solo cuando ya está alcanzada por el cursor; si no existe todavía se indica esa ausencia. La observación posterior no demuestra causalidad.

## Animación y funcionamiento local

Natación con trayectorias interiores, movimiento de colas, ondas pequeñas y brillos especulares decorativos. La superficie oscila ópticamente alrededor del nivel exacto fijo; no cambia volumen, biomasa ni estado matemático. El color usa la turbidez exacta retenida como ilustración. Burbujas, flujos, filtración e indicadores de regulación requieren media efectiva positiva del canal representado.

Calidad baja/media/alta con geometría de peces, sombras, partículas, brillos, escala de píxel y límite visual de fotogramas. No altera integración, frecuencia de control o precisión. Se respeta movimiento reducido, se suspende la vista oculta y se libera el renderizador al cerrar. Sin ambiente ni reproducción activa no se mantiene un bucle de renderizado. Three.js está incluido localmente y Plotly procede del paquete Python existente; no hay descarga de recursos externos durante la ejecución.

Modo presentación oculta temporalmente los formularios y restaura las cinco pestañas al salir. La demostración guiada solo recorre etapas respaldadas por registros. Las gráficas conservan tiempos y un cursor común; los clics en muestras o eventos seleccionan su instante.

## Resultados de software

| Verificación | Resultado |
| --- | --- |
| Suite completa existente y nueva | 109/109, 0 fallos, 0 errores, 0 omisiones |
| Pruebas específicas finales de reproducción y presentación | 8/8 |
| Reproducción y dashboard en Chromium | 60 comprobaciones |
| Recorrido existente de estanques en Chromium | 23 comprobaciones |
| Demostración, movimiento reducido dinámico, móvil y resultado posterior | 8 comprobaciones |
| Cambios en motor, RunConfig, sensores, estrategias, repositorio y dependencias | Ninguno; comparación binaria contra la base |
| Escrituras durante reproducción y capturas | Ninguna en los registros SQLite; conexión de reproducción de solo lectura |
| Red externa en renderizador, gráficas y demostración | Sin solicitudes externas |

Las pruebas incluyen límites de intervalos, retroceso, pausa, reinicio, velocidades, ocultación, muestras ausentes e inválidas, huecos de acciones, entrada de controlador ausente, alarmas activadas/cesadas y terminación parcial. Se comprobó movimiento de posición de peces, colas y vértices de agua manteniendo el nivel y tiempo fijo, cámaras, calidades, ambos estanques y pérdida de WebGL. Se conservan los resultados de la suite científica existente.

Las primeras ejecuciones de comprobación se corrigieron y repitieron: un render cargado antes del cambio de plantilla conservaba marcadores antiguos; el apagado de ambiente dejaba un fotograma pendiente; el ensayo por puntero del interruptor nativo chocaba con su etiqueta; y las capturas se ajustaron a la notificación asíncrona de movimiento reducido. Los resultados enlazados corresponden a ejecuciones finales satisfactorias. Los tiempos de espera de los verificadores opcionales contemplan la compilación gráfica de software; no son criterios de rendimiento del producto.

## RNF10 y limitaciones conservadas

**RNF10 permanece pendiente de evaluación** en Windows 10, Brave, Intel Core i5-8365U y 16 GB. Las ejecuciones en Linux/SwiftShader no acreditan ese hardware, ni un FPS objetivo. El test de software existente registra sus tiempos sin declarar elegibilidad del equipo de referencia.

pH y turbidez siguen siendo aproximaciones empíricas, sin validación de campo. Las animaciones y la apariencia del agua no constituyen evidencia biológica, óptica o productiva. 2.5D usa una proyección fija que se actualiza al seleccionar estados. Al reconstruir el documento con los selectores nativos se reinician reproducción y opciones de ese documento, como se explica en la guía. La vista histórica cargada es una instantánea coherente de los registros confirmados; para ver nuevas confirmaciones se recarga la vista.

[Instrucciones para Windows y conservación de una carpeta ZIP](AQUACONTROL_3D_WINDOWS.md). [Registros completos, capturas y video](../evidence/aquacontrol_replay/README.md).
