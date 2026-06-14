# App Streamlit - Soft Sensor LT411

import time
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from matplotlib.gridspec import GridSpec
from matplotlib.patches import Wedge


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
    [data-testid="stSidebar"] {
        background-color: #151a22;
        border-right: 1px solid #29313d;
    }
    [data-testid="stMetric"] {
        background-color: #151a22;
        border: 1px solid #29313d;
        border-radius: 9px;
        padding: 7px 10px;
        min-height: 78px;
    }
    [data-testid="stMetricLabel"] {color: #97a3b3;}
    [data-testid="stMetricValue"] {color: #f4f6f8;}
    .status-box {
        border-radius: 9px;
        padding: 12px 8px;
        text-align: center;
        font-size: 16px;
        font-weight: 700;
        min-height: 78px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .status-normal {
        background-color: rgba(52, 211, 153, 0.12);
        border: 1px solid #34d399;
        color: #6ee7b7;
    }
    .status-warning {
        background-color: rgba(251, 191, 36, 0.12);
        border: 1px solid #fbbf24;
        color: #fcd34d;
    }
    .status-alert {
        background-color: rgba(248, 113, 113, 0.14);
        border: 1px solid #f87171;
        color: #fca5a5;
    }
    .dashboard-title {
        color: #f4f6f8;
        font-size: 1.45rem;
        font-weight: 700;
        margin-bottom: 0.05rem;
    }

    .subtitle {
        color: #97a3b3;
        font-size: 0.86rem;
        margin-top: 0;
        margin-bottom: 0.55rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data(show_spinner=False)
def cargar_datos(ruta, umbral, muestras_alerta):
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
                    window=muestras_alerta,
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
    muestras = int(minutos * 60 / FRECUENCIA_SEGUNDOS)
    inicio = max(0, indice - muestras + 1)

    buffer = df.iloc[inicio:indice + 1].copy()
    buffer["minutos"] = (
        buffer["Time"] - df.iloc[indice]["Time"]
    ).dt.total_seconds() / 60

    return buffer


def configurar_eje(ax):
    ax.set_facecolor("#151a22")
    ax.tick_params(colors="#aeb8c6", labelsize=9)
    ax.xaxis.label.set_color("#c8d0dc")
    ax.yaxis.label.set_color("#c8d0dc")
    ax.title.set_color("#e5e9f0")

    for borde in ax.spines.values():
        borde.set_color("#394150")

    ax.grid(
        True,
        color="#2a313c",
        alpha=0.75,
        linewidth=0.7
    )


def dibujar_gauge(
    ax,
    titulo,
    valor,
    minimo,
    maximo,
    color,
    sufijo="",
    umbral=None
):
    ax.set_facecolor("#151a22")
    ax.set_aspect("equal")
    ax.axis("off")

    ax.add_patch(
        Wedge(
            (0, 0),
            1,
            0,
            180,
            width=0.22,
            facecolor="#2a313c",
            edgecolor="none"
        )
    )

    proporcion = np.clip(
        (valor - minimo) / (maximo - minimo),
        0,
        1
    )

    angulo_valor = 180 - proporcion * 180

    ax.add_patch(
        Wedge(
            (0, 0),
            1,
            angulo_valor,
            180,
            width=0.22,
            facecolor=color,
            edgecolor="none"
        )
    )

    if umbral is not None:
        proporcion_umbral = np.clip(
            (umbral - minimo) / (maximo - minimo),
            0,
            1
        )

        angulo_umbral = np.deg2rad(
            180 - proporcion_umbral * 180
        )

        ax.plot(
            [
                0.70 * np.cos(angulo_umbral),
                1.03 * np.cos(angulo_umbral)
            ],
            [
                0.70 * np.sin(angulo_umbral),
                1.03 * np.sin(angulo_umbral)
            ],
            color="#ffffff",
            linewidth=2
        )

    angulo_aguja = np.deg2rad(angulo_valor)

    ax.plot(
        [0, 0.68 * np.cos(angulo_aguja)],
        [0, 0.68 * np.sin(angulo_aguja)],
        color="#f4f6f8",
        linewidth=2.2
    )

    ax.scatter([0], [0], s=38, color="#f4f6f8", zorder=5)

    ax.text(
        0,
        0.30,
        titulo,
        ha="center",
        va="center",
        color="#aeb8c6",
        fontsize=9
    )

    ax.text(
        0,
        -0.18,
        f"{valor:.2f}{sufijo}",
        ha="center",
        va="center",
        color="#f4f6f8",
        fontsize=15,
        fontweight="bold"
    )

    ax.text(-0.93, -0.08, f"{minimo:.0f}", ha="center", color="#778291", fontsize=8)
    ax.text(0.93, -0.08, f"{maximo:.0f}", ha="center", color="#778291", fontsize=8)

    ax.set_xlim(-1.12, 1.12)
    ax.set_ylim(-0.35, 1.12)


def crear_dashboard(
    buffer,
    fila,
    umbral,
    minutos,
    minimo_nivel,
    maximo_nivel,
    maximo_error
):
    fig = plt.figure(
        figsize=(14.5, 6.15),
        facecolor="#0e1117"
    )

    grid = GridSpec(
        2,
        4,
        figure=fig,
        width_ratios=[1.25, 1.25, 1.25, 0.95],
        hspace=0.28,
        wspace=0.24
    )

    ax_nivel = fig.add_subplot(grid[0, :3])
    ax_error = fig.add_subplot(grid[1, :3])

    gauges = grid[:, 3].subgridspec(3, 1, hspace=0.26)
    ax_real = fig.add_subplot(gauges[0, 0])
    ax_pred = fig.add_subplot(gauges[1, 0])
    ax_err = fig.add_subplot(gauges[2, 0])

    ax_nivel.plot(
        buffer["minutos"],
        buffer["LT411_real"],
        label="LT411 real",
        color="#60a5fa",
        linewidth=2.1
    )

    ax_nivel.plot(
        buffer["minutos"],
        buffer["LT411_predicho"],
        label="LT411 calculado",
        color="#a78bfa",
        linewidth=2.1
    )

    ax_nivel.set_title(
        "Nivel real y nivel calculado",
        fontsize=12,
        fontweight="bold"
    )
    ax_nivel.set_ylabel("Nivel LT411 (%)")
    ax_nivel.set_xlim(-minutos, 0)
    ax_nivel.set_ylim(minimo_nivel, maximo_nivel)
    ax_nivel.legend(
        loc="upper left",
        facecolor="#151a22",
        edgecolor="#394150",
        labelcolor="#d7dde6"
    )
    configurar_eje(ax_nivel)

    ax_error.plot(
        buffer["minutos"],
        buffer["error_abs"],
        label="Error absoluto",
        color="#fb7185",
        linewidth=2.0
    )

    ax_error.fill_between(
        buffer["minutos"],
        buffer["error_abs"],
        color="#fb7185",
        alpha=0.10
    )

    ax_error.axhline(
        umbral,
        linestyle="--",
        linewidth=1.8,
        color="#fbbf24",
        label=f"Umbral {umbral:.1f}"
    )

    alertas = buffer[buffer["alerta_sostenida"]]

    if not alertas.empty:
        ax_error.scatter(
            alertas["minutos"],
            alertas["error_abs"],
            color="#ef4444",
            s=26,
            label="Alerta sostenida",
            zorder=5
        )

    ax_error.set_title(
        "Error absoluto y umbral",
        fontsize=12,
        fontweight="bold"
    )
    ax_error.set_xlabel("Últimos minutos")
    ax_error.set_ylabel("Error")
    ax_error.set_xlim(-minutos, 0)
    ax_error.set_ylim(0, maximo_error)
    ax_error.legend(
        loc="upper left",
        facecolor="#151a22",
        edgecolor="#394150",
        labelcolor="#d7dde6"
    )
    configurar_eje(ax_error)

    dibujar_gauge(
        ax_real,
        "LT411 real",
        fila["LT411_real"],
        0,
        100,
        "#60a5fa",
        " %"
    )

    dibujar_gauge(
        ax_pred,
        "LT411 calculado",
        fila["LT411_predicho"],
        0,
        100,
        "#a78bfa",
        " %"
    )

    color_error = (
        "#6ee7b7"
        if fila["error_abs"] <= umbral
        else "#fbbf24"
        if fila["error_abs"] <= umbral * 1.5
        else "#f87171"
    )

    dibujar_gauge(
        ax_err,
        "Error absoluto",
        fila["error_abs"],
        0,
        maximo_error,
        color_error,
        umbral=umbral
    )

    return fig


st.markdown(
    '<div class="dashboard-title">'
    'Soft Sensor LT411 — Panel de supervisión'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Nivel real, nivel calculado y detección de desviaciones del sensor.'
    '</div>',
    unsafe_allow_html=True
)


st.sidebar.header("Configuración")

escenario = st.sidebar.radio(
    "Escenario",
    ["Normal", "Fallo"]
)

umbral = st.sidebar.slider(
    "Umbral de error",
    min_value=0.0,
    max_value=30.0,
    value=5.0,
    step=0.1
)

minutos_alerta = st.sidebar.slider(
    "Tiempo para activar alerta",
    min_value=1,
    max_value=5,
    value=1,
    step=1,
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
    [0.8, 1.0, 1.5, 2.0],
    index=1,
    format_func=lambda valor: f"{valor:.1f} s"
)

reiniciar = st.sidebar.button(
    "Reiniciar",
    use_container_width=True
)

ruta = RUTA_FALLO if escenario == "Fallo" else RUTA_NORMAL
muestras_alerta = int(minutos_alerta * 60 / FRECUENCIA_SEGUNDOS)

df = cargar_datos(ruta, umbral, muestras_alerta)

muestras_buffer = int(buffer_minutos * 60 / FRECUENCIA_SEGUNDOS)
indice_inicial = min(max(muestras_buffer - 1, 0), len(df) - 1)


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


indice = min(st.session_state.indice, len(df) - 1)
fila = df.iloc[indice]
buffer = obtener_buffer(df, indice, buffer_minutos)

# Escalas robustas para mostrar mejor las oscilaciones
serie_nivel = pd.concat(
    [
        df["LT411_real"],
        df["LT411_predicho"]
    ],
    ignore_index=True
)

minimo_nivel = max(
    0,
    np.floor(
        (
            serie_nivel.quantile(0.01) - 3
        ) / 5
    ) * 5
)

maximo_nivel = min(
    100,
    np.ceil(
        (
            serie_nivel.quantile(0.99) + 3
        ) / 5
    ) * 5
)

if maximo_nivel - minimo_nivel < 30:
    centro_nivel = (
        maximo_nivel + minimo_nivel
    ) / 2

    minimo_nivel = max(
        0,
        centro_nivel - 15
    )

    maximo_nivel = min(
        100,
        centro_nivel + 15
    )

maximo_error = max(
    8.0,
    umbral * 1.6,
    float(
        df["error_abs"].quantile(0.95)
    ) * 1.15
)

maximo_error = (
    np.ceil(maximo_error / 2) * 2
)


if fila["alerta_sostenida"]:
    estado = "FALLO / ALERTA"
    clase_estado = "status-alert"
elif fila["alerta_raw"]:
    estado = "DESVIACIÓN"
    clase_estado = "status-warning"
else:
    estado = "NORMAL"
    clase_estado = "status-normal"


columnas = st.columns([1.20, 1, 1, 1, 0.85, 1.15])

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
        f'<div class="status-box {clase_estado}">{estado}</div>',
        unsafe_allow_html=True
    )


st.caption(
    f"Escenario: {escenario} · "
    f"Bloque: {str(fila['bloque']).upper()} · "
    f"Residual: {fila['residual']:.2f}"
)


fig = crear_dashboard(
    buffer,
    fila,
    umbral,
    buffer_minutos,
    minimo_nivel,
    maximo_nivel,
    maximo_error
)

st.pyplot(fig, use_container_width=True)
plt.close(fig)


with st.expander("Variables de proceso actuales", expanded=False):
    variables = st.columns(6)

    variables[0].metric("Densidad DT412", f"{fila['DT412']:.2f}")
    variables[1].metric("Temperatura TT413", f"{fila['TT413']:.2f}")
    variables[2].metric("Temperatura TT415", f"{fila['TT415']:.2f}")
    variables[3].metric("Vacío PT442", f"{fila['PT442']:.2f}")
    variables[4].metric("Caudal vapor", f"{fila['FQC400_1_corr']:.2f}")
    variables[5].metric("Intensidad P101", f"{fila['INT_P101']:.2f}")


if simular:
    time.sleep(velocidad)

    if indice >= len(df) - 1:
        st.session_state.indice = indice_inicial
    else:
        st.session_state.indice += 1

    st.rerun()
