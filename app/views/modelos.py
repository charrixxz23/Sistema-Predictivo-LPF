"""Modelos y validación: métricas exportadas por los notebooks 05 a 09."""

from datetime import date

import streamlit as st

from services.reporte_service import (
    FIGURAS,
    cv_temporal,
    poisson_prueba,
    prueba_final,
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


def _fecha(texto):
    try:
        return date.fromisoformat(texto).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return "-"


cv = cv_temporal()
final = prueba_final()
poisson = poisson_prueba()

prueba = (final or {}).get("prueba", {})
n_prueba = prueba.get("n_partidos")
periodo_prueba = (
    f"{_fecha(prueba.get('fecha_inicio'))} a {_fecha(prueba.get('fecha_fin'))}"
    if prueba
    else ""
)

chips = []

if cv:
    chips = [(f"{cv['n_folds']} folds temporales", ""), ("Ventana expansiva", "")]

page_header(
    "Modelos y validación",
    "Resultados obtenidos en los notebooks de la tesis y exportados a "
    "data/processed/metricas_validacion.json. La aplicación los muestra tal "
    "como se registraron; no recalcula nada.",
    chips=chips,
)

if cv is None and final is None:
    empty_state(
        "Métricas no disponibles",
        "No se encontró data/processed/metricas_validacion.json. Ejecuta los "
        "notebooks 05 a 09 hasta su última celda («Exportación de métricas») "
        "para generarlo.",
        icono="📊",
    )

# ------------------------------------------------------------
# Tarjetas resumen
# ------------------------------------------------------------

tarjetas = []

if cv:
    mejor_cv = max(cv["modelos"], key=lambda m: m["accuracy"])

    tarjetas += [
        (
            "Baseline temporal",
            _pct(cv["baseline_accuracy"]),
            "Accuracy promedio de la clase más frecuente",
            "",
        ),
        (
            "Mejor en validación",
            _pct(mejor_cv["accuracy"]),
            f"{mejor_cv['modelo']} · ± {mejor_cv['accuracy_sd'] * 100:.1f} pp",
            "brand",
        ),
    ]

if final:
    xgb_final = next(
        (m for m in final["modelos"] if m["modelo"] == "XGBoost"), None
    )
    base_final = final.get("baseline")

    if xgb_final and base_final:
        tarjetas.append(
            (
                "XGBoost, prueba final",
                _pct(xgb_final["accuracy"]),
                f"Baseline {_pct(base_final['accuracy'])} · {n_prueba} partidos",
                "",
            )
        )

if poisson:
    tarjetas.append(
        (
            "Marcador exacto (Poisson)",
            _pct(poisson["marcador_exacto"]),
            f"{poisson['marcadores_acertados']} de {poisson['n_partidos']} partidos",
            "",
        )
    )

if tarjetas:
    metric_row(tarjetas)

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

if cv:
    section_title("Validación cruzada temporal", "Notebook 09")

    mostrar(
        data_table_html(
            [
                "Modelo", "Accuracy", "± Desv.", "F1 macro",
                "Log loss", f"Folds sobre baseline (de {cv['n_folds']})",
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
                for m in cv["modelos"]
            ],
            destacar=cv["modelos"].index(mejor_cv),
        )
    )

    anios = cv.get("anios_validacion") or []
    rango = f"{anios[0]}-{anios[-1]}" if anios else ""

    st.caption(
        "Cada fold entrena con los años anteriores y valida con el año "
        f"siguiente (validación {rango}). Los partidos de 2026 quedaron "
        "reservados para la prueba final."
    )

# ------------------------------------------------------------
# Prueba final
# ------------------------------------------------------------

if final:
    section_title(
        "Prueba final",
        f"{n_prueba} partidos ({periodo_prueba}) · Notebooks 05 a 08",
    )

    filas = []

    if final.get("baseline"):
        filas.append(
            [
                "Baseline (clase más frecuente)",
                _pct(final["baseline"]["accuracy"]),
                "-",
                "-",
            ]
        )

    filas += [
        [
            m["modelo"],
            _pct(m["accuracy"]),
            _num(m["f1_macro"]),
            _num(m["log_loss"]),
        ]
        for m in final["modelos"]
    ]

    nombres = [f[0] for f in filas]

    mostrar(
        data_table_html(
            ["Modelo", "Accuracy", "F1 macro", "Log loss"],
            filas,
            destacar=nombres.index("XGBoost") if "XGBoost" in nombres else None,
        )
    )

    if poisson:
        mostrar(
            "<div class='lpf-section__hint' style='margin-top:12px'>"
            f"Poisson con características: MAE goles local {poisson['mae_local']:.4f} · "
            f"MAE goles visitante {poisson['mae_visitante']:.4f}.</div>"
        )

    st.caption(
        "El conjunto de prueba nunca entró al entrenamiento ni a la selección "
        "de hiperparámetros."
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
