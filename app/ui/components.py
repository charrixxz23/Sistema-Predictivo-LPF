"""Componentes reutilizables de la interfaz.

Cada función ``*_html`` devuelve marcado HTML (con el texto ya escapado) y
cada función sin sufijo lo dibuja con ``st.html``. Las clases CSS viven en
ui/styles.py; aquí no hay estilos propios, solo los colores de los clubes
(ui/team_colors.py) que se pasan como variables CSS.
"""

import base64
from datetime import date, datetime
from functools import lru_cache
from html import escape
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode

import numpy as np
import streamlit as st
from PIL import Image

from services.liga_service import etiqueta_conferencia, nombre_torneo
from services.poisson_service import calcular_matriz_marcadores
from services.team_assets import obtener_abreviatura, obtener_logo_path
from ui import team_colors as tc


# ============================================================
# CONSTANTES DE PRESENTACIÓN
# ============================================================

NOMBRE_APP = "Pronóstico LPF"

AUTOR = "Richard Smith"
UNIVERSIDAD = "Universidad Tecnológica de Panamá"
ANIO_TRABAJO = "2026"

AVISO_PIE = (
    f"Desarrollado por {AUTOR} · Proyecto académico, {UNIVERSIDAD} · "
    "No está afiliado a la Liga Panameña de Fútbol."
)

# Zonas de la tabla por conferencia (art. 10 y 12 del Anexo II del Reglamento).
# «Fuera de zona» y no «Eliminado»: a mitad del torneo ningún club lo está aún.
ZONAS = {
    "semifinal": "Semifinal directa",
    "playoff": "Playoff",
    "eliminado": "Fuera de zona",
}

# Diferencia (en probabilidad) por debajo de la cual el partido se rotula «parejo».
UMBRAL_PAREJO = 0.05

RESULTADO_LABELS = {
    "L": "Victoria local",
    "E": "Empate",
    "V": "Victoria visitante",
}

# Nombres cortos SOLO para la presentación (filas, tablas compactas).
# El nombre completo sigue siendo el que usan los datos y los modelos.
NOMBRES_CORTOS = {
    "CA Independiente de La Chorrera": "CAI La Chorrera",
    "Sporting San Miguelito": "Sporting SM",
    "San Francisco FC": "San Francisco",
}

_DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

_MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
    "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]

# Mapa de calor de marcadores: de papel a verde oscuro
_PAPEL = "#FBF8F2"
_VERDE_MAPA = "#006B4A"
_LADO_MAPA = 6  # 0 a 5 goles por equipo


# ============================================================
# FORMATO
# ============================================================

def nombre_corto(equipo):
    return NOMBRES_CORTOS.get(equipo, equipo)


def etiqueta_temporada(temporada):
    """'Apertura 2026 (temporada 2026/2027)' o, sin nombre de torneo, 'Temporada 2025'."""

    return nombre_torneo(temporada) or f"Temporada {temporada}"


def porcentaje(valor, decimales=1):
    return f"{valor * 100:.{decimales}f} %"


def numero(valor, decimales=2):
    return f"{valor:.{decimales}f}"


def texto_seguro(valor):
    if valor is None:
        return ""

    return escape(str(valor))


def formatear_fecha(valor):
    if hasattr(valor, "strftime"):
        return valor.strftime("%d/%m/%Y")

    try:
        return date.fromisoformat(str(valor)).strftime("%d/%m/%Y")
    except ValueError:
        return str(valor)


def formatear_fecha_hora(valor):
    try:
        return datetime.fromisoformat(str(valor)).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return str(valor).replace("T", " ")


def fecha_larga(valor):
    """date -> 'Sábado 20 de septiembre'."""

    return f"{_DIAS[valor.weekday()]} {valor.day} de {_MESES[valor.month - 1]}"


def mostrar(markup):
    st.html(markup)


# ============================================================
# ESCUDOS
# ============================================================

# Lado (px) de la miniatura según el tamaño en pantalla: el doble del tamaño CSS
# más grande de cada uso, para que no se vea borrosa en pantallas de alta densidad.
_LADO_MINIATURA = {"sm": 96, "md": 96, "duelo": 96, "lg": 192}


@lru_cache(maxsize=None)
def _miniatura_base64(ruta, lado=96):
    """Escudo reducido desde el original como data-URI (evita incrustar PNG de 200 KB)."""

    with Image.open(ruta) as imagen:
        imagen = imagen.convert("RGBA")
        imagen.thumbnail((lado, lado), Image.Resampling.LANCZOS)
        # Paleta de 256 colores: ~4x menos bytes por escudo, sin pérdida visible.
        imagen = imagen.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
        buffer = BytesIO()
        imagen.save(buffer, format="PNG", optimize=True)

    return base64.b64encode(buffer.getvalue()).decode("ascii")


def team_crest_html(equipo, tamano="sm"):
    """Escudo local del equipo o, si no existe, sus iniciales."""

    ruta = obtener_logo_path(equipo)

    if ruta is not None:
        try:
            datos = _miniatura_base64(str(ruta), _LADO_MINIATURA.get(tamano, 96))
            return (
                f"<span class='lpf-crest lpf-crest--{tamano}'>"
                f"<img alt='Escudo de {texto_seguro(equipo)}' "
                f"src='data:image/png;base64,{datos}'></span>"
            )
        except OSError:
            pass

    return (
        f"<span class='lpf-crest lpf-crest--{tamano} lpf-crest--fallback'>"
        f"{texto_seguro(obtener_abreviatura(equipo))}</span>"
    )


