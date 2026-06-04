# Soft Sensor LT-411 — Proyecto de Machine Learning Industrial

## 1. Resumen del proyecto

Este proyecto desarrolla un **sensor virtual** (*soft sensor*) para estimar el nivel del evaporador/cristalizador **VB-01**, medido por el sensor físico **LT-411**.

La idea principal es sencilla:

> Si el sensor físico LT-411 se ensucia o empieza a medir mal, un modelo de Machine Learning puede estimar cuál debería ser el nivel esperado usando otras variables del proceso.

El objetivo del proyecto no es sustituir un sistema industrial real, sino construir una metodología clara, reproducible y defendible dentro de un bootcamp de Data Science.

---

## 2. Contexto industrial explicado de forma simple

El proceso corresponde a una planta de evaporación/cristalización de salmuera.

De forma simplificada:

1. La salmuera entra en el sistema.
2. Se calienta mediante vapor.
3. Se evapora parte del agua bajo vacío.
4. La salmuera se concentra.
5. El nivel del equipo principal se mide con el sensor LT-411.
6. Si ese sensor se ensucia, puede dar una lectura falsa.

El modelo intentará estimar el nivel real esperado a partir de señales como presión, temperatura, vapor, vacío, densidad y caudales.

---

## 3. Datos disponibles

El proyecto utiliza datos históricos de PLC/SCADA en formato CSV.

| CSV | Registros aprox. | Contenido principal |
|---|---:|---|
| `Nivel_VB-01.csv` | 230.700 | Nivel LT-411, set point y válvula LV-411 |
| `Presion_VB01_HE01.csv` | 230.700 | Presiones PIT-410 y PIT-414 |
| `Temperatura_salmuera_HE01.csv` | 230.700 | Temperaturas TT-413 y TT-415 |
| `Den-Int_VB-01.csv` | 230.700 | Densidad DT-412 e intensidad/carga P-101 |
| `Vapor_HE-01.csv` | 230.700 | Caudal de vapor FQC-400-1 y válvula FV-400-1 |
| `Vacío.csv` | 230.700 | Presión de vacío PT-442 y válvula PV-442 |
| `Nivel_Caudal_PCT-02.csv` | 230.700 | Nivel LT-426 y caudal FT-428 |
| `TT_413.csv` | 230.701 | Señal duplicada de TT-413, pendiente de validación |

Periodo común documentado para los CSV principales:

- Inicio: `05/11/2021 08:00:00`
- Fin: `08/11/2021 00:04:59`
- Frecuencia original: 1 segundo
- Duración aproximada: 64 horas

---

## 4. Variable objetivo

La variable que se quiere predecir es:

| Variable | Descripción | Uso |
|---|---|---|
| `LT-411` | Nivel del evaporador/cristalizador VB-01 | Target del modelo |

El problema se plantea como una **regresión supervisada temporal**.

---

## 5. Variables principales del modelo

Variables candidatas principales:

- `PIT-410`: presión en VB-01
- `PIT-414`: presión en HE-01
- `TT-413`: temperatura de salida/flujo térmico asociado a HE-01
- `TT-415`: temperatura de entrada/flujo térmico asociado a HE-01
- `DT-412`: densidad de salmuera
- `FQC-400-1`: caudal de vapor
- `PT-442`: presión/vacío
- Intensidad/carga asociada a `P-101`

Variables que se analizarán con cautela:

- `LV-411`: muy informativa, pero peligrosa por lazo cerrado
- `FT-428`: caudal hacia PCT-02, pendiente de revisar
- `LT-426`: nivel en PCT-02, pendiente de revisar

---

## 6. Riesgo principal: leakage por lazo cerrado

La variable `LV-411` está asociada al lazo de control del nivel. Esto significa que puede reaccionar directamente a lo que mide `LT-411`.

Por tanto:

- El modelo base no usará `LV-411`.
- Después se podrá entrenar otro modelo con `LV-411` solo como comparación.
- Si el modelo mejora demasiado usando `LV-411`, puede ser una señal de contaminación por lazo cerrado.

---

## 7. Estrategia temporal

El histórico se dividirá de forma temporal, no aleatoria.

Criterio inicial:

- Dos primeros días: candidatos a entrenamiento base.
- Tercer día: contiene ensuciamiento/parada y se usará como test, validación o análisis de comportamiento.
- Los cortes exactos se decidirán mediante análisis gráfico.

---

## 8. Qué se mostrará en la presentación de 5 minutos

En la presentación se explicará:

1. Qué es un sensor virtual.
2. Qué problema industrial se intenta resolver.
3. Qué datos se tienen.
4. Qué variable se quiere predecir.
5. Qué riesgos metodológicos existen.
6. Por qué no se debe entrenar directamente con todas las variables.
7. Qué pasos se seguirán antes de modelar.

---

## 9. Estado actual del proyecto

Estado actual:

- Punto 1 del proyecto prácticamente cerrado.
- Target definido: `LT-411`.
- Variables candidatas identificadas.
- Riesgo de leakage identificado.
- Estrategia de split temporal definida.
- Pendiente: cargar CSV en notebook, validar datos reales y graficar señales.

---

## 10. Estructura prevista del repositorio

```text
ml-soft-sensor-lt411/
│
├── README.md
├── requirements.txt
│
├── data/
│   ├── raw/
│   │   ├── Den-Int_VB-01.csv
│   │   ├── Nivel_Caudal_PCT-02.csv
│   │   ├── Nivel_VB-01.csv
│   │   ├── Presion_VB01_HE01.csv
│   │   ├── Temperatura_salmuera_HE01.csv
│   │   ├── TT_413.csv
│   │   ├── Vacío.csv
│   │   └── Vapor_HE-01.csv
│   │
│   └── processed/
│
├── notebooks/
│   ├── 01_inspeccion_fuentes_y_csv.ipynb
│   ├── 02_limpieza_y_union_dataset.ipynb
│   ├── 03_analisis_grafico_lt411.ipynb
│   ├── 04_feature_engineering.ipynb
│   └── 05_modelado_baseline.ipynb
│
├── src/
│   ├── data_loading.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   └── evaluation.py
│
├── reports/
│   ├── figures/
│   └── guia_tecnica_actualizada.pdf
│
└── models/
```

---

## 11. Limitaciones declaradas

Este proyecto tiene limitaciones importantes:

- El histórico es corto: unos 2,7 días.
- Los datos tienen alta autocorrelación porque vienen cada segundo.
- El tercer día contiene ensuciamiento y parada.
- Algunas variables pueden introducir leakage.
- No se presenta como un sistema industrial listo para producción.

Aun así, es un proyecto válido para aprender y defender una metodología de Machine Learning industrial aplicada a un sensor virtual.

---

## 12. Próximos pasos

1. Actualizar la guía técnica del proyecto.
2. Revisar el PID/P&ID corregido.
3. Cargar los CSV en Jupyter.
4. Validar columnas, fechas, nulos y rangos.
5. Graficar LT-411 y variables clave.
6. Definir los cortes temporales exactos.
7. Crear el dataset modelable.
8. Entrenar un primer modelo base sin leakage.
