# AquaControl · Interfaz para presentación

Esta versión simplifica la configuración y reúne el estanque, los sensores, los equipos y las gráficas en **Ejecución y evolución**. La demostración conserva la ventana 3D, la cámara y el zoom al actualizar los datos.

Es un simulador académico del control de temperatura, oxígeno disuelto, pH, turbidez y nivel de un estanque. No está conectado a equipos físicos ni cuenta con validación de campo.

## Ejecutar en Windows

Desde la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Para mostrar el control, seleccione **S2 · Recuperación**, prepare la corrida y pulse **Iniciar demostración**. Cada tres segundos de pantalla se calcula un intervalo simulado. Puede pausar para explicar las lecturas y las acciones de los equipos.

- [Guía de funcionamiento y presentación](docs/GUIA_PRESENTACION_CONTROL.md)
- [Revisión del modelo y resultados de pruebas](docs/REVISION_CONTROL_2026-10-19.md)
- [Evidencia del arreglo del parpadeo](evidence/interfaz_sin_parpadeo/)

La revisión de control registra 107 pruebas únicas aprobadas. El cambio posterior de actualización visual se verificó con 20 pruebas de interfaz/presentación, dos pruebas JavaScript y una comprobación en navegador que conserva la misma ventana y el mismo lienzo durante 23 pasos.

## Antecedente: revisión de la primera implementación

Edición académica 0.6.0 para revisión. Contrato evaluado SPC-AGUA-001 0.5.0, modelo 1.0.0 y software 0.1.0. El PR 1 no se recomienda para integración hasta corregir OBS01 a OBS03 y revisar la evidencia actualizada. RNF10 conserva su evaluación local pendiente.

Abrir el informe Word actualizado y REVISION_COHERENCIA_PR1.md. Enviar OBSERVACIONES_CODEX_PR1.md a Codex junto con el paquete. Los archivos de docs son una propuesta de actualización académica; cotejar cambios antes de incorporarlos al repositorio. No reemplazar IMPLEMENTATION, TEST_RESULTS ni HANDOFF_CODEX con textos de Work. Se conserva la configuración ejecutable 0.5.0; 0.6.0 identifica esta edición del informe, no un contrato admitido por el programa actual.

El paquete contiene evidencia nueva de revisión y no duplica el repositorio ni las 60 exportaciones originales. Esas fuentes pertenecen al ZIP recibido y al commit revisado. La información histórica de HANDOFF_WORK se conserva como antecedente y el cierre R1 prevalece para el estado actual.