# ============================================================
# MARCA, ENCABEZADO, SECCIONES, DATOS, PIE
# ============================================================

def brand_bar(db_disponible=True):
    """Marca bajo la navegación superior."""

    aviso = (
        ""
        if db_disponible
        else "<span class='lpf-brand__aviso'>Historial no disponible</span>"
    )

    mostrar(
        "<div class='lpf-brand'>"
        "<span class='lpf-brand__name'>Pronóstico <b>LPF</b></span>"
        "<span class='lpf-brand__tag'>Predicción de partidos del fútbol panameño</span>"
        f"{aviso}"
        "</div>"
    )


def footer():
    mostrar(f"<footer class='lpf-footer'>{texto_seguro(AVISO_PIE)}</footer>")


def page_header_html(titulo, subtitulo=""):
    return (
        "<header class='lpf-header'>"
        f"<h1 class='lpf-header__title'>{texto_seguro(titulo)}</h1>"
        + (
            f"<p class='lpf-header__subtitle'>{texto_seguro(subtitulo)}</p>"
            if subtitulo
            else ""
        )
        + "</header>"
    )


def page_header(titulo, subtitulo=""):
    mostrar(page_header_html(titulo, subtitulo))


def section_title(titulo, pista=""):
    mostrar(
        "<div class='lpf-section'>"
        f"<h2 class='lpf-section__title'>{texto_seguro(titulo)}</h2>"
        f"<span class='lpf-section__hint'>{texto_seguro(pista)}</span>"
        "</div>"
    )


def day_heading(valor):
    mostrar(f"<div class='lpf-dia'>{texto_seguro(fecha_larga(valor))}</div>")


def data_line_html(datos):
    """Línea de datos. datos: iterable de (valor, texto); el valor va en negrita."""

    return (
        "<div class='lpf-datos'>"
        + "".join(
            f"<span><b>{texto_seguro(valor)}</b> {texto_seguro(texto)}</span>"
            for valor, texto in datos
        )
        + "</div>"
    )


def data_line(datos):
    mostrar(data_line_html(datos))


def foot_note(texto):
    mostrar(f"<p class='lpf-nota-pie'>{texto_seguro(texto)}</p>")


# ============================================================
# PARTIDOS: FILA DE DUELO
# ============================================================

def es_parejo(probabilidades):
    """True si los dos desenlaces más probables difieren en menos de 5 puntos."""

    valores = sorted((probabilidades.get(c, 0.0) for c in "LEV"), reverse=True)

    return valores[0] - valores[1] < UMBRAL_PAREJO


def frase_pronostico(probabilidades, local, visitante):
    """Lo más probable, sin afirmar un ganador: la probabilidad máxima suele ser 35-45 %."""

    if es_parejo(probabilidades):
        return "Partido parejo"

    codigo = max("LEV", key=lambda c: probabilidades.get(c, 0.0))
    valor = f"{probabilidades.get(codigo, 0.0) * 100:.0f} %"

    if codigo == "L":
        return f"Más probable: victoria de {nombre_corto(local)} ({valor})"

    if codigo == "V":
        return f"Más probable: victoria de {nombre_corto(visitante)} ({valor})"

    return f"Más probable: empate ({valor})"


def _resultado_real(goles_local, goles_visitante):
    if goles_local > goles_visitante:
        return "L"

    if goles_local < goles_visitante:
        return "V"

    return "E"


def _barra_1x2_html(probabilidades, rayado_local, rayado_visitante, clase="lpf-1x2"):
    """Barra 1X2: color del local (1), gris (X) y color del visitante (2)."""

    total = sum(probabilidades.get(c, 0.0) for c in "LEV") or 1.0

    def segmento(codigo, extra, rayado):
        ancho = probabilidades.get(codigo, 0.0) / total * 100
        marca = " rayado" if rayado else ""
        return f"<i class='{extra}{marca}' style='width:{ancho:.2f}%'></i>"

    return (
        f"<div class='{clase}' role='img' aria-label='Probabilidades 1X2'>"
        f"{segmento('L', 'u', rayado_local)}"
        f"{segmento('E', 'x', False)}"
        f"{segmento('V', 'd', rayado_visitante)}"
        "</div>"
    )


def analyze_href(local, visitante, fecha, temporada):
    """Enlace a la página Predicciones con el partido preseleccionado."""

    consulta = urlencode(
        {
            "local": local,
            "visitante": visitante,
            "fecha": fecha.isoformat(),
            "temporada": temporada,
        }
    )

    return f"/predicciones?{consulta}"


