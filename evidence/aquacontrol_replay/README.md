# Evidencia de AQUACONTROL 3D

Fecha: 16 de octubre de 2026. Corridas de prueba generadas por el motor existente y guardadas en bases aisladas bajo `work/`. No son observaciones de campo. No se incluyen bases funcionales ni se modifican sus registros.

- Regresión completa: **109 pruebas aprobadas**, sin fallos, errores ni omisiones. [Registro](pytest-final.log) y [JUnit](pytest-final.xml).
- Verificación específica final de reproducción: **8 pruebas aprobadas**. [JUnit](replay-focused.xml).
- Navegador/reproducción: **60 comprobaciones**. [Resultado](browser-results.json).
- Compatibilidad del recorrido de estanques existente: **23 comprobaciones**. [Resultado](browser-compatibility.json).
- Capturas y demostración: **8 comprobaciones**, sin escrituras SQLite, errores JavaScript ni solicitudes externas. [Resultado](demo-results.json).

## Capturas y video

- [Estanque circular, lazo cerrado](Circular-demostracion.png).
- [Estanque rectangular, lazo cerrado](Rectangular-demostracion.png).
- [Decisión al instante 600 s](decisiones.png): no se muestra una medición posterior que todavía quede después del cursor.
- [Decisión y observación posterior al final](decisiones-final.png): entrada a 3540 s y medición posterior a 3600 s, ambas registradas.
- [Vista móvil 2.5D, 390 px](movil-2.5D.png).
- [Alternativa circular 2.5D](Circular-2.5D.png) y [rectangular 2.5D](Rectangular-2.5D.png).
- [Aplicación real de Streamlit](Streamlit-dashboard.png).
- [Video MP4, seis segundos](demostracion.mp4). H.264, 1440 × 1240. Es una secuencia de 24 capturas del navegador presentada a 4 fps; su duración no mide rendimiento ni velocidad real de renderizado.

Las capturas principales corresponden a S2, lazo cerrado, horizonte de una hora y un evento `feed` registrado en [120,600) s. La demostración no introduce eventos durante la reproducción. El video usa el estanque rectangular y los controles reales de reproducción.

## Procedencia y límites

[Integridad del código protegido](integrity.json) y [entorno de validación](environment.json). Los hashes del recorrido de navegador conservan la versión de los archivos que se comprobó en esa etapa. El ajuste posterior de la guía para exigir un cambio observado posterior se verificó con las ocho pruebas específicas y en la captura de demostración (cambio registrado a 180 s).

El interruptor nativo de presentación se verificó por teclado, evitando dirigir el clic al input que cubre su etiqueta de Streamlit. Las comprobaciones del renderizador y controles históricos se hicieron en documentos locales sin red; la aplicación real solo pudo acceder a su servidor local.

**RNF10 continúa pendiente.** Linux/Chromium con renderizado de software no acredita Windows 10, Brave, Intel Core i5-8365U y 16 GB de RAM. Los tiempos de pytest son tiempos de pruebas de software. pH y turbidez conservan su carácter empírico, sin validación de campo.
