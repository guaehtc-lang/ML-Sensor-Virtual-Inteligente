# Presentación — Soft Sensor LT-411

## 1. El problema y objetivo

El proyecto consiste en desarrollar un **Soft Sensor** o sensor virtual para estimar el nivel de un evaporador/cristalizador industrial, medido por el sensor **LT-411**.

El problema industrial es que este sensor físico puede ensuciarse por costras o incrustaciones de sal. Cuando eso ocurre, la lectura deja de representar correctamente el nivel real del equipo.

El objetivo del proyecto es entrenar un modelo de Machine Learning que estime el **nivel físico esperado** usando otras variables del proceso, como presión, temperatura, vapor, vacío y densidad. No se busca sustituir directamente un sistema industrial real, sino construir una metodología reproducible.

---

## 2. Los datos disponibles

Trabajamos con datos históricos de PLC/SCADA procedentes de una planta de evaporación/cristalización de salmuera.

Los datos cubren aproximadamente **2,7 días**, con frecuencia original de **1 segundo**, y están repartidos en **7 archivos CSV**.

| CSV | Registros aprox. | Contenido principal |
|---|---:|---|
| `Nivel_VB-01.csv` | 230.700 | Nivel LT-411, consigna y válvula LV-411 |
| `Presion_VB01_HE01.csv` | 230.700 | Presiones PIT-410 y PIT-414 |
| `Temperatura_salmuera_HE01.csv` | 230.700 | Temperaturas TT-413 y TT-415 |
| `Den-Int_VB-01.csv` | 230.700 | Densidad DT-412 e intensidad/carga P-101 |
| `Vapor_HE-01.csv` | 230.700 | Caudal de vapor FQC-400-1 y válvula FV-400-1 |
| `Vacío.csv` | 230.700 | Presión de vacío PT-442 y válvula PV-442 |
| `Nivel_Caudal_PCT-02.csv` | 230.700 | Nivel LT-426 y caudal FT-428 |

El periodo común va desde **05/11/2021 08:00:00** hasta **08/11/2021 00:04:59**.

La decisión tomada es trabajar solo con las señales útiles para explicar el nivel de **VB-01**, evitando ruido técnico y variables fuera del perímetro del modelo.

---

## 3. Dinámica del proceso e ingeniería de lags 

El proceso químico tiene **inercia térmica e hidráulica**.

Por ejemplo, si cambia el caudal de vapor o la presión de vacío, el nivel no cambia instantáneamente al segundo siguiente. El efecto puede tardar varios minutos en aparecer.

Los modelos lineales, como Random Forest o XGBoost, leen cada fila como una foto fija. Para que puedan entender esa inercia, crearemos variables con retraso temporal, llamadas **lags**.

Ejemplo:

- presión actual;
- presión hace 5 minutos;
- presión hace 10 minutos;
- temperatura actual;
- temperatura hace 5 minutos.

### Para entrenar

En los datos históricos de los días 1 y 2, crearemos columnas del pasado usando desplazamientos temporales


### Para predecir

En una simulación utilizaremos una ventana o **buffer temporal** con los últimos minutos de señales.

Cada minuto nuevo, el sistema toma el dato actual y los valores guardados en el buffer para construir el vector de entrada del modelo y generar una predicción.

---

## 4. Clave de validación: riesgo de lazo cerrado 

El principal riesgo metodológico está en la variable **LV-411**, la válvula asociada al lazo de control de nivel.

Esta válvula es muy informativa, pero también peligrosa: si el sensor LT-411 mide mal, la válvula puede actuar mal. Si el modelo aprende demasiado de esa válvula, puede terminar copiando el fallo del sensor en lugar de estimar el nivel real.

Por eso se plantea un diseño experimental con dos modelos:

| Modelo | Descripción | Objetivo |
|---|---|---|
| **Modelo A — Baseline limpio** | Excluye LV-411 y sus retardos | Estimar el nivel desde variables físicas: vapor, vacío, presiones, temperaturas y densidad |
| **Modelo B — Comparativo** | Incluye LV-411 de forma controlada | Medir cuánto afecta el lazo cerrado y detectar posible contaminación |


La validación no se basará solo en métricas globales. También miraremos si el modelo se separa de LT-411 cuando el sensor empieza a fallar.

---

## 5. Conclusión

La estrategia queda definida:

- usamos un sensor virtual para estimar el nivel esperado;
- reducimos ruido con remuestreo a 1 minuto;
- capturamos la inercia del proceso con lags;
- evitamos leakage usando un modelo limpio sin LV-411;
- comparamos contra un segundo modelo para demostrar el efecto del lazo cerrado.