def match_card_html(partido, prediccion=None, temporada="", fecha_corte=None):
    """Fila de duelo de un partido (una fila por partido, en una sola columna).

    partido: dict con local, visitante, hora, fecha, estadio, estado,
             goles_local, goles_visitante.
    prediccion: dict con probabilidades, resultado, marcador y
                prob_marcador (o None si no se muestran predicciones).
    fecha_corte: última fecha vista por los modelos al entrenarse. El
                 indicador de acierto solo se muestra en partidos POSTERIORES
                 a esa fecha; los demás se rotulan como parte del período de
                 entrenamiento. Si es None no se muestra indicador.
    """

    local = partido["local"]
    visitante = partido["visitante"]
    finalizado = partido["estado"] == "finalizado"

    (c_local, ray_local), (c_visita, ray_visita) = tc.colores_barra(local, visitante)

    if finalizado:
        gl = int(partido["goles_local"])
        gv = int(partido["goles_visitante"])
        centro = f"<div class='lpf-duelo__marcador'>{gl} - {gv}</div>"
        estado = "Final"
    else:
        centro = "<div class='lpf-duelo__marcador vs'>vs</div>"
        estado = "Pendiente"

    estadio = partido.get("estadio") or "Estadio por confirmar"

    conferencia = etiqueta_conferencia(local, visitante, temporada)
    conf_html = (
        f"<em class='lpf-conf lpf-conf--{conferencia.lower()}'>{texto_seguro(conferencia)}</em>"
        if conferencia
        else ""
    )

    html = (
        f"<article class='lpf-duelo' style='--c1:{c_local};--c2:{c_visita}'>"
        "<div class='lpf-duelo__linea'>"
        "<div class='lpf-duelo__cuando'>"
        f"<b>{texto_seguro(partido['hora'])}</b><span>{estado}</span></div>"
        f"<div class='lpf-duelo__local' title='{texto_seguro(local)}'>"
        f"<span class='lpf-duelo__n'>{texto_seguro(nombre_corto(local))}</span>"
        f"{team_crest_html(local, 'duelo')}</div>"
        f"{centro}"
        f"<div class='lpf-duelo__visita' title='{texto_seguro(visitante)}'>"
        f"{team_crest_html(visitante, 'duelo')}"
        f"<span class='lpf-duelo__n'>{texto_seguro(nombre_corto(visitante))}</span></div>"
        "</div>"
    )

    if prediccion:
        probs = prediccion["probabilidades"]
        pick = prediccion["resultado"]
        marcador = prediccion["marcador"]

        marca = ""
        if finalizado and fecha_corte is not None:
            if partido["fecha"] <= fecha_corte:
                marca = (
                    " · <span class='lpf-marca-neutra'>"
                    "Dentro del período de entrenamiento</span>"
                )
            elif _resultado_real(gl, gv) == pick:
                marca = " · <span class='lpf-marca-ok'>✓ Acertó 1X2</span>"
            else:
                marca = " · <span class='lpf-marca-no'>✕ No acertó 1X2</span>"

        parejo = es_parejo(probs)

        def cifra(codigo, rotulo):
            # Con la abreviatura y la cifra pegadas («SFC 32 %») no se confunde con «132 %»
            texto = f"{rotulo} {probs.get(codigo, 0.0) * 100:.0f} %"
            resaltar = codigo == pick and not parejo
            return f"<span><b>{texto}</b></span>" if resaltar else f"<span>{texto}</span>"

        enlace = analyze_href(local, visitante, partido["fecha"], temporada)

        html += (
            "<div class='lpf-duelo__pred'>"
            "<div>"
            f"{_barra_1x2_html(probs, ray_local, ray_visita)}"
            f"<div class='lpf-1x2__n'>{cifra('L', obtener_abreviatura(local))}{cifra('E', 'Empate')}{cifra('V', obtener_abreviatura(visitante))}</div>"
            "</div>"
            "<div class='lpf-duelo__lado'>Marcador probable "
            f"<strong>{marcador['local']} - {marcador['visitante']}</strong> "
            f"({porcentaje(prediccion['prob_marcador'])})<br>"
            f"{texto_seguro(frase_pronostico(probs, local, visitante))}{marca}</div>"
            "</div>"
            "<div class='lpf-duelo__pie'>"
            f"<span>{conf_html}{texto_seguro(estadio)}</span>"
            f"<a class='lpf-enlace' target='_self' href='{escape(enlace)}'>"
            "Analizar a fondo →</a></div>"
        )
    else:
        html += (
            "<div class='lpf-duelo__pie'>"
            f"<span>{conf_html}{texto_seguro(estadio)}</span></div>"
        )

    return html + "</article>"


def match_grid(filas):
    mostrar(f"<div class='lpf-duelos'>{''.join(filas)}</div>")


# ============================================================
# TABLA DE CLASIFICACIÓN
# ============================================================

_COLUMNAS_TABLA = (
    ("pos", ""), ("equipo", "Equipo"), ("pj", "PJ"), ("g", "G"), ("e", "E"),
    ("p", "P"), ("gf", "GF"), ("gc", "GC"), ("dg", "DG"), ("pts", "Pts"),
    ("forma", "Forma"),
)

# Columnas de detalle: se ocultan en pantallas pequeñas (y siempre en la tabla compacta)
_DETALLE = {"g", "e", "p", "gf", "gc", "forma"}

_LETRAS_FORMA = {"G": "Ganó", "E": "Empató", "P": "Perdió"}

TEXTO_EMPATE_SIN_RESOLVER = (
    "Empate sin resolver (lo definiría el juego limpio o un sorteo)"
)


