# Preparamos los datos para aplicar el modelo final

import pandas as pd


# Cargamos los 7 CSV válidos

nivel_vb01 = pd.read_csv(
    "../data/original/Nivel_VB-01.csv",
    encoding="utf-16",
    sep=";",
    decimal=","
)

den_int_vb01 = pd.read_csv(
    "../data/original/Den-Int_VB-01.csv",
    encoding="utf-16",
    sep=";",
    decimal=","
)

vapor_he01 = pd.read_csv(
    "../data/original/Vapor_HE-01.csv",
    encoding="utf-16",
    sep=";",
    decimal=","
)

vacio = pd.read_csv(
    "../data/original/Vacío.csv",
    encoding="utf-16",
    sep=";",
    decimal=","
)

temp_salmuera_he01 = pd.read_csv(
    "../data/original/Temperatura_salmuera_HE01.csv",
    encoding="utf-16",
    sep=";",
    decimal=","
)

nivel_caudal_pct02 = pd.read_csv(
    "../data/original/Nivel_Caudal_PCT-02.csv",
    encoding="utf-16",
    sep=";",
    decimal=","
)

presion_vb01_he01 = pd.read_csv(
    "../data/original/Presion_VB01_HE01.csv",
    encoding="utf-16",
    sep=";",
    decimal=","
)


# Preparamos cada CSV para unirlo por Time

def preparar_time(df, columna_time, prefijo):
    df_tmp = df.copy()
    df_tmp = df_tmp.rename(columns={columna_time: "Time"})
    df_tmp["Time"] = pd.to_datetime(df_tmp["Time"], dayfirst=True)

    columnas_renombradas = {}

    for columna in df_tmp.columns:
        if columna != "Time":
            columnas_renombradas[columna] = prefijo + columna

    df_tmp = df_tmp.rename(columns=columnas_renombradas)

    return df_tmp


nivel_merge = preparar_time(
    nivel_vb01,
    "Valor proceso LT411 Time",
    "nivel_"
)

den_int_merge = preparar_time(
    den_int_vb01,
    "Valor densidad DT412 Time",
    "den_int_"
)

vapor_merge = preparar_time(
    vapor_he01,
    "Caudal vapor FQC-400-1 Time",
    "vapor_"
)

vacio_merge = preparar_time(
    vacio,
    "Valor proceso PT442 Time",
    "vacio_"
)

temp_merge = preparar_time(
    temp_salmuera_he01,
    "Temp TT413 Time",
    "temp_"
)

pct02_merge = preparar_time(
    nivel_caudal_pct02,
    "Valor proceso LT426 Time",
    "pct02_"
)

presion_merge = preparar_time(
    presion_vb01_he01,
    "Valor proceso PIT-410 Time",
    "presion_"
)


# Unimos todos los CSV por Time

dataset_limpio = nivel_merge.merge(den_int_merge, on="Time", how="inner")
dataset_limpio = dataset_limpio.merge(vapor_merge, on="Time", how="inner")
dataset_limpio = dataset_limpio.merge(vacio_merge, on="Time", how="inner")
dataset_limpio = dataset_limpio.merge(temp_merge, on="Time", how="inner")
dataset_limpio = dataset_limpio.merge(pct02_merge, on="Time", how="inner")
dataset_limpio = dataset_limpio.merge(presion_merge, on="Time", how="inner")


# Seleccionamos las columnas utilizadas en el proyecto

columnas_utiles = [
    "Time",
    "nivel_Valor proceso LT411 ValueY",
    "nivel_Set point ValueY",
    "nivel_Accion (valvula) LV411 ValueY",
    "den_int_Valor densidad DT412 ValueY",
    "den_int_Valor intensidad P-101 ValueY",
    "vapor_Caudal vapor FQC-400-1 ValueY",
    "vapor_Set point ValueY",
    "vapor_Acción válvula FV400-1 ValueY",
    "vacio_Valor proceso PT442 ValueY",
    "vacio_Set point ValueY",
    "vacio_Accion (valvula) PV442 ValueY",
    "temp_Temp TT413 ValueY",
    "temp_Temp TT415 ValueY",
    "pct02_Valor proceso LT426 ValueY",
    "pct02_Set point ValueY",
    "pct02_Accion (valvula) ValueY",
    "pct02_Caudal FT428 ValueY",
    "presion_Valor proceso PIT-410 ValueY",
    "presion_Valor proceso PIT-414 ValueY"
]

dataset_limpio = dataset_limpio[columnas_utiles].copy()


dataset_limpio = dataset_limpio.rename(columns={
    "nivel_Valor proceso LT411 ValueY": "LT411",
    "nivel_Set point ValueY": "SP_LT411",
    "nivel_Accion (valvula) LV411 ValueY": "LV411",
    "den_int_Valor densidad DT412 ValueY": "DT412",
    "den_int_Valor intensidad P-101 ValueY": "INT_P101",
    "vapor_Caudal vapor FQC-400-1 ValueY": "FQC400_1",
    "vapor_Set point ValueY": "SP_VAPOR",
    "vapor_Acción válvula FV400-1 ValueY": "FV400_1",
    "vacio_Valor proceso PT442 ValueY": "PT442",
    "vacio_Set point ValueY": "SP_PT442",
    "vacio_Accion (valvula) PV442 ValueY": "PV442",
    "temp_Temp TT413 ValueY": "TT413",
    "temp_Temp TT415 ValueY": "TT415",
    "pct02_Valor proceso LT426 ValueY": "LT426",
    "pct02_Set point ValueY": "SP_LT426",
    "pct02_Accion (valvula) ValueY": "ACCION_PCT02",
    "pct02_Caudal FT428 ValueY": "FT428",
    "presion_Valor proceso PIT-410 ValueY": "PIT410",
    "presion_Valor proceso PIT-414 ValueY": "PIT414"
})


