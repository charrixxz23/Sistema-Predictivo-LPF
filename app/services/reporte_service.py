"""Resultados de validación exportados por los notebooks, listos para mostrar.

La aplicación NO calcula ni transcribe métricas: lee
``data/processed/metricas_validacion.json``, que escriben los notebooks 05 a 09
(celda final de cada uno). Si el archivo no existe, las funciones devuelven
``None`` y la interfaz muestra un estado vacío.

Las figuras se leen de /figures.
"""

from datetime import date
from functools import lru_cache
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

FIGURES_DIR = ROOT / "figures"

METRICAS_JSON = ROOT / "data" / "processed" / "metricas_validacion.json"

VALIDACION_CSV = ROOT / "data" / "processed" / "lpf_validacion.csv"

# Orden de las filas en la tabla de prueba final.
ORDEN_PRUEBA = [
    "Regresión Logística",
    "Random Forest",
    "XGBoost",
    "Poisson (resultado derivado)",
]


@lru_cache(maxsize=4)
def _leer_json(ruta, mtime_ns):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


def cargar_metricas():
    """Contenido del JSON de métricas, o None si falta o no se puede leer."""

    try:
        return _leer_json(str(METRICAS_JSON), METRICAS_JSON.stat().st_mtime_ns)
    except (OSError, ValueError):
        return None


def _seccion(*ruta):
    nodo = cargar_metricas()

    for clave in ruta:
        if not isinstance(nodo, dict) or clave not in nodo:
            return None

        nodo = nodo[clave]

    return nodo


def metadatos():
    return _seccion("metadatos") or {}


def cv_temporal():
    """dict con n_folds, baseline_accuracy(_sd) y modelos, o None."""

    datos = _seccion("cv_temporal")

    return datos if datos and datos.get("modelos") else None


def prueba_final():
    """dict con baseline, modelos (en orden de presentación) y el conjunto de
    prueba (n_partidos, fecha_inicio, fecha_fin), o None."""

    datos = _seccion("prueba_final")

    if not datos or not datos.get("modelos"):
        return None

    modelos = datos["modelos"]

    ordenados = [
        {"modelo": nombre, **modelos[nombre]}
        for nombre in ORDEN_PRUEBA
        if nombre in modelos
    ]

    return {
        "baseline": datos.get("baseline"),
        "modelos": ordenados,
        "prueba": metadatos().get("prueba", {}),
    }


def poisson_prueba():
    return _seccion("poisson_prueba")


def fecha_corte_entrenamiento():
    """Última fecha de partido vista en el ajuste definitivo de los modelos.

    Se lee de los metadatos del JSON de métricas. Solo si el JSON no existe
    (o no trae la fecha) se usa el último partido de lpf_validacion.csv, que
    es el conjunto que se unió al de entrenamiento. Si tampoco está, devuelve
    None y la interfaz no muestra indicadores de acierto.
    """

    texto = metadatos().get("fecha_corte_entrenamiento")

    if texto:
        try:
            return date.fromisoformat(texto)
        except ValueError:
            pass

    try:
        fechas = pd.read_csv(
            VALIDACION_CSV,
            encoding="utf-8-sig",
            usecols=["fecha_partido"],
            parse_dates=["fecha_partido"],
        )["fecha_partido"]

        return fechas.max().date()
    except (OSError, ValueError, KeyError):
        return None


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
