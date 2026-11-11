"""Modelos y validación: métricas exportadas por los cuadernos 05 a 09."""

from datetime import date

import streamlit as st

from services.reporte_service import (
    FIGURAS,
    cv_temporal,
    metadatos,
    poisson_prueba,
    prueba_final,
    ruta_figura,
)
from ui.components import (
    ANIO_TRABAJO,
    AUTOR,
    UNIVERSIDAD,
    data_line,
    data_table_html,
    empty_state,
    fold_chart_html,
    foot_note,
    indicator_grid_html,
    mostrar,
    page_header,
    porcentaje,
    section_title,
    spec_sheet_html,
)
from ui.loaders import (
    obtener_calendario,
    obtener_historico,
    obtener_modelos,
    obtener_temporadas,
)


MODELO_APP = "XGBoost"

FUENTE_METRICAS = "data/processed/metricas_validacion.json"

# Texto de la elección del modelo (redactado por la autora del trabajo).
TEXTO_ELECCION = (
    "En la validación cruzada (2020–2025), Random Forest obtuvo el mejor "
    "promedio, aunque las diferencias entre los tres modelos (40.2 % a 41.8 %) "
    "son menores que su variación entre pliegues (± 2.7 a ± 3.4 pp). En la "
    "prueba final con los 151 partidos de 2026, Random Forest quedó por debajo "
    "de la línea base (35.8 % frente a 37.1 %) y XGBoost la superó (39.7 %); "
    "por ello la aplicación utiliza XGBoost. Dado que la prueba final también "
    "influyó en esta elección, el 39.7 % debe interpretarse como una "
    "estimación optimista."
)

NOTAS_CV = {
    "Random Forest": "Mejor promedio en validación",
    MODELO_APP: "Modelo utilizado por la aplicación",
}


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
meta = metadatos()

prueba = (final or {}).get("prueba", {})
n_prueba = prueba.get("n_partidos")

page_header(
    "Modelos y validación",
    "Métricas obtenidas en la fase experimental del trabajo de graduación. Se "
    "presentan tal como se registraron en los cuadernos de análisis, sin "
    "recálculos.",
)

if cv is None and final is None:
    empty_state(
        "Métricas no disponibles",
        "No se encontró el archivo de métricas exportado por los cuadernos de "
        "análisis. Para generarlo, ejecutar los cuadernos 05 a 09 hasta su "
        "última celda («Exportación de métricas»).",
        icono="📊",
    )
    foot_note(f"Fuente esperada: {FUENTE_METRICAS}")

# ------------------------------------------------------------
# Indicadores principales (cuadrícula de 2 × 2)
# ------------------------------------------------------------

indicadores = []

if cv:
    mejor_cv = max(cv["modelos"], key=lambda m: m["accuracy"])
    indicadores += [
        (
            _pct(cv["baseline_accuracy"]),
            "Línea base (baseline) temporal: clase más frecuente",
        ),
        (
            _pct(mejor_cv["accuracy"]),
            f"{mejor_cv['modelo']}: mejor exactitud (accuracy) promedio en la "
            f"validación cruzada (± {mejor_cv['accuracy_sd'] * 100:.1f} pp)",
        ),
    ]

if final:
    xgb_final = next((m for m in final["modelos"] if m["modelo"] == MODELO_APP), None)
    base_final = final.get("baseline")

    if xgb_final and base_final:
        indicadores.append(
            (
                _pct(xgb_final["accuracy"]),
                f"{MODELO_APP} en la prueba final (línea base: "
                f"{_pct(base_final['accuracy'])}; {n_prueba} partidos)",
            )
        )

if poisson:
    indicadores.append(
        (
            _pct(poisson["marcador_exacto"]),
            "Marcador exacto con regresión de Poisson "
            f"({poisson['marcadores_acertados']} de {poisson['n_partidos']} partidos)",
        )
    )

if indicadores:
    mostrar(indicator_grid_html(indicadores))

