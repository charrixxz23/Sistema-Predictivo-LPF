"""Tabla de clasificación por temporada (con conferencias cuando el reglamento las define)."""

from datetime import date

import streamlit as st

from services.liga_service import nombre_torneo
from ui.components import (
    bracket_html,
    data_line,
    empates_sin_resolver,
    empty_state,
    error_state,
    foot_note,
    etiqueta_temporada,
    mostrar,
    page_header,
    section_title,
    standings_table,
    zone_legend_html,
)
from ui.loaders import (
    obtener_calendario,
    obtener_clasificacion,
    obtener_clasificacion_oficial,
    obtener_cruces_si_terminara_hoy,
    obtener_historico,
    obtener_temporadas,
    temporada_acumula_torneos,
)


try:
    historico = obtener_historico()
    temporadas = obtener_temporadas()
except Exception as exc:
    page_header("Clasificación")
    error_state(
        "No se pudieron cargar los datos",
        "Verificar que exista el histórico de partidos procesado.",
        detalle=str(exc),
    )
    st.stop()

page_header(
    "Tabla de posiciones",
    "Acumulado de la temporada a partir de los resultados registrados. "
    "Orden: puntos y, entre empatados, el desempate del Reglamento de "
    "Competencias de la LPF (art. 11).",
)

temporada = st.selectbox(
    "Temporada",
    temporadas,
    index=len(temporadas) - 1,
    key="clasificacion_temporada",
    format_func=lambda t: nombre_torneo(t) or str(t),
)

tabla = obtener_clasificacion(temporada)

if tabla.empty:
    empty_state(
        "Sin resultados para esta temporada",
        "Seleccione otra temporada para ver su clasificación.",
        icono="🏆",
    )
    st.stop()

oficial = obtener_clasificacion_oficial(temporada)

goles = int(tabla["gf"].sum())
partidos = int(tabla["pj"].sum() // 2)
promedio = goles / partidos if partidos else 0.0
mejor_ataque = tabla.sort_values("gf", ascending=False).iloc[0]
mejor_defensa = tabla.sort_values("gc", ascending=True).iloc[0]

if oficial is not None:
    lideres = [
        (f"Líder {c}", f"{oficial[c].iloc[0]['equipo']} · {oficial[c].iloc[0]['pts']} pts")
        for c in ("Este", "Oeste")
    ]
else:
    lider = tabla.iloc[0]
    lideres = [("Líder", f"{lider['equipo']} · {lider['pts']} pts")]

# Métricas en una línea de datos sobre la tabla (sin tarjetas)
data_line(
    lideres
    + [
        (str(partidos), f"partidos jugados ({goles} goles)"),
        (f"{promedio:.2f}", "goles por partido"),
        ("Mejor ataque", f"{mejor_ataque['equipo']} · {mejor_ataque['gf']} GF"),
        ("Mejor defensa", f"{mejor_defensa['equipo']} · {mejor_defensa['gc']} GC"),
    ]
)

acumulada = temporada_acumula_torneos(temporada)

if oficial is not None:
    vista = st.segmented_control(
        "Vista",
        ["Por conferencia", "Tabla general (12 equipos)"],
        default="Por conferencia",
        key="clasificacion_vista",
    )

    if vista == "Tabla general (12 equipos)":
        section_title("Tabla general", etiqueta_temporada(temporada))
        standings_table(oficial["General"])
        foot_note(
            "Los cupos a la fase final se definen por conferencia (art. 10), "
            "por eso esta tabla no marca zonas."
        )
        pendientes_sr = empates_sin_resolver(oficial["General"])
    else:
        este_col, oeste_col = st.columns(2, gap="large")

        for columna, conferencia in ((este_col, "Este"), (oeste_col, "Oeste")):
            with columna:
                section_title(f"Conferencia {conferencia}", "6 clubes")
                standings_table(
                    oficial[conferencia],
                    corto=True,
                    ocultar={"gf", "gc"},
                    zonas=True,
                )

        mostrar(zone_legend_html())

        section_title(
            "Si el torneo terminara hoy",
            "Fase de clasificación completa" if oficial["completa"] else "Con la tabla actual",
        )

        cruces = obtener_cruces_si_terminara_hoy(temporada)

        if cruces is not None:
            mostrar(bracket_html(cruces, oficial["completa"]))

        pendientes_sr = empates_sin_resolver(oficial["Este"]) + empates_sin_resolver(
            oficial["Oeste"]
        )
else:
    section_title(
        "Tabla acumulada (Apertura + Clausura)" if acumulada else "Posiciones",
        etiqueta_temporada(temporada),
    )

    standings_table(tabla)
    pendientes_sr = empates_sin_resolver(tabla)

# Nota al pie: criterios y alcance de los datos
detalle = (
    "Calculada con los datos del sistema. Suma los partidos con resultado "
    "registrado, sin playoffs. Desempate según el art. 11 del Reglamento de "
    "Competencias de la LPF (enero de 2026): diferencia de goles, goles a "
    "favor, resultados entre los empatados y goles como visitante. Los puntos "
    "de juego limpio (tarjetas) no se aplican porque los datos no distinguen "
    "el tipo de tarjeta; si tras esos criterios persiste un empate, se marca "
    "«Empate sin resolver»."
)

if oficial is not None:
    detalle += (
        " El reglamento descuenta además 3 puntos por los minutos de jugadores "
        "de ascenso (art. 6); ese descuento no está en los datos y no se aplica."
    )
else:
    detalle += (
        " Ese reglamento rige para el Clausura 2026; en temporadas anteriores "
        "se usa el mismo orden como referencia y las reglas de entonces "
        "pudieron ser otras."
    )

if acumulada and oficial is None:
    detalle += (
        " Esta temporada reúne Apertura y Clausura en una sola tabla; los "
        "datos no permiten separarlos."
    )

if pendientes_sr:
    detalle += (
        " Empate sin resolver entre: " + ", ".join(pendientes_sr) + " "
        "(lo definiría el juego limpio o un sorteo)."
    )

try:
    calendario, temporada_cal = obtener_calendario()

    if str(temporada) == str(temporada_cal):
        sin_resultado = calendario[
            (calendario["estado"] == "pendiente")
            & (calendario["fecha"] < date.today())
        ]

        if len(sin_resultado):
            detalle += (
                f" Existen {len(sin_resultado)} partidos con fecha pasada y sin "
                "resultado en los datos; no se incluyen en el cálculo."
            )
except Exception:
    pass

foot_note(detalle)

foot_note(
    "PJ partidos jugados · G ganados · E empatados · P perdidos · "
    "GF/GC goles a favor/en contra · DG diferencia · Forma: últimos 5 "
    "partidos (G ganó en verde, E empató en gris, P perdió en rojo); el "
    "cuadro con borde es el más reciente."
)
