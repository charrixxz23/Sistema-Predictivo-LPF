"""Historial completo de análisis guardados en SQLite (solo lectura)."""

import pandas as pd
import streamlit as st

from ui.components import (
    RESULTADO_LABELS,
    empty_state,
    error_state,
    formatear_fecha,
    formatear_fecha_hora,
    history_cards_html,
    metric_row,
    mostrar,
    page_header,
    section_title,
)
from ui.loaders import leer_historial, preparar_base_datos


page_header(
    "Historial",
    "Análisis guardados",
    "Cada análisis ejecutado en la sección Predicciones queda registrado "
    "en la base SQLite local.",
)

if not preparar_base_datos():
    error_state(
        "Historial no disponible",
        "No fue posible abrir la base SQLite local en database/.",
    )
    st.stop()

registros, error = leer_historial(100000)

if error is not None:
    error_state(
        "No se pudo leer el historial",
        "La consulta a la base local falló.",
        detalle=str(error),
    )
    st.stop()

if not registros:
    empty_state(
        "Aún no hay análisis guardados",
        "Ve a Predicciones, elige un partido y pulsa «Analizar partido».",
        icono="🗂",
    )
    st.stop()


df = pd.DataFrame(registros)

conteo = df["resultado_predicho"].value_counts()
equipos = pd.concat([df["equipo_local"], df["equipo_visitante"]]).value_counts()

metric_row(
    [
        ("Análisis guardados", str(len(df)), "Total en la base local", "accent"),
        (
            "Pronósticos locales",
            str(int(conteo.get("L", 0))),
            f"{int(conteo.get('E', 0))} empates · {int(conteo.get('V', 0))} visitantes",
            "",
        ),
        (
            "Equipo más consultado",
            str(equipos.index[0]),
            f"{int(equipos.iloc[0])} análisis",
            "gold",
        ),
        (
            "Último análisis",
            formatear_fecha(str(df.iloc[0]["fecha_consulta"])[:10]),
            formatear_fecha_hora(df.iloc[0]["fecha_consulta"]),
            "",
        ),
    ]
)

section_title("Registros", "Del más reciente al más antiguo")

vista_col, limite_col = st.columns([3, 2], vertical_alignment="bottom")

with vista_col:
    vista = st.segmented_control(
        "Vista",
        ["Tarjetas", "Tabla"],
        default="Tarjetas",
        key="historial_vista",
    )

with limite_col:
    opciones = [n for n in (10, 25, 50, 100) if n < len(df)] + [len(df)]
    limite = st.selectbox(
        "Mostrar",
        opciones,
        index=0,
        format_func=lambda n: "Todos" if n == len(df) else f"Últimos {n}",
        key="historial_limite",
    )

visibles = df.head(limite)

if vista == "Tabla":
    tabla = pd.DataFrame(
        {
            "Analizado": visibles["fecha_consulta"].map(formatear_fecha_hora),
            "Fecha partido": visibles["fecha_partido"].map(formatear_fecha),
            "Temporada": visibles["temporada"],
            "Local": visibles["equipo_local"],
            "Visitante": visibles["equipo_visitante"],
            "P. local": visibles["prob_local"],
            "P. empate": visibles["prob_empate"],
            "P. visitante": visibles["prob_visitante"],
            "Pronóstico": visibles["resultado_predicho"].map(
                lambda c: RESULTADO_LABELS.get(c, c)
            ),
            "Marcador": visibles["marcador_local"].astype(str)
            + " - "
            + visibles["marcador_visitante"].astype(str),
        }
    )

    st.dataframe(
        tabla,
        hide_index=True,
        width="stretch",
        column_config={
            "P. local": st.column_config.NumberColumn(format="percent"),
            "P. empate": st.column_config.NumberColumn(format="percent"),
            "P. visitante": st.column_config.NumberColumn(format="percent"),
        },
    )

    st.download_button(
        "Descargar CSV",
        tabla.to_csv(index=False).encode("utf-8-sig"),
        file_name="historial_predicciones.csv",
        mime="text/csv",
        icon=":material/download:",
    )
else:
    mostrar(history_cards_html(visibles.to_dict("records")))
