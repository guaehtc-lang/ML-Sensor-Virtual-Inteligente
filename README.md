# Soft Sensor LT411 — Sensor Virtual Inteligente

## 1. Descripción

Este proyecto desarrolla un **sensor virtual** para estimar el nivel esperado de VB-01, medido por el sensor físico `LT411`.

El sistema compara:

- el nivel medido por `LT411`;
- el nivel estimado por un modelo de Machine Learning;
- la diferencia entre ambas señales;
- una alerta cuando la desviación se mantiene durante un tiempo.

El proyecto se plantea como un prototipo funcional y reproducible de Machine Learning industrial. No se presenta como un sistema validado para producción.

---

## 2. Contexto industrial

El proceso corresponde a una planta de evaporación y cristalización de salmuera bajo vacío.

El nivel de VB-01 está relacionado con distintas variables del proceso:

- temperaturas;
- presiones;
- vacío;
- caudal de vapor;
- densidad;
- intensidad de la bomba de recirculación;
- nivel y caudal de extracción.

Cuando el sensor físico `LT411` se ensucia o empieza a medir de forma incorrecta, el sensor virtual estima cuál debería ser el nivel esperado a partir del resto de señales disponibles.

---

## 3. Datos utilizados

El proyecto utiliza 7 CSV principales:

- `Den-Int_VB-01.csv`
- `Nivel_Caudal_PCT-02.csv`
- `Nivel_VB-01.csv`
- `Presion_VB01_HE01.csv`
- `Temperatura_salmuera_HE01.csv`
- `Vacío.csv`
- `Vapor_HE-01.csv`

El archivo `TT_413.csv` se conserva dentro de los datos originales por trazabilidad, pero queda excluido del flujo principal por tener un periodo temporal diferente y contener una señal redundante.

Características principales:

- frecuencia original: 1 segundo;
- duración aproximada: 2,7 días;
- dataset modelable: remuestreo a 10 segundos;
- target: `LT411`.

---

## 4. Metodología

### Split temporal

El histórico se divide de forma cronológica:

- Día 1: entrenamiento;
- Día 2: validación;
- Día 3: test y análisis de comportamiento.

No se utiliza un split aleatorio porque los datos tienen una fuerte dependencia temporal.

### Modelo A limpio

El modelo principal no utiliza:

- `LV411`;
- `SP_LT411`;
- `LT411` como variable predictora;
- lags de `LT411`.

Estas exclusiones reducen el riesgo de leakage y evitan que el modelo copie directamente el sensor físico o aprenda información contaminada por el lazo de control.

### Feature engineering

El dataset final contiene 222 variables predictoras:

- 16 variables base;
- 96 lags;
- 90 rolling features;
- 20 deltas temporales.

Las transformaciones temporales utilizan únicamente información presente o pasada.

---

## 5. Modelos comparados

En el baseline se comparan cinco modelos supervisados:

- Linear Regression;
- Ridge;
- Random Forest;
- Gradient Boosting;
- SVR.

Después de la optimización, el modelo seleccionado para la versión actual es:

```text
RandomForestRegressor optimizado
```

El modelo se guarda en:

```text
models/modelo_randomforest_LT411.pkl
```

---

## 6. Estructura del proyecto

```text
ML-Sensor-Virtual-Inteligente/
│
├── README.md
├── .gitignore
├── requirements.txt
│
├── data/
│   ├── original/
│   └── data_limpio/
│
├── notebooks/
│   ├── EDA.ipynb
│   ├── limpieza.ipynb
│   ├── EDA_10s.ipynb
│   ├── feature_engineering.ipynb
│   ├── modelo_A_baseline.ipynb
│   └── modelo_A_optimizacion.ipynb
│
├── src/
│   ├── preparar_datos.py
│   └── aplicar_modelo.py
│
├── models/
│   └── modelo_randomforest_LT411.pkl
│
├── app_streamlit/
│   ├── app_streamlit.py
│   ├── requirements_streamlit.txt
│   ├── README_demo_streamlit.md
│   ├── data/
│   └── assets/
│
└── docs/
    ├── memoria.md
    └── presentacion.md
```

