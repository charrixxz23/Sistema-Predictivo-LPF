"""Tabla de clasificación por temporada."""

from datetime import date

import streamlit as st

from ui.components import (
    data_line,
    empty_state,
    error_state,
    foot_note,
    page_header,
    section_title,
    standings_table,
)
from ui.loaders import (
    obtener_calendario,
    obtener_clasificacion,
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
        "Revisa que exista data/processed/lpf_historico_modelado.csv.",
        detalle=str(exc),
    )
    st.stop()

page_header(
    "Tabla de posiciones",
    "Acumulado de la temporada a partir de los resultados registrados. "
    "Orden: puntos, diferencia de goles y goles a favor.",
)

temporada = st.selectbox(
    "Temporada",
    temporadas,
    index=len(temporadas) - 1,
    key="clasificacion_temporada",
)

tabla = obtener_clasificacion(temporada)

if tabla.empty:
    empty_state(
        "Sin resultados para esta temporada",
        "Elige otra temporada para ver su clasificación.",
        icono="🏆",
    )
    st.stop()

lider = tabla.iloc[0]
goles = int(tabla["gf"].sum())
partidos = int(tabla["pj"].sum() // 2)
promedio = goles / partidos if partidos else 0.0
mejor_ataque = tabla.sort_values("gf", ascending=False).iloc[0]
mejor_defensa = tabla.sort_values("gc", ascending=True).iloc[0]

# Métricas en una línea de datos sobre la tabla (sin tarjetas)
data_line(
    [
        ("Líder", f"{lider['equipo']} · {lider['pts']} pts"),
        (str(partidos), f"partidos jugados ({goles} goles)"),
        (f"{promedio:.2f}", "goles por partido"),
        ("Mejor ataque", f"{mejor_ataque['equipo']} · {mejor_ataque['gf']} GF"),
        ("Mejor defensa", f"{mejor_defensa['equipo']} · {mejor_defensa['gc']} GC"),
    ]
)

acumulada = temporada_acumula_torneos(temporada)

section_title(
    "Tabla acumulada (Apertura + Clausura)" if acumulada else "Posiciones",
    f"Temporada {temporada}",
)

standings_table(tabla)

# Nota al pie: criterios y alcance de los datos
detalle = (
    "Calculada con los datos del sistema. Suma los partidos con resultado "
    "registrado, sin playoffs. Desempate: diferencia de goles, goles a favor y "
    "orden alfabético; no se aplican otros criterios oficiales."
)

if acumulada:
    detalle += (
        " Esta temporada reúne Apertura y Clausura en una sola tabla; los "
        "datos no permiten separarlos."
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
                f" Hay {len(sin_resultado)} partidos con fecha pasada y sin "
                "resultado en los datos; no están contados."
            )
except Exception:
    pass

foot_note(detalle)

foot_note(
    "PJ partidos jugados · G ganados · E empatados · P perdidos · "
    "GF/GC goles a favor/en contra · DG diferencia · Forma: últimos 5 "
    "(azul gana, gris empata, rojo pierde)."
)
