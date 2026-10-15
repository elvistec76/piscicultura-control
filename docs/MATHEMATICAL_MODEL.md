# Especificación matemática de la simulación

SPC-AGUA-001 · Versión 0.5.0 · Modelo M-AGUA-DEMO-1 versión 1.0.0 · 2026-10-14.
Estado: etapa 4 aprobada por el estudiante mediante «aprobado» el 14 de octubre de 2026; sin implementación ni validación experimental. Modelo académico aprobado para implementación, no validado en campo.
Propietario: Work. MODEL_DEFAULTS.json y ACCEPTANCE_PLAN.md forman parte de esta especificación.

## 1 Naturaleza y supuestos

Modelo académico de parámetros concentrados para un estanque rectangular bien mezclado. No representa estratificación, crecimiento, reproducción, enfermedades, amoníaco, química completa ni instalaciones de campo. La biomasa permanece fija en 50 kg por defecto. Las tres especies se diferencian mediante perfiles y temperatura de referencia; los coeficientes biológicos comunes son demostrativos y no caracterizaciones validadas de cada pez.

La ecuación de saturación del oxígeno se toma del memorando USGS WQ.2011.03, anexo ecuaciones 1 y 7–11, página PDF 6. Los balances y acoplamientos restantes son formulaciones propuestas; sus coeficientes son demostrativos salvo las aproximaciones físicas declaradas. pH y turbidez son modelos empíricos, no balances químicos ni conversiones a sólidos. Los valores no son recomendaciones para operación real.

## 2 Estado y unidades

Tiempo t en segundos. Estado físico x=(T,C,p,U,h): °C, mg/L de oxígeno, pH adimensional, NTU y m. Geometría A en m² y volumen V=A h en m³. El factor 1000 convierte m³ a litros en la demanda de oxígeno.

Estados auxiliares z=(zT,zC,zp,zU,zh), adimensionales. zT,zp,zh pertenecen a [-1,1]; zC,zU a [0,1]. El sistema integrado contiene diez estados, en el orden x seguido de z. Los cinco estados auxiliares representan respuesta de actuadores, no cinco nuevas variables de calidad.

Las acciones dobles usan un solo estado firmado por pareja. Así, calentamiento y enfriamiento, incremento y disminución de pH, y llenado y vaciado no actúan en oposición simultáneamente. El recambio explícito de agua es un flujo adicional coordinado, por defecto cero.

## 3 Actuadores y capacidades

Para cada grupo j: dzj/dt=(vj−zj)/tau_j, con vj constante durante cada intervalo de control y tau_j=30 s por defecto. El comando cerrado pertenece a {-1,0,1} en grupos firmados y {0,1} en aireación y filtración. El abierto puede utilizar cualquier valor admisible continuo. Limitar órdenes a su dominio y registrar la limitación; no recortar el estado físico para corregir errores.

Definir pos(a)=max(a,0). Disponibilidades gH,gK,gA,gB,gD,gF,gI,gO en [0,1], inicialmente 1:

- aH=gH pos(zT); aK=gK pos(−zT).
- aA=gA zC; aB=gB pos(zp); aD=gD pos(−zp).
- aF=gF zU; aI=gI pos(zh); aO=gO pos(−zh).
- qin=Qin aI+qx; qout=Qout aO+qx, ambos en m³/s.

Las ocho acciones efectivas se registran por separado. Una avería cambia g y puede introducir un salto en la acción efectiva; el estado del agua continúa siendo continuo. Se trata de una discontinuidad de disponibilidad, no de un ajuste instantáneo del agua. Los estados z continúan respondiendo al comando aunque la capacidad disponible sea nula.

Qin=Qout=0.002 m³/s; potencia térmica máxima de calentamiento y enfriamiento PH=PK=20000 W; qx=0 por defecto. No se exige una dosificación química en mL: aB y aD son intensidades virtuales normalizadas.

