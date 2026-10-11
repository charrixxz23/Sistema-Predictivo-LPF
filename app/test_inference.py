from services.feature_service import (
    cargar_historico
)

from services.model_service import (
    cargar_modelos
)

from services.prediction_service import (
    analizar_partido
)


historico = cargar_historico()
modelos = cargar_modelos()


resultado = analizar_partido(
    historico=historico,
    modelos=modelos,
    equipo_local="Alianza",
    equipo_visitante="CA Independiente de La Chorrera",
    fecha="2026-03-15",
    temporada="2026"
)


print("\n==============================")
print("   PRUEBA MOTOR PREDICTIVO")
print("==============================\n")


print("XGBoost")
print("------------------------------")

print(
    "Resultado principal:",
    resultado["xgboost"]["resultado"]
)

print(
    "Probabilidades:",
    resultado["xgboost"]["probabilidades"]
)


print("\nPoisson")
print("------------------------------")

print(
    "Lambda local:",
    round(
        resultado["goles"]["lambda_local"],
        4
    )
)

print(
    "Lambda visitante:",
    round(
        resultado["goles"]["lambda_visitante"],
        4
    )
)


print("\nProbabilidades Poisson")
print("------------------------------")

for clase, probabilidad in (
    resultado[
        "poisson_resultado"
    ].items()
):

    print(
        clase,
        ":",
        f"{probabilidad * 100:.2f}%"
    )


print("\nMarcador más probable")
print("------------------------------")

marcador = (
    resultado[
        "marcador_probable"
    ]
)

print(
    f"{marcador['local']} - "
    f"{marcador['visitante']}"
)

print(
    "Probabilidad:",
    f"{marcador['probabilidad'] * 100:.2f}%"
)


print("\nTop 5 marcadores")
print("------------------------------")

for i, item in enumerate(
    resultado["top_marcadores"],
    start=1
):

    print(
        f"{i}. "
        f"{item['local']}-"
        f"{item['visitante']} "
        f"({item['probabilidad'] * 100:.2f}%)"
    )


print("\n==============================")
print("PRUEBA COMPLETADA")
print("==============================")