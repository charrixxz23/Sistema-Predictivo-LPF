"""Modelos y validación: métricas exportadas por los notebooks 05 a 09."""

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
    mostrar,
    page_header,
    porcentaje,
    section_title,
    spec_sheet_html,
)
from ui.loaders import (
    leer_historial,
    obtener_calendario,
    obtener_historico,
    obtener_modelos,
    obtener_temporadas,
)


MODELO_APP = "XGBoost"

# Texto de la elección del modelo (redactado por la autora de la tesis).
TEXTO_ELECCION = (
    "En la validación cruzada (2020–2025), Random Forest obtuvo el mejor "
    "promedio, aunque las diferencias entre los tres modelos (40.2 % a 41.8 %) "
    "son menores que su variación entre folds (±2.7 a ±3.4 pp). En la prueba "
    "final con los 151 partidos de 2026, Random Forest quedó por debajo del "
    "baseline (35.8 % frente a 37.1 %) y XGBoost lo superó (39.7 %); por eso la "
    "aplicación usa XGBoost. Como la prueba final también influyó en esta "
    "elección, su 39.7 % debe leerse como una estimación optimista."
)

NOTAS_CV = {
    "Random Forest": "Mejor promedio en validación",
    MODELO_APP: "Modelo que usa la app",
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
    "Resultados obtenidos en los notebooks de la tesis y exportados a "
    "data/processed/metricas_validacion.json. La aplicación los muestra tal "
    "como se registraron; no recalcula nada.",
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
# Resumen en una línea de datos
# ------------------------------------------------------------

resumen = []

if cv:
    mejor_cv = max(cv["modelos"], key=lambda m: m["accuracy"])
    resumen += [
        (_pct(cv["baseline_accuracy"]), "baseline temporal (clase más frecuente)"),
        (
            _pct(mejor_cv["accuracy"]),
            f"{mejor_cv['modelo']}, mejor promedio en validación "
            f"(± {mejor_cv['accuracy_sd'] * 100:.1f} pp)",
        ),
    ]

if final:
    xgb_final = next((m for m in final["modelos"] if m["modelo"] == MODELO_APP), None)
    base_final = final.get("baseline")

    if xgb_final and base_final:
        resumen.append(
            (
                _pct(xgb_final["accuracy"]),
                f"{MODELO_APP} en la prueba final (baseline "
                f"{_pct(base_final['accuracy'])}, {n_prueba} partidos)",
            )
        )

if poisson:
    resumen.append(
        (
            _pct(poisson["marcador_exacto"]),
            f"marcador exacto con Poisson ({poisson['marcadores_acertados']} "
            f"de {poisson['n_partidos']})",
        )
    )

if resumen:
    data_line(resumen)

# ------------------------------------------------------------
# Ficha técnica (leída de los modelos que usa la app y del JSON)
# ------------------------------------------------------------

section_title("Ficha técnica", "Modelos que usa la aplicación")

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
            f"máxima {params_xgb['max_depth']}, tasa de aprendizaje "
            f"{params_xgb['learning_rate']}",
        ),
        (
            "Goles",
            "Poisson, un modelo para el local y otro para el visitante; "
            f"regularización alpha {alpha}",
        ),
        (
            "Características",
            f"{n_variables} variables: forma de los últimos 5 partidos, "
            "rendimiento histórico, de la temporada y como local o visitante, "
            "y días de descanso",
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
            f"{_fecha(meta['fecha_corte_entrenamiento'])}"
            if isinstance(n_entrenamiento, int)
            else f"hasta el {_fecha(meta['fecha_corte_entrenamiento'])}",
        )
    )

if prueba:
    ficha.append(
        (
            "Prueba final",
            f"{prueba.get('n_partidos', '-')} partidos "
            f"({_fecha(prueba.get('fecha_inicio'))} a {_fecha(prueba.get('fecha_fin'))})",
        )
    )

if cv:
    anios = cv.get("anios_validacion") or []
    rango = f", {anios[0]}-{anios[-1]}" if anios else ""
    ficha.append(
        ("Validación", f"ventana expansiva, {cv['n_folds']} folds temporales{rango}")
    )

