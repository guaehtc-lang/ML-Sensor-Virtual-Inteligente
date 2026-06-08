# Soft Sensor LT-411 — Proyecto de Machine Learning Industrial

## 1. Resumen del proyecto

Este proyecto desarrolla un **sensor virtual** (*soft sensor*) para estimar el nivel del cristalizador/evaporador **VB-01**, medido por el sensor físico **LT-411**.

La idea principal es sencilla:

> Si el sensor físico LT-411 se ensucia o empieza a medir mal, un modelo de Machine Learning puede estimar cuál debería ser el nivel esperado usando otras variables del proceso.

El objetivo del proyecto no es sustituir un sistema industrial real, sino construir una metodología clara, reproducible y defendible dentro de un bootcamp de Data Science.

---

## 2. Contexto industrial explicado de forma simple

El proceso corresponde a una planta de evaporación/cristalización de salmuera.

De forma simplificada:

1. La salmuera circula por el sistema.
2. Se calienta mediante vapor.
3. Se evapora parte del agua bajo vacío.
4. La salmuera se concentra.
5. El nivel del equipo principal se mide con el sensor LT-411.
6. Si ese sensor se ensucia, puede dar una lectura falsa.
7. El soft sensor intenta estimar el nivel esperado usando otras señales de proceso.

El modelo utiliza señales como presión, temperatura, vapor, vacío, densidad, intensidad de bomba y caudales para estimar el comportamiento esperado del nivel.

---

## 3. Objetivo del proyecto

El objetivo es construir una metodología reproducible para estimar el nivel físico esperado de **VB-01** mediante Machine Learning.

La variable objetivo es:

| Variable | Descripción | Uso |
|---|---|---|
| `LT411` | Nivel medido en VB-01 | Target del modelo |

El problema se plantea como una **regresión supervisada temporal**.

---

## 4. Datos utilizados

El proyecto utiliza datos históricos de PLC/SCADA en formato CSV.

Se trabaja únicamente con **7 CSV válidos**:

| CSV | Contenido principal |
|---|---|
| `Nivel_VB-01.csv` | Nivel LT-411, setpoint y válvula LV-411 |
| `Presion_VB01_HE01.csv` | Presiones PIT-410 y PIT-414 |
| `Temperatura_salmuera_HE01.csv` | Temperaturas TT-413 y TT-415 |
| `Den-Int_VB-01.csv` | Densidad DT-412 e intensidad/carga P-101 |
| `Vapor_HE-01.csv` | Caudal de vapor FQC-400-1 y válvula FV-400-1 |
| `Vacío.csv` | Presión de vacío PT-442 y válvula PV-442 |
| `Nivel_Caudal_PCT-02.csv` | Nivel LT-426 y caudal FT-428 |

Periodo común de los CSV principales:

- Inicio: `2021-11-05 08:00:00`
- Fin: `2021-11-08 00:04:59`
- Frecuencia original: 1 segundo
- Registros aproximados por CSV: 230.700
- Duración aproximada: 64 horas

---

## 5. Archivo excluido

El archivo `TT_413.csv` queda excluido definitivamente del flujo principal.

Motivos:

- no comparte exactamente el mismo periodo temporal que los 7 CSV principales;
- aporta información redundante;
- puede introducir inconsistencias en la unión temporal.

Por tanto, `TT_413.csv` no se usa en limpieza, unión, modelado ni evaluación.

---

## 6. Datasets generados

El proyecto genera dos datasets principales:

| Dataset | Frecuencia | Uso |
|---|---:|---|
| `dataset_unificado_1s.csv` | 1 segundo | Dataset maestro unido |
| `dataset_modelable_10s.csv` | 10 segundos | Dataset reducido para análisis, features y modelos |

La frecuencia original de 1 segundo se conserva como trazabilidad.

El dataset modelable se genera a 10 segundos porque mantiene la dinámica principal de LT-411 y reduce ruido/autocorrelación.