def form_html(forma):
    """Últimos partidos como letras G, E, P en cuadros pequeños.

    El orden es del más antiguo (izquierda) al más reciente (derecha); el más
    reciente lleva un borde oscuro. Verde = G, gris = E, rojo = P, siempre con la letra.
    """

    forma = list(forma)

    cuadros = "".join(
        f"<i class='{r}{' u' if n == len(forma) - 1 else ''}' "
        f"title='{_LETRAS_FORMA.get(r, r)}{' (el más reciente)' if n == len(forma) - 1 else ''}'>"
        f"{texto_seguro(r)}</i>"
        for n, r in enumerate(forma)
    )

    resumen = ", ".join(_LETRAS_FORMA.get(r, r) for r in forma)

    return (
        "<span class='forma' role='img' "
        f"aria-label='Últimos partidos, del más antiguo al más reciente: {resumen}'>"
        f"{cuadros}</span>"
    )


def standings_table_html(tabla, corto=False, compacta=False, ocultar=(), zonas=False):
    """Tabla de posiciones con una franja del color de cada club.

    ocultar: claves de columnas que no se muestran (p. ej. {'gf', 'gc'}).
    compacta: oculta todas las columnas de detalle (G, E, P, GF, GC, Forma).
    zonas: si la tabla trae la columna 'zona' (semifinal / playoff / eliminado),
           la rotula con texto bajo el nombre y separa las zonas con una línea.
    """

    ocultar = set(ocultar) | (_DETALLE if compacta else set())
    visibles = [(k, t) for k, t in _COLUMNAS_TABLA if k not in ocultar]

    def clase(clave):
        extra = " hide-sm" if clave in _DETALLE else ""
        return ("e" if clave == "equipo" else "") + extra

    cabecera = "".join(
        f"<th class='{clase(k).strip()}'"
        + (
            " title='Últimos 5 partidos; el cuadro con borde es el más reciente'"
            if k == "forma"
            else ""
        )
        + f">{t}</th>"
        for k, t in visibles
    )

    registros = list(tabla.itertuples(index=False))
    filas = []

    for n, fila in enumerate(registros):
        dg = f"+{fila.dg}" if fila.dg > 0 else str(fila.dg)
        nombre = nombre_corto(fila.equipo) if corto else fila.equipo
        club = tc.colores_club(fila.equipo)["primario"]

        zona = getattr(fila, "zona", None) if zonas else None
        sin_resolver = bool(getattr(fila, "sin_resolver", False))
        siguiente = (
            getattr(registros[n + 1], "zona", None) if zonas and n + 1 < len(registros) else zona
        )

        rotulos = ""

        if zona:
            rotulos += f"<small class='zona zona--{zona}'>{ZONAS.get(zona, '')}</small>"

        if sin_resolver:
            rotulos += (
                f"<small class='sr' title='{texto_seguro(TEXTO_EMPATE_SIN_RESOLVER)}'>"
                "Empate sin resolver</small>"
            )

        nombre_html = (
            f"<span class='eq__t'><span class='eq__n'>{texto_seguro(nombre)}</span>{rotulos}</span>"
            if rotulos
            else f"<span>{texto_seguro(nombre)}</span>"
        )

        celdas = {
            "pos": f"<td class='club'>{fila.pos}</td>",
            "equipo": (
                "<td class='e'>"
                f"<div class='eq' title='{texto_seguro(fila.equipo)}'>"
                f"{team_crest_html(fila.equipo)}{nombre_html}</div></td>"
            ),
            "pj": f"<td>{fila.pj}</td>",
            "g": f"<td class='hide-sm'>{fila.g}</td>",
            "e": f"<td class='hide-sm'>{fila.e}</td>",
            "p": f"<td class='hide-sm'>{fila.p}</td>",
            "gf": f"<td class='hide-sm'>{fila.gf}</td>",
            "gc": f"<td class='hide-sm'>{fila.gc}</td>",
            "dg": f"<td>{dg}</td>",
            "pts": f"<td class='pts'>{fila.pts}</td>",
            "forma": f"<td class='hide-sm'>{form_html(fila.forma)}</td>",
        }

        fin_zona = " fin-zona" if zonas and siguiente != zona else ""

        filas.append(
            f"<tr class='{fin_zona.strip()}' style='--club:{club}'>"
            + "".join(celdas[k] for k, _ in visibles)
            + "</tr>"
        )

    return (
        "<div class='lpf-tabla-wrap'><table class='lpf-tabla'>"
        f"<thead><tr>{cabecera}</tr></thead>"
        f"<tbody>{''.join(filas)}</tbody></table></div>"
    )


def standings_table(tabla, corto=False, compacta=False, ocultar=(), zonas=False):
    mostrar(standings_table_html(tabla, corto, compacta, ocultar, zonas))


def empates_sin_resolver(tabla):
    """Nombres de los equipos con empate sin resolver en una tabla (lista vacía si no hay)."""

    if "sin_resolver" not in tabla.columns:
        return []

    return tabla.loc[tabla["sin_resolver"].astype(bool), "equipo"].tolist()


