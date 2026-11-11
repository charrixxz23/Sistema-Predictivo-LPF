"""Resultados de validación ya obtenidos en los notebooks, listos para mostrar.

Los valores NO se recalculan aquí: están transcritos de las salidas de los
notebooks indicados en cada bloque, y las figuras se leen de /figures.
"""

from datetime import date
from functools import lru_cache
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

FIGURES_DIR = ROOT / "figures"


# Notebook 09: validación cruzada temporal (ventana expansiva, 6 folds:
# entrenamiento 2014-2019 -> validación 2020, ..., 2014-2024 -> 2025).
CV_TEMPORAL = [
    {
        "modelo": "Random Forest",
        "accuracy": 0.4181, "accuracy_sd": 0.0272,
        "f1_macro": 0.4099, "log_loss": 1.0779, "folds_sobre_baseline": 6,
    },
    {
        "modelo": "Regresión Logística",
        "accuracy": 0.4028, "accuracy_sd": 0.0326,
        "f1_macro": 0.3936, "log_loss": 1.0891, "folds_sobre_baseline": 4,
    },
    {
        "modelo": "XGBoost",
        "accuracy": 0.4016, "accuracy_sd": 0.0345,
        "f1_macro": 0.3499, "log_loss": 1.0823, "folds_sobre_baseline": 6,
    },
]

CV_BASELINE_ACCURACY = 0.3812
CV_N_FOLDS = 6


# Notebooks 07 y 08: prueba final (151 partidos reservados, 2026-01-16 a
# 2026-09-14: temporadas "2026" y "2026/2027"; nunca entraron al entrenamiento).
PRUEBA_FINAL = [
    {"modelo": "Baseline (clase más frecuente)", "accuracy": 0.3709,
     "f1_macro": None, "log_loss": None},
    {"modelo": "Regresión Logística", "accuracy": 0.3642,
     "f1_macro": 0.3673, "log_loss": 1.0910},
    {"modelo": "Random Forest", "accuracy": 0.3576,
     "f1_macro": 0.3539, "log_loss": 1.0862},
    {"modelo": "XGBoost", "accuracy": 0.3974,
     "f1_macro": 0.3587, "log_loss": 1.0836},
    {"modelo": "Poisson (resultado derivado)", "accuracy": 0.3709,
     "f1_macro": 0.2232, "log_loss": 1.0928},
]

PRUEBA_FINAL_PARTIDOS = 151

PRUEBA_FINAL_PERIODO = "enero a septiembre de 2026"


# Corte de entrenamiento de los modelos que carga la app.
# Los modelos definitivos (XGBoost y Poisson) se ajustaron con entrenamiento +
# validación (2.075 partidos, hasta el 2025-11-29; notebook 07 celda 81 y
# notebook 08 celda 77). Se comprobó sobre los .joblib: las medianas del
# imputador coinciden con las de entrenamiento+validación y no con las de
# entrenamiento solo ni con las de entrenamiento+validación+prueba, y el
# escalador de Poisson vio 2.075 muestras.
FECHA_CORTE_RESPALDO = date(2025, 11, 29)

VALIDACION_CSV = ROOT / "data" / "processed" / "lpf_validacion.csv"


@lru_cache(maxsize=1)
def fecha_corte_entrenamiento():
    """Última fecha de partido vista en el ajuste definitivo de los modelos.

    Se lee del último partido del conjunto de validación (que se unió al de
    entrenamiento); si el archivo no está disponible, se usa el valor
    documentado arriba.
    """

    try:
        fechas = pd.read_csv(
            VALIDACION_CSV,
            encoding="utf-8-sig",
            usecols=["fecha_partido"],
            parse_dates=["fecha_partido"],
        )["fecha_partido"]

        return fechas.max().date()
    except (OSError, ValueError, KeyError):
        return FECHA_CORTE_RESPALDO

# Notebook 08: Poisson con características, prueba final.
POISSON_PRUEBA = {
    "mae_local": 0.9557,
    "mae_visitante": 0.8187,
    "marcador_exacto": 0.1656,
    "marcadores_acertados": 25,
}


# Figuras agrupadas por pestaña: (archivo, título)
FIGURAS = {
    "Validación temporal": [
        ("cv_temporal_accuracy.png", "Accuracy por fold temporal"),
        ("cv_temporal_f1_macro.png", "F1 macro por fold temporal"),
    ],
    "XGBoost": [
        ("xgboost_prueba_final.png", "Prueba final"),
        ("xgboost_importancia_caracteristicas.png", "Importancia de características"),
        ("xgb_f1_train_vs_val_compromiso.png", "F1 entrenamiento vs validación"),
    ],
    "Poisson": [
        ("poisson_prueba_final.png", "Prueba final"),
        ("poisson_goles_local.png", "Goles del local"),
        ("poisson_goles_visitante.png", "Goles del visitante"),
    ],
    "Otros modelos": [
        ("random_forest_prueba_final.png", "Random Forest, prueba final"),
        ("regresion_logistica_prueba_final.png", "Regresión Logística, prueba final"),
    ],
}


def ruta_figura(nombre):
    ruta = FIGURES_DIR / nombre

    return ruta if ruta.exists() else None