## 4 Dinámica del volumen y del nivel

dV/dt = qin + qr − qout − ql − qe.

dh/dt = (qin + qr − qout − ql − qe)/A.

qr: lluvia o aporte externo de agua; ql: fuga; qe: evaporación; todos no negativos en m³/s. A=10 m², h_ref=1 m y altura geométrica máxima 1.5 m. V0=10 m³ en el escenario nominal. qe=2e−7 m³/s; ql y qr de base son cero. La lluvia y los caudales se calculan como tasas, no saltos de nivel. La filtración recirculante no modifica V.

## 5 Dinámica de temperatura

Qnet = H(Te−T)+PH aH−PK aK.

dT/dt = Qnet/(rho cp V) + [qin(Tin−T)+qr(Tr−T)]/V.

H=250 W/K; rho=1000 kg/m³ y cp=4186 J/(kg K), aproximaciones constantes. Tin y Tr son temperaturas de entradas; por defecto coinciden con T_ref. Te=T_ref−2+Eamp sin(2 pi t/86400)+dTe(t), con Eamp=2 °C en el escenario nominal. S0 y S2 usan Eamp=0.

La descarga y la fuga llevan agua a la temperatura del estanque y cancelan en el balance específico bajo mezcla perfecta. Se omiten calor latente de evaporación, radiación separada, calor de equipos auxiliares y temperatura del suelo. Por eso es un balance térmico simplificado, no una predicción de campo.

## 6 Oxígeno disuelto

Definir fT=2^((T−20)/10), F(t) intensidad de alimentación adimensional no negativa y L(C)=C/(KC+C), KC=0.5 mg/L. La demanda se define como:

R = [rB B fT(1+0.5 F)/(1000 V)+rW fT] L(C).

dC/dt = (k0+kA aA)(Csat−C)−R + [qin(Cin−C)+qr(Cr−C)]/V + qe C/V.

rB=0.05 mg/(kg s), B=50 kg; rW=2.5e−5 mg/(L s); k0=1e−5 s⁻¹ y kA=6e−4 s⁻¹. Cin=Cr=0.95 Csat(T_ref,P,S), constantes de cada corrida. No usar Csat(T actual) para cambiar retroactivamente la composición de la entrada.

La evaporación se supone sin transporte de oxígeno disuelto; por eso aparece qe C/V. La descarga y la fuga de agua bien mezclada cancelan en la ecuación de concentración. Se omiten fotosíntesis explícita y demanda de sedimentos separada; sus efectos no se atribuyen al término rB. La demanda se anula cuando C=0; no se añade oxígeno libre al alcanzar un mínimo.

### 6.1 Saturación bibliográfica

K=T+273.15; P_atm=P_Pa/101325; S en ‰; exp y ln son exponencial y logaritmo naturales.

ln(C0)=−139.34411+157570.1/K−66423080/K²+12438000000/K³−862194900000/K⁴.

FS=exp[−S(0.017674−10.754/K+2140.7/K²)].

w=exp(11.8571−3840.70/K−216961/K²).

theta=0.000975−1.426e−5 T+6.436e−8 T².

FP=(P_atm−w)(1−theta P_atm)/[(1−w)(1−theta)].

Csat=exp(ln(C0)) FS FP, en mg/L.

Fuente: U.S. Geological Survey (2011), ecuaciones 1 y 7–11 del anexo. El dominio bibliográfico es T de 0 a 40 °C, P de 0.5 a 1.1 atm y S de 0 a 40 ‰. El proyecto restringe S a 0–0.5 ‰ para sus perfiles de agua dulce. P inicial=101325 Pa y S=0; no representan automáticamente La Paz ni un estanque real.

Antes de iniciar, comprobar rC+deltaC < 0.98 Csat(T_max_operativo,P,S). Si no se cumple, rechazar el perfil modificado con explicación de inviabilidad de la referencia. La comprobación no garantiza capacidad bajo cualquier perturbación; solo evita un objetivo nominal incompatible con la saturación considerada.

