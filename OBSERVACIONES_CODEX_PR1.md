# Correcciones solicitadas para el PR 1

Base revisada: 41ec9f2d21edb21499c14437b3d00dd9e135e0d2 · software 0.1.0 · SPC-AGUA-001 0.5.0 · modelo 1.0.0.

La revisión recomienda **solicitar cambios y mantener el PR en borrador**. La suite original vuelve a pasar 58/58 y los resultados de S2 se corroboran, pero aparecen tres defectos fuera de su cobertura. No integrar ni aprobar formalmente el PR como consecuencia de este documento. El trabajo solicitado se limita a correcciones y nuevas evidencias; preservar las ecuaciones, parámetros y tolerancias aprobadas.

## OBS01 Prioridad alta Bandas degeneradas y errores de métricas

Ubicación: piscicultura/config.py, líneas 150–156; piscicultura/metrics.py, líneas 35–37; piscicultura/service.py, líneas 55–56 y 72–87.

La validación permite banda térmica [28.5,28.5]. Se acepta la configuración S0 abierta, horizonte 3600 s. El motor completa y guarda COMPLETED; J divide entre escala cero, produce NaN y save_metrics lanza ValueError «Out of range float values are not JSON compliant: nan». No se guardan métricas. Al avanzar 60 s y detener se reproduce el mismo problema con STOPPED. La interfaz no cubre de manera consistente este camino de fallo. La banda de oxígeno también determina una escala y necesita la misma protección.

Corrección solicitada: rechazar bandas T/C con ancho <=0 antes de preparar una corrida; identificar variable y campo en el error. Validar finitud de resultados derivados y gestionar su fallo de forma explícita, conservando datos ya confirmados. Distinguir final de integración y disponibilidad de métricas. No convertir NaN a cero, no inventar métricas ni modificar J para evitar la causa. Si proponen un nuevo estado o campo de diagnóstico, describir su contrato para revisión de Work.

Evidencia requerida: pruebas de rechazo para T y C con límites iguales; nueva prueba de generación/persistencia de métricas fallida con causa visible y datos previos intactos; recorrido de interfaz sin excepción no gestionada. La configuración inválida no debe crear una corrida. Repetir AC01, AC12, AC17 y AC19 según el impacto, además de la regresión completa.

Afecta RF02.2, RF02.3, RF10.2, RNF02 y RNF07.

## OBS02 Prioridad media Regla unilateral de turbidez en y

Ubicación: piscicultura/metrics.py, líneas 12–13 y 45–47.

series_metrics aplica la excepción de turbidez solo cuando recibe cinco columnas. evaluate calcula cada serie y por separado y pierde su identidad. Reproducción: banda U=[5,20], rU=10, xU=yU=2 NTU, tiempos [0,1800]. La configuración es admitida. Métricas x: fuera=0 s y recuperación=0 s. Métricas y: fuera=1800 s y recuperación=null. La sección 14 establece que U solo penaliza el exceso superior.

Corrección solicitada: pasar la identidad de variable o la regla de banda de forma explícita a la función de métricas. Aplicarla tanto a x como a y y en ventanas/comparaciones. Conservar cobertura y ausencia de datos; no rellenar lecturas inválidas. No cambiar el modelo a una penalización bilateral.

Evidencia requerida: prueba x=y con banda inferior positiva y valores válidos por debajo de ella; comprobar tiempo fuera, fracción, recuperación e IAE. Debe conservar IAE respecto a rU mientras no penaliza inferiormente la banda. Incluir exceso superior y datos ausentes. Repetir AC19 y pruebas de comparación afectadas.

Afecta RF10.2. No invalida las métricas originales S2 con banda U=[0,20].

## OBS03 Prioridad media Ventana temporal recortada

Ubicación: piscicultura/metrics.py, líneas 38–41 y convención izquierda en líneas 12–14.

