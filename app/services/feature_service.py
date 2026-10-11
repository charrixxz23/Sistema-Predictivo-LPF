from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]

HISTORICO_PATH = (
    ROOT
    / "data"
    / "processed"
    / "lpf_historico_modelado.csv"
)


VENTANA_FORMA = 5


CARACTERISTICAS_EQUIPO = [
    "partidos_previos",
    "dias_descanso",
    "n_partidos_forma",

    "puntos_ult5",
    "ppg_ult5",
    "gf_prom_ult5",
    "gc_prom_ult5",
    "dg_prom_ult5",

    "ppg_historico_prev",
    "gf_prom_historico_prev",
    "gc_prom_historico_prev",

    "partidos_previos_temporada",
    "ppg_temporada_prev",
    "gf_prom_temporada_prev",
    "gc_prom_temporada_prev",

    "partidos_previos_condicion",
    "ppg_condicion_prev",
    "gf_prom_condicion_prev",
    "gc_prom_condicion_prev"
]


COLUMNAS_DIFERENCIA = [
    "dif_ppg_ult5",
    "dif_dg_prom_ult5",
    "dif_ppg_historico",
    "dif_ppg_temporada",
    "dif_ppg_condicion",
    "dif_dias_descanso"
]


def cargar_historico():

    df = pd.read_csv(
        HISTORICO_PATH,
        encoding="utf-8-sig",
        parse_dates=["fecha_partido"]
    )

    return (
        df
        .sort_values(
            [
                "fecha_partido",
                "registro_id"
            ]
        )
        .reset_index(drop=True)
    )


def construir_historial_equipos(df_partidos):

    df_local = pd.DataFrame({
        "registro_id":
            df_partidos["registro_id"],

        "fecha_partido":
            df_partidos["fecha_partido"],

        "temporada":
            df_partidos["temporada"],

        "equipo":
            df_partidos["home_team_name"],

        "rival":
            df_partidos["away_team_name"],

        "condicion":
            "Local",

        "goles_favor":
            df_partidos[
                "home_team_goal_count"
            ],

        "goles_contra":
            df_partidos[
                "away_team_goal_count"
            ],

        "resultado_partido":
            df_partidos["resultado"]
    })

    df_local[
        "resultado_equipo"
    ] = (
        df_local[
            "resultado_partido"
        ]
        .map({
            "L": "G",
            "E": "E",
            "V": "P"
        })
    )


    df_visitante = pd.DataFrame({
        "registro_id":
            df_partidos["registro_id"],

        "fecha_partido":
            df_partidos["fecha_partido"],

        "temporada":
            df_partidos["temporada"],

        "equipo":
            df_partidos["away_team_name"],

        "rival":
            df_partidos["home_team_name"],

        "condicion":
            "Visitante",

        "goles_favor":
            df_partidos[
                "away_team_goal_count"
            ],

        "goles_contra":
            df_partidos[
                "home_team_goal_count"
            ],

        "resultado_partido":
            df_partidos["resultado"]
    })

    df_visitante[
        "resultado_equipo"
    ] = (
        df_visitante[
            "resultado_partido"
        ]
        .map({
            "L": "P",
            "E": "E",
            "V": "G"
        })
    )


    historial = pd.concat(
        [
            df_local,
            df_visitante
        ],
        ignore_index=True
    )

    historial["puntos"] = (
        historial[
            "resultado_equipo"
        ]
        .map({
            "G": 3,
            "E": 1,
            "P": 0
        })
    )

    historial[
        "diferencia_goles_partido"
    ] = (
        historial["goles_favor"]
        -
        historial["goles_contra"]
    )

    return (
        historial
        .sort_values(
            [
                "equipo",
                "fecha_partido",
                "registro_id"
            ]
        )
        .reset_index(drop=True)
    )


def obtener_temporadas_disponibles(
    historico
):

    temporadas = (
        historico[
            "temporada"
        ]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
    )

    return temporadas


def obtener_equipos_temporada(
    historico,
    temporada
):

    df_temp = historico[
        historico[
            "temporada"
        ].astype(str)
        ==
        str(temporada)
    ]

    equipos = sorted(
        set(
            df_temp[
                "home_team_name"
            ].dropna()
        )
        |
        set(
            df_temp[
                "away_team_name"
            ].dropna()
        )
    )

    return equipos


