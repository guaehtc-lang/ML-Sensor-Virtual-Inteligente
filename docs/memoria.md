# Memoria final — Soft Sensor LT411

## 1. Introducción

El proyecto desarrolla un sensor virtual para estimar el nivel esperado de VB-01, medido por el sensor físico `LT411`.

El objetivo principal es construir y documentar un flujo completo de Machine Learning industrial:

```text
datos
→ inspección
→ limpieza
→ análisis exploratorio
→ feature engineering
→ comparación de modelos
→ optimización
→ guardado del modelo
→ aplicación
→ visualización en Streamlit
```

La finalidad no es declarar el sistema listo para producción, sino demostrar una metodología reproducible que pueda reutilizarse con nuevos datos.

---

## 2. Problema industrial

En procesos de evaporación y cristalización, los sensores de nivel pueden verse afectados por:

- ensuciamiento;
- incrustaciones;
- cambios de densidad;
- condiciones de vacío;
- espuma;
- perturbaciones del proceso;
- cambios de régimen operativo.

Cuando el sensor físico empieza a desviarse, puede seguir entregando una señal aparentemente válida aunque no represente correctamente el nivel real.

El soft sensor utiliza otras variables del proceso para estimar el nivel esperado de VB-01 y comparar esa estimación con la lectura de `LT411`.

---

## 3. Problema de Machine Learning

Tipo de problema:

```text
Regresión supervisada temporal
```

Target:

```text
LT411
```

El modelo aprende la relación entre las variables físicas del proceso y el nivel esperado del recipiente.

Posteriormente, la diferencia entre la señal medida y la señal predicha se utiliza como indicador de posible anomalía.

---

## 4. Datos disponibles

Se utilizan 7 CSV principales:

- `Den-Int_VB-01.csv`
- `Nivel_Caudal_PCT-02.csv`
- `Nivel_VB-01.csv`
- `Presion_VB01_HE01.csv`
- `Temperatura_salmuera_HE01.csv`
- `Vacío.csv`
- `Vapor_HE-01.csv`

El archivo `TT_413.csv` queda excluido del flujo principal porque:

- presenta un periodo temporal diferente;
- tiene una fila adicional;
- contiene una señal redundante;
- no está alineado con los 7 CSV principales.

Se conserva dentro de los datos originales únicamente por trazabilidad.

Características del histórico:

- frecuencia original: 1 segundo;
- duración aproximada: 2,7 días;
- 230.700 registros por CSV principal;
- inicio común: `2021-11-05 08:00:00`;
- fin común: `2021-11-08 00:04:59`;
- frecuencia constante de 1 segundo.

---

## 5. Preparación de datos

El flujo de preparación genera tres datasets principales:

```text
dataset_unificado_1s.csv
dataset_modelable_10s.csv
features_modelo_A.csv
```

### Dataset unificado a 1 segundo

Se cargan los 7 CSV válidos, se normalizan los nombres de columnas y se unen mediante la variable temporal `Time`.

Este dataset mantiene la resolución original y actúa como fuente maestra.

### Dataset modelable a 10 segundos

El dataset se remuestrea a 10 segundos mediante la media de cada ventana.

Se eligió esta frecuencia porque:

- reduce ruido y tamaño;
- mantiene la dinámica principal;
- conserva mejor las oscilaciones que un remuestreo a 1 minuto;
- reduce parte de la autocorrelación extrema de los datos a 1 segundo.

### Tratamiento de `FQC400_1`

Los valores negativos de `FQC400_1` se conservan durante la limpieza para mantener la trazabilidad del dato original.

En feature engineering se crean:

```text
FQC400_1_corr
FQC400_1_negativo_flag
```

La primera variable corrige los valores negativos a cero y la segunda identifica cuándo se produjo esa condición físicamente imposible.

---

## 6. División temporal

El histórico se divide cronológicamente:

- Día 1: entrenamiento;
- Día 2: validación;
- Día 3: test y análisis de comportamiento.

Esta división evita mezclar información futura con datos pasados.

No se utiliza un split aleatorio porque:

- los datos están ordenados temporalmente;
- existe autocorrelación;
- el proceso presenta cambios de régimen;
- la validación debe simular una aplicación futura.

---