S2 permite dt=135 s y horizonte 43200 s, sin eventos. El filtro t>=14400 selecciona como primer instante 14445, por lo que window_4_12h evalúa 28755 s y omite 45 s del tramo exigido de 28800 s. En una serie sintética con T fuera de banda a 14310 s y dentro en las demás muestras, informa fracción 1; al ponderar la intersección con [14400,43200] y la convención izquierda, el valor es 1−45/28800=0.9984375.

Corrección solicitada: calcular las intersecciones de los intervalos con la ventana exacta, mantener el denominador 28800 s y la regla izquierda para tiempo fuera; declarar la regla aplicable a IAE en extremos. Puede extraerse una función de evaluación de ventanas. No rechazar dt=135 solo para ocultar el problema: pertenece al dominio aprobado, salvo propuesta justificada de cambio de alcance para Work.

Evidencia requerida: caso anterior, extremos coincidentes y no coincidentes con la malla, y caso próximo al umbral de permanencia .95. Registrar duración e intervalo evaluados explícitos. Repetir AC12/AC19 y comprobar que dt=60 conserva las cifras de referencia dentro de tolerancia.

Afecta RF10.2. No cambia los resultados S2 originales con dt=60.

## OBS04 Correcciones documentales de Work

Se comprobó equivalencia binaria de los 12 documentos académicos/de especificación y los 4 diagramas entre el ZIP 0.5.0 y el árbol recibido de Codex. La duda técnica principal queda resuelta. No existe equivalencia completa de entrega: el README remoto solo tiene dos líneas y no coincide; PROMPT_INICIO_CODEX.txt y el Word consolidado están ausentes.

La frase «RNF01/RNF10 pendientes de aprobación» era un error de la documentación de Work. Los criterios se aprobaron en etapa 4; lo que seguía pendiente era su ejecución o aceptación. La propuesta corregida distingue RNF01 con evidencia y RNF10 pendiente de medición contextual. No atribuir esta contradicción a un cambio de ecuaciones realizado por Codex.

El paquete contiene el informe académico actualizado y propuestas de edición para docs propiedad de Work. Incorporarlas mediante comparación; no sobrescribir IMPLEMENTATION, TEST_RESULTS ni HANDOFF_CODEX. Los documentos históricos conservan su contexto. 0.6.0 es la edición académica de esta revisión; el programa evaluado continúa usando spec_version=0.5.0 y model_version=1.0.0. No cambiar esos identificadores en el código solo por el nombre del nuevo informe. Restaurar README e instrucciones y entregar acceso al Word; no es necesario versionar el binario en Git si se mantiene un enlace/documento de entrega adecuado.

## OBS05 RNF10 Pendiente de evaluación local

Mantener AC20 parcial y RNF10 pendiente/no evaluable en el hardware virtual aportado. Conservar los tres tiempos originales y su mediana descriptiva; no usar la reejecución de Work como acreditación de SSD local. Ejecutar S8 con tres bases nuevas en el equipo de referencia, registrar CPU, núcleos, RAM, almacenamiento, SO y versiones, y evaluar la mediana <=60 s. Si el equipo no reúne las condiciones del plan, registrar la limitación sin ampliar el criterio.

## Devolución solicitada

1. Commits de corrección de OBS01 a OBS03 y pruebas que fallen antes del arreglo y pasen después. Mantener ecuaciones y umbrales.
2. Reejecución de regresión apropiada, XML y exportaciones afectadas, sin sustituir ni atribuir como propios los registros anteriores de Work.
3. Actualizar los tres documentos propiedad de Codex con esperado, observado, versión, comandos y limitaciones. Conservar como históricos los 58/58 de la versión inicial; el nuevo conteo incluirá las pruebas añadidas y se identificará por commit.
4. Resolver OBS04 con los archivos académicos aprobados/propuestos y mantener OBS05 abierto hasta evidencia válida.
5. Solicitar nueva revisión de integración. La aceptación integral requiere cerrar los requisitos parciales y RNF10; una integración técnica con RNF10 abierto necesitaría una decisión explícita del estudiante que no equivalga a aceptación total.

No se publicaron comentarios ni se cambió el estado del PR desde esta revisión. Las observaciones están preparadas para que el estudiante las entregue a Codex.
