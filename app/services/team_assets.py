from pathlib import Path
import base64


ROOT = Path(__file__).resolve().parents[2]

LOGOS_DIR = (
    ROOT
    / "app"
    / "assets"
    / "logos"
)


EQUIPOS_ACTIVOS = [
    "Alianza",
    "CA Independiente de La Chorrera",
    "Herrera",
    "Plaza Amador",
    "San Francisco FC",
    "Sporting San Miguelito",
    "Tauro",
    "UMECIT",
    "Universitario",
    "Unión Coclé",
    "Veraguas",
    "Árabe Unido",
]


TEAM_ASSETS = {
    "Alianza": {
        "logo": "alianza.png",
        "short": "ALI"
    },

    "CA Independiente de La Chorrera": {
        "logo": "cai.png",
        "short": "CAI"
    },

    "Herrera": {
        "logo": "herrera.png",
        "short": "HER"
    },

    "Plaza Amador": {
        "logo": "plaza_amador.png",
        "short": "PLA"
    },

    "San Francisco FC": {
        "logo": "san_francisco.png",
        "short": "SFC"
    },

    "Sporting San Miguelito": {
        "logo": "sporting_sm.png",
        "short": "SSM"
    },

    "Tauro": {
        "logo": "tauro.png",
        "short": "TAU"
    },

    "UMECIT": {
        "logo": "umecit.png",
        "short": "UME"
    },

    "Universitario": {
        "logo": "universitario.png",
        "short": "CDU"
    },

    "Unión Coclé": {
        "logo": "union_cocle.png",
        "short": "UCO"
    },

    "Veraguas": {
        "logo": "veraguas.png",
        "short": "VER"
    },

    "Árabe Unido": {
        "logo": "arabe_unido.png",
        "short": "DAU"
    }
}


def obtener_logo_path(equipo):

    config = TEAM_ASSETS.get(equipo)

    if config is None:
        return None

    ruta = LOGOS_DIR / config["logo"]

    if not ruta.exists():
        return None

    return ruta


def obtener_logo_base64(equipo):

    ruta = obtener_logo_path(equipo)

    if ruta is None:
        return None

    with open(ruta, "rb") as archivo:

        return base64.b64encode(
            archivo.read()
        ).decode("utf-8")


def obtener_abreviatura(equipo):

    config = TEAM_ASSETS.get(equipo)

    if config:
        return config["short"]

    palabras = equipo.split()

    return "".join(
        palabra[0]
        for palabra in palabras[:3]
    ).upper()
