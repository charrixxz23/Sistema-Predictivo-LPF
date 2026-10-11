import numpy as np

from scipy.stats import poisson


MAX_GOLES = 10


def calcular_matriz_marcadores(
    lambda_local,
    lambda_visitante,
    max_goles=MAX_GOLES
):

    goles = np.arange(
        max_goles + 1
    )

    p_local = poisson.pmf(
        goles,
        lambda_local
    )

    p_visitante = poisson.pmf(
        goles,
        lambda_visitante
    )

    matriz = np.outer(
        p_local,
        p_visitante
    )

    matriz = (
        matriz
        / matriz.sum()
    )

    return matriz


def resultado_poisson(matriz):

    p_local = np.tril(
        matriz,
        k=-1
    ).sum()

    p_empate = np.trace(
        matriz
    )

    p_visitante = np.triu(
        matriz,
        k=1
    ).sum()

    return {
        "L": float(p_local),
        "E": float(p_empate),
        "V": float(p_visitante)
    }


def marcador_mas_probable(matriz):

    indice = np.unravel_index(
        np.argmax(matriz),
        matriz.shape
    )

    return {
        "local": int(indice[0]),
        "visitante": int(indice[1]),
        "probabilidad":
            float(matriz[indice])
    }


def top_marcadores(
    matriz,
    cantidad=5
):

    marcadores = []

    for goles_local in range(
        matriz.shape[0]
    ):

        for goles_visitante in range(
            matriz.shape[1]
        ):

            marcadores.append({
                "local":
                    goles_local,

                "visitante":
                    goles_visitante,

                "probabilidad":
                    float(
                        matriz[
                            goles_local,
                            goles_visitante
                        ]
                    )
            })

    marcadores = sorted(
        marcadores,
        key=lambda x:
            x["probabilidad"],
        reverse=True
    )

    return marcadores[
        :cantidad
    ]