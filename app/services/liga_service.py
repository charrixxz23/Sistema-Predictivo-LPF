"""Adaptadores de LECTURA para la capa de presentación.

No contiene lógica predictiva: solo lee el calendario de la temporada
(data/raw/partidos) y resume resultados históricos ya existentes para la
tabla de clasificación. No escribe en ningún archivo ni en la base de datos.
"""

from datetime import datetime, timedelta, timezone
from functools import lru_cache
import json
from pathlib import Path
import re
import unicodedata

import pandas as pd

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


HUECO_TORNEOS_DIAS = 20
MINIMO_PARTIDOS_POR_TORNEO = 40


def acumula_apertura_clausura(historico, temporada):
    """True si la temporada reúne más de un torneo (Apertura y Clausura).

    Criterio basado en los datos: la columna ``torneo`` trae Apertura y
    Clausura, o bien el calendario tiene un salto de más de 20 días con al
    menos 40 partidos a cada lado (receso entre torneos). Una suspensión
    corta de un solo torneo, como la de 2020, no cumple el mínimo.
    """

    partidos = historico[historico["temporada"].astype(str) == str(temporada)]

    if "tipo_fase" in partidos.columns:
        partidos = partidos[partidos["tipo_fase"] != "Playoffs"]

    if partidos.empty:
        return False

    if "torneo" in partidos.columns:
        torneos = set(partidos["torneo"].dropna().astype(str))

        if {"Apertura", "Clausura"} <= torneos:
            return True

    fechas = partidos["fecha_partido"].sort_values().reset_index(drop=True)
    saltos = fechas.diff().dt.days

    for i in saltos.index[saltos > HUECO_TORNEOS_DIAS]:
        if (
            i >= MINIMO_PARTIDOS_POR_TORNEO
            and len(fechas) - i >= MINIMO_PARTIDOS_POR_TORNEO
        ):
            return True

    return False


def construir_clasificacion(historico, temporada):
    """Tabla general de posiciones de una temporada a partir del histórico.

    Orden: puntos y, entre empatados, el desempate del artículo 11 del
    Reglamento de Competencias de la LPF (ver ``clasificar_grupo``). Para las
    temporadas con conferencias solo cuenta la fase de clasificación. Si un
    empate no se resuelve con esos criterios, la fila lleva ``sin_resolver``.
    """

    columnas = [
        "pos", "equipo", "pj", "g", "e", "p",
        "gf", "gc", "dg", "pts", "forma",
        "sin_resolver", "desempate", "empatado_con",
    ]

    partidos = historico[
        historico["temporada"].astype(str) == str(temporada)
    ]

    if partidos.empty:
        return pd.DataFrame(columns=columnas)

    if tiene_conferencias(temporada):
        return construir_clasificacion_oficial(historico, temporada)["General"][columnas]

    # La clasificación es de fase regular: los playoffs (2017/2018) no suman.
    if "tipo_fase" in partidos.columns:
        partidos = partidos[partidos["tipo_fase"] != "Playoffs"]

    if partidos.empty:
        return pd.DataFrame(columns=columnas)

    partidos = partidos.sort_values(["fecha_partido", "registro_id"])

    resultados = list(
        zip(
            partidos["home_team_name"],
            partidos["away_team_name"],
            partidos["home_team_goal_count"].astype(int),
            partidos["away_team_goal_count"].astype(int),
        )
    )

    equipos = sorted(set(partidos["home_team_name"]) | set(partidos["away_team_name"]))

    return clasificar_grupo(resultados, equipos)[columnas]


# ============================================================
# CONFERENCIAS Y CLASIFICACIÓN OFICIAL (Reglamento LPF, Anexo II)
# ============================================================

CONFIG_CONFERENCIAS = ROOT / "app" / "config" / "conferencias.json"

CONFERENCIAS = ("Este", "Oeste")

# Criterios de desempate del artículo 11 que pueden aplicarse con estos datos
# (el 5, puntos por tarjetas, y el 6, sorteo, no: ver clasificar_grupo).
CRITERIOS_DESEMPATE = (
    "diferencia de goles",
    "goles a favor",
    "marcadores directos entre los empatados",
    "goles como visitante",
)