def zone_legend_html():
    return (
        "<p class='lpf-nota-pie lpf-leyenda'>"
        "<b>Semifinal directa</b>: 1.º de cada conferencia · "
        "<b>Playoff</b>: 2.º y 3.º (partido único; el 2.º juega de local) · "
        "<b>Fuera de zona</b>: 4.º a 6.º. Posiciones según la tabla de hoy."
        "</p>"
    )


def bracket_html(cruces, completa=False):
    """Bloque «Si el torneo terminara hoy»: ordena la tabla actual, no simula nada."""

    def equipo(nombre, pos, conf):
        return (
            "<span class='lpf-llave__eq'>"
            f"{team_crest_html(nombre)}"
            f"<span><b>{texto_seguro(nombre_corto(nombre))}</b>"
            f"<small>{pos}.º {texto_seguro(conf)}</small></span></span>"
        )

    directos = "".join(
        f"<li>{equipo(x['equipo'], 1, x['conferencia'])}</li>"
        for x in cruces["semifinal_directa"]
    )

    playoffs = "".join(
        "<li class='lpf-llave__cruce'>"
        f"{equipo(x['local'], x['local_pos'], x['local_conferencia'])}"
        "<em>vs</em>"
        f"{equipo(x['visitante'], x['visitante_pos'], x['visitante_conferencia'])}"
        "</li>"
        for x in cruces["playoff"]
    )

    notas = [
        "Solo ordena la tabla de hoy según el Reglamento (art. 10 y 12): no es una "
        "predicción ni una simulación."
    ]

    if not completa:
        notas.append("Aún faltan partidos de la fase de clasificación: los cruces pueden cambiar.")

    if cruces.get("incierto"):
        notas.append(
            "Hay un empate sin resolver entre los cuatro primeros de una conferencia; "
            "el orden mostrado es provisional."
        )

    return (
        "<section class='lpf-llave'>"
        "<div><h3 class='lpf-subseccion'>Semifinal directa</h3>"
        f"<ul>{directos}</ul></div>"
        "<div><h3 class='lpf-subseccion'>Playoff · partido único</h3>"
        f"<ul>{playoffs}</ul>"
        "<p class='lpf-nota-pie'>El 2.º de cada conferencia juega de local.</p></div>"
        "</section>"
        f"<p class='lpf-nota-pie'>{texto_seguro(' '.join(notas))}</p>"
    )


# ============================================================
# PREDICCIÓN DE PARTIDO
# ============================================================

def versus_html(local, visitante, temporada, fecha):
    """Cabecera dividida en diagonal con los colores de los dos clubes.

    Si ninguna tinta cumple contraste AA sobre el color de un club, su nombre
    va fuera del color (debajo de la cabecera).
    """

    c_local, c_visita, _ = tc.colores_partido(local, visitante)

    lados, fuera = [], []

    for equipo, color, rol in ((local, c_local, "LOCAL"), (visitante, c_visita, "VISITANTE")):
        tinta, cumple = tc.tinta_sobre(color)

        dentro = (
            f"<span class='lpf-vs__rol'>{rol}</span>" if cumple else ""
        )
        nombre = (
            f"<span class='lpf-vs__nombre'>{texto_seguro(equipo)}</span>"
            f"<span class='lpf-vs__abrev'>{texto_seguro(obtener_abreviatura(equipo))}</span>"
            if cumple
            else ""
        )

        lados.append(
            f"<div class='lpf-vs__lado' style='--tinta:{tinta}'>"
            f"{dentro}{team_crest_html(equipo, 'lg')}{nombre}</div>"
        )
        fuera.append(
            ""
            if cumple
            else f"<span><small>{rol}</small>{texto_seguro(equipo)}</span>"
        )

    return (
        "<section class='lpf-versus'>"
        f"<div class='lpf-vs' style='--c1:{c_local};--c2:{c_visita}'>"
        f"{lados[0]}{lados[1]}<div class='lpf-vs__centro'>VS</div></div>"
        f"<div class='lpf-vs__fuera'>{fuera[0]}{fuera[1]}</div>"
        f"<p class='lpf-vs__meta'>{texto_seguro(etiqueta_temporada(temporada))} · "
        f"{fecha.strftime('%d/%m/%Y')}</p>"
        "</section>"
    )


def prediction_panel_html(resultado, local, visitante):
    """Probabilidades 1X2 de XGBoost: barra con colores de los clubes y tres cifras."""

    xgb = resultado["xgboost"]
    probabilidades = xgb["probabilidades"]
    pick = xgb["resultado"]

    (c_local, ray_local), (c_visita, ray_visita) = tc.colores_barra(local, visitante)

    nombres = {"L": local, "E": "Empate", "V": visitante}
    rotulos = {"L": "Local", "E": "Empate", "V": "Visitante"}

    columnas = "".join(
        f"<div class='lpf-prob3__col{' pick' if codigo == pick else ''}'>"
        f"<small>{rotulos[codigo]}</small>"
        f"<b>{probabilidades.get(codigo, 0.0) * 100:.1f} %</b>"
        f"<span>{texto_seguro(nombres[codigo])}</span></div>"
        for codigo in "LEV"
    )

    return (
        f"<section class='lpf-prob3' style='--c1:{c_local};--c2:{c_visita}'>"
        f"{_barra_1x2_html(probabilidades, ray_local, ray_visita, 'lpf-prob3__barra')}"
        f"<div class='lpf-prob3__cols'>{columnas}</div>"
        "<p class='lpf-prob3__pick'>Predicción principal: "
        f"<strong>{texto_seguro(RESULTADO_LABELS.get(pick, pick)).upper()}</strong></p>"
        "</section>"
    )


