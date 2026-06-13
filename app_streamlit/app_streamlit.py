# App Streamlit - Soft Sensor LT411

import time
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


RUTA_NORMAL = "data/dataset_presentacion_streamlit.csv"
RUTA_FALLO = "data/dataset_presentacion_fallo_streamlit.csv"

FRECUENCIA_SEGUNDOS = 10


st.set_page_config(
    page_title="Soft Sensor LT411",
    page_icon="📊",
    layout="wide"
)


st.markdown(
    """
    <style>
    .stApp {background-color: #0e1117;}
    [data-testid="stSidebar"] {background-color: #151a22;}
    [data-testid="stMetric"] {
        background-color: #151a22;
        border: 1px solid #29313d;
        border-radius: 8px;
        padding: 10px;
    }
    .estado {
        border-radius: 8px;
        padding: 16px;
        text-align: center;
        font-size: 19px;
        font-weight: bold;
    }
    .normal {
        background-color: #123a2b;
        border: 1px solid #39d98a;
        color: #67e8a8;
    }
    .aviso {
        background-color: #473719;
        border: 1px solid #f7b731;
        color: #ffd166;
    }
    .alerta {
        background-color: #4a2027;
        border: 1px solid #ff5d73;
        color: #ff8fa0;
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data(show_spinner=False)
def cargar_datos(ruta, umbral, muestras_alerta):
    # El CSV y las alertas se calculan una sola vez
    df = pd.read_csv(ruta)

    df["Time"] = pd.to_datetime(df["Time"])
    df = df.sort_values("Time").reset_index(drop=True)

    df["alerta_raw"] = df["error_abs"] > umbral

    df["alerta_sostenida"] = (
        df.groupby("bloque")["alerta_raw"]
        .transform(
            lambda serie: (
                serie.astype(int)
                .rolling(
                    muestras_alerta,
                    min_periods=muestras_alerta
                )
                .sum()
                .ge(muestras_alerta)
            )
        )
        .fillna(False)
        .astype(bool)
    )

    return df


def obtener_buffer(df, indice, minutos):
    muestras = int(
        minutos * 60 / FRECUENCIA_SEGUNDOS
    )

    inicio = max(
        0,
        indice - muestras + 1
    )

    buffer = df.iloc[
        inicio:indice + 1
    ].copy()

    buffer["minutos"] = (
        buffer["Time"]
        - df.iloc[indice]["Time"]
    ).dt.total_seconds() / 60

    return buffer


def crear_grafico(buffer, umbral, minutos, maximo_error):
    # Un único gráfico reduce el trabajo de Streamlit
    fig, axes = plt.subplots(
        2,
        1,
        figsize=(14, 7),
        sharex=True
    )

    axes[0].plot(
        buffer["minutos"],
        buffer["LT411_real"],
        label="LT411 real",
        linewidth=2
    )

    axes[0].plot(
        buffer["minutos"],
        buffer["LT411_predicho"],
        label="LT411 calculado",
        linewidth=2
    )

    axes[0].set_title(
        "Nivel real y nivel calculado"
    )

    axes[0].set_ylabel(
        "Nivel LT411 (%)"
    )

    axes[0].set_ylim(
        0,
        100
    )

    axes[0].grid(
        True,
        alpha=0.25
    )

    axes[0].legend(
        loc="upper left"
    )


    axes[1].plot(
        buffer["minutos"],
        buffer["error_abs"],
        label="Error absoluto",
        linewidth=2
    )

    axes[1].axhline(
        umbral,
        linestyle="--",
        label=f"Umbral {umbral:.1f}"
    )

    alertas = buffer[
        buffer["alerta_sostenida"]
    ]

    if not alertas.empty:
        axes[1].scatter(
            alertas["minutos"],
            alertas["error_abs"],
            label="Alerta sostenida",
            s=25
        )

    axes[1].set_title(
        "Error absoluto y umbral"
    )

    axes[1].set_xlabel(
        "Últimos minutos"
    )

    axes[1].set_ylabel(
        "Error"
    )

    axes[1].set_xlim(
        -minutos,
        0
    )

    axes[1].set_ylim(
        0,
        maximo_error
    )

    axes[1].grid(
        True,
        alpha=0.25
    )

    axes[1].legend(
        loc="upper left"
    )

    plt.tight_layout()

    return fig


st.title(
    "Soft Sensor LT411 — Panel de supervisión"
)

st.caption(
    "Nivel real, nivel calculado "
    "y detección de desviaciones."
)


st.sidebar.header(
    "Configuración"
)

escenario = st.sidebar.radio(
    "Escenario",
    ["Normal", "Fallo"]
)

umbral = st.sidebar.slider(
    "Umbral de error",
    0.0,
    30.0,
    5.0,
    0.1
)

minutos_alerta = st.sidebar.slider(
    "Tiempo de alerta",
    1,
    5,
    1,
    1,
    format="%d min"
)

buffer_minutos = st.sidebar.selectbox(
    "Ventana visible",
    [5, 10, 15, 30],
    index=2
)

simular = st.sidebar.checkbox(
    "Ejecutar simulación",
    value=True
)

velocidad = st.sidebar.selectbox(
    "Velocidad visual",
    [0.5, 1.0, 1.5, 2.0],
    index=1,
    format_func=lambda valor: f"{valor:.1f} s"
)

reiniciar = st.sidebar.button(
    "Reiniciar",
    use_container_width=True
)

avanzar = st.sidebar.button(
    "Avanzar 10 segundos",
    use_container_width=True,
    disabled=simular
)


ruta = (
    RUTA_FALLO
    if escenario == "Fallo"
    else RUTA_NORMAL
)

muestras_alerta = int(
    minutos_alerta
    * 60
    / FRECUENCIA_SEGUNDOS
)

df = cargar_datos(
    ruta,
    umbral,
    muestras_alerta
)

muestras_buffer = int(
    buffer_minutos
    * 60
    / FRECUENCIA_SEGUNDOS
)

indice_inicial = min(
    max(muestras_buffer - 1, 0),
    len(df) - 1
)


if "indice" not in st.session_state:
    st.session_state.indice = indice_inicial

if "escenario" not in st.session_state:
    st.session_state.escenario = escenario

if "buffer" not in st.session_state:
    st.session_state.buffer = buffer_minutos


if (
    reiniciar
    or st.session_state.escenario != escenario
    or st.session_state.buffer != buffer_minutos
):
    st.session_state.indice = indice_inicial
    st.session_state.escenario = escenario
    st.session_state.buffer = buffer_minutos


if avanzar:
    st.session_state.indice = min(
        st.session_state.indice + 1,
        len(df) - 1
    )


indice = min(
    st.session_state.indice,
    len(df) - 1
)

fila = df.iloc[indice]

buffer = obtener_buffer(
    df,
    indice,
    buffer_minutos
)

maximo_error = max(
    15.0,
    umbral * 3,
    float(df["error_abs"].quantile(0.99)) * 1.10
)


if fila["alerta_sostenida"]:
    estado = "FALLO / ALERTA"
    clase = "alerta"

elif fila["alerta_raw"]:
    estado = "DESVIACIÓN"
    clase = "aviso"

else:
    estado = "NORMAL"
    clase = "normal"


columnas = st.columns(6)

columnas[0].metric(
    "Fecha y hora",
    fila["Time"].strftime("%H:%M:%S"),
    fila["Time"].strftime("%d/%m/%Y")
)

columnas[1].metric(
    "LT411 real",
    f"{fila['LT411_real']:.2f}"
)

columnas[2].metric(
    "LT411 calculado",
    f"{fila['LT411_predicho']:.2f}"
)

columnas[3].metric(
    "Error absoluto",
    f"{fila['error_abs']:.2f}"
)

columnas[4].metric(
    "Umbral",
    f"{umbral:.1f}"
)

with columnas[5]:
    st.markdown(
        f'<div class="estado {clase}">'
        f'{estado}'
        f'</div>',
        unsafe_allow_html=True
    )


st.caption(
    f"Escenario: {escenario} · "
    f"Bloque: {str(fila['bloque']).upper()} · "
    f"Residual: {fila['residual']:.2f}"
)


fig = crear_grafico(
    buffer,
    umbral,
    buffer_minutos,
    maximo_error
)

st.pyplot(
    fig,
    use_container_width=True
)

plt.close(fig)


if simular:
    time.sleep(velocidad)

    if indice >= len(df) - 1:
        st.session_state.indice = indice_inicial
    else:
        st.session_state.indice += 1

    st.rerun()