# ------------------------------------------------------------
# Ficha técnica (leída de los modelos que usa la app y del JSON)
# ------------------------------------------------------------

section_title("Ficha técnica", "Modelos utilizados por la aplicación")

ficha = []

try:
    modelos = obtener_modelos()
    xgb = modelos["xgboost"]
    params_xgb = xgb.named_steps["modelo"].get_params()
    alpha = modelos["poisson_local"].named_steps["modelo"].alpha
    n_variables = len(xgb.feature_names_in_)

    ficha += [
        (
            "Resultado 1X2",
            f"{MODELO_APP}: {params_xgb['n_estimators']} árboles, profundidad "
            f"máxima {params_xgb['max_depth']} y tasa de aprendizaje "
            f"{params_xgb['learning_rate']}.",
        ),
        (
            "Goles",
            "Regresión de Poisson, con un modelo para los goles del local y "
            f"otro para los del visitante (regularización α = {alpha}).",
        ),
        (
            "Características",
            f"{n_variables} variables calculadas antes del partido: forma "
            "reciente (últimos 5 partidos), rendimiento histórico y de la "
            "temporada, rendimiento como local o visitante y días de descanso.",
        ),
    ]
except Exception:
    pass

if meta.get("fecha_corte_entrenamiento"):
    n_entrenamiento = meta.get("n_partidos_entrenamiento_final")
    ficha.append(
        (
            "Entrenamiento",
            f"{n_entrenamiento:,} partidos hasta el "
            f"{_fecha(meta['fecha_corte_entrenamiento'])}."
            if isinstance(n_entrenamiento, int)
            else f"Hasta el {_fecha(meta['fecha_corte_entrenamiento'])}.",
        )
    )

if prueba:
    ficha.append(
        (
            "Prueba final",
            f"{prueba.get('n_partidos', '-')} partidos, del "
            f"{_fecha(prueba.get('fecha_inicio'))} al "
            f"{_fecha(prueba.get('fecha_fin'))}.",
        )
    )

if cv:
    anios = cv.get("anios_validacion") or []
    rango = f"; {anios[0]}–{anios[-1]}" if anios else ""
    ficha.append(
        (
            "Validación",
            "Validación cruzada temporal con ventana expansiva, "
            f"{cv['n_folds']} pliegues (folds{rango}).",
        )
    )

if ficha:
    mostrar(spec_sheet_html(ficha))

# ------------------------------------------------------------
# Datos (antes «Resumen de la base»)
# ------------------------------------------------------------

section_title("Datos", "Datos utilizados por la aplicación")

try:
    historico = obtener_historico()
    temporadas = obtener_temporadas()
    calendario, temporada_cal = obtener_calendario()

    anios_datos = historico["fecha_partido"].dt.year

    data_line(
        [
            (
                f"{len(historico):,}",
                f"partidos registrados ({int(anios_datos.min())}–{int(anios_datos.max())})",
            ),
            (str(len(temporadas)), "temporadas con datos para el modelado"),
            (
                str(int(calendario["jornada"].max())),
                f"jornadas en el calendario de la temporada {temporada_cal}",
            ),
        ]
    )
except Exception:
    empty_state(
        "Datos no disponibles",
        "No fue posible leer los datos utilizados por la aplicación.",
        icono="📊",
    )

# ------------------------------------------------------------
# Validación cruzada temporal: tabla, texto y gráfico por pliegue
# ------------------------------------------------------------

