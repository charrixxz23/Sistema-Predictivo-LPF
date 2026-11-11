"""Inicio: resumen de la temporada, próxima jornada y líderes."""

import streamlit as st

from ui.components import (
    error_state,
    match_card_html,
    match_grid,
    metric_row,
    mostrar,
    page_header,
    section_title,
    skeleton_html,
    standings_table,
)
from ui.loaders import (
    leer_historial,
    obtener_calendario,
    obtener_clasificacion,
    obtener_historico,
    obtener_temporadas,
    predecir_partido_calendario,
)
from services.liga_service import jornada_sugerida
from services.reporte_service import fecha_corte_entrenamiento


try:
    historico = obtener_historico()
    temporadas = obtener_temporadas()
    calendario, temporada_cal = obtener_calendario()
except Exception as exc:
    page_header("Inicio", "LPF Predictive Center")
    error_state(
        "No se pudieron cargar los datos",
        "Revisa que existan los archivos de data/processed y data/raw/partidos.",
        detalle=str(exc),
    )
    st.stop()


jornada = jornada_sugerida(calendario)
total_jornadas = int(calendario["jornada"].max()) if not calendario.empty else 0

registros, _ = leer_historial(100000)

page_header(
    "Inicio",
    "Predicción deportiva con Machine Learning",
    "XGBoost estima el resultado 1X2 y los modelos Poisson los goles y el "
    "marcador más probable de cada partido.",
    chips=[(f"Temporada {temporada_cal}", "accent")],
)

metric_row(
    [
        ("Partidos en la base", f"{len(historico):,}", "Histórico 2014-2026", "accent"),
        ("Temporadas", str(len(temporadas)), "Con datos para modelado", ""),
        (
            "Jornada en foco",
            f"{jornada} de {total_jornadas}" if jornada else "-",
            "Primera con partidos pendientes",
            "gold",
        ),
        ("Análisis guardados", str(len(registros)), "En el historial local", ""),
    ]
)


# ------------------------------------------------------------
# Próxima jornada
# ------------------------------------------------------------

section_title(
    "Próxima jornada",
    f"Jornada {jornada}" if jornada else "",
)

if calendario.empty or jornada is None:
    mostrar("<div class='lpf-section__hint'>Aún no hay calendario cargado.</div>")
else:
    partidos = calendario[calendario["jornada"] == jornada].head(3)

    hueco = st.empty()
    hueco.html(skeleton_html(len(partidos)))

    tarjetas = []

    for partido in partidos.to_dict("records"):
        try:
            prediccion = predecir_partido_calendario(
                partido["local"],
                partido["visitante"],
                partido["fecha"].isoformat(),
                temporada_cal,
            )
        except Exception:
            prediccion = None

        tarjetas.append(
            match_card_html(
                partido,
                prediccion,
                temporada_cal,
                fecha_corte_entrenamiento(),
            )
        )

    hueco.empty()
    match_grid(tarjetas)

    st.page_link(
        "views/calendario.py",
        label="Ver calendario completo",
        icon=":material/calendar_month:",
    )


# ------------------------------------------------------------
# Clasificación
# ------------------------------------------------------------

section_title("Líderes de la temporada", f"Top 5 · {temporada_cal}")

tabla = obtener_clasificacion(temporada_cal)

if tabla.empty:
    mostrar("<div class='lpf-section__hint'>Sin partidos jugados todavía.</div>")
else:
    standings_table(tabla.head(5))

st.page_link(
    "views/clasificacion.py",
    label="Ver tabla completa",
    icon=":material/leaderboard:",
)
