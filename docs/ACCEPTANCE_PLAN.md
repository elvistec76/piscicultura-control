# Plan de aceptación de la especificación matemática

SPC-AGUA-001 · Versión 0.5.0 · 2026-10-14 · Propietario Work.
Todos los casos están PENDIENTES DE EJECUCIÓN POR CODEX. Los umbrales fueron aprobados como criterios de diseño en etapa 4; no son resultados observados. La aceptación del software no valida un estanque real.

## 1 Configuración de referencia y escenarios

Usar MODEL_DEFAULTS.json y MATHEMATICAL_MODEL.md. Cada escenario se ejecuta con cada una de las tres especies salvo indicación. Registrar cambios al default y guardar la tabla de ruido, eventos, versiones y entorno.

| Escenario | Configuración exacta respecto al default | Finalidad |
|---|---|---|
| S0 equilibrio | 6 h; x0=r; z0=v*; abierto calibrado; Eamp=0; F=0; ruido=0; sin eventos | Verificar equilibrio nominal realizable |
| S1 nominal | 48 h; x0=r; z0=v*; Eamp=2; F=1 en [8,8.5) y [20,20.5) h de cada día; ruido default | Ejecutar ambas estrategias en condiciones variables |
| S2 recuperación | 12 h; T0=rT−2, C0=rC−1.5, p0=6.8, U0=40, h0=0.85; z0=v*; Eamp=0; F=0; ruido=0 | Comparación principal de recuperación |
| S3 fuga | S1, pero 12 h y fuga adicional 0.0008 m³/s en [6,7) h | Comprobar respuesta del nivel y consumos de agua |
| S4 carga térmica | S1, pero 24 h y dTe=+20 °C en [6,12) h | Comparar perturbación térmica demostrativa severa |
| S5 lectura ausente | S1, pero 6 h y sensor de oxígeno MISSING en [2,2.1666666667) h; fin exacto=7800 s | Verificar política ante medición inválida |
| S6 aireación averiada | S1, pero 12 h y gA=0 en [2,6) h | Observar limitación y retorno de disponibilidad |
| S7 sesgo plausible | S1, pero 6 h y sesgo de oxígeno −0.5 mg/L en [2,4) h | Verificar que auditoría no equivale a detección automática |
| S8 rendimiento | S1 sin interfaz, una corrida cerrada por repetición, base SQLite nueva | Medir carga de 2880 intervalos y persistencia |
| S9 capacidad insuficiente | S1, pero 8 h y fuga adicional 0.003 m³/s en [2,8) h | Exigir fallo explícito al salir del dominio; no corrección artificial |

S4 es una prueba de estrés virtual y no una predicción de clima local. En S5 usar los segundos exactos 7200 y 7800, ambos múltiplos de 60. S8 se mide con tilapia; los otros perfiles deben pasar funcionalmente S1. No se exige que el cerrado gane todos los escenarios.

## 2 Casos de aceptación

