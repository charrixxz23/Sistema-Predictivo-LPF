"""Predicciones: análisis de un partido con XGBoost y Poisson."""

from datetime import date

import streamlit as st

from services.database_service import guardar_prediccion
from services.liga_service import nombre_torneo
from services.prediction_service import analizar_partido
from services.team_assets import EQUIPOS_ACTIVOS
from ui.components import (
    error_state,
    history_cards_html,
    mostrar,
    page_header,
    poisson_panel_html,
    prediction_panel_html,
    section_title,
    versus_html,
    empty_state,
)
from ui.loaders import (
    leer_historial,
    obtener_historico,
    obtener_modelos,
    obtener_temporadas,
    preparar_base_datos,
)


# ============================================================
# ESTADO INICIAL Y PRESELECCIÓN DESDE EL CALENDARIO
# ============================================================

def _sembrar_desde_enlace(temporadas):
    """Aplica ?local=&visitante=&fecha=&temporada= (enlace del calendario)."""

    params = st.query_params

    if "local" not in params:
        return

    local = params.get("local")
    visitante = params.get("visitante")
    temporada = params.get("temporada")

    try:
        fecha = date.fromisoformat(params.get("fecha", ""))
    except ValueError:
        fecha = None

    if (
        local in EQUIPOS_ACTIVOS
        and visitante in EQUIPOS_ACTIVOS
        and temporada in temporadas
        and fecha is not None
    ):
        st.session_state["equipo_local"] = local
        st.session_state["equipo_visitante"] = visitante
        st.session_state["pred_temporada"] = temporada
        st.session_state["pred_fecha"] = fecha

    st.query_params.clear()


def _limpiar_estado_equipos(equipos):
    for clave in ("equipo_local", "equipo_visitante"):
        if st.session_state.get(clave) not in equipos:
            st.session_state.pop(clave, None)


def guardar_resultado_en_historial(
    resultado, temporada, fecha_partido, equipo_local, equipo_visitante
):
    xgb = resultado["xgboost"]
    probabilidades = xgb["probabilidades"]
    goles = resultado["goles"]
    marcador = resultado["marcador_probable"]

    return guardar_prediccion(
        temporada=temporada,
        fecha_partido=fecha_partido.isoformat(),
        equipo_local=equipo_local,
        equipo_visitante=equipo_visitante,
        prob_local=probabilidades.get("L", 0.0),
        prob_empate=probabilidades.get("E", 0.0),
        prob_visitante=probabilidades.get("V", 0.0),
        resultado_predicho=xgb["resultado"],
        lambda_local=goles["lambda_local"],
        lambda_visitante=goles["lambda_visitante"],
        marcador_local=marcador["local"],
        marcador_visitante=marcador["visitante"],
        prob_marcador=marcador["probabilidad"],
    )


# ============================================================
# DATOS
# ============================================================

db_disponible = preparar_base_datos()

try:
    historico = obtener_historico()
    temporadas = obtener_temporadas()
except Exception as exc:
    page_header("Predicción de partido")
    error_state(
        "No se pudieron cargar los datos",
        "Verifique que exista el histórico de partidos procesado.",
        detalle=str(exc),
    )
    st.stop()


page_header(
    "Predicción de partido",
    "Estimación de las probabilidades 1X2 y del marcador de un encuentro de "
    "la Liga Panameña de Fútbol.",
)

equipos = EQUIPOS_ACTIVOS.copy()

_sembrar_desde_enlace(temporadas)
_limpiar_estado_equipos(equipos)

st.session_state.setdefault("pred_temporada", temporadas[-1])
st.session_state.setdefault("pred_fecha", date.today())
st.session_state.setdefault("equipo_local", equipos[0])
st.session_state.setdefault(
    "equipo_visitante",
    equipos[1] if len(equipos) > 1 else equipos[0],
)


# ============================================================
# CONFIGURACIÓN DEL PARTIDO
# ============================================================

with st.container(key="match-controls"):
    meta_col, fecha_col = st.columns([1, 1], gap="large", vertical_alignment="bottom")

    with meta_col:
        temporada = st.selectbox(
            "Temporada",
            temporadas,
            key="pred_temporada",
            format_func=lambda t: nombre_torneo(t) or str(t),
        )

    with fecha_col:
        fecha_partido = st.date_input(
            "Fecha del partido", key="pred_fecha", format="DD/MM/YYYY"
        )

    local_col, visitante_col = st.columns([1, 1], gap="large")

    with local_col:
        equipo_local = st.selectbox("Equipo local", equipos, key="equipo_local")

    with visitante_col:
        equipo_visitante = st.selectbox(
            "Equipo visitante", equipos, key="equipo_visitante"
        )


mostrar(versus_html(equipo_local, equipo_visitante, temporada, fecha_partido))


# ============================================================
# ANÁLISIS
# ============================================================

_, centro, _ = st.columns([2, 3, 2])

with centro:
    analizar = st.button(
        "Analizar partido",
        type="primary",
        icon=":material/analytics:",
        key="analyze-button",
        width="stretch",
    )

if analizar:
    if equipo_local == equipo_visitante:
        st.error(
            "Seleccione dos equipos diferentes para ejecutar el análisis.",
            icon=":material/error:",
        )
    else:
        with st.spinner("Calculando la predicción con los modelos entrenados…"):
            modelos = obtener_modelos()
            resultado = analizar_partido(
                historico=historico,
                modelos=modelos,
                equipo_local=equipo_local,
                equipo_visitante=equipo_visitante,
                fecha=fecha_partido,
                temporada=temporada,
            )

            if db_disponible:
                try:
                    guardar_resultado_en_historial(
                        resultado,
                        temporada,
                        fecha_partido,
                        equipo_local,
                        equipo_visitante,
                    )
                except Exception:
                    st.warning(
                        "El análisis se calculó correctamente, "
                        "pero no se pudo guardar en el historial local.",
                        icon=":material/info:",
                    )
            else:
                st.warning(
                    "El análisis se calculó correctamente, "
                    "pero la base SQLite local no está disponible.",
                    icon=":material/info:",
                )

        section_title("Pronóstico del partido", "XGBoost")
        mostrar(prediction_panel_html(resultado, equipo_local, equipo_visitante))

        section_title("Goles esperados y marcadores", "Poisson")
        mostrar(poisson_panel_html(resultado, equipo_local, equipo_visitante))


# ============================================================
# ÚLTIMOS ANÁLISIS
# ============================================================

section_title("Últimos análisis", "Historial local")

if not db_disponible:
    error_state(
        "Historial no disponible",
        "El historial local no está disponible en este momento.",
    )
else:
    registros, error = leer_historial(5)

    if error is not None:
        error_state(
            "No se pudo leer el historial",
            "No fue posible leer el historial local.",
        )
    elif not registros:
        empty_state(
            "Aún no hay análisis guardados",
            "Al ejecutar «Analizar partido», el resultado se registrará en esta sección.",
            icono="🗂",
        )
    else:
        mostrar(history_cards_html(registros))
