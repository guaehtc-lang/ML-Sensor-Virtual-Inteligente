# App Streamlit - Soft Sensor LT411

import time
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from PIL import Image


RUTA_DATOS_NORMAL = "data/dataset_presentacion_streamlit.csv"
RUTA_DATOS_FALLO = "data/dataset_presentacion_fallo_streamlit.csv"
RUTA_IMG_COLOR = "assets/esquema.png"
RUTA_IMG_BN = "assets/esquema_bn.png"

FRECUENCIA_SEGUNDOS = 10
UMBRAL_DEFECTO = 5.0
MINUTOS_ALERTA_DEFECTO = 1
BUFFER_MINUTOS_DEFECTO = 15

VARIABLES_FUTURAS = [
    "LT411",
    "DT412",
    "TT413",
    "TT415",
    "PIT410",
    "PIT414",
    "PT442",
    "FQC400_1"
]


st.set_page_config(
    page_title="Soft Sensor LT411",
    layout="wide"
)


def cargar_datos(modo_simulacion):
    # Cargamos el dataset según el escenario
    if modo_simulacion == "Fallo":
        ruta_datos = RUTA_DATOS_FALLO
    else:
        ruta_datos = RUTA_DATOS_NORMAL

    df = pd.read_csv(ruta_datos)
    df["Time"] = pd.to_datetime(df["Time"])
    df = df.sort_values("Time").reset_index(drop=True)

    return df


def recalcular_alerta(df, umbral, muestras_alerta):
    # Calculamos la alerta con los valores elegidos
    df = df.copy()

    df["alerta_raw"] = df["error_abs"] > umbral

    df["alerta_sostenida"] = (
        df["alerta_raw"]
        .astype(int)
        .rolling(window=muestras_alerta)
        .sum()
        >= muestras_alerta
    )

    df["alerta_sostenida"] = (
        df["alerta_sostenida"]
        .fillna(False)
        .astype(bool)
    )

    return df


def obtener_buffer(df, indice_actual, buffer_minutos):
    # Seleccionamos los últimos minutos visibles
    muestras_buffer = int(
        (buffer_minutos * 60) / FRECUENCIA_SEGUNDOS
    )

    inicio = max(
        0,
        indice_actual - muestras_buffer + 1
    )

    df_buffer = df.iloc[
        inicio:indice_actual + 1
    ].copy()

    tiempo_actual = df.iloc[indice_actual]["Time"]

    df_buffer["minutos_buffer"] = (
        df_buffer["Time"] - tiempo_actual
    ).dt.total_seconds() / 60

    return df_buffer


def preparar_indice_inicial(df, buffer_minutos):
    # Empezamos con el buffer completo
    muestras_buffer = int(
        (buffer_minutos * 60) / FRECUENCIA_SEGUNDOS
    )

    return min(
        max(muestras_buffer - 1, 0),
        len(df) - 1
    )


def grafico_real_vs_predicho(df_buffer, buffer_minutos):
    # Comparamos el sensor real y el sensor virtual
    fig, ax = plt.subplots(figsize=(12, 4))

    ax.plot(
        df_buffer["minutos_buffer"],
        df_buffer["LT411_real"],
        label="LT411 real"
    )

    ax.plot(
        df_buffer["minutos_buffer"],
        df_buffer["LT411_predicho"],
        label="LT411 sensor virtual"
    )

    ax.set_title("LT411 real vs LT411 sensor virtual")
    ax.set_xlabel("Últimos minutos")
    ax.set_ylabel("Nivel LT411 (%)")
    ax.set_xlim(-buffer_minutos, 0)
    ax.grid(True)
    ax.legend()
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


def grafico_residual(df_buffer, umbral, buffer_minutos):
    # Mostramos el error absoluto y el umbral
    fig, ax = plt.subplots(figsize=(12, 3))

    ax.plot(
        df_buffer["minutos_buffer"],
        df_buffer["error_abs"],
        label="Error absoluto"
    )

    ax.axhline(
        umbral,
        linestyle="--",
        label="Umbral"
    )

    alertas = df_buffer[
        df_buffer["alerta_sostenida"] == True
    ]

    if not alertas.empty:
        ax.scatter(
            alertas["minutos_buffer"],
            alertas["error_abs"],
            label="Alerta sostenida"
        )

    ax.set_title("Error absoluto y umbral de alerta")
    ax.set_xlabel("Últimos minutos")
    ax.set_ylabel("Error absoluto")
    ax.set_xlim(-buffer_minutos, 0)
    ax.grid(True)
    ax.legend()
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)