def _color_celda(probabilidad, maximo):
    return tc.mezclar(_PAPEL, _VERDE_MAPA, min(1.0, (probabilidad / maximo) ** 0.75))


def score_matrix_html(resultado, local, visitante):
    """Mapa de calor de marcadores (0 a 5 goles por equipo).

    Usa calcular_matriz_marcadores (la misma matriz que ya calcula la
    aplicación) con las lambdas del modelo. El marcador más probable que
    muestra la app queda resaltado si cae dentro de la matriz.
    """

    goles = resultado["goles"]
    matriz = calcular_matriz_marcadores(
        goles["lambda_local"], goles["lambda_visitante"]
    )
    caja = matriz[:_LADO_MAPA, :_LADO_MAPA]
    maximo = float(caja.max())

    marcador = resultado["marcador_probable"]
    resaltado = (
        (marcador["local"], marcador["visitante"])
        if marcador["local"] < _LADO_MAPA and marcador["visitante"] < _LADO_MAPA
        else None
    )

    c_local, c_visita, _ = tc.colores_partido(local, visitante)

    cabecera = "<th></th>" + "".join(f"<th>{g}</th>" for g in range(_LADO_MAPA))

    filas = []

    for a in range(_LADO_MAPA):
        celdas = []

        for b in range(_LADO_MAPA):
            color = _color_celda(float(caja[a, b]), maximo)
            tinta, _ = tc.tinta_sobre(color)
            clase = " class='max'" if (a, b) == resaltado else ""

            celdas.append(
                f"<td{clase} style='background:{color};color:{tinta}' "
                f"title='{texto_seguro(local)} {a} - {b} {texto_seguro(visitante)}: "
                f"{caja[a, b] * 100:.2f} %'>{caja[a, b] * 100:.1f}</td>"
            )

        filas.append(f"<tr><th>{a}</th>{''.join(celdas)}</tr>")

    if resaltado is not None:
        i, j = resaltado
        pie = (
            f"Más oscuro = más probable (% de cada marcador). Resaltado: {i} - {j} "
            f"({caja[i, j] * 100:.2f} %), el marcador más probable."
        )
    else:
        pie = (
            f"El marcador más probable ({marcador['local']} - {marcador['visitante']}) "
            "queda fuera de esta matriz de 0 a 5 goles."
        )

    return (
        "<div class='lpf-mapa-caja'>"
        f"<div class='lpf-mapa__eje'><span style='border-bottom-color:{c_visita}'>"
        f"Goles de {texto_seguro(visitante)}</span></div>"
        "<div class='lpf-mapa__fila'>"
        f"<div class='lpf-mapa__v' style='border-right-color:{c_local}'>"
        f"Goles de {texto_seguro(local)}</div>"
        f"<table class='lpf-mapa'><thead><tr>{cabecera}</tr></thead>"
        f"<tbody>{''.join(filas)}</tbody></table></div>"
        f"<p class='lpf-mapa-pie'>{texto_seguro(pie)} "
        f"La matriz cubre {caja.sum() * 100:.1f} % de la probabilidad.</p>"
        "</div>"
    )


def poisson_panel_html(resultado, local, visitante):
    """Goles esperados, marcadores más probables y matriz de Poisson."""

    goles = resultado["goles"]
    c_local, c_visita, _ = tc.colores_partido(local, visitante)

    top = "".join(
        "<li>"
        f"<span>{m['local']} - {m['visitante']}</span>"
        f"<b>{porcentaje(m['probabilidad'], 2)}</b></li>"
        for m in resultado["top_marcadores"]
    )

    return (
        "<section class='lpf-poisson'>"
        f"<div>{score_matrix_html(resultado, local, visitante)}</div>"
        "<div>"
        "<div class='lpf-xg3'>"
        f"<div style='--c:{c_local}'><small>{texto_seguro(local)}</small>"
        f"<b>{numero(goles['lambda_local'])}</b></div>"
        f"<div style='--c:{c_visita}'><small>{texto_seguro(visitante)}</small>"
        f"<b>{numero(goles['lambda_visitante'])}</b></div>"
        "</div>"
        "<p class='lpf-nota-pie'>Goles esperados por equipo</p>"
        "<h3 class='lpf-subseccion'>Marcadores más probables</h3>"
        f"<ul class='lpf-top'>{top}</ul>"
        "</div>"
        "</section>"
    )


# ============================================================
# HISTORIAL
# ============================================================