## 7 pH empírico

dp/dt = kp(pbg−p)+gp(aB−aD)+dp_ext(t)−gf F(t).

kp=1/86400 s⁻¹; pbg=7.4; gp=1e−4 s⁻¹; gf=2e−5 s⁻¹. dp_ext es una tasa externa firmada con unidad s⁻¹. p representa directamente una salida empírica, adimensional.

Esta ecuación es una aproximación fenomenológica declarada. No modela actividad de hidrógeno, alcalinidad ni carbono inorgánico y no calcula pH de mezclas, concentraciones de reactivo o dosificaciones reales. Los efectos del recambio y de la temperatura sobre pH se omiten. La escala logarítmica de su definición se respeta al no presentar esta ecuación como un balance químico. Se podrá reemplazar en una versión posterior sin cambiar el contrato de salida p.

## 8 Turbidez empírica

dU/dt = [qin(Uin−U)+qr(Ur−U)]/V+sU(1+F)−(ks+kF aF)U+dU_ext(t).

sU=5e−4 NTU/s; ks=2e−5 s⁻¹; kF=2e−4 s⁻¹; Uin=Ur=5 NTU. dU_ext es un aporte externo no negativo en NTU/s. Es una aproximación empírica de la señal óptica; la mezcla lineal es un supuesto del índice virtual, no una ley de mezcla de turbidez real. No se convierte a mg/L de sólidos ni a centímetros Secchi. No se incluye concentración por evaporación ni resuspensión; se declara esa limitación.

## 9 Parámetros y perfiles

MODEL_DEFAULTS.json contiene todos los valores de esta versión, unidades en nombres de campo y metadatos de origen. Las temperaturas de referencia se seleccionan dentro de antecedentes B01, B03 y B09; son valores derivados elegidos para la demostración. Las otras consignas, bandas, límites y umbrales son demostrativos. No se rotularán como rangos certificados por especie.

| Perfil | rT y banda °C | rC y banda mg/L | pH objetivo y banda | Turbidez objetivo y banda NTU | Nivel objetivo y banda m |
|---|---|---|---|---|---|
| Tilapia del Nilo | 28.5; 27–30 | 6; 5–8.5 | 7.5; 7–8 | 10; 0–20 | 1; 0.9–1.1 |
| Trucha arcoíris | 14; 13–15 | 9; 8–11.5 | 7.5; 7–8 | 10; 0–20 | 1; 0.9–1.1 |
| Carpa común | 25; 23–26 | 6; 5–8.5 | 7.5; 7–8 | 10; 0–20 | 1; 0.9–1.1 |

Límites críticos demostrativos: T tilapia [26,31], trucha [12,16], carpa [22,27]; C tilapia y carpa [4,9.5], trucha [6,12.5]; pH [6.5,8.5]; U [0,50]; h [0.8,1.2]. Para U solo existe alarma superior. Un valor exactamente en el límite no activa alarma; la activa superar el límite hacia el exterior. Volver al intervalo lo desactiva. La alarma crítica tiene prioridad de presentación y no impone acciones ocultas.

Los límites de operación y los críticos son distintos de los dominios matemáticos: T [0,40], C [0,20], p [4,10], U [0,200], h [0.25,1.45]. Cruce hacia fuera del dominio causa FAILED; los límites críticos solo generan alarmas. Los estados iniciales pueden estar fuera de la banda operativa, siempre que estén dentro del dominio matemático.

Los parámetros deben ser finitos. A, rho, cp, tau y KC serán estrictamente positivos; tasas, biomasa, capacidades, desviaciones y caudales no negativos. Horizonte entre 1 y 72 h; intervalo de control entre 30 y 300 s, divisor exacto del horizonte; default 48 h y 60 s. Eventos en esa malla, con inicio menor que fin y sin exceder el horizonte. Configuraciones de prueba pueden anular tasas para aislar balances, dejando esos cambios registrados.

