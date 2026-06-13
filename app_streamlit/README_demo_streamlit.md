# Demo Streamlit — Soft Sensor LT411

## 1. Objetivo

Esta aplicación muestra una demostración visual del sensor virtual desarrollado para estimar el nivel `LT411` de VB-01.

La aplicación no entrena el modelo. Utiliza datasets preparados previamente por:

```bash
python aplicar_modelo.py
```

---

## 2. Archivos necesarios

La carpeta debe contener:

```text
app_streamlit/
├── app_streamlit.py
├── requirements_streamlit.txt
├── README_demo_streamlit.md
│
├── data/
│   ├── dataset_presentacion_streamlit.csv
│   └── dataset_presentacion_fallo_streamlit.csv
│
└── assets/
    ├── esquema.png
    └── esquema_bn.png
```

---

## 3. Instalación

Abrir una terminal dentro de `app_streamlit/`:

```bash
pip install -r requirements_streamlit.txt
```

---

## 4. Ejecución

```bash
streamlit run app_streamlit.py
```

---

## 5. Modos de simulación

### Normal

Reproduce el histórico general preparado para la demostración.

### Fallo

Reproduce un tramo específico del bloque de validación alrededor del mínimo de `LT411`, observado aproximadamente en:

```text
2021-11-06 19:51:50
```

Este escenario se utiliza para mostrar cómo aumenta la diferencia entre el sensor real y el sensor virtual.

No se presenta como un fallo formalmente etiquetado, sino como un tramo de demostración.

---

## 6. Elementos de la pantalla

La aplicación muestra:

- error absoluto actual;
- estado del sensor;
- umbral configurado;
- planta real;
- planta virtual;
- valor real de `LT411`;
- valor estimado por el modelo;
- gráfica real frente a predicho;
- gráfica del error absoluto;
- buffer temporal de los últimos minutos.

---

## 7. Umbral y alerta

El error se calcula como:

```text
error absoluto = |LT411 real - LT411 predicho|
```

El umbral inicial es:

```text
5 puntos de nivel
```

El usuario puede modificarlo desde el panel lateral.

La alerta sostenida se activa cuando el error supera el umbral durante el tiempo configurado.

Con datos cada 10 segundos:

```text
6 muestras = 1 minuto
```

Una desviación puntual no activa directamente una alerta sostenida.

---

## 8. Simulación temporal

Cada fila del dataset representa 10 segundos de proceso.

La velocidad visible de reproducción se puede modificar desde Streamlit, pero esto solo cambia la velocidad de la demo. No modifica la frecuencia original del proceso.

---

## 9. Alcance

La aplicación utiliza datos históricos almacenados en CSV.

En una aplicación industrial real:

- los datos llegarían desde SCADA o PLC;
- el sistema mantendría un buffer temporal;
- se calcularían lags y rolling features;
- el modelo generaría una predicción en cada ciclo;
- la alerta se enviaría al sistema de supervisión.
