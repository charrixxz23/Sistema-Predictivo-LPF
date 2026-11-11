"""Historial completo de análisis guardados en SQLite (solo lectura)."""

import pandas as pd
import streamlit as st

from ui.components import (
    RESULTADO_LABELS,
    empty_state,
    error_state,
    formatear_fecha,
    formatear_fecha_hora,
    data_line,
    history_cards_html,
    mostrar,
    page_header,
    section_title,
)
from ui.loaders import leer_historial, preparar_base_datos


page_header(
    "Historial de análisis",
    "Registro de los análisis ejecutados en la sección Predicciones, "
    "almacenado en una base de datos local (SQLite).",
)

if not preparar_base_datos():
    error_state(
        "Historial no disponible",
        "No fue posible abrir la base de datos local.",
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
        "Los análisis ejecutados en la sección Predicciones se registrarán aquí.",
        icono="🗂",
    )
    st.stop()


df = pd.DataFrame(registros)

conteo = df["resultado_predicho"].value_counts()
equipos = pd.concat([df["equipo_local"], df["equipo_visitante"]]).value_counts()

data_line(
    [
        (str(len(df)), "análisis guardados"),
        (
            str(int(conteo.get("L", 0))),
            f"pronósticos locales ({int(conteo.get('E', 0))} empates, "
            f"{int(conteo.get('V', 0))} visitantes)",
        ),
        ("Más consultado", f"{equipos.index[0]} · {int(equipos.iloc[0])} análisis"),
        ("Último", formatear_fecha_hora(df.iloc[0]["fecha_consulta"])),
    ]
)

section_title("Registros", "Del más reciente al más antiguo")

vista_col, limite_col = st.columns([3, 2], vertical_alignment="bottom")

with vista_col:
    vista = st.segmented_control(
        "Vista",
        ["Lista", "Tabla"],
        default="Lista",
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