## 10 Control cerrado por histéresis

Se elige control muestreado sin acción integral. No hay ganancias PID ni anti-windup pendientes. La memoria del controlador son cinco modos inicializados a cero, distintos de los estados de respuesta z.

### 10.1 Grupos firmados T, p y h

DeltaT=0.3 °C, Deltap=0.15 y Deltah=0.03 m. En modo cero: si y<r−delta, pasar a +1; si y>r+delta, pasar a −1; en otro caso, mantener cero. En modo +1: mantener hasta y>=r, entonces pasar a cero. En modo −1: mantener hasta y<=r, entonces pasar a cero. Al desactivar no se invierte en ese mismo muestreo: la decisión contraria requiere el siguiente. Los signos positivos significan calentar, incrementar pH o llenar.

### 10.2 Aireación y filtración

En aireación: estando apagada, encender si yC<=rC−0.2; estando encendida, apagar si yC>=rC+0.2. En filtración: encender si yU>=15 y apagar si yU<=10. Conservar el modo entre umbrales. Este uso de dos umbrales sigue el principio de histéresis; las igualdades y valores concretos son decisiones de este proyecto, no parámetros copiados de un equipo.

Las órdenes v son las salidas de esos modos. Una medida requerida inválida detiene la corrida cerrada en el instante del muestreo, antes de una nueva orden. Una medida válida pero sesgada puede producir una decisión equivocada; no se consulta x para corregirla.

## 11 Lazo abierto calibrado y condiciones iniciales

La comparación principal usará comandos constantes calculados para el equilibrio nominal sin ciclo ambiental ni alimentación, no actuadores arbitrariamente apagados. Utilizar Vref=A href, qin*=qe, qout*=0, Te*=rT−2, Tin=rT y disponibilidad completa.

vT*=H(rT−Te*)/PH=0.025.

Definir Rref con T=rT, C=rC, F=0 y V=Vref. Entonces:

vC*={ [Rref−(qe/Vref)Cin]/[Csat(rT,P,S)−rC]−k0 }/kA.

vp*=kp(rp−pbg)/gp.

vU*={ [sU+(qe/Vref)(Uin−rU)]/rU−ks }/kF.

vh*=qe/Qin=0.0001.

Comprobar los dominios de v; rechazar una calibración no realizable, sin recortarla silenciosamente. Los valores completos se guardan en el JSON, no solo los redondeados de una tabla. En cada comparación, ambas corridas arrancan con el mismo x0 y z0=v*. El controlador cerrado comienza con memoria de modos cero; el abierto usa v* durante toda la corrida. La configuración registra esa diferencia de estrategia.

Pueden admitirse otros programas abiertos por tiempo predefinidos, pero no se usarán para la aceptación de la comparación principal. Las mediciones observacionales inválidas no modifican las órdenes abiertas. Un error numérico termina el experimento en ambos modos.

## 12 Sensores y realización exógena

yj,k = xj(tk)+bj,k+sigma_j epsilon_j,k. Sigma=(0.03,0.02,0.01,0.1,0.002), en las unidades respectivas. Epsilon se obtiene de una normal estándar, recortando el ruido a [-3,3] antes de escalarlo; no se recorta x. Semilla=20261014. Generar una tabla completa (N+1) por cinco columnas, conservarla y usar la misma en ambas estrategias.

Generar mediante numpy.random.Generator con PCG64(seed), una matriz (N+1,5) en el orden fijo de variables, y luego recortar epsilon. La tabla persistida es la autoridad de reproducción; registrar algoritmo generador y entorno. Los refinamientos del integrador reutilizan esa tabla: no generan ruido en evaluaciones internas. El ruido es de medición, no una fuerza aleatoria integrada.