dataset_limpio = dataset_limpio.sort_values("Time").reset_index(drop=True)


# Guardamos el dataset unificado a 1 segundo

dataset_limpio.to_csv(
    "../data/data_limpio/dataset_unificado_1s.csv",
    index=False
)


# Creamos el dataset modelable a 10 segundos

df_10s = dataset_limpio.copy()
df_10s = df_10s.set_index("Time")
df_10s = df_10s.resample("10s").mean(numeric_only=True)
df_10s = df_10s.reset_index()

dataset_modelable = df_10s.copy()


dataset_modelable.to_csv(
    "../data/data_limpio/dataset_modelable_10s.csv",
    index=False
)


# Creamos los bloques temporales

inicio_train = pd.Timestamp("2021-11-05 08:00:00")
fin_train = pd.Timestamp("2021-11-06 07:59:59")

inicio_valid = pd.Timestamp("2021-11-06 08:00:00")
fin_valid = pd.Timestamp("2021-11-07 07:59:59")

inicio_test = pd.Timestamp("2021-11-07 08:00:00")
fin_test = dataset_modelable["Time"].max()


dataset_modelable["bloque"] = "sin_asignar"

dataset_modelable.loc[
    (dataset_modelable["Time"] >= inicio_train)
    & (dataset_modelable["Time"] <= fin_train),
    "bloque"
] = "train"

dataset_modelable.loc[
    (dataset_modelable["Time"] >= inicio_valid)
    & (dataset_modelable["Time"] <= fin_valid),
    "bloque"
] = "validacion"

dataset_modelable.loc[
    (dataset_modelable["Time"] >= inicio_test)
    & (dataset_modelable["Time"] <= fin_test),
    "bloque"
] = "test"


# Creamos las variables físicas corregidas

dataset_modelable["FQC400_1_negativo_flag"] = (
    dataset_modelable["FQC400_1"] < 0
).astype(int)

dataset_modelable["FQC400_1_corr"] = (
    dataset_modelable["FQC400_1"].clip(lower=0)
)

dataset_modelable["DELTA_TT"] = (
    dataset_modelable["TT413"] - dataset_modelable["TT415"]
)

dataset_modelable["DELTA_PIT"] = (
    dataset_modelable["PIT414"] - dataset_modelable["PIT410"]
)


# Definimos las variables del Modelo A

variables_base = [
    "DT412",
    "INT_P101",
    "FQC400_1_corr",
    "FQC400_1_negativo_flag",
    "FV400_1",
    "PT442",
    "PV442",
    "TT413",
    "TT415",
    "LT426",
    "ACCION_PCT02",
    "FT428",
    "PIT410",
    "PIT414",
    "DELTA_TT",
    "DELTA_PIT"
]

variables_lag = variables_base.copy()

variables_temporales = [
    "DT412",
    "INT_P101",
    "FQC400_1_corr",
    "PT442",
    "TT413",
    "TT415",
    "PIT410",
    "PIT414",
    "DELTA_TT",
    "DELTA_PIT"
]

lags = [1, 2, 3, 6, 12, 18]
ventanas_rolling = [6, 30, 90]
deltas = [1, 6]


# Creamos lags, rolling y deltas por bloque

def crear_features_temporales(datos):
    datos = datos.sort_values("Time").copy()

    nuevas_features = {}

    for variable in variables_lag:
        for lag in lags:
            nuevas_features[
                variable + "_lag_" + str(lag)
            ] = datos[variable].shift(lag)

    for variable in variables_temporales:
        for ventana in ventanas_rolling:
            nuevas_features[
                variable + "_roll_mean_" + str(ventana)
            ] = datos[variable].rolling(window=ventana).mean()

            nuevas_features[
                variable + "_roll_std_" + str(ventana)
            ] = datos[variable].rolling(window=ventana).std()

            nuevas_features[
                variable + "_roll_range_" + str(ventana)
            ] = (
                datos[variable].rolling(window=ventana).max()
                - datos[variable].rolling(window=ventana).min()
            )

    for variable in variables_temporales:
        for delta in deltas:
            nuevas_features[
                variable + "_delta_" + str(delta)
            ] = datos[variable] - datos[variable].shift(delta)

    df_nuevas_features = pd.DataFrame(
        nuevas_features,
        index=datos.index
    )

    datos = pd.concat(
        [datos, df_nuevas_features],
        axis=1
    )

    return datos


columnas_base = ["Time", "bloque", "LT411"] + variables_base

df_base = dataset_modelable[columnas_base].copy()


df_train_feat = crear_features_temporales(
    df_base[df_base["bloque"] == "train"]
)

df_valid_feat = crear_features_temporales(
    df_base[df_base["bloque"] == "validacion"]
)

df_test_feat = crear_features_temporales(
    df_base[df_base["bloque"] == "test"]
)


df_features = pd.concat(
    [df_train_feat, df_valid_feat, df_test_feat],
    axis=0
)

df_features = df_features.sort_values("Time").reset_index(drop=True)

df_features_limpio = df_features.dropna().copy()


# Guardamos el dataset final del Modelo A

df_features_limpio.to_csv(
    "../data/data_limpio/features_modelo_A.csv",
    index=False
)


print("Dataset unificado guardado.")
print("Dataset modelable a 10 segundos guardado.")
print("Features del Modelo A guardadas.")
print("Filas finales:", df_features_limpio.shape[0])
print("Variables predictoras:", df_features_limpio.shape[1] - 3)
