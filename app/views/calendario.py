"""Calendario por jornadas, con predicción en cada partido."""

import streamlit as st

from services.liga_service import jornada_sugerida
from services.reporte_service import fecha_corte_entrenamiento
from services.team_assets import EQUIPOS_ACTIVOS
from ui.components import (
    data_line,
    day_heading,
    empty_state,
    error_state,
    etiqueta_temporada,
    foot_note,
    match_card_html,
    match_grid,
    page_header,
    skeleton_html,
)
from ui.loaders import obtener_calendario, predecir_partido_calendario


try:
    calendario, temporada = obtener_calendario()
except Exception as exc:
    page_header("Calendario")
    error_state(
        "No se pudo cargar el calendario",
        "No se encontró el archivo de partidos de la temporada.",
        detalle=str(exc),
    )
    st.stop()

if calendario.empty:
    page_header("Calendario")
    empty_state(
        "Sin partidos programados",
        "El archivo de calendario no contiene jornadas.",
        icono="📅",
    )
    st.stop()


corte_entrenamiento = fecha_corte_entrenamiento()

jornadas = sorted(calendario["jornada"].unique().tolist())

if st.session_state.get("jornada_sel") not in jornadas:
    st.session_state["jornada_sel"] = jornada_sugerida(calendario)


def _mover_jornada(paso):
    actual = jornadas.index(st.session_state["jornada_sel"])
    nuevo = min(max(actual + paso, 0), len(jornadas) - 1)
    st.session_state["jornada_sel"] = jornadas[nuevo]


page_header(
    f"Calendario · {etiqueta_temporada(temporada)}",
    "Partidos de cada jornada, con horarios en hora de Panamá y la predicción "
    "de cada encuentro.",
)

with st.container(key="jornada-selector", horizontal=True, vertical_alignment="center"):
    st.button(
        "Anterior",
        icon=":material/chevron_left:",
        key="jornada-prev",
        on_click=_mover_jornada,
        args=(-1,),
        disabled=st.session_state["jornada_sel"] == jornadas[0],
    )
    st.pills(
        "Jornada",
        jornadas,
        key="jornada_sel",
        format_func=lambda j: f"J{j}",
        required=True,
        label_visibility="collapsed",
    )
    st.button(
        "Siguiente",
        icon=":material/chevron_right:",
        icon_position="right",
        key="jornada-next",
        on_click=_mover_jornada,
        args=(1,),
        disabled=st.session_state["jornada_sel"] == jornadas[-1],
    )

filtro_col, pred_col = st.columns([3, 2], vertical_alignment="bottom")

with filtro_col:
    equipo = st.selectbox(
        "Filtrar por equipo",
        ["Todos los equipos"] + EQUIPOS_ACTIVOS,
        key="calendario_equipo",
    )

with pred_col:
    con_predicciones = st.toggle(
        "Mostrar predicciones",
        value=True,
        key="calendario_predicciones",
    )

jornada = int(st.session_state["jornada_sel"])

partidos = calendario[calendario["jornada"] == jornada]

if equipo != "Todos los equipos":
    partidos = partidos[(partidos["local"] == equipo) | (partidos["visitante"] == equipo)]

if partidos.empty:
    empty_state(
        "Sin partidos para este filtro",
        "Seleccione otro equipo u otra jornada.",
        icono="🔍",
    )
    st.stop()


pendientes = int((partidos["estado"] == "pendiente").sum())

data_line(
    [
        (f"Jornada {jornada}", ""),
        (str(len(partidos)), "partidos"),
        (str(pendientes), "pendientes"),
    ]
)

predicciones = {}

if con_predicciones:
    hueco = st.empty()
    hueco.html(skeleton_html(len(partidos)))

    for partido in partidos.to_dict("records"):
        try:
            predicciones[(partido["local"], partido["visitante"])] = (
                predecir_partido_calendario(
                    partido["local"],
                    partido["visitante"],
                    partido["fecha"].isoformat(),
                    temporada,
                )
            )
        except Exception:
            predicciones[(partido["local"], partido["visitante"])] = None

    hueco.empty()

    if any(p is None for p in predicciones.values()):
        st.warning(
            "No se pudo calcular la predicción de algunos partidos.",
            icon=":material/info:",
        )

for fecha, grupo in partidos.groupby("fecha", sort=True):
    day_heading(fecha)

    match_grid(
        [
            match_card_html(
                partido,
                predicciones.get((partido["local"], partido["visitante"])),
                temporada,
                corte_entrenamiento,
            )
            for partido in grupo.to_dict("records")
        ]
    )

if con_predicciones and corte_entrenamiento is not None:
    foot_note(
        "Cada predicción emplea únicamente partidos anteriores a la fecha del "
        "encuentro. El indicador «Acertó / No acertó» se muestra solo para los "
        f"partidos posteriores al {corte_entrenamiento.strftime('%d/%m/%Y')}, "
        "última fecha de datos usada en el entrenamiento de los modelos; los "
        "anteriores se rotulan «Dentro del período de entrenamiento», pues el "
        "modelo ya conocía su resultado. Un acierto aislado no sustituye la "
        "validación presentada en la sección Modelos."
    )