if cv:
    section_title("Validación cruzada temporal", "Cuaderno 09")

    nombres_cv = [m["modelo"] for m in cv["modelos"]]

    mostrar(
        data_table_html(
            [
                "Modelo", "Exactitud", "Desv. estándar", "F1 macro",
                "Pérdida logarítmica (log loss)",
                f"Pliegues sobre la línea base (de {cv['n_folds']})", "Nota",
            ],
            [
                [
                    m["modelo"],
                    _pct(m["accuracy"]),
                    f"{m['accuracy_sd'] * 100:.1f} pp",
                    _num(m["f1_macro"]),
                    _num(m["log_loss"]),
                    str(m["folds_sobre_baseline"]),
                    NOTAS_CV.get(m["modelo"], ""),
                ]
                for m in cv["modelos"]
            ],
            destacar=nombres_cv.index(MODELO_APP) if MODELO_APP in nombres_cv else None,
        )
    )

    foot_note(f"Fuente: {FUENTE_METRICAS} (cuaderno 09).")

    texto_col, grafico_col = st.columns([1, 1], gap="large")

    with texto_col:
        st.markdown(
            f"<p class='lpf-explica'>{TEXTO_ELECCION}</p>",
            unsafe_allow_html=True,
        )
        foot_note(
            "Cada pliegue se entrena con los años anteriores y se valida con "
            "el año siguiente. Los partidos de 2026 (enero a septiembre) se "
            "reservaron para la prueba final."
        )

    with grafico_col:
        if cv.get("folds"):
            mostrar(fold_chart_html(cv["folds"], MODELO_APP))
            foot_note(
                "Exactitud por pliegue de validación frente a la línea base "
                "(línea discontinua)."
            )

# ------------------------------------------------------------
# Prueba final
# ------------------------------------------------------------

if final:
    section_title(
        "Prueba final",
        f"{n_prueba} partidos ({_fecha(prueba.get('fecha_inicio'))} a "
        f"{_fecha(prueba.get('fecha_fin'))}) · Cuadernos 05 a 08",
    )

    filas = []

    if final.get("baseline"):
        filas.append(
            ["Línea base (clase más frecuente)", _pct(final["baseline"]["accuracy"]), "-", "-"]
        )

    filas += [
        [m["modelo"], _pct(m["accuracy"]), _num(m["f1_macro"]), _num(m["log_loss"])]
        for m in final["modelos"]
    ]

    nombres = [f[0] for f in filas]

    mostrar(
        data_table_html(
            ["Modelo", "Exactitud", "F1 macro", "Pérdida logarítmica"],
            filas,
            destacar=nombres.index(MODELO_APP) if MODELO_APP in nombres else None,
        )
    )

    foot_note(f"Fuente: {FUENTE_METRICAS} (cuadernos 05 a 08).")

    if poisson:
        foot_note(
            "Regresión de Poisson con características: error absoluto medio "
            f"(MAE) de {poisson['mae_local']:.4f} goles para el local y "
            f"{poisson['mae_visitante']:.4f} para el visitante. El conjunto de "
            "prueba no se utilizó en el entrenamiento ni en la selección de "
            "hiperparámetros."
        )

# ------------------------------------------------------------
# Figuras
# ------------------------------------------------------------

section_title("Figuras", "Generadas en los cuadernos de análisis")

pestanas = st.tabs(list(FIGURAS))

for pestana, (nombre, figuras) in zip(pestanas, FIGURAS.items()):
    with pestana:
        disponibles = [(ruta_figura(f), t) for f, t in figuras if ruta_figura(f)]

        if not disponibles:
            empty_state(
                "Sin figuras disponibles",
                "No se encontraron las figuras generadas por los cuadernos de análisis.",
                icono="🖼",
            )
            continue

        columnas = st.columns(min(2, len(disponibles)))

        for i, (ruta, titulo) in enumerate(disponibles):
            with columnas[i % len(columnas)]:
                st.image(str(ruta), caption=titulo, width="stretch")

# ------------------------------------------------------------
# Ficha del trabajo
# ------------------------------------------------------------

section_title("Ficha del trabajo", "Autoría")

mostrar(
    spec_sheet_html(
        [
            (
                "Trabajo",
                "Pronóstico LPF: sistema predictivo de partidos de la Liga "
                "Panameña de Fútbol",
            ),
            ("Autor", AUTOR),
            ("Universidad", UNIVERSIDAD),
            ("Año", ANIO_TRABAJO),
            (
                "Naturaleza",
                "Proyecto académico; no está afiliado a la Liga Panameña de Fútbol",
            ),
        ]
    )
)
