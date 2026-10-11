from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

MODELS_DIR = ROOT / "models"


XGB_PATH = (
    MODELS_DIR
    / "xgboost_lpf.joblib"
)

XGB_ENCODER_PATH = (
    MODELS_DIR
    / "xgboost_label_encoder.joblib"
)

POISSON_LOCAL_PATH = (
    MODELS_DIR
    / "poisson_local_lpf.joblib"
)

POISSON_VISITANTE_PATH = (
    MODELS_DIR
    / "poisson_visitante_lpf.joblib"
)


def cargar_modelos():

    modelo_xgb = joblib.load(
        XGB_PATH
    )

    label_encoder = joblib.load(
        XGB_ENCODER_PATH
    )

    modelo_poisson_local = joblib.load(
        POISSON_LOCAL_PATH
    )

    modelo_poisson_visitante = joblib.load(
        POISSON_VISITANTE_PATH
    )

    return {
        "xgboost":
            modelo_xgb,

        "label_encoder":
            label_encoder,

        "poisson_local":
            modelo_poisson_local,

        "poisson_visitante":
            modelo_poisson_visitante
    }


def alinear_features(
    modelo,
    X
):

    if hasattr(
        modelo,
        "feature_names_in_"
    ):

        columnas = list(
            modelo.feature_names_in_
        )

        faltantes = [
            c
            for c in columnas
            if c not in X.columns
        ]

        if faltantes:

            raise ValueError(
                "Faltan características "
                f"requeridas: {faltantes}"
            )

        return X[columnas].copy()

    return X.copy()


def predecir_resultado(
    modelo_xgb,
    label_encoder,
    X
):

    X = alinear_features(
        modelo_xgb,
        X
    )

    probabilidades = (
        modelo_xgb
        .predict_proba(X)[0]
    )

    clases_codificadas = (
        modelo_xgb.classes_
    )

    clases = (
        label_encoder
        .inverse_transform(
            clases_codificadas
        )
    )

    probabilidades_dict = {
        str(clase): float(prob)
        for clase, prob
        in zip(
            clases,
            probabilidades
        )
    }

    resultado = max(
        probabilidades_dict,
        key=probabilidades_dict.get
    )

    return {
        "resultado":
            resultado,

        "probabilidades":
            probabilidades_dict
    }


def predecir_goles(
    modelo_local,
    modelo_visitante,
    X
):

    X_local = alinear_features(
        modelo_local,
        X
    )

    X_visitante = alinear_features(
        modelo_visitante,
        X
    )

    lambda_local = float(
        modelo_local
        .predict(X_local)[0]
    )

    lambda_visitante = float(
        modelo_visitante
        .predict(X_visitante)[0]
    )

    return {
        "lambda_local":
            lambda_local,

        "lambda_visitante":
            lambda_visitante
    }