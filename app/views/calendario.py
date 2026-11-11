"""Calendario por jornadas, con predicción en cada partido."""

import streamlit as st

from services.liga_service import jornada_sugerida
from services.reporte_service import fecha_corte_entrenamiento
from services.team_assets import EQUIPOS_ACTIVOS
from ui.components import (
    day_heading,
    empty_state,
    error_state,
    fecha_larga,
    match_card_html,
    match_grid,
    mostrar,
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
        "Revisa que exista un archivo de partidos en data/raw/partidos.",
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
    f"Calendario · Temporada {temporada}",
    "Elige una jornada para ver sus partidos, horarios (hora de Panamá) y la "
    "predicción de cada encuentro.",
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
        "Prueba con otro equipo o elige otra jornada.",
        icono="🔍",
    )
    st.stop()


pendientes = int((partidos["estado"] == "pendiente").sum())

mostrar(
    "<div class='lpf-section__hint' style='margin-top:12px'>"
    f"Jornada {jornada} · {len(partidos)} partidos · "
    f"{pendientes} pendientes</div>"
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

if con_predicciones:
    st.caption(
        "Cada predicción usa solo partidos anteriores a la fecha del encuentro. "
        "El indicador «Acertó / No acertó» aparece únicamente en partidos "
        f"posteriores al {corte_entrenamiento.strftime('%d/%m/%Y')}, último día "
        "de datos con que se entrenaron los modelos; los anteriores se rotulan "
        "«Dentro del período de entrenamiento» porque el modelo ya conocía ese "
        "resultado. Un acierto aislado no sustituye la validación de la "
        "sección Modelos."
    )
