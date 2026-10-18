# Evidencias — Auditoría de equidad, mitigación y explicabilidad

**Alumno:** Julian Rachitzky · **Caso:** sistema de reclutamiento de Amazon (Dastin, 2018) · **Dataset:** Utrecht Fairness Recruitment dataset, empresa B (Burda & Van Otterloo, 2025)

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

### Interpretación (consigna 8.d)

> El patrón coincide con el del caso de Amazon (Dastin, 2018). La exactitud es casi la misma en los dos grupos (0,887 en mujeres y 0,877 en hombres), así que mirando solo esa métrica el modelo parece funcionar bien para todos. La tasa de selección muestra otra cosa: recomienda contratar al 11,3% de las candidatas y al 42,6% de los candidatos, casi cuatro veces más. Eso es la demographic parity difference de 0,313.
>
> La diferencia no viene de las calificaciones. En la empresa B las mujeres tienen mejor nota promedio (64,2 contra 60,8) y el doble de experiencia en programación (44% contra 21%), pero en los datos fueron contratadas en el 14,0% de los casos y los hombres en el 45,5%. El modelo aprende esa decisión histórica y la repite, que es lo que la unidad llama sesgo histórico (Mehrabi et al., 2021) y lo mismo que le pasó a Amazon al entrenar con diez años de CVs de una plantilla mayoritariamente masculina.
>
> La equalized odds difference de 0,345 sale de la tasa de verdaderos positivos: de las personas que en los datos sí fueron contratadas, el modelo encuentra al 84,5% de los hombres y al 50% de las mujeres (0,845 − 0,500 = 0,345). Una candidata que en la realidad fue contratada tiene la mitad de chances de que el modelo la recomiende que un candidato en la misma situación.

## Comparación antes / después de la mitigación

| Escenario | Exactitud | Demographic parity diff. | Equalized odds diff. |
|---|---|---|---|
| Modelo base (sin mitigar) | 0.881 | 0.313 | 0.345 |
| ExponentiatedGradient | 0.803 | 0.007 | 0.427 |
| ThresholdOptimizer | 0.793 | 0.044 | 0.477 |

![Comparación de métricas de equidad](outputs/comparacion_metricas.png)

### Interpretación (consigna 9.c)

> Sobre la métrica que se le pidió optimizar (paridad demográfica), las dos técnicas funcionaron: ExponentiatedGradient bajó la demographic parity difference de 0,313 a 0,007 y ThresholdOptimizer a 0,044. Después de mitigar, el modelo recomienda casi la misma proporción de mujeres que de hombres.
>
> Pero tuvo dos costos. La exactitud bajó de 0,881 a 0,803 y 0,793. Y la equalized odds difference empeoró (de 0,345 a 0,427 y 0,477): para igualar cuántas personas recomienda de cada grupo sin mirar el resultado real, el modelo empieza a equivocarse distinto con cada uno. Sube los aciertos y también los falsos positivos en las mujeres, y baja la tasa de verdaderos positivos en los hombres. Es lo que plantea la unidad: no hay una sola definición de equidad y dos métricas pueden ir en direcciones opuestas, así que elegir cuál priorizar es una decisión ética y no solo técnica (Verma & Rubin, 2018).
>
> Para comparar hice otra corrida con `FAIRNESS_CONSTRAINT=equalized_odds` (guardada en `outputs/corrida_equalized_odds/`):
>
> | Escenario | Exactitud | Demographic parity diff. | Equalized odds diff. |
> |---|---|---|---|
> | Modelo base (sin mitigar) | 0.881 | 0.313 | 0.345 |
> | ExponentiatedGradient | 0.858 | 0.201 | 0.054 |
> | ThresholdOptimizer | 0.861 | 0.186 | 0.076 |
>
> Con esa restricción pasa lo contrario: equalized odds baja a 0,054 perdiendo menos exactitud, pero queda una brecha de selección de alrededor de 0,19 a 0,20. Para contratación me parece más defendible esta segunda opción, porque busca que una candidata calificada tenga las mismas chances que un candidato calificado, en vez de forzar proporciones iguales sobre etiquetas históricas que ya vienen sesgadas. Ninguna de las dos arregla el problema de fondo, que es que la variable objetivo (la decisión de contratar del pasado) está contaminada.
>
> Otras limitaciones: las dos técnicas son aleatorizadas, así que las métricas mitigadas cambian un poco entre corridas (ExponentiatedGradient dio entre 0,800 y 0,807 de exactitud en distintas ejecuciones); ThresholdOptimizer necesita saber el género de cada candidato al momento de predecir, lo que en contratación puede ser un problema legal; y el test tiene 295 casos (133 mujeres), así que diferencias chicas no son confiables. Además el dataset es sintético: sirve para mostrar el mecanismo, no para estimar cuánto sesgo tenía el sistema real.

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

### Interpretación (consigna 10.b, vinculada a la consigna 4)

> Sí, SHAP sobre el modelo base hubiera mostrado el problema antes de usarlo. En la predicción 4, que es una candidata mujer, el género le resta 0,388 al log-odds de ser contratada (−0,19 por `gender_female` y −0,19 por `gender_male`). En el resumen global se ve que esa resta se aplica a todas las mujeres y que a los hombres el género les suma. Incluso la predicción elegida como la que "no discrimina" (la 0, un candidato varón) tiene una contribución del género de 0,281: en este modelo el género nunca es neutral, cambia el signo y algo la magnitud.
>
> El resumen global también muestra proxies, que es lo más parecido al caso de Amazon. La experiencia en programación (44% de las mujeres y 21% de los hombres) tiene aporte negativo, o sea que el modelo castiga un antecedente que debería sumar; lo mismo pasa con haber estudiado una carrera exacta. En cambio el club de debate (35% de los hombres contra 13% de las mujeres), el rugby (27% contra 8%) y la cantidad de idiomas suman. Es el mismo mecanismo que con la palabra "women's" o los verbos más comunes en CVs de hombres: aunque se sacara la columna de género, el sesgo seguiría entrando por estas variables.
>
> Por eso una auditoría previa tendría que combinar las dos cosas: métricas por grupo (MetricFrame) para ver que hay una brecha, y SHAP o LIME para entender qué variables la producen (Lundberg & Lee, 2017).

## Captura de la ejecución final

![Ejecución exitosa en el Codespace](outputs/captura_ejecucion.png)

## Referencias

- Burda, P., & Van Otterloo, S. (2025). Fairness definitions explained and illustrated with examples. *Computers and Society Research Journal*, 2025(2). https://doi.org/10.54822/PASR6281
- Dastin, J. (2018, 10 de octubre). Amazon scraps secret AI recruiting tool that showed bias against women. *Reuters*.
- Lundberg, S. M., & Lee, S. I. (2017). A unified approach to interpreting model predictions. *NeurIPS 30*.
- Mehrabi, N., Morstatter, F., Saxena, N., Lerman, K., & Galstyan, A. (2021). A survey on bias and fairness in machine learning. *ACM Computing Surveys, 54*(6), 1–35.
- Verma, S., & Rubin, J. (2018). Fairness definitions explained. *FairWare 2018*.

