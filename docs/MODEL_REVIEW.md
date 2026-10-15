# Revisión algebraica del modelo propuesto

Versión 0.5.0 · 2026-10-14. Cálculos de diseño; no ejecución de la aplicación ni prueba de aceptación aprobada.

Se evaluó el lado derecho en el equilibrio nominal construido para el lazo abierto, sin ciclo ambiental ni alimentación. Los residuos expresan coherencia de esa calibración, no estabilidad o validación de campo.

| Perfil | Saturación mg/L | Comando de aireación | Comprobación individual de las cinco tasas |
|---|---|---|---|
| Tilapia del Nilo | 7.759023675 | 0.416727638 | <1e−12 en las unidades de cada tasa |
| Trucha arcoíris | 10.305803762 | 0.202467150 | <1e−12 en las unidades de cada tasa |
| Carpa común | 8.263456698 | 0.247557273 | <1e−12 en las unidades de cada tasa |

Cada residuo se comparó individualmente en su propia unidad. No se sumaron tasas dimensionalmente distintas. Los números redondeados de la tabla no reemplazan los valores completos del JSON.

Las soluciones analíticas aisladas y los valores calculados de saturación están en MATHEMATICAL_MODEL y ACCEPTANCE_PLAN. AC01 a AC20 continúan pendientes de ejecución por Codex. No se integró aquí una corrida para afirmar recuperación, estabilidad, mejora porcentual o rendimiento.
