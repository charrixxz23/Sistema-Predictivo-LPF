from pathlib import Path

import numpy as np
import pandas as pd

from services.feature_service import (
    cargar_historico,
    construir_features_partido
)


ROOT = Path(__file__).resolve().parents[1]

FEATURES_PATH = (
    ROOT
    / "data"
    / "processed"
    / "lpf_features_modelado.csv"
)


historico = cargar_historico()

df_features = pd.read_csv(
    FEATURES_PATH,
    encoding="utf-8-sig",
    parse_dates=["fecha_partido"]
)


# Utilizamos un partido avanzado del histórico
# para garantizar que exista suficiente información previa.
fila_real = (
    df_features
    .iloc[-100]
)


X_generada = construir_features_partido(
    historico=historico,

    equipo_local=
        fila_real[
            "home_team_name"
        ],

    equipo_visitante=
        fila_real[
            "away_team_name"
        ],

    fecha=
        fila_real[
            "fecha_partido"
        ],

    temporada=
        fila_real[
            "temporada"
        ]
)


columnas_no_comparar = {
    "registro_id",
    "fecha_partido",
    "temporada",
    "home_team_goal_count",
    "away_team_goal_count",
    "total_goal_count",
    "resultado"
}


columnas_modelo = [
    c
    for c in df_features.columns
    if c not in columnas_no_comparar
]


errores = []


for columna in columnas_modelo:

    esperado = fila_real[
        columna
    ]

    obtenido = X_generada.iloc[
        0
    ][columna]


    if (
        pd.isna(esperado)
        and
        pd.isna(obtenido)
    ):
        continue


    if (
        isinstance(
            esperado,
            (int, float, np.number)
        )
        and
        isinstance(
            obtenido,
            (int, float, np.number)
        )
    ):

        if not np.isclose(
            esperado,
            obtenido,
            equal_nan=True
        ):

            errores.append(
                (
                    columna,
                    esperado,
                    obtenido
                )
            )

    else:

        if esperado != obtenido:

            errores.append(
                (
                    columna,
                    esperado,
                    obtenido
                )
            )


print(
    "Partido utilizado:"
)

print(
    fila_real[
        "home_team_name"
    ],
    "vs",
    fila_real[
        "away_team_name"
    ]
)

print(
    "Fecha:",
    fila_real[
        "fecha_partido"
    ]
)

print()

print(
    "Columnas comparadas:",
    len(columnas_modelo)
)

print(
    "Diferencias encontradas:",
    len(errores)
)


if errores:

    print(
        "\nPrimeras diferencias:"
    )

    for error in errores[:20]:

        print(
            error
        )

else:

    print(
        "\nOK: "
        "feature_service reproduce "
        "las características del notebook."
    )