@lru_cache(maxsize=1)
def _config_conferencias():
    try:
        return json.loads(CONFIG_CONFERENCIAS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def config_temporada(temporada):
    """Configuración de conferencias de una temporada, o None si no tiene."""

    return _config_conferencias().get("temporadas", {}).get(str(temporada))


def tiene_conferencias(temporada):
    return config_temporada(temporada) is not None


def nombre_torneo(temporada):
    """'Clausura 2026 (temporada 2026)' o None si la temporada no tiene nombre."""

    cfg = config_temporada(temporada)

    if cfg is None:
        return None

    return f"{cfg['torneo']} (temporada {temporada})"


def conferencia_de(equipo, temporada):
    cfg = config_temporada(temporada)

    if cfg is None:
        return None

    for nombre, equipos in cfg["conferencias"].items():
        if equipo in equipos:
            return nombre

    return None


def etiqueta_conferencia(local, visitante, temporada):
    """'Este', 'Oeste' o 'Interconferencia' (None si la temporada no tiene conferencias)."""

    cl, cv = conferencia_de(local, temporada), conferencia_de(visitante, temporada)

    if cl is None or cv is None:
        return None

    return cl if cl == cv else "Interconferencia"


def zona_de_posicion(pos):
    """'semifinal' (1.º), 'playoff' (2.º y 3.º) o 'eliminado' (4.º en adelante)."""

    plazas = _config_conferencias().get("plazas", {})

    if pos in plazas.get("semifinal_directa", [1]):
        return "semifinal"

    if pos in plazas.get("playoff", [2, 3]):
        return "playoff"

    return "eliminado"


def fase_clasificacion(partidos, jugados=16):
    """Partidos de la fase de clasificación (excluye playoffs, semifinales y final).

    partidos: DataFrame con fecha_partido, registro_id, home_team_name y
    away_team_name. Se recorre en orden cronológico y un partido cuenta solo
    mientras ambos equipos tienen menos de ``jugados`` partidos: así la fase
    final, que los datos de la temporada 2026 traen sin marcar, queda fuera.
    """

    ordenados = partidos.sort_values(["fecha_partido", "registro_id"])

    vistos = {}
    incluir = []

    for local, visitante in zip(
        ordenados["home_team_name"], ordenados["away_team_name"]
    ):
        cuenta = vistos.get(local, 0) < jugados and vistos.get(visitante, 0) < jugados
        incluir.append(cuenta)

        if cuenta:
            vistos[local] = vistos.get(local, 0) + 1
            vistos[visitante] = vistos.get(visitante, 0) + 1

    return ordenados[incluir]


def _totales(partidos, equipos):
    """Totales por equipo a partir de tuplas (local, visitante, goles_l, goles_v)."""

    tot = {
        e: {
            "pj": 0, "g": 0, "e": 0, "p": 0, "gf": 0, "gc": 0,
            "pts": 0, "gf_visita": 0, "forma": [],
        }
        for e in equipos
    }

    for local, visitante, gl, gv in partidos:
        for equipo, gf, gc, es_visita in (
            (local, gl, gv, False),
            (visitante, gv, gl, True),
        ):
            if equipo not in tot:
                continue

            t = tot[equipo]
            t["pj"] += 1
            t["gf"] += gf
            t["gc"] += gc

            if es_visita:
                t["gf_visita"] += gf

            if gf > gc:
                t["g"] += 1
                t["pts"] += 3
                t["forma"].append("G")
            elif gf == gc:
                t["e"] += 1
                t["pts"] += 1
                t["forma"].append("E")
            else:
                t["p"] += 1
                t["forma"].append("P")

    for t in tot.values():
        t["dg"] = t["gf"] - t["gc"]

    return tot


def _clave_directos(equipo, empatados, partidos):
    """Marcadores directos: puntos, diferencia y goles en los partidos entre los empatados."""

    pts = gf = gc = 0

    for local, visitante, gl, gv in partidos:
        if local not in empatados or visitante not in empatados:
            continue

        if equipo == local:
            propios, ajenos = gl, gv
        elif equipo == visitante:
            propios, ajenos = gv, gl
        else:
            continue

        gf += propios
        gc += ajenos
        pts += 3 if propios > ajenos else 1 if propios == ajenos else 0

    return (pts, gf - gc, gf)


def _resolver(equipos, nivel, tot, partidos, motivo=None):
    """Ordena equipos empatados en puntos con los criterios 1 a 4 del artículo 11.

    Cada criterio se aplica solo a los equipos que siguen empatados tras el
    anterior. Devuelve [(equipo, sin_resolver, motivo)], donde ``motivo`` es el
    criterio que separó al equipo de sus empatados (None si nunca estuvo
    empatado) y ``sin_resolver`` indica un empate que ningún criterio rompe.
    """

    if len(equipos) == 1:
        return [(equipos[0], False, motivo)]

    if nivel >= len(CRITERIOS_DESEMPATE):
        return [(e, True, None) for e in sorted(equipos)]

    if nivel == 0:
        def clave(e):
            return tot[e]["dg"]
    elif nivel == 1:
        def clave(e):
            return tot[e]["gf"]
    elif nivel == 2:
        def clave(e):
            return _clave_directos(e, set(equipos), partidos)
    else:
        def clave(e):
            return tot[e]["gf_visita"]

    claves = {e: clave(e) for e in equipos}
    valores = sorted(set(claves.values()), reverse=True)

    resultado = []

    for valor in valores:
        grupo = [e for e in equipos if claves[e] == valor]
        siguiente = CRITERIOS_DESEMPATE[nivel] if len(valores) > 1 else motivo
        resultado += _resolver(grupo, nivel + 1, tot, partidos, siguiente)

    return resultado


def clasificar_grupo(partidos, equipos):
    """Tabla de posiciones de un grupo con el desempate oficial (art. 11, criterios 1 a 4).

    partidos: lista cronológica de (local, visitante, goles_local, goles_visitante)
    de la fase de clasificación (pueden incluir rivales ajenos al grupo).
    equipos: equipos a ordenar. Orden: puntos y, entre empatados, 1) diferencia de
    goles, 2) goles a favor, 3) marcadores directos entre los empatados (puntos,
    diferencia y goles de esos partidos), 4) goles como visitante. Si el empate
    persiste, ``sin_resolver`` es True: lo definirían los puntos de juego limpio
    (criterio 5, no calculable con estos datos) o un sorteo (criterio 6).
    """

    columnas = [
        "pos", "equipo", "pj", "g", "e", "p", "gf", "gc", "dg", "pts",
        "gf_visita", "forma", "sin_resolver", "desempate", "empatado_con",
    ]

    equipos = list(equipos)

    if not equipos:
        return pd.DataFrame(columns=columnas)

    tot = _totales(partidos, equipos)

    ordenados = []

    for pts in sorted({tot[e]["pts"] for e in equipos}, reverse=True):
        empatados = [e for e in equipos if tot[e]["pts"] == pts]
        ordenados += _resolver(empatados, 0, tot, partidos)

    sin_resolver = [e for e, no_resuelto, _ in ordenados if no_resuelto]

    filas = []

    for pos, (equipo, no_resuelto, motivo) in enumerate(ordenados, start=1):
        t = tot[equipo]

        filas.append(
            {
                "pos": pos,
                "equipo": equipo,
                "pj": t["pj"],
                "g": t["g"],
                "e": t["e"],
                "p": t["p"],
                "gf": t["gf"],
                "gc": t["gc"],
                "dg": t["dg"],
                "pts": t["pts"],
                "gf_visita": t["gf_visita"],
                "forma": t["forma"][-5:],
                "sin_resolver": no_resuelto,
                "desempate": motivo,
                "empatado_con": [
                    otro
                    for otro in sin_resolver
                    if no_resuelto
                    and otro != equipo
                    and tot[otro]["pts"] == t["pts"]
                    and tot[otro]["dg"] == t["dg"]
                    and tot[otro]["gf"] == t["gf"]
                    and tot[otro]["gf_visita"] == t["gf_visita"]
                ],
            }
        )

    return pd.DataFrame(filas, columns=columnas)


def construir_clasificacion_oficial(historico, temporada):
    """Tablas Este, Oeste y General de una temporada con conferencias.

    Devuelve None si la temporada no tiene conferencias configuradas. Si las
    tiene: {"Este": df, "Oeste": df, "General": df, "partidos": n, "completa": bool}.
    Solo cuenta la fase de clasificación (16 partidos por equipo). Las posiciones
    de cada conferencia llevan la zona ('semifinal', 'playoff' o 'eliminado').
    """

    cfg = config_temporada(temporada)

    if cfg is None:
        return None

    objetivo = _config_conferencias().get("partidos_por_equipo", 16)

    datos = historico[historico["temporada"].astype(str) == str(temporada)]
    datos = fase_clasificacion(datos, objetivo)

    partidos = list(
        zip(
            datos["home_team_name"],
            datos["away_team_name"],
            datos["home_team_goal_count"].astype(int),
            datos["away_team_goal_count"].astype(int),
        )
    )

    todos = [e for equipos in cfg["conferencias"].values() for e in equipos]

    tablas = {}

    for nombre in CONFERENCIAS:
        tabla = clasificar_grupo(partidos, cfg["conferencias"].get(nombre, []))
        tabla["zona"] = tabla["pos"].map(zona_de_posicion)
        tablas[nombre] = tabla

    tablas["General"] = clasificar_grupo(partidos, todos)
    tablas["partidos"] = len(partidos)
    tablas["completa"] = bool(
        len(tablas["General"]) and (tablas["General"]["pj"] >= objetivo).all()
    )

    return tablas


def cruces_si_terminara_hoy(tablas):
    """Clasificados a semifinales y cruces de playoff según la tabla actual (art. 10 y 12).

    Solo ordena la tabla de hoy: no simula partidos ni predice nada.
    ``incierto`` es True si hay un empate sin resolver dentro de los cuatro
    primeros puestos de alguna conferencia.
    """

    este, oeste = tablas["Este"], tablas["Oeste"]

    if len(este) < 3 or len(oeste) < 3:
        return None

    def equipo(tabla, pos):
        return tabla.iloc[pos - 1]["equipo"]

    incierto = bool(
        este.head(4)["sin_resolver"].any() or oeste.head(4)["sin_resolver"].any()
    )

    return {
        "semifinal_directa": [
            {"conferencia": "Este", "equipo": equipo(este, 1)},
            {"conferencia": "Oeste", "equipo": equipo(oeste, 1)},
        ],
        # Los segundos juegan de local (art. 12)
        "playoff": [
            {
                "local": equipo(este, 2), "local_conferencia": "Este", "local_pos": 2,
                "visitante": equipo(oeste, 3), "visitante_conferencia": "Oeste", "visitante_pos": 3,
            },
            {
                "local": equipo(oeste, 2), "local_conferencia": "Oeste", "local_pos": 2,
                "visitante": equipo(este, 3), "visitante_conferencia": "Este", "visitante_pos": 3,
            },
        ],
        "incierto": incierto,
    }
