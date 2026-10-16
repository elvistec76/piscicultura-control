# Three.js local

- Paquete oficial: `three@0.170.0` de npm.
- Entrada: `build/three.module.js`.
- Empaquetador: `esbuild@0.25.10`, `--bundle --format=iife --global-name=THREE --minify`.
- Salida: `three.min.js`, incluida directamente en el iframe; sin CDN/importaciones en ejecución.
- Licencia: MIT, texto íntegro en `THREE-LICENSE.txt`.
- No se requiere Node.js para ejecutar la aplicación Python.

La receta de regeneración y las limitaciones están en `docs/TANK_VIEW.md`.