def main():
    st.title(
        "Soft Sensor LT411 — Sensor Virtual Inteligente VB-01"
    )

    st.sidebar.header("Configuración")

    variable_objetivo = st.sidebar.selectbox(
        "Variable objetivo",
        VARIABLES_FUTURAS
    )

    if variable_objetivo != "LT411":
        st.warning(
            "Modelo no disponible todavía para esta variable. "
            "Esta funcionalidad está preparada para futuras versiones."
        )
        st.stop()

    umbral = st.sidebar.slider(
        "Umbral de error",
        min_value=0.0,
        max_value=30.0,
        value=UMBRAL_DEFECTO,
        step=0.1
    )

    minutos_alerta = st.sidebar.slider(
        "Tiempo para activar alerta (min)",
        min_value=1,
        max_value=5,
        value=MINUTOS_ALERTA_DEFECTO,
        step=1
    )

    muestras_alerta = int(
        (minutos_alerta * 60) / FRECUENCIA_SEGUNDOS
    )

    buffer_minutos = st.sidebar.selectbox(
        "Ventana visible del buffer",
        [5, 10, 15, 30],
        index=2
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("SIMULACIÓN")

    modo_simulacion = st.sidebar.radio(
        "Escenario",
        ["Normal", "Fallo"],
        help=(
            "Normal reproduce el histórico general. "
            "Fallo reproduce el tramo preparado alrededor del mínimo "
            "de LT411 en validación, observado a las 19:51:50."
        )
    )

    ejecutar_simulacion = st.sidebar.checkbox(
        "Ejecutar simulación",
        value=True
    )

    velocidad = st.sidebar.slider(
        "Velocidad de simulación (segundos)",
        min_value=0.1,
        max_value=3.0,
        value=0.5,
        step=0.1
    )

    df = cargar_datos(modo_simulacion)
    df = recalcular_alerta(
        df,
        umbral,
        muestras_alerta
    )

    imagen_color = Image.open(RUTA_IMG_COLOR)
    imagen_bn = Image.open(RUTA_IMG_BN)

    if "modo_anterior" not in st.session_state:
        st.session_state.modo_anterior = modo_simulacion

    if "buffer_anterior" not in st.session_state:
        st.session_state.buffer_anterior = buffer_minutos

    if "indice_actual" not in st.session_state:
        st.session_state.indice_actual = preparar_indice_inicial(
            df,
            buffer_minutos
        )

    if (
        st.session_state.modo_anterior != modo_simulacion
        or st.session_state.buffer_anterior != buffer_minutos
    ):
        st.session_state.indice_actual = preparar_indice_inicial(
            df,
            buffer_minutos
        )

        st.session_state.modo_anterior = modo_simulacion
        st.session_state.buffer_anterior = buffer_minutos

    indice_max = len(df) - 1

    st.session_state.indice_actual = min(
        st.session_state.indice_actual,
        indice_max
    )

    fila = df.iloc[st.session_state.indice_actual]

    df_buffer = obtener_buffer(
        df,
        st.session_state.indice_actual,
        buffer_minutos
    )

    estado = "OK"

    if fila["alerta_sostenida"]:
        estado = "ALERTA"
    elif fila["alerta_raw"]:
        estado = "DESVIACIÓN PUNTUAL"

    st.sidebar.markdown("---")
    st.sidebar.write("**Fecha/hora leída**")
    st.sidebar.write(
        fila["Time"].strftime("%Y-%m-%d %H:%M:%S")
    )
    st.sidebar.caption(
        "Cada paso representa 10 segundos de proceso."
    )

    col_error, col_estado, col_umbral = st.columns(3)

    col_error.metric(
        "Error absoluto",
        f"{fila['error_abs']:.2f}"
    )

    if estado == "OK":
        col_estado.success("ESTADO SENSOR: OK")
    elif estado == "DESVIACIÓN PUNTUAL":
        col_estado.warning(
            "ESTADO SENSOR: DESVIACIÓN PUNTUAL"
        )
    else:
        col_estado.error("ESTADO SENSOR: ALERTA")

    col_umbral.metric(
        "Umbral",
        f"{umbral:.2f}"
    )

    st.markdown("---")

    col_real, col_virtual = st.columns(2)

    with col_real:
        st.subheader("Planta real")
        st.image(
            imagen_color,
            use_container_width=True
        )
        st.metric(
            "LT411 real",
            f"{fila['LT411_real']:.2f}"
        )

    with col_virtual:
        st.subheader("Planta virtual / sensor virtual")
        st.image(
            imagen_bn,
            use_container_width=True
        )
        st.metric(
            "LT411 sensor virtual",
            f"{fila['LT411_predicho']:.2f}"
        )

    st.markdown("---")

    grafico_real_vs_predicho(
        df_buffer,
        buffer_minutos
    )

    grafico_residual(
        df_buffer,
        umbral,
        buffer_minutos
    )

    st.info(
        "Esta demo simula la llegada de datos cada 10 segundos usando "
        "un CSV histórico. En una aplicación real, los datos vendrían "
        "del SCADA/PLC y el sistema mantendría un buffer temporal para "
        "calcular lags y rolling."
    )

    if ejecutar_simulacion:
        time.sleep(velocidad)

        if st.session_state.indice_actual >= indice_max:
            st.session_state.indice_actual = preparar_indice_inicial(
                df,
                buffer_minutos
            )
        else:
            st.session_state.indice_actual += 1

        st.rerun()


if __name__ == "__main__":
    main()
