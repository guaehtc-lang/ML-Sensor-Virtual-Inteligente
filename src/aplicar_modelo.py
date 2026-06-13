# Aplicamos el modelo RandomForest optimizado

import pickle
import pandas as pd


# Cargamos las features y el modelo final

df = pd.read_csv(
    "../data/data_limpio/features_modelo_A.csv"
)

df["Time"] = pd.to_datetime(df["Time"])

with open("../models/modelo_randomforest_LT411.pkl", "rb") as archivo:
    modelo = pickle.load(archivo)


# Preparamos las variables y generamos las predicciones

X = df.drop(["Time", "bloque", "LT411"], axis=1)

predicciones = modelo.predict(X)


df_presentacion = pd.DataFrame()

df_presentacion["Time"] = df["Time"]
df_presentacion["bloque"] = df["bloque"]
df_presentacion["LT411_real"] = df["LT411"]
df_presentacion["LT411_predicho"] = predicciones

df_presentacion["residual"] = (
    df_presentacion["LT411_real"]
    - df_presentacion["LT411_predicho"]
)

df_presentacion["error_abs"] = (
    df_presentacion["residual"].abs()
)


# Añadimos las variables físicas principales

variables_proceso = [
    "DT412",
    "INT_P101",
    "FQC400_1_corr",
    "FV400_1",
    "PT442",
    "PV442",
    "TT413",
    "TT415",
    "LT426",
    "FT428",
    "PIT410",
    "PIT414",
    "DELTA_TT",
    "DELTA_PIT"
]

for variable in variables_proceso:
    df_presentacion[variable] = df[variable]


# Creamos la alerta con un umbral inicial de 5 puntos

umbral = 5
muestras_alerta = 6

df_presentacion["alerta_raw"] = (
    df_presentacion["error_abs"] > umbral
)

df_presentacion["alerta_sostenida"] = False

for bloque in df_presentacion["bloque"].unique():
    mascara = df_presentacion["bloque"] == bloque

    serie_alerta = (
        df_presentacion.loc[mascara, "alerta_raw"].astype(int)
    )

    alerta_sostenida = (
        serie_alerta.rolling(window=muestras_alerta).sum()
        >= muestras_alerta
    )

    df_presentacion.loc[
        mascara,
        "alerta_sostenida"
    ] = alerta_sostenida.fillna(False).values


# Guardamos el dataset general de presentación

df_presentacion.to_csv(
    "../app_streamlit/data/dataset_presentacion_streamlit.csv",
    index=False
)


# Creamos el escenario de fallo desde el mínimo de LT411 en validación

df_validacion = df_presentacion[
    df_presentacion["bloque"] == "validacion"
].copy()

indice_minimo = df_validacion["LT411_real"].idxmin()
tiempo_minimo = df_validacion.loc[indice_minimo, "Time"]

inicio_fallo = tiempo_minimo - pd.Timedelta(minutes=20)
fin_fallo = tiempo_minimo + pd.Timedelta(minutes=10)


df_fallo = df_validacion[
    (df_validacion["Time"] >= inicio_fallo)
    & (df_validacion["Time"] <= fin_fallo)
].copy()


df_fallo = df_fallo.sort_values("Time").reset_index(drop=True)


df_fallo.to_csv(
    "../app_streamlit/data/dataset_presentacion_fallo_streamlit.csv",
    index=False
)


print("Predicciones creadas con el modelo RandomForest.")
print("Dataset general de presentación guardado.")
print("Dataset de simulación de fallo guardado.")
print("Punto mínimo de validación:", tiempo_minimo)