if ficha:
    mostrar(spec_sheet_html(ficha))

# ------------------------------------------------------------
# Resumen de la base (antes en Inicio)
# ------------------------------------------------------------

section_title("Resumen de la base", "Datos con que trabaja la aplicación")

try:
    historico = obtener_historico()
    temporadas = obtener_temporadas()
    calendario, temporada_cal = obtener_calendario()
    registros, _ = leer_historial(100000)

    anios = historico["fecha_partido"].dt.year

    data_line(
        [
            (
                f"{len(historico):,}",
                f"partidos en la base ({int(anios.min())}-{int(anios.max())})",
            ),
            (str(len(temporadas)), "temporadas con datos para modelado"),
            (
                str(int(calendario["jornada"].max())),
                f"jornadas en el calendario {temporada_cal}",
            ),
            (str(len(registros)), "análisis guardados"),
        ]
    )
except Exception:
    empty_state(
        "Resumen no disponible",
        "No se pudieron leer los datos de la base.",
        icono="📊",
    )

# ------------------------------------------------------------
# Validación cruzada temporal: tabla, texto y gráfico por fold
# ------------------------------------------------------------

if cv:
    section_title("Validación cruzada temporal", "Notebook 09")

    nombres_cv = [m["modelo"] for m in cv["modelos"]]

    mostrar(
        data_table_html(
            [
                "Modelo", "Accuracy", "± Desv.", "F1 macro", "Log loss",
                f"Folds sobre baseline (de {cv['n_folds']})", "Nota",
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

    texto_col, grafico_col = st.columns([1, 1], gap="large")

    with texto_col:
        st.markdown(
            f"<p class='lpf-explica'>{TEXTO_ELECCION}</p>",
            unsafe_allow_html=True,
        )
        foot_note(
            "Cada fold entrena con los años anteriores y valida con el año "
            "siguiente. Los partidos de 2026 (enero a septiembre) quedaron "
            "reservados para la prueba final."
        )

    with grafico_col:
        if cv.get("folds"):
            mostrar(fold_chart_html(cv["folds"], MODELO_APP))
            foot_note(
                "Accuracy por fold de validación frente al baseline (línea "
                "discontinua)."
            )

# ------------------------------------------------------------
# Prueba final
# ------------------------------------------------------------

if final:
    section_title(
        "Prueba final",
        f"{n_prueba} partidos ({_fecha(prueba.get('fecha_inicio'))} a "
        f"{_fecha(prueba.get('fecha_fin'))}) · Notebooks 05 a 08",
    )

    filas = []

    if final.get("baseline"):
        filas.append(
            ["Baseline (clase más frecuente)", _pct(final["baseline"]["accuracy"]), "-", "-"]
        )

    filas += [
        [m["modelo"], _pct(m["accuracy"]), _num(m["f1_macro"]), _num(m["log_loss"])]
        for m in final["modelos"]
    ]

    nombres = [f[0] for f in filas]

    mostrar(
        data_table_html(
            ["Modelo", "Accuracy", "F1 macro", "Log loss"],
            filas,
            destacar=nombres.index(MODELO_APP) if MODELO_APP in nombres else None,
        )
    )

    if poisson:
        foot_note(
            f"Poisson con características: MAE goles local {poisson['mae_local']:.4f} · "
            f"MAE goles visitante {poisson['mae_visitante']:.4f}. El conjunto de "
            "prueba nunca entró al entrenamiento ni a la selección de hiperparámetros."
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

# ------------------------------------------------------------
# Ficha del trabajo
# ------------------------------------------------------------

section_title("Ficha del trabajo", "Autoría")

mostrar(
    spec_sheet_html(
        [
            ("Trabajo", "Pronóstico LPF: sistema predictivo de partidos de la Liga Panameña de Fútbol"),
            ("Autor", AUTOR),
            ("Universidad", UNIVERSIDAD),
            ("Año", ANIO_TRABAJO),
            ("Naturaleza", "Proyecto académico; no está afiliado a la Liga Panameña de Fútbol"),
        ]
    )
)