def history_cards_html(registros):
    """Lista de análisis guardados: una fila por registro."""

    filas = []

    for registro in registros:
        pick = registro.get("resultado_predicho", "")
        etiqueta = RESULTADO_LABELS.get(pick, pick)
        marcador = (
            f"{registro.get('marcador_local', '-')}"
            " - "
            f"{registro.get('marcador_visitante', '-')}"
        )
        local = registro.get("equipo_local", "")
        visitante = registro.get("equipo_visitante", "")
        c_local, c_visita, _ = tc.colores_partido(local, visitante)

        filas.append(
            f"<article class='lpf-hist' style='--c1:{c_local};--c2:{c_visita}'>"
            "<div class='lpf-hist__linea'>"
            "<div class='lpf-hist__cuando'>"
            f"<b>{texto_seguro(formatear_fecha(registro.get('fecha_partido')))}</b>"
            f"<span>{texto_seguro(etiqueta_temporada(registro.get('temporada')))}</span></div>"
            "<div class='lpf-hist__partido'>"
            f"<span class='lpf-hist__eq' title='{texto_seguro(local)}'>"
            f"{team_crest_html(local)}{texto_seguro(nombre_corto(local))}</span>"
            "<em>vs</em>"
            f"<span class='lpf-hist__eq' title='{texto_seguro(visitante)}'>"
            f"{team_crest_html(visitante)}{texto_seguro(nombre_corto(visitante))}</span></div>"
            "<div class='lpf-hist__dato'><small>Pronóstico</small>"
            f"<b>{texto_seguro(etiqueta)}</b></div>"
            "<div class='lpf-hist__dato'><small>Marcador Poisson</small>"
            f"<b>{texto_seguro(marcador)}</b></div>"
            "<div class='lpf-hist__dato lpf-hist__dato--fin'>"
            f"<small>Analizado {texto_seguro(formatear_fecha_hora(registro.get('fecha_consulta')))}</small>"
            f"<b>{porcentaje(float(registro.get('prob_marcador') or 0.0), 2)}</b></div>"
            "</div></article>"
        )

    return f"<div class='lpf-duelos'>{''.join(filas)}</div>"


# ============================================================
# ESTADOS: VACÍO, ERROR, CARGA
# ============================================================

def empty_state(titulo, mensaje, icono="∅"):
    mostrar(
        "<div class='lpf-state'>"
        f"<div class='lpf-state__icon'>{texto_seguro(icono)}</div>"
        f"<h3 class='lpf-state__title'>{texto_seguro(titulo)}</h3>"
        f"<p class='lpf-state__text'>{texto_seguro(mensaje)}</p>"
        "</div>"
    )


def error_state(titulo, mensaje, detalle=""):
    mostrar(
        "<div class='lpf-state lpf-state--error' role='alert'>"
        "<div class='lpf-state__icon'>!</div>"
        f"<h3 class='lpf-state__title'>{texto_seguro(titulo)}</h3>"
        f"<p class='lpf-state__text'>{texto_seguro(mensaje)}</p>"
        + (
            f"<div class='lpf-state__detail'>{texto_seguro(detalle)}</div>"
            if detalle
            else ""
        )
        + "</div>"
    )


def skeleton_html(cantidad=6):
    return (
        "<div class='lpf-skeleton' aria-busy='true' aria-label='Cargando'>"
        + "<div class='lpf-skeleton__fila'></div>" * cantidad
        + "</div>"
    )


# ============================================================
# TABLAS GENÉRICAS, FICHA TÉCNICA Y GRÁFICO POR FOLD (Modelos)
# ============================================================

def data_table_html(encabezados, filas, destacar=None):
    """Tabla simple. filas: listas de textos ya formateados; destacar: índice
    de la fila resaltada."""

    cabecera = "".join(
        f"<th class='{'e' if i == 0 else ''}'>{texto_seguro(t)}</th>"
        for i, t in enumerate(encabezados)
    )

    cuerpo = []

    for n, fila in enumerate(filas):
        celdas = "".join(
            f"<td class='{'e' if i == 0 else ''}'>{texto_seguro(valor)}</td>"
            for i, valor in enumerate(fila)
        )
        estilo = " class='is-destacada'" if n == destacar else ""
        cuerpo.append(f"<tr{estilo}>{celdas}</tr>")

    return (
        "<div class='lpf-tabla-wrap'><table class='lpf-tabla lpf-tabla--datos'>"
        f"<thead><tr>{cabecera}</tr></thead>"
        f"<tbody>{''.join(cuerpo)}</tbody></table></div>"
    )


def spec_sheet_html(filas):
    """Ficha técnica compacta. filas: iterable de (etiqueta, texto)."""

    return (
        "<dl class='lpf-ficha'>"
        + "".join(
            f"<div><dt>{texto_seguro(etiqueta)}</dt><dd>{texto_seguro(texto)}</dd></div>"
            for etiqueta, texto in filas
        )
        + "</dl>"
    )


_FUENTES_DIR = Path(__file__).resolve().parents[1] / "static" / "fonts"


@lru_cache(maxsize=1)
def _fuentes_svg():
    """@font-face (data-URI) de Barlow para el SVG del gráfico: dentro de una
    imagen SVG no se heredan las fuentes de la página."""

    caras = []

    for archivo, peso in (("Barlow-500.woff2", 500), ("Barlow-700.woff2", 700)):
        ruta = _FUENTES_DIR / archivo

        if ruta.exists():
            datos = base64.b64encode(ruta.read_bytes()).decode("ascii")
            caras.append(
                "@font-face{font-family:'Barlow';font-weight:%d;"
                "src:url(data:font/woff2;base64,%s) format('woff2');}" % (peso, datos)
            )

    return "".join(caras)