---

## 7. Riesgo principal: leakage por lazo cerrado

La variable `LV411` está asociada al lazo de control del nivel.

Esto significa que puede reaccionar directamente a lo que mide `LT411`.

Por tanto:

- `LV411` no se usa en el Modelo A limpio.
- Los lags de `LV411` tampoco se usan en el Modelo A.
- `LV411` solo se usará más adelante en el Modelo B como auditoría.

Si el Modelo B mejora mucho al incluir `LV411`, esa mejora no se interpreta automáticamente como mejor modelo, sino como posible señal de contaminación por lazo cerrado.

---

## 8. Modelo A limpio

El **Modelo A** es el modelo principal del proyecto.

Reglas:

- no usar `LV411`;
- no usar lags de `LV411`;
- no usar `SP_LT411`;
- no usar `LT411` como feature;
- no usar `LT411 lagged`;
- no usar split aleatorio;
- no usar variables futuras;
- no usar medias móviles centradas;
- no usar backfill.

El objetivo del Modelo A es estimar `LT411` usando variables físicas de proceso y evitando contaminación directa del lazo de nivel.

---

## 9. Modelo B de auditoría

El **Modelo B** se entrenará solo después del Modelo A.

Su objetivo es comparar qué ocurre si se incluye `LV411`.

El Modelo B no será el modelo principal salvo justificación extraordinaria.

Se usará para medir el impacto del lazo cerrado y explicar el riesgo de leakage.

---

## 10. Correcciones físicas antes del resampleo

Antes de generar el dataset a 10 segundos se aplican correcciones físicas básicas.

La corrección principal es:

| Variable | Corrección |
|---|---|
| `FQC400_1` | Los valores negativos se corrigen a 0 |

El caudal de vapor no puede ser negativo. Corregirlo antes del resampleo evita crear medias físicas falsas.

---

## 11. Feature engineering temporal

El nivel de un cristalizador no depende solo del valor instantáneo de las variables, sino también de su evolución reciente.

Por eso se crearán variables temporales:

- lags;
- rolling mean;
- rolling std.

Las ventanas iniciales serán:

| Ventana | Equivalencia a 10s |
|---:|---:|
| 1 paso | 10 segundos |
| 6 pasos | 1 minuto |
| 30 pasos | 5 minutos |
| 90 pasos | 15 minutos |

Reglas:

- los lags serán siempre hacia atrás;
- las rolling serán trailing;
- no se usarán medias centradas;
- no se usará información futura;
- se auditará cuántas filas se pierden con `dropna()`.

---

## 12. Split temporal

El proyecto usa split temporal, no aleatorio.

| Bloque | Uso |
|---|---|
| Día 1 | Train |
| Día 2 | Validación |
| Día 3 | Test / análisis de anomalía |

Este criterio permite entrenar con el periodo más limpio, validar en otro día y analizar el comportamiento del modelo durante el tercer día, donde aparecen señales de ensuciamiento/parada.

---

## 13. Modelos comparados

El Modelo A comparará varios algoritmos:

| Modelo | Objetivo |
|---|---|
| `DummyRegressor` | Baseline mínimo |
| `LinearRegression` | Modelo lineal simple |
| `Ridge` | Modelo lineal regularizado |
| `RandomForestRegressor` | Modelo no lineal |
| `GradientBoostingRegressor` | Modelo boosting clásico |
| `HistGradientBoostingRegressor` | Boosting eficiente |

No se elegirá el modelo solo por una métrica global.

También se revisará:

- diferencia entre train y validación;
- comportamiento temporal;
- residuales;
- estabilidad en Día 3.

---

## 14. Evaluación

La evaluación incluirá:

- MAE;
- RMSE;
- R2;
- gráfico real vs predicho;
- análisis de residuales;
- métricas por split;
- métricas segmentadas.

En Día 3 se intentará separar:

