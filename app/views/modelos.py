"""Modelos y validación: resultados de los notebooks 07, 08 y 09."""

import streamlit as st

from services.reporte_service import (
    CV_BASELINE_ACCURACY,
    CV_N_FOLDS,
    CV_TEMPORAL,
    FIGURAS,
    POISSON_PRUEBA,
    PRUEBA_FINAL,
    PRUEBA_FINAL_PARTIDOS,
    PRUEBA_FINAL_PERIODO,
    ruta_figura,
)
from ui.components import (
    data_table_html,
    empty_state,
    metric_row,
    mostrar,
    page_header,
    porcentaje,
    section_title,
)


def _pct(valor):
    return "-" if valor is None else porcentaje(valor, 1)


def _num(valor):
    return "-" if valor is None else f"{valor:.4f}"


page_header(
    "Modelos y validación",
    "Qué tan confiable es la predicción",
    "Resultados obtenidos en los notebooks de la tesis. Se muestran tal como "
    "se registraron; no se recalculan al abrir esta página.",
    chips=[(f"{CV_N_FOLDS} folds temporales", ""), ("Ventana expansiva", "")],
)

xgb_cv = next(m for m in CV_TEMPORAL if m["modelo"] == "XGBoost")
mejor_cv = max(CV_TEMPORAL, key=lambda m: m["accuracy"])
xgb_final = next(m for m in PRUEBA_FINAL if m["modelo"] == "XGBoost")
base_final = next(m for m in PRUEBA_FINAL if m["modelo"].startswith("Baseline"))

metric_row(
    [
        (
            "Baseline temporal",
            _pct(CV_BASELINE_ACCURACY),
            "Accuracy promedio de la clase más frecuente",
            "",
        ),
        (
            "Mejor en validación",
            _pct(mejor_cv["accuracy"]),
            f"{mejor_cv['modelo']} · ± {mejor_cv['accuracy_sd'] * 100:.1f} pp",
            "accent",
        ),
        (
            "XGBoost, prueba final",
            _pct(xgb_final["accuracy"]),
            f"Baseline {_pct(base_final['accuracy'])} · {PRUEBA_FINAL_PARTIDOS} partidos",
            "gold",
        ),
        (
            "Marcador exacto (Poisson)",
            _pct(POISSON_PRUEBA["marcador_exacto"]),
            f"{POISSON_PRUEBA['marcadores_acertados']} de {PRUEBA_FINAL_PARTIDOS} partidos",
            "",
        ),
    ]
)


# ------------------------------------------------------------
# Modelos en uso
# ------------------------------------------------------------

section_title("Modelos que usa la aplicación")

mostrar(
    "<div class='lpf-xg'>"
    "<article class='lpf-xg__card'><span>XGBoost</span>"
    "<strong>Resultado 1X2</strong>"
    "<small>Clasifica el partido en victoria local, empate o victoria "
    "visitante y entrega una probabilidad para cada caso.</small></article>"
    "<article class='lpf-xg__card'><span>Poisson (local y visitante)</span>"
    "<strong>Goles esperados</strong>"
    "<small>Estima los goles de cada equipo y de ahí el marcador más "
    "probable y la lista de marcadores frecuentes.</small></article>"
    "<article class='lpf-xg__card'><span>Características</span>"
    "<strong>Forma e historial</strong>"
    "<small>Últimos 5 partidos, rendimiento histórico, de la temporada y "
    "como local o visitante, y días de descanso.</small></article>"
    "</div>"
)


# ------------------------------------------------------------
# Validación cruzada temporal
# ------------------------------------------------------------

section_title("Validación cruzada temporal", "Notebook 09")

mostrar(
    data_table_html(
        [
            "Modelo", "Accuracy", "± Desv.", "F1 macro",
            "Log loss", f"Folds sobre baseline (de {CV_N_FOLDS})",
        ],
        [
            [
                m["modelo"],
                _pct(m["accuracy"]),
                f"{m['accuracy_sd'] * 100:.1f} pp",
                _num(m["f1_macro"]),
                _num(m["log_loss"]),
                str(m["folds_sobre_baseline"]),
            ]
            for m in CV_TEMPORAL
        ],
        destacar=CV_TEMPORAL.index(mejor_cv),
    )
)

st.caption(
    "Cada fold entrena con los años anteriores y valida con el año siguiente "
    "(2014-2019 → 2020, …, 2014-2024 → 2025). Los partidos de 2026 "
    "(enero a septiembre) quedaron reservados para la prueba final."
)


# ------------------------------------------------------------
# Prueba final
# ------------------------------------------------------------

section_title(
    "Prueba final",
    f"{PRUEBA_FINAL_PARTIDOS} partidos de {PRUEBA_FINAL_PERIODO} · Notebooks 07 y 08",
)

mostrar(
    data_table_html(
        ["Modelo", "Accuracy", "F1 macro", "Log loss"],
        [
            [m["modelo"], _pct(m["accuracy"]), _num(m["f1_macro"]), _num(m["log_loss"])]
            for m in PRUEBA_FINAL
        ],
        destacar=PRUEBA_FINAL.index(xgb_final),
    )
)

mostrar(
    "<div class='lpf-section__hint' style='margin-top:12px'>"
    f"Poisson con características: MAE goles local {POISSON_PRUEBA['mae_local']:.4f} · "
    f"MAE goles visitante {POISSON_PRUEBA['mae_visitante']:.4f}.</div>"
)


# ------------------------------------------------------------
# Figuras
# ------------------------------------------------------------

section_title("Figuras", "Generadas en los notebooks")

pestanas = st.tabs(list(FIGURAS))

for pestana, (nombre, figuras) in zip(pestanas, FIGURAS.items()):
    with pestana:
        disponibles = [(ruta_figura(f), t) for f, t in figuras if ruta_figura(f)]

        if not disponibles:
            empty_state(
                "Sin figuras disponibles",
                "No se encontraron archivos en la carpeta figures/.",
                icono="🖼",
            )
            continue

        columnas = st.columns(min(2, len(disponibles)))

        for i, (ruta, titulo) in enumerate(disponibles):
            with columnas[i % len(columnas)]:
                st.image(str(ruta), caption=titulo, width="stretch")
