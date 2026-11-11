"""Adaptadores de LECTURA para la capa de presentación.

No contiene lógica predictiva: solo lee el calendario de la temporada
(data/raw/partidos) y resume resultados históricos ya existentes para la
tabla de clasificación. No escribe en ningún archivo ni en la base de datos.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import unicodedata

import pandas as pd

from services.feature_service import construir_historial_equipos
from services.team_assets import EQUIPOS_ACTIVOS


ROOT = Path(__file__).resolve().parents[2]

PARTIDOS_RAW_DIR = ROOT / "data" / "raw" / "partidos"

# Panamá no usa horario de verano: UTC-5 fijo.
ZONA_PANAMA = timezone(timedelta(hours=-5))

COLUMNAS_CALENDARIO = [
    "jornada",
    "fecha_hora",
    "fecha",
    "hora",
    "local",
    "visitante",
    "estadio",
    "estado",
    "goles_local",
    "goles_visitante",
]


def _clave(texto):
    """Clave sin tildes ni mayúsculas para emparejar nombres de equipos."""

    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.casefold().strip()


_NOMBRES_CANONICOS = {_clave(e): e for e in EQUIPOS_ACTIVOS}


def normalizar_equipo(nombre):
    return _NOMBRES_CANONICOS.get(_clave(nombre), str(nombre).strip())


def _archivo_calendario():
    archivos = sorted(PARTIDOS_RAW_DIR.glob("panama-lpf-matches-*-stats.csv"))

    if not archivos:
        raise FileNotFoundError(
            "No se encontró ningún calendario en data/raw/partidos."
        )

    return archivos[-1]


def temporada_de_archivo(ruta):
    """'panama-lpf-matches-2026-to-2027-stats.csv' -> '2026/2027'."""

    coincidencia = re.search(r"matches-(\d{4})-to-(\d{4})", Path(ruta).name)

    if not coincidencia:
        return ""

    inicio, fin = coincidencia.groups()

    return inicio if inicio == fin else f"{inicio}/{fin}"


def cargar_calendario(ruta=None):
    """Devuelve (DataFrame de partidos, temporada). Vacío si no hay datos."""

    ruta = Path(ruta) if ruta else _archivo_calendario()

    bruto = pd.read_csv(ruta, encoding="utf-8")

    bruto = bruto.dropna(subset=["timestamp", "Game Week"]).copy()

    fecha_hora = [
        datetime.fromtimestamp(int(t), tz=ZONA_PANAMA).replace(tzinfo=None)
        for t in bruto["timestamp"]
    ]

    estado = bruto["status"].astype(str).str.lower().map(
        lambda s: "finalizado" if s == "complete" else "pendiente"
    )

    finalizado = estado.eq("finalizado")

    df = pd.DataFrame(
        {
            "jornada": bruto["Game Week"].astype(int).to_numpy(),
            "fecha_hora": pd.to_datetime(fecha_hora),
            "local": bruto["home_team_name"].map(normalizar_equipo).to_numpy(),
            "visitante": bruto["away_team_name"].map(normalizar_equipo).to_numpy(),
            "estadio": bruto["stadium_name"].fillna("").astype(str).to_numpy(),
            "estado": estado.to_numpy(),
            "goles_local": bruto["home_team_goal_count"]
            .where(finalizado)
            .to_numpy(),
            "goles_visitante": bruto["away_team_goal_count"]
            .where(finalizado)
            .to_numpy(),
        }
    )

    df["fecha"] = df["fecha_hora"].dt.date
    df["hora"] = df["fecha_hora"].dt.strftime("%H:%M")

    df = (
        df[COLUMNAS_CALENDARIO]
        .sort_values(["jornada", "fecha_hora", "local"])
        .reset_index(drop=True)
    )

    return df, temporada_de_archivo(ruta)


def jornada_sugerida(calendario):
    """Primera jornada con partidos pendientes (o la última si ya terminó)."""

    if calendario.empty:
        return None

    pendientes = calendario[calendario["estado"] == "pendiente"]

    if pendientes.empty:
        return int(calendario["jornada"].max())

    return int(pendientes["jornada"].min())


def construir_clasificacion(historico, temporada):
    """Tabla de posiciones de una temporada a partir del histórico.

    Orden: puntos, diferencia de goles, goles a favor, nombre.
    """

    columnas = [
        "pos", "equipo", "pj", "g", "e", "p",
        "gf", "gc", "dg", "pts", "forma",
    ]

    partidos = historico[
        historico["temporada"].astype(str) == str(temporada)
    ]

    # La clasificación es de fase regular: los playoffs (2017/2018) no suman.
    if "tipo_fase" in partidos.columns:
        partidos = partidos[partidos["tipo_fase"] != "Playoffs"]

    if partidos.empty:
        return pd.DataFrame(columns=columnas)

    historial = construir_historial_equipos(partidos)

    filas = []

    for equipo, grupo in historial.groupby("equipo"):
        grupo = grupo.sort_values(["fecha_partido", "registro_id"])

        filas.append(
            {
                "equipo": equipo,
                "pj": len(grupo),
                "g": int((grupo["resultado_equipo"] == "G").sum()),
                "e": int((grupo["resultado_equipo"] == "E").sum()),
                "p": int((grupo["resultado_equipo"] == "P").sum()),
                "gf": int(grupo["goles_favor"].sum()),
                "gc": int(grupo["goles_contra"].sum()),
                "pts": int(grupo["puntos"].sum()),
                "forma": grupo["resultado_equipo"].tail(5).tolist(),
            }
        )

    tabla = pd.DataFrame(filas)
    tabla["dg"] = tabla["gf"] - tabla["gc"]

    tabla = tabla.sort_values(
        ["pts", "dg", "gf", "equipo"],
        ascending=[False, False, False, True],
    ).reset_index(drop=True)

    tabla.insert(0, "pos", range(1, len(tabla) + 1))

    return tabla[columnas]