Rangos instrumentales: T [-5,45], C [0,25], p [0,14], U [0,500], h [0,2]. Una lectura no finita o fuera de rango se marca INVALID y se entrega como nula con diagnóstico; no se sustituye por cero. Pérdida de lectura produce MISSING. Solo GOOD entra a una decisión cerrada.

Un sesgo se suma a la lectura; congelación conserva la última lectura GOOD anterior al inicio del fallo y no aplica nuevo ruido mientras dure. Si no existe lectura anterior, produce MISSING. Sesgo o congelación plausibles continúan GOOD: el motor registra la inyección para auditoría sin dársela al controlador. Tras el fin se recupera el muestreo ordinario usando la fila de ruido del índice temporal correspondiente.

## 13 Secuencia temporal e integración

tk=k Delta; default Delta=60 s, H=172800 s, N=2880. Cada evento usa el intervalo [inicio,fin); sus efectos entran exactamente en la malla. Eventos de grupos distintos se combinan; se suman tasas de perturbación, se suman sesgos y se toma el menor factor de disponibilidad coincidente. Dos congelaciones o una congelación con pérdida del mismo sensor se rechazan para evitar ambigüedad. Pérdida y sesgo simultáneos se pueden rechazar como configuración redundante.

1. Al preparar: congelar configuración, realización y x0,z0. No medir ni integrar por dibujar la interfaz.
2. Para cada k de 0 a N−1: aplicar condiciones de escenario vigentes en tk; registrar cambios de eventos y fallos; obtener o reutilizar la muestra k una sola vez.
3. Evaluar alarmas medidas; si cerrado y alguna lectura requerida no es GOOD, confirmar muestra y causa de fallo sin otra decisión ni avance físico.
4. Obtener decisión k con lectura k y referencia; en abierto consultar solo el programa. Mantener v durante [tk,tk+1).
5. Integrar los diez estados hasta tk+1 con RK45, rtol=1e−7 y atol=(1e−8,1e−8,1e−9,1e−7,1e−10,1e−9,1e−9,1e−9,1e−9,1e−9); max_step=10 s o Delta/6, el menor. Las fórmulas del ambiente se evalúan en el tiempo del integrador; F y fallos son constantes por tramos de la malla.
6. En el extremo tk+1: procesar eventos de ese instante, producir muestra k+1 una sola vez, evaluar alarmas y guardar el lote con decisión k, acciones y estado final. La próxima llamada reutiliza esa muestra y el cursor de eventos ya procesados; no repite eventos ni consume otra fila de ruido. Una lectura terminal inválida en cerrado deja FAILED; no se genera una decisión N.
7. Confirmar reloj, contador y recibo de comando después de la transacción. En k=N−1 y sin fallos, marcar COMPLETED.

La muestra 0 se guarda en el primer lote aceptado; al completar se tienen N+1 muestras y N decisiones. Una pausa no integra ni genera muestras. Una orden de avance repetida devuelve el recibo previo. Si falla una transacción, descartar el avance provisional y terminar desde el último estado confirmado; conservar el error cuando sea posible sin fingir confirmación.

Detectar cruces hacia el exterior de los dominios con eventos terminales e identificar su instante. Conservar el estado de terminación en runs/termination_state y evento, aunque caiga fuera de la malla; no inventar una lectura con ruido interpolado allí. Las muestras anteriores siguen en su malla. No recortar el agua. Desviaciones numéricas negativas de C o U de magnitud menor que 1e−7 se señalan como tolerancia numérica, se conservan en auditoría y no se presentan como mediciones válidas; si afectan una decisión cerrada, se aplica su regla de invalidez. Una salida mayor causa FAILED. Un fallo de dominio dentro del intervalo confirma un resultado parcial con la decisión ya aplicada, el instante y el estado de terminación; no inventa una muestra de malla ni un intervalo completo. El recibo del comando conserva ese resultado terminal y permite reintento sin repetir integración. La detección requiere cruce hacia fuera: un estado inicial exactamente cero que permanece cero no es un fallo por sí mismo.