def _resumen_equipo(
    historial_equipo,
    fecha,
    temporada,
    condicion
):

    fecha = pd.Timestamp(fecha)

    previo = (
        historial_equipo[
            historial_equipo[
                "fecha_partido"
            ] < fecha
        ]
        .sort_values(
            "fecha_partido"
        )
        .copy()
    )

    n_previos = len(previo)

    if n_previos > 0:

        ultima_fecha = (
            previo[
                "fecha_partido"
            ].max()
        )

        dias_descanso = (
            fecha
            -
            ultima_fecha
        ).days

    else:

        dias_descanso = np.nan


    ultimos5 = previo.tail(
        VENTANA_FORMA
    )

    n_forma = min(
        n_previos,
        VENTANA_FORMA
    )


    if len(ultimos5) > 0:

        puntos_ult5 = (
            ultimos5[
                "puntos"
            ].sum()
        )

        ppg_ult5 = (
            ultimos5[
                "puntos"
            ].mean()
        )

        gf_prom_ult5 = (
            ultimos5[
                "goles_favor"
            ].mean()
        )

        gc_prom_ult5 = (
            ultimos5[
                "goles_contra"
            ].mean()
        )

        dg_prom_ult5 = (
            ultimos5[
                "diferencia_goles_partido"
            ].mean()
        )

    else:

        puntos_ult5 = np.nan
        ppg_ult5 = np.nan
        gf_prom_ult5 = np.nan
        gc_prom_ult5 = np.nan
        dg_prom_ult5 = np.nan


    if n_previos > 0:

        ppg_historico_prev = (
            previo[
                "puntos"
            ].mean()
        )

        gf_prom_historico_prev = (
            previo[
                "goles_favor"
            ].mean()
        )

        gc_prom_historico_prev = (
            previo[
                "goles_contra"
            ].mean()
        )

    else:

        ppg_historico_prev = np.nan
        gf_prom_historico_prev = np.nan
        gc_prom_historico_prev = np.nan


    previo_temporada = (
        previo[
            previo[
                "temporada"
            ].astype(str)
            ==
            str(temporada)
        ]
    )

    n_temporada = len(
        previo_temporada
    )

    if n_temporada > 0:

        ppg_temporada_prev = (
            previo_temporada[
                "puntos"
            ].mean()
        )

        gf_prom_temporada_prev = (
            previo_temporada[
                "goles_favor"
            ].mean()
        )

        gc_prom_temporada_prev = (
            previo_temporada[
                "goles_contra"
            ].mean()
        )

    else:

        ppg_temporada_prev = np.nan
        gf_prom_temporada_prev = np.nan
        gc_prom_temporada_prev = np.nan


    previo_condicion = (
        previo[
            previo[
                "condicion"
            ] == condicion
        ]
    )

    n_condicion = len(
        previo_condicion
    )

    if n_condicion > 0:

        ppg_condicion_prev = (
            previo_condicion[
                "puntos"
            ].mean()
        )

        gf_prom_condicion_prev = (
            previo_condicion[
                "goles_favor"
            ].mean()
        )

        gc_prom_condicion_prev = (
            previo_condicion[
                "goles_contra"
            ].mean()
        )

    else:

        ppg_condicion_prev = np.nan
        gf_prom_condicion_prev = np.nan
        gc_prom_condicion_prev = np.nan


    return {
        "partidos_previos":
            n_previos,

        "dias_descanso":
            dias_descanso,

        "n_partidos_forma":
            n_forma,

        "puntos_ult5":
            puntos_ult5,

        "ppg_ult5":
            ppg_ult5,

        "gf_prom_ult5":
            gf_prom_ult5,

        "gc_prom_ult5":
            gc_prom_ult5,

        "dg_prom_ult5":
            dg_prom_ult5,

        "ppg_historico_prev":
            ppg_historico_prev,

        "gf_prom_historico_prev":
            gf_prom_historico_prev,

        "gc_prom_historico_prev":
            gc_prom_historico_prev,

        "partidos_previos_temporada":
            n_temporada,

        "ppg_temporada_prev":
            ppg_temporada_prev,

        "gf_prom_temporada_prev":
            gf_prom_temporada_prev,

        "gc_prom_temporada_prev":
            gc_prom_temporada_prev,

        "partidos_previos_condicion":
            n_condicion,

        "ppg_condicion_prev":
            ppg_condicion_prev,

        "gf_prom_condicion_prev":
            gf_prom_condicion_prev,

        "gc_prom_condicion_prev":
            gc_prom_condicion_prev
    }


def construir_features_partido(
    historico,
    equipo_local,
    equipo_visitante,
    fecha,
    temporada
):

    fecha = pd.Timestamp(fecha)

    historial_equipos = (
        construir_historial_equipos(
            historico
        )
    )

    historial_local = (
        historial_equipos[
            historial_equipos[
                "equipo"
            ] == equipo_local
        ]
    )

    historial_visitante = (
        historial_equipos[
            historial_equipos[
                "equipo"
            ] == equipo_visitante
        ]
    )


    resumen_local = _resumen_equipo(
        historial_local,
        fecha,
        temporada,
        "Local"
    )

    resumen_visitante = _resumen_equipo(
        historial_visitante,
        fecha,
        temporada,
        "Visitante"
    )


    features = {
        "home_team_name":
            equipo_local,

        "away_team_name":
            equipo_visitante
    }


    for columna, valor in (
        resumen_local.items()
    ):

        features[
            f"local_{columna}"
        ] = valor


    for columna, valor in (
        resumen_visitante.items()
    ):

        features[
            f"visitante_{columna}"
        ] = valor


    features[
        "dif_ppg_ult5"
    ] = (
        resumen_local[
            "ppg_ult5"
        ]
        -
        resumen_visitante[
            "ppg_ult5"
        ]
    )

    features[
        "dif_dg_prom_ult5"
    ] = (
        resumen_local[
            "dg_prom_ult5"
        ]
        -
        resumen_visitante[
            "dg_prom_ult5"
        ]
    )

    features[
        "dif_ppg_historico"
    ] = (
        resumen_local[
            "ppg_historico_prev"
        ]
        -
        resumen_visitante[
            "ppg_historico_prev"
        ]
    )

    features[
        "dif_ppg_temporada"
    ] = (
        resumen_local[
            "ppg_temporada_prev"
        ]
        -
        resumen_visitante[
            "ppg_temporada_prev"
        ]
    )

    features[
        "dif_ppg_condicion"
    ] = (
        resumen_local[
            "ppg_condicion_prev"
        ]
        -
        resumen_visitante[
            "ppg_condicion_prev"
        ]
    )

    features[
        "dif_dias_descanso"
    ] = (
        resumen_local[
            "dias_descanso"
        ]
        -
        resumen_visitante[
            "dias_descanso"
        ]
    )


    features[
        "mes_partido"
    ] = fecha.month

    features[
        "dia_semana"
    ] = fecha.dayofweek


    return pd.DataFrame(
        [features]
    )