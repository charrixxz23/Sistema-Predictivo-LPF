"""Cargadores con caché compartidos por todas las páginas.

Envuelven las funciones existentes de services/ sin modificarlas.
"""

import streamlit as st

from services.database_service import (
    inicializar_base_datos,
    obtener_ultimas_predicciones,
)
from services.feature_service import (
    cargar_historico,
    obtener_temporadas_disponibles,
)
from services.liga_service import (
    acumula_apertura_clausura,
    cargar_calendario,
    construir_clasificacion,
    construir_clasificacion_oficial,
    cruces_si_terminara_hoy,
)
from services.model_service import cargar_modelos
from services.prediction_service import analizar_partido


def preparar_base_datos():
    """True si la base SQLite local está disponible."""

    try:
        inicializar_base_datos()
        return True
    except Exception:
        return False


@st.cache_data(show_spinner=False)
def obtener_historico():
    return cargar_historico()


@st.cache_resource(show_spinner=False)
def obtener_modelos():
    return cargar_modelos()


def obtener_temporadas():
    return obtener_temporadas_disponibles(obtener_historico())


@st.cache_data(show_spinner=False)
def obtener_calendario():
    return cargar_calendario()


@st.cache_data(show_spinner=False)
def obtener_clasificacion(temporada):
    return construir_clasificacion(obtener_historico(), temporada)


@st.cache_data(show_spinner=False)
def obtener_clasificacion_oficial(temporada):
    """Tablas Este / Oeste / General (o None si la temporada no tiene conferencias)."""

    return construir_clasificacion_oficial(obtener_historico(), temporada)


@st.cache_data(show_spinner=False)
def obtener_cruces_si_terminara_hoy(temporada):
    tablas = construir_clasificacion_oficial(obtener_historico(), temporada)

    return None if tablas is None else cruces_si_terminara_hoy(tablas)


@st.cache_data(show_spinner=False)
def temporada_acumula_torneos(temporada):
    return acumula_apertura_clausura(obtener_historico(), temporada)


@st.cache_data(show_spinner=False)
def predecir_partido_calendario(local, visitante, fecha_iso, temporada):
    """Predicción de un partido del calendario (misma lógica que la página
    Predicciones). No escribe en el historial."""

    resultado = analizar_partido(
        historico=obtener_historico(),
        modelos=obtener_modelos(),
        equipo_local=local,
        equipo_visitante=visitante,
        fecha=fecha_iso,
        temporada=temporada,
    )

    return {
        "probabilidades": resultado["xgboost"]["probabilidades"],
        "resultado": resultado["xgboost"]["resultado"],
        "marcador": resultado["marcador_probable"],
        "prob_marcador": resultado["marcador_probable"]["probabilidad"],
    }


def leer_historial(limite):
    """Devuelve (registros, error). error es None si la lectura funcionó."""

    try:
        return obtener_ultimas_predicciones(limite=limite), None
    except Exception as exc:
        return [], exc
