from datetime import date, datetime
from html import escape
from pathlib import Path

import streamlit as st

from services.database_service import (
    guardar_prediccion,
    inicializar_base_datos,
    obtener_ultimas_predicciones,
)
from services.feature_service import (
    cargar_historico,
    obtener_temporadas_disponibles,
)
from services.model_service import cargar_modelos
from services.prediction_service import analizar_partido
from services.team_assets import (
    EQUIPOS_ACTIVOS,
    obtener_abreviatura,
    obtener_logo_path,
)


# ============================================================
# RUTAS
# ============================================================

APP_DIR = Path(__file__).resolve().parent

CSS_PATH = APP_DIR / "assets" / "styles" / "main.css"

LPF_LOGO = APP_DIR / "assets" / "logos" / "lpf.png"


# ============================================================
# CONFIGURACION
# ============================================================

st.set_page_config(
    page_title="LPF Predictive Center",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CONSTANTES DE UI
# ============================================================

RESULTADO_LABELS = {
    "L": "Victoria local",
    "E": "Empate",
    "V": "Victoria visitante",
}

RESULTADO_ROLES = {
    "L": "LOCAL",
    "E": "EMPATE",
    "V": "VISITANTE",
}


# ============================================================
# UTILIDADES
# ============================================================

def cargar_css():
    if CSS_PATH.exists():
        st.html(CSS_PATH)


def render_html(markup):
    st.html(markup)


def porcentaje(valor, decimales=1):
    return f"{valor * 100:.{decimales}f} %"


def numero(valor, decimales=2):
    return f"{valor:.{decimales}f}"


def texto_seguro(valor):
    if valor is None:
        return ""

    return escape(str(valor))


def formatear_fecha(valor):
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")

    try:
        return date.fromisoformat(str(valor)).strftime("%d/%m/%Y")
    except ValueError:
        return str(valor)


def formatear_fecha_hora(valor):
    try:
        return datetime.fromisoformat(str(valor)).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return str(valor).replace("T", " ")


# ============================================================
# DATOS Y MODELOS
# ============================================================

def preparar_base_datos():
    try:
        inicializar_base_datos()
        return True
    except Exception:
        return False


@st.cache_data(show_spinner=False)
def obtener_historico():
    return cargar_historico()


@st.cache_resource(show_spinner=False)
def obtener_modelos():
    return cargar_modelos()


# ============================================================
# RENDER
# ============================================================

def render_header():
    with st.container(key="app-header"):
        logo_col, title_col, status_col = st.columns(
            [1.25, 5.9, 2.05],
            vertical_alignment="center",
        )

        with logo_col:
            if LPF_LOGO.exists():
                st.image(
                    str(LPF_LOGO),
                    width=170,
                    alt="Logo de la Liga Panameña de Fútbol",
                )

        with title_col:
            render_html(
                "<div class='header-kicker'>LIGA PANAMEÑA DE FÚTBOL</div>"
                "<div class='header-title'>LPF Predictive Center</div>"
                "<div class='header-subtitle'>Predicción deportiva mediante Machine Learning</div>"
            )

        with status_col:
            render_html(
                "<div class='system-status'>"
                "<span class='status-dot'></span>"
                "<span>SISTEMA ACTIVO</span>"
                "</div>"
            )

    render_html("<div class='header-divider'></div>")


def render_match_center_intro():
    render_html(
        "<section class='match-center-intro'>"
        "<div class='section-kicker'>MATCH CENTER</div>"
        "<h1>Predicción de partido</h1>"
        "<p>Centro de análisis para encuentros de la Liga Panameña de Fútbol</p>"
        "</section>"
    )


def limpiar_estado_selector_equipos(equipos):
    for clave in ("equipo_local", "equipo_visitante"):
        if st.session_state.get(clave) not in equipos:
            st.session_state.pop(clave, None)


def render_match_controls(temporadas):
    with st.container(border=True, key="match-controls"):
        render_html(
            "<div class='controls-title'>"
            "<span>Configuración del partido</span>"
            "<strong>Temporada, fecha y clubes</strong>"
            "</div>"
        )

        meta_col, fecha_col = st.columns(
            [1, 1],
            gap="large",
            vertical_alignment="bottom",
        )

        with meta_col:
            temporada = st.selectbox(
                "Temporada",
                temporadas,
                index=len(temporadas) - 1,
            )

        with fecha_col:
            fecha_partido = st.date_input(
                "Fecha del partido",
                value=date.today(),
            )

        equipos = EQUIPOS_ACTIVOS.copy()
        limpiar_estado_selector_equipos(equipos)

        local_col, vs_col, visitante_col = st.columns(
            [5, 1.1, 5],
            gap="large",
            vertical_alignment="bottom",
        )

        with local_col:
            equipo_local = st.selectbox(
                "Equipo local",
                equipos,
                key="equipo_local",
            )

        with vs_col:
            render_html("<div class='selector-vs'>VS</div>")

        with visitante_col:
            indice_visitante = 1 if len(equipos) > 1 else 0

            equipo_visitante = st.selectbox(
                "Equipo visitante",
                equipos,
                index=indice_visitante,
                key="equipo_visitante",
            )

    return temporada, fecha_partido, equipo_local, equipo_visitante


def render_team_card(equipo, rol, lado):
    abreviatura = escape(obtener_abreviatura(equipo))
    equipo_seguro = escape(equipo)
    logo = obtener_logo_path(equipo)

    with st.container(border=True, key=f"team-card-{lado}"):
        render_html(f"<div class='team-role'>{escape(rol)}</div>")

        with st.container(horizontal_alignment="center", key=f"crest-shell-{lado}"):
            if logo:
                st.image(
                    str(logo),
                    width="stretch",
                    alt=f"Escudo de {equipo}",
                )
            else:
                render_html("<div class='crest-placeholder'>SIN LOGO</div>")

        render_html(
            f"<div class='team-name'>{equipo_seguro}</div>"
            f"<div class='team-code'>{abreviatura}</div>"
        )


def render_vs_block():
    render_html(
        "<div class='central-vs'>"
        "<div class='central-vs-small'>PARTIDO</div>"
        "<div class='central-vs-main'>VS</div>"
        "</div>"
    )


def render_matchup(equipo_local, equipo_visitante, temporada, fecha_partido):
    render_html(
        "<div class='fixture-meta'>"
        f"<span>Temporada {escape(str(temporada))}</span>"
        f"<span>{escape(fecha_partido.strftime('%d/%m/%Y'))}</span>"
        "</div>"
    )

    local_col, vs_col, visitante_col = st.columns(
        [5, 1.25, 5],
        gap="large",
        vertical_alignment="center",
    )

    with local_col:
        render_team_card(equipo_local, "LOCAL", "local")

    with vs_col:
        render_vs_block()

    with visitante_col:
        render_team_card(equipo_visitante, "VISITANTE", "visitante")


def render_analysis_button():
    left, center, right = st.columns([2.4, 3.2, 2.4])

    with center:
        return st.button(
            "ANALIZAR PARTIDO",
            type="primary",
            icon=":material/analytics:",
            key="analyze-button",
            width="stretch",
        )


def render_prediction_section(resultado, equipo_local, equipo_visitante):
    xgb = resultado["xgboost"]
    probabilidades = xgb["probabilidades"]
    prediccion = xgb["resultado"]

    equipos = {
        "L": equipo_local,
        "E": "Empate",
        "V": equipo_visitante,
    }

    cards = []

    for codigo in ("L", "E", "V"):
        probabilidad = probabilidades.get(codigo, 0.0)
        barra = max(0.0, min(probabilidad * 100, 100.0))
        activo = " is-active" if codigo == prediccion else ""

        cards.append(
            "<article class='prob-card"
            f"{activo}'>"
            f"<span class='prob-role'>{RESULTADO_ROLES[codigo]}</span>"
            f"<strong>{escape(equipos[codigo])}</strong>"
            f"<div class='prob-value'>{porcentaje(probabilidad)}</div>"
            "<div class='prob-track'>"
            f"<span class='prob-fill' style='--bar:{barra:.2f}%;'></span>"
            "</div>"
            f"<small>{RESULTADO_LABELS[codigo]}</small>"
            "</article>"
        )

    render_html(
        "<section class='prediction-panel fade-in'>"
        "<div class='panel-heading'>"
        "<span>PRONÓSTICO PRINCIPAL</span>"
        "<h2>Pronóstico del partido</h2>"
        "</div>"
        f"<div class='prob-grid'>{''.join(cards)}</div>"
        "<div class='main-pick'>"
        "<span>Predicción principal</span>"
        f"<strong>{escape(RESULTADO_LABELS.get(prediccion, prediccion)).upper()}</strong>"
        "</div>"
        "</section>"
    )


def render_poisson_section(resultado, equipo_local, equipo_visitante):
    goles = resultado["goles"]
    marcador = resultado["marcador_probable"]
    top_marcadores = resultado["top_marcadores"]

    top_cards = []

    for item in top_marcadores:
        top_cards.append(
            "<article class='score-pill'>"
            f"<strong>{item['local']} - {item['visitante']}</strong>"
            f"<span>{porcentaje(item['probabilidad'], 2)}</span>"
            "</article>"
        )

    render_html(
        "<section class='poisson-panel fade-in'>"
        "<div class='panel-heading'>"
        "<span>ANÁLISIS DE GOLES</span>"
        "<h2>Goles esperados y marcadores</h2>"
        "</div>"
        "<div class='poisson-layout'>"
        "<div class='expected-goals'>"
        "<article class='goal-card'>"
        f"<span>{escape(equipo_local)}</span>"
        f"<strong>{numero(goles['lambda_local'])}</strong>"
        "<small>Goles esperados</small>"
        "</article>"
        "<article class='goal-card'>"
        f"<span>{escape(equipo_visitante)}</span>"
        f"<strong>{numero(goles['lambda_visitante'])}</strong>"
        "<small>Goles esperados</small>"
        "</article>"
        "</div>"
        "<article class='modal-score'>"
        "<span>MARCADOR MÁS PROBABLE</span>"
        f"<strong>{marcador['local']} - {marcador['visitante']}</strong>"
        f"<small>{porcentaje(marcador['probabilidad'], 2)}</small>"
        "</article>"
        "</div>"
        "<div class='top-scores'>"
        "<span>MARCADORES MÁS PROBABLES</span>"
        f"<div class='score-list'>{''.join(top_cards)}</div>"
        "</div>"
        "</section>"
    )


def render_results(resultado, equipo_local, equipo_visitante):
    render_prediction_section(
        resultado,
        equipo_local,
        equipo_visitante,
    )

    render_poisson_section(
        resultado,
        equipo_local,
        equipo_visitante,
    )


def guardar_resultado_en_historial(
    resultado,
    temporada,
    fecha_partido,
    equipo_local,
    equipo_visitante,
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


def render_history_section(db_disponible):
    if not db_disponible:
        render_html(
            "<section class='history-panel'>"
            "<div class='history-heading'>"
            "<span>HISTORIAL DE ANÁLISIS</span>"
            "<h2>Últimos análisis</h2>"
            "</div>"
            "<div class='history-empty'>"
            "El historial local no está disponible en este momento."
            "</div>"
            "</section>"
        )
        return

    try:
        registros = obtener_ultimas_predicciones(limite=5)
    except Exception:
        render_html(
            "<section class='history-panel'>"
            "<div class='history-heading'>"
            "<span>HISTORIAL DE ANÁLISIS</span>"
            "<h2>Últimos análisis</h2>"
            "</div>"
            "<div class='history-empty'>"
            "No fue posible leer el historial local."
            "</div>"
            "</section>"
        )
        return

    if not registros:
        render_html(
            "<section class='history-panel'>"
            "<div class='history-heading'>"
            "<span>HISTORIAL DE ANÁLISIS</span>"
            "<h2>Últimos análisis</h2>"
            "</div>"
            "<div class='history-empty'>"
            "Aún no hay análisis guardados."
            "</div>"
            "</section>"
        )
        return

    cards = []

    for registro in registros:
        prediccion = registro.get("resultado_predicho", "")
        etiqueta = RESULTADO_LABELS.get(
            prediccion,
            prediccion,
        )
        marcador = (
            f"{registro.get('marcador_local', '-')}"
            " - "
            f"{registro.get('marcador_visitante', '-')}"
        )

        cards.append(
            "<article class='history-card'>"
            "<div class='history-meta'>"
            f"<span>{texto_seguro(formatear_fecha(registro.get('fecha_partido')))}</span>"
            f"<span>Temporada {texto_seguro(registro.get('temporada'))}</span>"
            "</div>"
            "<div class='history-match'>"
            f"<strong>{texto_seguro(registro.get('equipo_local'))}</strong>"
            "<span>vs</span>"
            f"<strong>{texto_seguro(registro.get('equipo_visitante'))}</strong>"
            "</div>"
            "<div class='history-detail'>"
            "<div>"
            "<span>Pronóstico</span>"
            f"<strong>{texto_seguro(etiqueta)}</strong>"
            "</div>"
            "<div>"
            "<span>Marcador Poisson</span>"
            f"<strong>{texto_seguro(marcador)}</strong>"
            "</div>"
            "</div>"
            "<div class='history-footer'>"
            f"<span>Analizado {texto_seguro(formatear_fecha_hora(registro.get('fecha_consulta')))}</span>"
            f"<span>{porcentaje(float(registro.get('prob_marcador') or 0.0), 2)}</span>"
            "</div>"
            "</article>"
        )

    render_html(
        "<section class='history-panel fade-in'>"
        "<div class='history-heading'>"
        "<span>HISTORIAL DE ANÁLISIS</span>"
        "<h2>Últimos análisis</h2>"
        "</div>"
        f"<div class='history-grid'>{''.join(cards)}</div>"
        "</section>"
    )


# ============================================================
# APP
# ============================================================

cargar_css()
db_disponible = preparar_base_datos()

historico = obtener_historico()
temporadas = obtener_temporadas_disponibles(historico)

render_header()
render_match_center_intro()

temporada, fecha_partido, equipo_local, equipo_visitante = render_match_controls(
    temporadas,
)

render_matchup(
    equipo_local,
    equipo_visitante,
    temporada,
    fecha_partido,
)

analizar = render_analysis_button()

if analizar:
    if equipo_local == equipo_visitante:
        st.error(
            "Selecciona dos equipos diferentes para ejecutar el análisis.",
            icon=":material/error:",
        )
    else:
        with st.spinner("Ejecutando inferencia con los modelos entrenados..."):
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
                        (
                            "El análisis se calculó correctamente, "
                            "pero no se pudo guardar en el historial local."
                        ),
                        icon=":material/info:",
                    )
            else:
                st.warning(
                    (
                        "El análisis se calculó correctamente, "
                        "pero la base SQLite local no está disponible."
                    ),
                    icon=":material/info:",
                )

        render_results(
            resultado,
            equipo_local,
            equipo_visitante,
        )

render_history_section(db_disponible)
