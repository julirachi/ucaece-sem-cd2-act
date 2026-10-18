# Evidencias — Auditoría de equidad, mitigación y explicabilidad

_Generado automáticamente el 2026-10-18 15:26._

## Configuración de la corrida

- **Dataset:** data/empresa_b_limpio.csv
- **Columna objetivo:** `decision` (clase positiva: `True`)
- **Atributo sensible:** `gender`
- **Método de mitigación:** `ambos`
- **Restricción de equidad:** `demographic_parity`

## Auditoría de equidad — modelo base (pre-mitigación)

- **Exactitud global:** 0.881
- **Demographic parity difference:** 0.313
- **Equalized odds difference:** 0.345

### Métricas por grupo

| Grupo | Exactitud | Tasa de selección |
|---|---|---|
| female | 0.887 | 0.113 |
| male | 0.877 | 0.426 |

> TODO estudiante: interpretá esta tabla vinculándola con el sesgo documentado en el caso real analizado en la consigna 3 (¿el patrón que ves acá es consistente con lo que reportó el caso?).

## Comparación antes / después de la mitigación

| Escenario | Exactitud | Demographic parity diff. | Equalized odds diff. |
|---|---|---|---|
| Modelo base (sin mitigar) | 0.881 | 0.313 | 0.345 |
| ExponentiatedGradient | 0.803 | 0.007 | 0.427 |
| ThresholdOptimizer | 0.793 | 0.044 | 0.477 |

![Comparación de métricas de equidad](outputs/comparacion_metricas.png)

> TODO estudiante: discutí qué tan efectiva resultó la mitigación aplicada y qué limitaciones observaste (consigna 9.c) — por ejemplo, si mejoró la equidad pero bajó la exactitud, o si algún escenario no logró reducir la disparidad.

## Explicabilidad (SHAP) — modelo base

SHAP se aplica siempre sobre el modelo base, antes de cualquier mitigación: el objetivo es ver qué técnica de auditoría preventiva podría haber detectado el problema antes del despliegue (consigna 4).

### Predicción 4 — el atributo sensible más influyó

- Contribución absoluta de `gender`: 0.388
- Predicción del modelo: 1 · Valor real: 0

![SHAP de la predicción donde el modelo discrimina](outputs/shap_prediccion_discrimina.png)

### Predicción 0 — el atributo sensible casi no influyó

- Contribución absoluta de `gender`: 0.281
- Predicción del modelo: 1 · Valor real: 1

![SHAP de la predicción donde el modelo no discrimina](outputs/shap_prediccion_no_discrimina.png)

### Resumen global

![Resumen SHAP de todas las predicciones de test](outputs/shap_resumen.png)

> TODO estudiante: vinculá esta evidencia con la consigna 4 — ¿SHAP sobre el modelo base hubiera permitido detectar este problema antes del despliegue?
