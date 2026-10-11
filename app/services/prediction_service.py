from services.feature_service import (
    construir_features_partido
)

from services.model_service import (
    predecir_resultado,
    predecir_goles
)

from services.poisson_service import (
    calcular_matriz_marcadores,
    resultado_poisson,
    marcador_mas_probable,
    top_marcadores
)


def analizar_partido(
    historico,
    modelos,
    equipo_local,
    equipo_visitante,
    fecha,
    temporada
):

    if equipo_local == equipo_visitante:
        raise ValueError(
            "El equipo local y visitante "
            "deben ser diferentes."
        )

    X = construir_features_partido(
        historico=historico,
        equipo_local=equipo_local,
        equipo_visitante=equipo_visitante,
        fecha=fecha,
        temporada=temporada
    )

    resultado_xgb = predecir_resultado(
        modelos["xgboost"],
        modelos["label_encoder"],
        X
    )

    goles = predecir_goles(
        modelos["poisson_local"],
        modelos["poisson_visitante"],
        X
    )

    matriz = calcular_matriz_marcadores(
        goles["lambda_local"],
        goles["lambda_visitante"]
    )

    probabilidades_poisson = resultado_poisson(
        matriz
    )

    marcador = marcador_mas_probable(
        matriz
    )

    mejores_marcadores = top_marcadores(
        matriz,
        cantidad=5
    )

    return {
        "features": X,
        "xgboost": resultado_xgb,
        "goles": goles,
        "poisson_resultado": probabilidades_poisson,
        "marcador_probable": marcador,
        "top_marcadores": mejores_marcadores
    }