| ID | Caso y procedimiento | Criterio propuesto | Requisitos principales |
|---|---|---|---|
| AC01 | Revisar JSON, perfiles y procedencia; probar valores inválidos | Tres perfiles correctos; rechazo de datos no finitos, geometría inválida, eventos fuera de malla o referencia de O2 no realizable | RF01, RF02, RF11, RNF02 |
| AC02 | Saturación de O2 con T=10,20,30 °C, P=101325 Pa, S=0 | 11.28794737, 9.09242604 y 7.55879605 mg/L, error absoluto <=1e−6; P=1 atm y S=0 dan FP=FS=1 | RF03, RNF02 |
| AC03 | Volumen aislado: A=10, h0=1, qin=.001, qout=.0002, ql=.0001, qe=.00001, qr=0, tasas constantes, 600 s | h final=1.0414 m, error <=1e−7 m; entradas 0.6 m³ y salidas descargadas 0.12 m³ | RF03, RF10 |
| AC04 | Calor aislado: V=10, T0=20, H=0, sin caudales, potencia constante 10000 W, 3600 s | T final=20.8600095557 °C, error <=1e−6 °C | RF03, RNF02 |
| AC05 | Oxígeno aislado: T=20 constante, V constante, k0=1e−4, sin demanda, caudales ni aireador; C0=2; 3600 s | C=Csat+(2−Csat) exp(−0.36), error <=1e−5 mg/L | RF03, RF05 |
| AC06 | pH aislado con actuadores, alimentación y dp_ext anulados; p0=8; 3600 s | p=7.4+0.6 exp(−1/24), error <=1e−6 | RF03 |
| AC07 | Turbidez aislada: sin fuentes, caudales ni filtro, ks=2e−5, U0=40, 3600 s | U=40 exp(−0.072), error <=1e−4 NTU | RF03, RF05 |
| AC08 | Respuesta auxiliar: z0=0, v=1, tau=30 s; después probar cambio firmado +1 a −1 | z(30)=1−exp(−1), error <=1e−7; las acciones opuestas no son positivas al mismo tiempo; dividir integral al cruce cero | RF05, RNF02 |
| AC09 | Umbrales de cada controlador, incluyendo igualdad y memoria | Cumplir exactamente sección 10 del modelo; apagado no implica inversión en el mismo muestreo; abierto no cambia orden al alterar y | RF06, RF04 |
| AC10 | S0 en cada especie | Permanecer dentro de tolerancias de reproducción respecto a x0 durante 6 h; comandos calculados dentro de sus dominios | RF03, RF06, RF10 |
| AC11 | S1 dos veces en el mismo entorno y realización | 2881 muestras, 2880 decisiones; estados COMPLETED; diferencias máximas de x dentro de tolerancias de reproducción | RF03, RF09, RF11, RNF01 |
| AC12 | S2 abierto y cerrado | Cerrado completa; cada variable recupera banda antes de 14400 s y permanece dentro >=95 % del tramo [4,12] h; J cerrado <=0.8 J abierto | RF06, RF10 |
| AC13 | S3 y S4 con ambas estrategias | Registrar efectos, alarmas y métricas; en cerrado, nivel vuelve a banda antes de 1 h tras fin de S3 y no sale del dominio; cerrado S4 no sale del dominio y no oculta saturación | RF07, RF08, RF10 |
| AC14 | S5 y S7 | S5 cerrado termina FAILED exactamente a 7200 s, sin decisión en ese instante; abierto conserva sus comandos y registra ausencia. S7 conserva sesgo sin inventar diagnóstico automático | RF04, RF07, RF08 |
| AC15 | S6 y S9 | gA=0 produce acción efectiva nula durante avería. En S9 registrar cruce de límite de nivel y FAILED con instante y estado de terminación, sin recortar h a referencia o límite | RF05, RF07, RF08 |
| AC16 | Pausar y continuar S1; repetir command_id; refrescar pestañas | Misma serie que corrida sin pausa; ninguna muestra extra al refrescar; un reintento no duplica pasos ni filas | RF03, RF09, RNF05 |
| AC17 | Forzar fallo de escritura en medio de un lote, abrir historial y exportar | Ningún lote parcial confirmado; causa explícita; historial anterior íntegro; JSON/CSV con unidades, versiones y corridas; huérfanas se distinguen de completadas | RF09, RF11, RNF03, RNF07, RNF09 |
| AC18 | Refinamiento numérico de S2 | Repetir con max_step=5 s, rtol=1e−9 y atol 100 veces menores; misma malla de control y ruido; diferencias de x en malla bajo tolerancias de refinamiento | RF03, RF10, RNF01 |
| AC19 | Indicadores con serie sintética x=[0,2,0], r=0, banda [−1,1], tiempos=[0,1,2] | IAE trapezoidal=2 unidad·s y tiempo fuera=1 s; se usa convención izquierda; no sumar magnitudes con unidades distintas | RF10, RNF02 |
| AC20 | S8, ejecución local sin red y sin presentación | Núcleo ejecutable sin Streamlit/Plotly; consulta y exportación disponibles sin red; mediana <=60 s bajo equipo y protocolo descritos | RNF04, RNF08, RNF10 |