def fold_chart_html(folds, modelo_app="XGBoost"):
    """Gráfico de líneas: accuracy por fold de cada modelo frente al baseline.

    folds: lista de dicts {anio, baseline_accuracy, modelos: {nombre: accuracy}}
    (de data/processed/metricas_validacion.json). SVG en línea, sin librerías.
    """

    if not folds:
        return ""

    nombres = list(folds[0]["modelos"])
    anios = [f["anio"] for f in folds]

    valores = [f["baseline_accuracy"] for f in folds] + [
        v for f in folds for v in f["modelos"].values()
    ]
    minimo = np.floor((min(valores) - 0.015) * 40) / 40
    maximo = np.ceil((max(valores) + 0.015) * 40) / 40

    ancho, alto = 640, 340
    izq, der, sup, inf = 58, 168, 40, 44
    area_w, area_h = ancho - izq - der, alto - sup - inf

    def x(i):
        return izq + (area_w * i / max(len(anios) - 1, 1))

    def y(v):
        return sup + area_h * (1 - (v - minimo) / (maximo - minimo))

    estilos = {
        modelo_app: ("#00875A", 4, ""),
        "Random Forest": ("#17181A", 2.4, ""),
        "Regresión Logística": ("#8A8F96", 2.4, ""),
    }

    partes = [
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {ancho} {alto}' "
        f"width='{ancho}' height='{alto}'>"
        "<style>"
        f"{_fuentes_svg()}"
        "text{font-family:'Barlow','Segoe UI',sans-serif}"
        ".g{stroke:#E4DED2;stroke-width:1}"
        ".base{fill:none;stroke:#57534B;stroke-width:2;stroke-dasharray:6 5}"
        ".t{font-size:17px;fill:#6A665D}"
        ".n{font-size:18px}"
        "</style>"
    ]

    paso = 0.025
    nivel = np.ceil(minimo / paso) * paso
    while nivel <= maximo + 1e-9:
        py = y(nivel)
        partes.append(
            f"<line x1='{izq}' x2='{ancho - der}' y1='{py:.1f}' y2='{py:.1f}' class='g'/>"
            f"<text x='{izq - 8}' y='{py + 5:.1f}' text-anchor='end' class='t'>"
            f"{nivel * 100:.1f}</text>"
        )
        nivel += paso

    for i, anio in enumerate(anios):
        partes.append(
            f"<text x='{x(i):.1f}' y='{alto - 14}' text-anchor='middle' class='t'>{anio}</text>"
        )

    # Baseline (discontinuo)
    puntos = " ".join(f"{x(i):.1f},{y(f['baseline_accuracy']):.1f}" for i, f in enumerate(folds))
    partes.append(f"<polyline points='{puntos}' class='base'/>")

    etiquetas = [("Baseline", folds[-1]["baseline_accuracy"], "#57534B")]

    otros = [n for n in nombres if n != modelo_app]
    for nombre in otros + [modelo_app]:
        color, grosor, _ = estilos.get(nombre, ("#8A8F96", 2.4, ""))
        puntos = " ".join(
            f"{x(i):.1f},{y(f['modelos'][nombre]):.1f}" for i, f in enumerate(folds)
        )
        partes.append(
            f"<polyline points='{puntos}' fill='none' stroke='{color}' "
            f"stroke-width='{grosor}' stroke-linejoin='round' stroke-linecap='round'/>"
        )

        for i, f in enumerate(folds):
            partes.append(
                f"<circle cx='{x(i):.1f}' cy='{y(f['modelos'][nombre]):.1f}' "
                f"r='{4.5 if nombre == modelo_app else 3.5}' fill='{color}'>"
                f"<title>{texto_seguro(nombre)} {f['anio']}: {f['modelos'][nombre] * 100:.1f} %</title></circle>"
            )

        etiquetas.append((nombre, folds[-1]["modelos"][nombre], color))

    # Etiquetas directas al final de cada línea (separadas para no solaparse)
    etiquetas.sort(key=lambda e: y(e[1]))
    previo = -1e9
    for nombre, valor, color in etiquetas:
        py = max(y(valor), previo + 19)
        previo = py
        peso = 700 if nombre == modelo_app else 500
        sufijo = " (la app)" if nombre == modelo_app else ""
        partes.append(
            f"<text x='{ancho - der + 12}' y='{py + 5:.1f}' fill='{color}' "
            f"font-weight='{peso}' class='n'>{texto_seguro(nombre)}{sufijo}</text>"
        )

    partes.append(
        f"<text x='{izq - 44}' y='20' class='t'>Accuracy (%)</text></svg>"
    )

    svg = "".join(partes)
    datos = base64.b64encode(svg.encode("utf-8")).decode("ascii")

    resumen = "; ".join(
        f"{f['anio']}: " + ", ".join(
            f"{n} {v * 100:.1f} %" for n, v in f["modelos"].items()
        ) + f", baseline {f['baseline_accuracy'] * 100:.1f} %"
        for f in folds
    )

    return (
        "<div class='lpf-fold-caja'>"
        "<img class='lpf-fold' "
        f"alt='Accuracy por fold de la validación cruzada frente al baseline. {texto_seguro(resumen)}' "
        f"src='data:image/svg+xml;base64,{datos}'></div>"
    )
