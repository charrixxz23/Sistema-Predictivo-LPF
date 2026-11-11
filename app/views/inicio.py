"""Inicio: abre con la jornada y sus partidos, como un sitio deportivo."""

import streamlit as st

from services.liga_service import jornada_sugerida
from services.reporte_service import fecha_corte_entrenamiento
from ui.components import (
    day_heading,
    empty_state,
    error_state,
    etiqueta_temporada,
    match_card_html,
    match_grid,
    mostrar,
    page_header,
    section_title,
    skeleton_html,
    standings_table,
    zone_legend_html,
)
from ui.loaders import (
    obtener_calendario,
    obtener_clasificacion,
    obtener_clasificacion_oficial,
    obtener_historico,
    predecir_partido_calendario,
)


try:
    obtener_historico()
    calendario, temporada_cal = obtener_calendario()
except Exception as exc:
    page_header("Inicio")
    error_state(
        "No se pudieron cargar los datos",
        "Verificar que estén disponibles los datos procesados y el calendario de partidos.",
        detalle=str(exc),
    )
    st.stop()


jornada = jornada_sugerida(calendario)

if calendario.empty or jornada is None:
    page_header("Inicio")
    empty_state(
        "Calendario no disponible",
        "La jornada en curso se mostrará cuando exista un calendario de partidos "
        "cargado.",
        icono="📅",
    )
    st.stop()


total_jornadas = int(calendario["jornada"].max())
partidos = calendario[calendario["jornada"] == jornada]
pendientes = int((partidos["estado"] == "pendiente").sum())

page_header(
    f"Jornada {jornada} de {total_jornadas}",
    f"{len(partidos)} partidos · {pendientes} pendientes · {etiqueta_temporada(temporada_cal)}",
)

partidos_col, tabla_col = st.columns([3, 2], gap="large")


# ------------------------------------------------------------
# Partidos de la jornada
# ------------------------------------------------------------

with partidos_col:
    hueco = st.empty()
    hueco.html(skeleton_html(len(partidos)))

    predicciones = {}

    for partido in partidos.to_dict("records"):
        try:
            predicciones[(partido["local"], partido["visitante"])] = (
                predecir_partido_calendario(
                    partido["local"],
                    partido["visitante"],
                    partido["fecha"].isoformat(),
                    temporada_cal,
                )
            )
        except Exception:
            predicciones[(partido["local"], partido["visitante"])] = None

    hueco.empty()

    corte = fecha_corte_entrenamiento()

    for fecha, grupo in partidos.groupby("fecha", sort=True):
        day_heading(fecha)

        match_grid(
            [
                match_card_html(
                    partido,
                    predicciones.get((partido["local"], partido["visitante"])),
                    temporada_cal,
                    corte,
                )
                for partido in grupo.to_dict("records")
            ]
        )

    st.page_link(
        "views/calendario.py",
        label="Ver todas las jornadas",
        icon=":material/calendar_month:",
    )


# ------------------------------------------------------------
# Clasificación
# ------------------------------------------------------------

with tabla_col:
    section_title("Clasificación", "Fase de clasificación")

    oficial = obtener_clasificacion_oficial(temporada_cal)

    if oficial is not None and not oficial["General"].empty:
        # Temporada con conferencias: las dos tablas (6 + 6) con sus zonas
        for conferencia in ("Este", "Oeste"):
            mostrar(f"<h3 class='lpf-subseccion'>Conferencia {conferencia}</h3>")
            standings_table(
                oficial[conferencia], corto=True, compacta=True, zonas=True
            )

        mostrar(zone_legend_html())
    else:
        tabla = obtener_clasificacion(temporada_cal)

        if tabla.empty:
            empty_state(
                "Sin partidos jugados todavía",
                "La tabla se mostrará cuando existan resultados registrados.",
                icono="🏆",
            )
        else:
            standings_table(tabla.head(8), corto=True, compacta=True)

    st.page_link(
        "views/clasificacion.py",
        label="Ver tabla completa",
        icon=":material/leaderboard:",
    )