## 7. Modelo A limpio

El modelo principal excluye:

- `LV411`;
- `SP_LT411`;
- `LT411` como feature;
- lags de `LT411`;
- transformaciones derivadas directamente de `LT411`.

### Motivo de excluir `LV411`

`LV411` es la válvula esclava del lazo de control de nivel.

Su comportamiento depende directamente de `LT411`, por lo que incluirla podría introducir información contaminada por el propio sensor que se pretende sustituir.

### Motivo de excluir `LT411` y sus lags

El objetivo no es crear un modelo de persistencia que copie el sensor, sino estimar el nivel esperado a partir de variables físicas independientes o menos contaminadas.

---

## 8. Feature engineering

El dataset final contiene 222 variables predictoras.

Distribución:

```text
16 variables base
96 lags
90 rolling features
20 deltas temporales
```

Total:

```text
16 + 96 + 90 + 20 = 222
```

### Lags

Se utilizan retardos:

```text
1, 2, 3, 6, 12 y 18 pasos
```

Con una frecuencia de 10 segundos equivalen a:

```text
10 s, 20 s, 30 s, 1 min, 2 min y 3 min
```

### Rolling features

Se crean ventanas trailing:

```text
6, 30 y 90 pasos
```

Equivalentes a:

```text
1 min, 5 min y 15 min
```

Para cada ventana se calculan:

- media;
- desviación estándar;
- rango.

Las ventanas no utilizan información futura.

### Deltas

Se calculan variaciones temporales de distintas señales físicas para representar cambios de tendencia y dinámica.

También se incluyen variables derivadas:

```text
DELTA_TT = TT413 - TT415
DELTA_PIT = PIT414 - PIT410
```

---

## 9. Modelos comparados

Se comparan cinco modelos supervisados:

- Linear Regression;
- Ridge;
- Random Forest;
- Gradient Boosting;
- SVR.

Los modelos lineales presentan limitaciones para representar la dinámica no lineal del proceso.

Random Forest, Gradient Boosting y SVR muestran mejores resultados y pasan a la fase de optimización.

---

## 10. Modelo final actual

El modelo seleccionado para la versión actual es:

```text
RandomForestRegressor optimizado
```

Parámetros:

```text
n_estimators = 400
max_depth = 15
min_samples_leaf = 10
max_features = 0.7
random_state = 42
n_jobs = -1
```

El modelo se guarda en:

```text
models/modelo_randomforest_LT411.pkl
```

El Random Forest se selecciona por su equilibrio entre:

- capacidad de modelar relaciones no lineales;
- estabilidad;
- interpretación industrial;
- facilidad de despliegue;
- compatibilidad con el dataset de features creado.

---

## 11. Métricas de referencia

Las métricas de validación del modelo final son aproximadamente:

```text
MAE  ≈ 3.76
RMSE ≈ 5.52
R²   ≈ 0.21
```

Estas métricas muestran que el modelo capta parte de la dinámica del nivel, aunque todavía existe margen de mejora.

El proyecto no debe evaluarse únicamente mediante una métrica global. También es necesario revisar:

- comportamiento temporal;
- capacidad para seguir tendencias;
- respuesta ante perturbaciones;
- diferencia entre periodos normales y anómalos;
- comportamiento del residual.

---

## 12. Residual y alerta

El residual se calcula como:

```text
residual = LT411 real - LT411 predicho
```

El error absoluto se calcula como:

```text
error_abs = |residual|
```

La demo utiliza inicialmente un umbral configurable de:

```text
5 puntos de nivel
```

La alerta sostenida requiere que el error supere el umbral durante varias muestras consecutivas.

Con datos cada 10 segundos:

```text
6 muestras = 1 minuto
```

Este criterio reduce la posibilidad de activar alarmas por desviaciones puntuales.

---

## 13. Scripts ejecutables

### `src/preparar_datos.py`

Reproduce de forma directa los pasos principales de limpieza y feature engineering:

```text
CSV originales
→ dataset_unificado_1s.csv
→ dataset_modelable_10s.csv
→ features_modelo_A.csv
```

### `src/aplicar_modelo.py`

Carga:

```text
features_modelo_A.csv
modelo_randomforest_LT411.pkl
```

Y genera:

```text
predicción
residual
error absoluto
alerta
datasets para Streamlit
```

Los análisis, métricas, gráficos y comparaciones de modelos se mantienen en los notebooks.

---

## 14. Aplicación Streamlit

La aplicación contiene dos escenarios:

- Normal;
- Fallo.

El escenario Fallo utiliza un tramo alrededor del mínimo de `LT411` localizado en validación:

```text
2021-11-06 19:51:50
LT411 ≈ 22.5868
```

La aplicación muestra:

- planta real;
- planta virtual;
- nivel real;
- nivel predicho;
- error absoluto;
- umbral;
- estado del sensor;
- alerta sostenida;
- buffer temporal;
- simulación histórica cada 10 segundos.

La demo no vuelve a entrenar el modelo. Utiliza los datasets generados previamente por `aplicar_modelo.py`.

---

## 15. Limitaciones

### Histórico corto

El conjunto de datos cubre aproximadamente 2,7 días. Este periodo es suficiente para desarrollar y demostrar la metodología, pero no para validar industrialmente el modelo.

### Alta autocorrelación

Los datos originales tienen una frecuencia de 1 segundo, por lo que existe una fuerte dependencia entre observaciones consecutivas.

El remuestreo a 10 segundos reduce este efecto, pero no lo elimina completamente.

### Falta de etiquetado formal

No existe una etiqueta oficial que identifique con precisión:

- inicio del ensuciamiento;
- final del ensuciamiento;
- parada;
- recuperación;
- otros fallos.

El escenario Fallo de Streamlit se utiliza como demostración visual y no como una etiqueta industrial certificada.

### Cambios de régimen

Los bloques de entrenamiento, validación y test no presentan exactamente las mismas condiciones operativas.

Esto afecta a la capacidad de generalización y explica parte de la diferencia entre métricas.

### Variables de lazo cerrado

`LV411` contiene información muy relacionada con el target, pero se excluye del Modelo A para reducir leakage.

En el futuro podría utilizarse únicamente en un modelo comparativo de auditoría.

### Validación limitada

El modelo ha sido validado sobre un único periodo corto.

No se ha probado todavía con:

- otras campañas;
- otras concentraciones;
- otros niveles de producción;
- otras condiciones de vacío;
- otras fases de limpieza;
- datos de meses diferentes.

### Aplicación histórica

Streamlit reproduce datos históricos preparados previamente.

No existe todavía una conexión real con:

- PLC;
- SCADA;
- historiador industrial;
- sistema de alarmas;
- base de datos en tiempo real.

### No validado para producción

El proyecto no debe utilizarse para tomar decisiones automáticas de proceso sin:

- nuevos datos;
- validación industrial;
- revisión de instrumentación;
- pruebas de robustez;
- gestión de alarmas;
- supervisión de personal de planta.

---

## 16. Conclusiones

El proyecto demuestra que es posible construir un soft sensor para estimar el nivel esperado de VB-01 utilizando variables físicas del proceso y evitando depender directamente del sensor `LT411`.

Se ha completado un flujo reproducible:

```text
datos originales
→ dataset unificado
→ remuestreo
→ feature engineering
→ comparación de modelos
→ optimización
→ guardado del modelo
→ aplicación
→ residual
→ alerta
→ demo Streamlit
```

El Random Forest optimizado ofrece una primera solución funcional y comprensible.

La principal aportación del proyecto no es únicamente el modelo, sino la metodología:

- trazabilidad de datos;
- control de leakage;
- separación temporal;
- ingeniería de variables;
- evaluación crítica;
- despliegue sencillo;
- visualización para usuario no técnico.

---

## 17. Mejoras futuras

La estructura conceptual del proyecto queda cerrada.

Las mejoras futuras se realizarán sobre esta misma base:

- incorporar más histórico;
- ajustar nuevas features;
- optimizar el Random Forest;
- comparar nuevos modelos;
- analizar importancia de variables;
- mejorar el umbral de alerta;
- reducir falsos positivos;
- mejorar visualmente Streamlit;
- crear nuevas simulaciones;
- conectar el sistema con datos en tiempo real;
- extender el enfoque a otros sensores del proceso.

Estas mejoras no requieren cambiar la arquitectura principal del proyecto.