Los casos aislados anulan términos del modelo con una configuración de prueba declarada; no cambian ecuaciones a escondidas. Deben construirse entradas que mantengan constantes las magnitudes indicadas. No se interpretan esos ensayos como estanques poblados reales.

## 3 Tolerancias y fórmulas

Orden de variables T,C,p,U,h.

- Reproducción en entorno fijado: error absoluto máximo (1e−5 °C,1e−5 mg/L,1e−6,1e−4 NTU,1e−7 m).
- Refinamiento AC18: (0.002 °C,0.002 mg/L,0.0002,0.02 NTU,0.00002 m).
- Recuperación: primera muestra en banda seguida por 1800 s consecutivos en banda. AC12 exige que el comienzo de esa ventana sea anterior o igual a 14400 s.
- Fracción en banda de AC12: complemento de tiempo fuera, usando indicador de extremo izquierdo y denominador 8 h en [4,12] h. Las cinco variables deben cumplir individualmente.
- J: fórmula de la sección 14 del modelo sobre el horizonte completo de S2. No se permite comparar un tramo truncado contra un horizonte completo para dar por satisfecho AC12.
- Si el abierto o cerrado de S2 falla antes de 12 h, AC12 no se aprueba automáticamente por menor J; informar fallo y revisar la especificación.
- La energía parcial de 10000 W constantes durante 3600 s debe ser 10 kWh si solo se incluye ese consumo; tolerancia 1e−6 kWh. La actividad virtual de pH no se convierte a dosificación física.

Las diferencias de conmutación en refinamiento pueden causar diferencias puntuales si una lectura cae casi exactamente en un umbral. No se amplían tolerancias silenciosamente: documentar el caso y proponer ajuste del diseño si AC18 no pasa. No se confunde una prueba numérica con un estudio analítico de estabilidad global.

## 4 Rendimiento y entorno de referencia

Carga S8: 48 h, intervalo 60 s, diez estados, cinco sensores, 2880 integraciones, 2881 muestras, registro de decisiones, ocho acciones efectivas, eventos y métricas en una base nueva. Medir desde preparación de realización hasta confirmación de resultados y métricas. Excluir instalación/importaciones iniciales, interfaz, gráficos y exportación a imagen.

Equipo de referencia para esta meta propuesta: computadora local de 64 bits, al menos dos núcleos de CPU de 2 GHz, 8 GB de RAM y unidad SSD, sin otras cargas intensivas. Codex registrará modelo exacto de CPU, RAM, almacenamiento, sistema operativo y versiones. Ejecutar tres veces con base nueva y misma configuración; informar las tres duraciones y mediana. Meta: mediana <=60 s. Si el equipo no corresponde, reportar rendimiento como no evaluado para este criterio y conservar la medición descriptiva; no declarar cumplimiento sin ese contexto.

## 5 Evidencias y responsabilidades

Codex redactará TEST_RESULTS con caso, configuración, versión, comando de reproducción, resultado esperado, resultado observado, error o duración y estado. IMPLEMENTATION describirá módulos y contratos reales; HANDOFF_CODEX informará diferencias y problemas. Work no llena esos archivos con resultados supuestos.

Todos los AC01 a AC20 y RNF siguen pendientes. Si un objetivo de desempeño no se alcanza, se revisarán modelo, controlador o criterio con justificación y nueva versión. No se reetiquetará un fallo como éxito ni se elegirá únicamente una corrida favorable.

## 6 Comprobación complementaria de interfaz

La matriz numérica AC01 a AC20 no sustituye la revisión de todos los subrequisitos. Codex vinculará cada uno de los 33 RF detallados y 10 RNF a una evidencia. En particular, revisar RNF06 mediante recorrido de configuración, ejecución, alarmas, comparación e historial: textos en español, unidades, procedencia, calidad y estados visibles; comprobar RF01.3 al duplicar un perfil y preservar corridas previas. RF08.1 exige las cinco series, bandas y acciones; RNF08 exige además gráficos e historial sin red. Estas comprobaciones pueden ser manuales, registrando versión, pasos y resultado; no inventar identificadores AC adicionales ni marcar toda una familia como aprobada por una sola prueba parcial.