- tramo normal;
- tramo de ensuciamiento;
- tramo de parada o vaciado.

No se mezclará operación normal, fallo de sensor y parada como si fueran el mismo régimen.

---

## 15. Residual y alerta

El cierre funcional del proyecto será el análisis del residual:

```text
residual = LT411_medido - LT411_predicho
```

El objetivo es detectar cuándo el sensor físico se separa del nivel esperado estimado por el soft sensor.

Se definirá una alerta inicial cuando:

```text
abs(residual) > umbral
```

Y una alerta sostenida cuando esa desviación se mantenga durante varias muestras consecutivas.

Ejemplo inicial:

```text
abs(residual) > 3 puntos durante N muestras consecutivas
```

El umbral definitivo se ajustará analizando el residual en periodos considerados limpios.

---

## 16. Orden de notebooks

El proyecto se rehace con notebooks simples y ordenados:

| Notebook | Objetivo |
|---|---|
| `01_limpieza_union_10s.ipynb` | Cargar 7 CSV, excluir TT_413, unir datos, corregir señales y crear datasets 1s/10s |
| `02_segmentacion_visual.ipynb` | Graficar señales clave y separar Día 1, Día 2, Día 3, ensuciamiento y parada |
| `03_feature_engineering_modelo_A.ipynb` | Crear lags y rolling features sin leakage para Modelo A |
| `04_modelo_A_baseline.ipynb` | Entrenar y comparar modelos limpios |
| `05_modelo_B_auditoria_LV411.ipynb` | Repetir modelado incluyendo LV411 solo como auditoría |
| `06_evaluacion_residual_alertas.ipynb` | Calcular residual, métricas segmentadas y alerta sostenida |

---

## 17. Estructura del repositorio

```text
ML-Sensor-Virtual-Inteligente/
│
├── README.md
├── guia_tecnica_actualizada.md
│
├── data/
│   ├── Den-Int_VB-01.csv
│   ├── Nivel_Caudal_PCT-02.csv
│   ├── Nivel_VB-01.csv
│   ├── Presion_VB01_HE01.csv
│   ├── Temperatura_salmuera_HE01.csv
│   ├── Vacío.csv
│   └── Vapor_HE-01.csv
│
├── data_limpio/
│   ├── dataset_unificado_1s.csv
│   └── dataset_modelable_10s.csv
│
├── img/
│   └── esquema.png
│
├── 01_limpieza_union_10s.ipynb
├── 02_segmentacion_visual.ipynb
├── 03_feature_engineering_modelo_A.ipynb
├── 04_modelo_A_baseline.ipynb
├── 05_modelo_B_auditoria_LV411.ipynb
└── 06_evaluacion_residual_alertas.ipynb
```

---

## 18. Limitaciones

Este proyecto tiene limitaciones importantes:

- histórico corto, aproximadamente 2,7 días;
- alta autocorrelación temporal;
- posible ensuciamiento/parada en Día 3;
- ausencia de etiquetado formal de fallo;
- riesgo de leakage por lazo cerrado;
- necesidad de segmentación visual;
- validación industrial limitada.

Por tanto, el proyecto no debe presentarse como un soft sensor industrial validado para producción.

Debe presentarse como una metodología reproducible y técnicamente defendible de Machine Learning industrial.

---

## 19. Narrativa final

Narrativa técnica:

> Se desarrolla una metodología reproducible para estimar el nivel físico esperado de VB-01 mediante un soft sensor, controlando lazo cerrado, señal sucia, segmentación temporal y calidad de datos industriales.

Narrativa simple:

> Cuando el sensor físico de nivel puede ensuciarse y medir mal, usamos otras señales de la planta para estimar cuál debería ser el nivel esperado. Si la diferencia entre el sensor real y el sensor virtual se mantiene durante un tiempo, puede ser una alerta temprana de fallo o ensuciamiento del sensor.