---

## 7. Orden de los notebooks

### `EDA.ipynb`

Inspección inicial de los CSV originales:

- dimensiones;
- columnas;
- tipos de datos;
- fechas;
- nulos;
- duplicados;
- frecuencia temporal;
- coherencia general de las señales.

### `limpieza.ipynb`

Preparación del dataset:

- carga de los 7 CSV válidos;
- exclusión de `TT_413.csv`;
- normalización de nombres;
- unión por `Time`;
- creación de `dataset_unificado_1s.csv`;
- remuestreo a 10 segundos;
- creación de `dataset_modelable_10s.csv`.

### `EDA_10s.ipynb`

Análisis visual del dataset modelable:

- comportamiento temporal de `LT411`;
- variables principales;
- correlaciones;
- comparación de bloques;
- definición de train, validación y test.

### `feature_engineering.ipynb`

Creación de las variables del Modelo A:

- variables base;
- corrección y flag de `FQC400_1`;
- lags;
- rolling mean;
- rolling std;
- rolling range;
- deltas temporales;
- variables físicas derivadas;
- auditoría de `dropna()`.

Genera:

```text
data/data_limpio/features_modelo_A.csv
```

### `modelo_A_baseline.ipynb`

Comparación inicial de cinco modelos supervisados:

- Linear Regression;
- Ridge;
- Random Forest;
- Gradient Boosting;
- SVR.

### `modelo_A_optimizacion.ipynb`

Optimización de los modelos candidatos y selección del Random Forest final.

El modelo definitivo se guarda en:

```text
models/modelo_randomforest_LT411.pkl
```

---

## 8. Ejecución del proyecto

### Instalar dependencias

Desde la carpeta raíz:

```bash
pip install -r requirements.txt
```

### Preparar los datos

Abrir una terminal dentro de `src/`:

```bash
cd src
python preparar_datos.py
```

El script genera:

```text
data/data_limpio/dataset_unificado_1s.csv
data/data_limpio/dataset_modelable_10s.csv
data/data_limpio/features_modelo_A.csv
```

### Aplicar el modelo

Desde la misma carpeta `src/`:

```bash
python aplicar_modelo.py
```

El script genera:

```text
app_streamlit/data/dataset_presentacion_streamlit.csv
app_streamlit/data/dataset_presentacion_fallo_streamlit.csv
```

### Ejecutar Streamlit

```bash
cd ../app_streamlit
streamlit run app_streamlit.py
```

---

## 9. Demo Streamlit

La aplicación muestra:

- planta real;
- planta virtual;
- `LT411` real;
- `LT411` predicho;
- error absoluto;
- umbral configurable;
- alerta sostenida;
- buffer temporal;
- escenario Normal;
- escenario Fallo.

El escenario Fallo se construye alrededor del mínimo de `LT411` localizado en el bloque de validación:

```text
2021-11-06 19:51:50
LT411 ≈ 22.5868
```

La aplicación utiliza datos históricos simulados cada 10 segundos.

---

## 10. Limitaciones

- histórico corto;
- alta autocorrelación temporal;
- ausencia de etiquetado formal de fallo;
- validación limitada a un periodo operativo concreto;
- diferencias entre entrenamiento y validación;
- demo basada en datos históricos;
- ausencia de conexión real con SCADA o PLC;
- modelo no validado para producción.

---

## 11. Mejoras futuras

Sin modificar la estructura conceptual del proyecto, se podrán incorporar:

- nuevos periodos de planta;
- nuevas variables físicas;
- optimización adicional del Random Forest;
- comparación con otros modelos;
- análisis de importancia de variables;
- ajuste del umbral de alerta;
- mejora visual de Streamlit;
- simulaciones más realistas;
- conexión futura con datos de proceso en tiempo real.

---

## 12. Resumen

> Cuando el sensor físico de nivel puede ensuciarse y medir mal, el modelo utiliza otras señales del proceso para estimar cuál debería ser el nivel esperado. Si la diferencia entre el sensor real y el sensor virtual se mantiene durante un tiempo, el sistema genera una alerta temprana.