## 14 Registro de acciones e indicadores

Para cada intervalo, guardar comandos, z inicial/final, disponibilidad y acciones efectivas medias. Como z tiene respuesta de primer orden a comando fijo, puede reconstruirse: z(tk+s)=v+(z(tk)−v) exp(−s/tau). Si un grupo firmado cruza cero, separar el intervalo en la raíz para integrar pos(z) y pos(−z); no usar pos(promedio z) como promedio de la acción. Guardar los parámetros permite reconstruir las curvas.

Métricas principales sobre x; métricas sobre y separadas y con cobertura de datos. Muestreo final irregular por terminación se incorpora solo a la evaluación de x mediante termination_state. Las aproximaciones temporales se declaran:

- IAE_j: suma trapezoidal de |xj−rj| por intervalo, en unidad_j·s.
- Tiempo fuera de banda: suma de Delta_i si el estado izquierdo está fuera; fracción fuera=tiempo fuera/duración observada. El límite exacto se considera dentro. Para U solo se penaliza superar 20 NTU.
- J: promedio de IAE_j/(sj H_eval), con escalas sT=(Tmax−Tmin)/2, sC=(Cmax−Cmin)/2, sp=0.5, sU=20 y sh=0.1. J es adimensional y no sustituye métricas individuales.
- Recuperación: primera muestra dentro de banda tras el inicio del caso, seguida de al menos 1800 s consecutivos dentro. Si no ocurre, informar no recuperado, sin asignar cero. Recuperación conjunta=max de las cinco recuperaciones.
- Agua repuesta y descargada: integrales de qin y qout en m³, incluyendo recambio; lluvia, fuga y evaporación por separado.
- Actividad pH: integrales de aB y aD, en segundos normalizados; no en mL.
- Energía parcial estimada: integrar PH aH+PK aK/COP+300 aA+200 aF+100 aI+100 aO, dividir entre 3.6e6 para kWh; COP=3 demostrativo. Excluye dosificadores, recambio externo y otros consumos; no llamarla energía total de una piscigranja.

Si falta una medición y, no interpolar para ocultarla: informar cobertura y no calcular una integral completa de y sin una regla adicional explícita. Para comparación con terminación anticipada, usar tramo común más un resumen separado del horizonte solicitado y causas; una corrida fallida no se declara ganadora por observar menos tiempo.

## 15 Comprobaciones algebraicas del diseño

Son cálculos de las fórmulas propuestas, no resultados de la aplicación: Csat a 20 °C, una atm y S=0 es 9.09242604 mg/L; a 10 °C es 11.28794737; a 30 °C es 7.55879605. Son referencias calculadas a partir de la transcripción, no mediciones de campo ni valores extraídos de una tabla independiente.

Para 10 m³, potencia aislada de 10000 W durante 3600 s produce DeltaT=0.8600095557 °C si no hay otros términos. Para A=10 m², qin=0.001, qout=0.0002, ql=0.0001, qe=0.00001 y qr=0, dh/dt=0.000069 m/s. Sirven como casos con solución analítica en ACCEPTANCE_PLAN.

Comandos abiertos de aireación calculados: tilapia 0.416728 aproximadamente, trucha 0.202467 y carpa 0.247557. Están dentro de [0,1] en el caso nominal. Esta comprobación de realizabilidad no demuestra estabilidad, recuperación ni superioridad del lazo cerrado.

## 16 Alcance de aceptación

ACCEPTANCE_PLAN fija escenarios, soluciones de referencia, tolerancias, recuperación, comparación, fallos, persistencia y rendimiento. Todos figuran pendientes de ejecución por Codex. Los valores numéricos constituyen objetivos de aceptación propuestos, no resultados observados. Cualquier cambio de ecuación, perfil o criterio requiere nueva versión y registro de impacto.
