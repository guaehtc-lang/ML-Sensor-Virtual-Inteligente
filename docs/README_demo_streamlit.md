# Demo Streamlit - Soft Sensor LT411

Esta demo muestra un prototipo funcional de sensor virtual para LT411.

## Archivos principales

```text
00_crear_features_modelo_A.py
01_entrenar_modelo_final.py
02_crear_dataset_presentacion.py
app_streamlit.py
requirements_demo_streamlit.txt
```

## Orden de ejecución

```bash
pip install -r requirements_demo_streamlit.txt
python 00_crear_features_modelo_A.py
python 01_entrenar_modelo_final.py
python 02_crear_dataset_presentacion.py
streamlit run app_streamlit.py
```

Si ya existe `data_limpio/features_modelo_A.csv`, puedes empezar por:

```bash
python 01_entrenar_modelo_final.py
python 02_crear_dataset_presentacion.py
streamlit run app_streamlit.py
```

## Qué genera

```text
models/modelo_randomforest_LT411.pkl
models/columnas_modelo_LT411.json
data_limpio/dataset_presentacion_streamlit.csv
data_limpio/dataset_presentacion_fallo_streamlit.csv
img/esquema_bn.png
```

## Cambios de la versión final

- Umbral inicial fijado en 5 puntos de nivel.
- Umbral configurable desde Streamlit.
- Alerta sostenida por defecto: 1 minuto.
- La cabecera muestra Error absoluto, Estado del sensor y Umbral.
- Se elimina la tabla inferior "USO EN ML" de los diagramas.
- Se eliminan las métricas masivas de variables físicas.
- Las gráficas muestran solo el buffer reciente en minutos relativos.
- Se elimina el selector de bloque temporal.
- Se elimina el botón manual de avanzar 10 segundos.
- Se añade modo SIMULACIÓN: Normal / Fallo.
- El modo Fallo carga un dataset preparado alrededor de las 17:00 de validación.

## Narrativa correcta

Este proyecto no es un soft sensor industrial validado para producción.

Es un prototipo funcional y demostrador de sensor virtual basado en datos históricos, con potencial de integración futura en SCADA/PLC.
