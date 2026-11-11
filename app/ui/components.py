"""Componentes reutilizables de la interfaz.

Cada función ``*_html`` devuelve marcado HTML (con el texto ya escapado) y
cada función sin sufijo lo dibuja con ``st.html``. Las clases CSS viven en
ui/styles.py; aquí no hay estilos.
"""

import base64
from datetime import date, datetime
from functools import lru_cache
from html import escape
from io import BytesIO
from urllib.parse import urlencode

import streamlit as st
from PIL import Image

from services.team_assets import obtener_abreviatura, obtener_logo_path


# ============================================================
# CONSTANTES DE PRESENTACIÓN
# ============================================================

NOMBRE_APP = "Pronóstico LPF"

AVISO_PIE = (
    "Proyecto académico, Universidad Tecnológica de Panamá. "
    "No está afiliado a la Liga Panameña de Fútbol."
)

RESULTADO_LABELS = {
    "L": "Victoria local",
    "E": "Empate",
    "V": "Victoria visitante",
}

RESULTADO_ROLES = {
    "L": "LOCAL",
    "E": "EMPATE",
    "V": "VISITANTE",
}

# Nombres cortos SOLO para la presentación (tarjetas, tablas compactas).
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


# ============================================================
# FORMATO
# ============================================================

def nombre_corto(equipo):
    return NOMBRES_CORTOS.get(equipo, equipo)


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

@lru_cache(maxsize=None)
def _miniatura_base64(ruta, lado=96):
    """Escudo reducido como data-URI (evita incrustar PNG de 200 KB)."""

    with Image.open(ruta) as imagen:
        imagen = imagen.convert("RGBA")
        imagen.thumbnail((lado, lado))
        # Paleta reducida: ~4x menos bytes por escudo, indistinguible a 28-96 px.
        imagen = imagen.quantize(colors=192, method=Image.Quantize.FASTOCTREE)
        buffer = BytesIO()
        imagen.save(buffer, format="PNG", optimize=True)

    return base64.b64encode(buffer.getvalue()).decode("ascii")


def team_crest_html(equipo, tamano="md"):
    """Escudo local del equipo o, si no existe, sus iniciales."""

    ruta = obtener_logo_path(equipo)

    if ruta is not None:
        try:
            datos = _miniatura_base64(str(ruta))
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
# MARCA, ENCABEZADO, SECCIONES, CHIPS, PIE
# ============================================================

def chip_html(texto, tono=""):
    """tono: '' | 'brand' | 'hit' | 'miss' | 'pending'."""

    clase = f" lpf-chip--{tono}" if tono else ""

    return f"<span class='lpf-chip{clase}'>{texto_seguro(texto)}</span>"


def brand_bar(db_disponible=True):
    """Franja de marca bajo la navegación superior."""

    aviso = (
        ""
        if db_disponible
        else "<div class='lpf-brand__status'>"
        + chip_html("Historial no disponible", "miss")
        + "</div>"
    )

    mostrar(
        "<div class='lpf-brand'>"
        f"<span class='lpf-brand__name'>Pronóstico <b>LPF</b></span>"
        "<span class='lpf-brand__tag'>Predicción de partidos del fútbol panameño</span>"
        f"{aviso}"
        "</div>"
    )


def footer():
    mostrar(f"<footer class='lpf-footer'>{texto_seguro(AVISO_PIE)}</footer>")


def page_header_html(titulo, subtitulo="", chips=()):
    chips_html = "".join(chip_html(t, tono) for t, tono in chips)

    return (
        "<header class='lpf-header'>"
        "<div>"
        f"<h1 class='lpf-header__title'>{texto_seguro(titulo)}</h1>"
        + (
            f"<p class='lpf-header__subtitle'>{texto_seguro(subtitulo)}</p>"
            if subtitulo
            else ""
        )
        + "</div>"
        + (f"<div class='lpf-header__chips'>{chips_html}</div>" if chips_html else "")
        + "</header>"
    )


def page_header(titulo, subtitulo="", chips=()):
    mostrar(page_header_html(titulo, subtitulo, chips))


def note_html(titulo, texto=""):
    return (
        "<aside class='lpf-note' role='note'>"
        f"<strong>{texto_seguro(titulo)}</strong>"
        + (f"<span>{texto_seguro(texto)}</span>" if texto else "")
        + "</aside>"
    )


def note(titulo, texto=""):
    mostrar(note_html(titulo, texto))


def section_title(titulo, pista=""):
    mostrar(
        "<div class='lpf-section'>"
        f"<h2 class='lpf-section__title'>{texto_seguro(titulo)}</h2>"
        f"<span class='lpf-section__hint'>{texto_seguro(pista)}</span>"
        "</div>"
    )


def day_heading(valor):
    mostrar(
        "<div class='lpf-day'>"
        f"<span class='lpf-day__date'>{texto_seguro(fecha_larga(valor))}</span>"
        "</div>"
    )


# ============================================================
# TARJETA DE MÉTRICA
# ============================================================

def metric_card_html(etiqueta, valor, pista="", tono=""):
    clase = f" lpf-metric--{tono}" if tono else ""

    return (
        f"<article class='lpf-metric{clase}'>"
        f"<div class='lpf-metric__label'>{texto_seguro(etiqueta)}</div>"
        f"<div class='lpf-metric__value'>{texto_seguro(valor)}</div>"
        + (
            f"<div class='lpf-metric__hint'>{texto_seguro(pista)}</div>"
            if pista
            else ""
        )
        + "</article>"
    )


def metric_row(metricas):
    """metricas: iterable de (etiqueta, valor, pista, tono)."""

    mostrar(
        "<div class='lpf-metrics'>"
        + "".join(metric_card_html(*m) for m in metricas)
        + "</div>"
    )


# ============================================================
# PREDICCIÓN: PIEZAS COMPARTIDAS
# ============================================================

def _etiqueta_pronostico(codigo, local, visitante):
    if codigo == "L":
        return f"Gana {nombre_corto(local)}"

    if codigo == "V":
        return f"Gana {nombre_corto(visitante)}"

    return "Empate"


def _barra_probabilidades_html(probabilidades):
    total = sum(probabilidades.get(c, 0.0) for c in "LEV") or 1.0

    return (
        "<div class='lpf-bar' role='img' aria-label='Probabilidades 1X2'>"
        + "".join(
            f"<span class='lpf-bar__seg lpf-bar__seg--{c}' "
            f"style='width:{probabilidades.get(c, 0.0) / total * 100:.2f}%'></span>"
            for c in "LEV"
        )
        + "</div>"
    )


def _cuotas_html(probabilidades, pronostico):
    nombres = {"L": "1 · Local", "E": "X · Empate", "V": "2 · Visitante"}

    return (
        "<div class='lpf-odds'>"
        + "".join(
            f"<div class='lpf-odd lpf-odd--{c}{' is-pick' if c == pronostico else ''}'>"
            f"<strong>{porcentaje(probabilidades.get(c, 0.0), 0)}</strong>"
            f"<span>{nombres[c]}</span></div>"
            for c in "LEV"
        )
        + "</div>"
    )


def _resultado_real(goles_local, goles_visitante):
    if goles_local > goles_visitante:
        return "L"

    if goles_local < goles_visitante:
        return "V"

    return "E"


# ============================================================
# TARJETA DE PARTIDO (CALENDARIO)
# ============================================================

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
    """Tarjeta compacta de un partido.

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

    if finalizado:
        gl = int(partido["goles_local"])
        gv = int(partido["goles_visitante"])
        centro = (
            f"<div class='lpf-match__score'>{gl} - {gv}</div>"
            "<div class='lpf-match__tag'>Final</div>"
        )
        chip_estado = chip_html("Finalizado")
    else:
        centro = (
            f"<div class='lpf-match__time'>{texto_seguro(partido['hora'])}</div>"
            "<div class='lpf-match__tag'>Hora de Panamá</div>"
        )
        chip_estado = chip_html("Pendiente", "pending")

    estadio = partido.get("estadio") or "Estadio por confirmar"

    html = (
        "<article class='lpf-match'>"
        "<div class='lpf-match__meta'>"
        f"<span class='lpf-match__venue'>{texto_seguro(estadio)}</span>"
        f"{chip_estado}"
        "</div>"
        "<div class='lpf-match__teams'>"
        f"<div class='lpf-team' title='{texto_seguro(local)}'>"
        f"{team_crest_html(local, 'sm')}"
        f"<span class='lpf-team__name'>{texto_seguro(nombre_corto(local))}</span></div>"
        f"<div class='lpf-match__center'>{centro}</div>"
        f"<div class='lpf-team lpf-team--away' title='{texto_seguro(visitante)}'>"
        f"{team_crest_html(visitante, 'sm')}"
        f"<span class='lpf-team__name'>{texto_seguro(nombre_corto(visitante))}</span></div>"
        "</div>"
    )

    if prediccion:
        probs = prediccion["probabilidades"]
        pick = prediccion["resultado"]
        marcador = prediccion["marcador"]

        acierto = ""
        if finalizado and fecha_corte is not None:
            if partido["fecha"] <= fecha_corte:
                acierto = chip_html("Dentro del período de entrenamiento")
            elif _resultado_real(gl, gv) == pick:
                acierto = chip_html("Acertó 1X2", "hit")
            else:
                acierto = chip_html("No acertó 1X2", "miss")

        enlace = analyze_href(local, visitante, partido["fecha"], temporada)

        html += (
            "<div class='lpf-pred'>"
            f"{_barra_probabilidades_html(probs)}"
            f"{_cuotas_html(probs, pick)}"
            "<div class='lpf-pred__foot'>"
            "<span>Marcador probable "
            f"<strong>{marcador['local']} - {marcador['visitante']}</strong> "
            f"({porcentaje(prediccion['prob_marcador'], 1)})</span>"
            f"{acierto}"
            "</div>"
            "<div class='lpf-pred__foot'>"
            f"<span class='lpf-pred__pick'>{texto_seguro(_etiqueta_pronostico(pick, local, visitante))}</span>"
            f"<a class='lpf-link' target='_self' href='{escape(enlace)}'>"
            "Analizar a fondo →</a>"
            "</div>"
            "</div>"
        )

    return html + "</article>"


def match_grid(tarjetas):
    mostrar(f"<div class='lpf-matches'>{''.join(tarjetas)}</div>")


# ============================================================
# TABLA DE CLASIFICACIÓN
# ============================================================

def standings_table_html(tabla, corto=False, compacta=False):
    encabezados = [
        ("#", ""), ("Equipo", "is-team"), ("PJ", ""), ("G", "hide-sm"),
        ("E", "hide-sm"), ("P", "hide-sm"), ("GF", "hide-sm"),
        ("GC", "hide-sm"), ("DG", ""), ("Pts", ""), ("Forma", "hide-sm"),
    ]

    cabecera = "".join(
        f"<th class='{clase}'>{texto}</th>" for texto, clase in encabezados
    )

    filas = []

    for fila in tabla.itertuples(index=False):
        primero = " lpf-pos--first" if fila.pos == 1 else ""
        forma = "".join(f"<span class='{r}'>{r}</span>" for r in fila.forma)
        dg = f"+{fila.dg}" if fila.dg > 0 else str(fila.dg)
        nombre = nombre_corto(fila.equipo) if corto else fila.equipo

        filas.append(
            "<tr>"
            f"<td><span class='lpf-pos{primero}'>{fila.pos}</span></td>"
            "<td class='is-team'>"
            f"<div class='lpf-team-cell' title='{texto_seguro(fila.equipo)}'>"
            f"{team_crest_html(fila.equipo, 'sm')}"
            f"<span>{texto_seguro(nombre)}</span></div></td>"
            f"<td>{fila.pj}</td>"
            f"<td class='hide-sm'>{fila.g}</td>"
            f"<td class='hide-sm'>{fila.e}</td>"
            f"<td class='hide-sm'>{fila.p}</td>"
            f"<td class='hide-sm'>{fila.gf}</td>"
            f"<td class='hide-sm'>{fila.gc}</td>"
            f"<td>{dg}</td>"
            f"<td class='is-pts'>{fila.pts}</td>"
            f"<td class='hide-sm'><span class='lpf-form'>{forma}</span></td>"
            "</tr>"
        )

    clase = " lpf-table--compact" if compacta else ""

    return (
        f"<div class='lpf-table-wrap'><table class='lpf-table{clase}'>"
        f"<thead><tr>{cabecera}</tr></thead>"
        f"<tbody>{''.join(filas)}</tbody></table></div>"
    )


def standings_table(tabla, corto=False, compacta=False):
    mostrar(standings_table_html(tabla, corto, compacta))


# ============================================================
# PREDICCIÓN DE PARTIDO
# ============================================================

def versus_html(local, visitante, temporada, fecha):
    def equipo(nombre, rol):
        return (
            "<div class='lpf-versus__team'>"
            f"<span class='lpf-versus__role'>{rol}</span>"
            f"{team_crest_html(nombre, 'lg')}"
            f"<span class='lpf-versus__name'>{texto_seguro(nombre)}</span>"
            f"<span class='lpf-versus__code'>"
            f"{texto_seguro(obtener_abreviatura(nombre))}</span>"
            "</div>"
        )

    return (
        "<section class='lpf-versus'>"
        "<div class='lpf-versus__meta'>"
        f"{chip_html('Temporada ' + str(temporada))}"
        f"{chip_html(fecha.strftime('%d/%m/%Y'))}"
        "</div>"
        "<div class='lpf-versus__teams'>"
        f"{equipo(local, 'LOCAL')}"
        "<div class='lpf-versus__vs'>VS</div>"
        f"{equipo(visitante, 'VISITANTE')}"
        "</div>"
        "</section>"
    )


def prediction_panel_html(resultado, local, visitante):
    xgb = resultado["xgboost"]
    probabilidades = xgb["probabilidades"]
    pick = xgb["resultado"]

    nombres = {"L": local, "E": "Empate", "V": visitante}

    tarjetas = []

    for codigo in ("L", "E", "V"):
        probabilidad = probabilidades.get(codigo, 0.0)
        barra = max(0.0, min(probabilidad * 100, 100.0))
        activo = " is-pick" if codigo == pick else ""

        tarjetas.append(
            f"<article class='lpf-prob lpf-prob--{codigo}{activo}'>"
            f"<span class='lpf-prob__role'>{RESULTADO_ROLES[codigo]}</span>"
            f"<strong class='lpf-prob__name'>{texto_seguro(nombres[codigo])}</strong>"
            f"<div class='lpf-prob__value'>{porcentaje(probabilidad)}</div>"
            "<div class='lpf-prob__track'>"
            f"<span class='lpf-prob__fill' style='width:{barra:.2f}%'></span></div>"
            f"<small>{RESULTADO_LABELS[codigo]}</small>"
            "</article>"
        )

    return (
        "<section class='lpf-panel'>"
        "<div class='lpf-panel__head'>"
        "<div class='lpf-panel__kicker'>Pronóstico principal · XGBoost</div>"
        "<h2 class='lpf-panel__title'>Pronóstico del partido</h2></div>"
        f"<div class='lpf-probs'>{''.join(tarjetas)}</div>"
        "<div class='lpf-pick'><span>Predicción principal</span>"
        f"<strong>{texto_seguro(RESULTADO_LABELS.get(pick, pick)).upper()}</strong>"
        "</div></section>"
    )


def poisson_panel_html(resultado, local, visitante):
    goles = resultado["goles"]
    marcador = resultado["marcador_probable"]

    top = "".join(
        "<span class='lpf-score'>"
        f"<strong>{m['local']} - {m['visitante']}</strong>"
        f"<span>{porcentaje(m['probabilidad'], 2)}</span></span>"
        for m in resultado["top_marcadores"]
    )

    return (
        "<section class='lpf-panel'>"
        "<div class='lpf-panel__head'>"
        "<div class='lpf-panel__kicker'>Análisis de goles · Poisson</div>"
        "<h2 class='lpf-panel__title'>Goles esperados y marcadores</h2></div>"
        "<div class='lpf-xg'>"
        "<article class='lpf-xg__card'>"
        f"<span>{texto_seguro(local)}</span>"
        f"<strong>{numero(goles['lambda_local'])}</strong>"
        "<small>Goles esperados</small></article>"
        "<article class='lpf-xg__card'>"
        f"<span>{texto_seguro(visitante)}</span>"
        f"<strong>{numero(goles['lambda_visitante'])}</strong>"
        "<small>Goles esperados</small></article>"
        "<article class='lpf-xg__card lpf-xg__card--main'>"
        "<span>Marcador más probable</span>"
        f"<strong>{marcador['local']} - {marcador['visitante']}</strong>"
        f"<small>{porcentaje(marcador['probabilidad'], 2)}</small></article>"
        "</div>"
        "<div class='lpf-section__hint lpf-hint-gap'>"
        "Marcadores más probables</div>"
        f"<div class='lpf-scores'>{top}</div>"
        "</section>"
    )


# ============================================================
# HISTORIAL
# ============================================================

def history_cards_html(registros):
    tarjetas = []

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

        tarjetas.append(
            "<article class='lpf-hist'>"
            "<div class='lpf-hist__meta'>"
            f"<span>{texto_seguro(formatear_fecha(registro.get('fecha_partido')))}</span>"
            f"<span>Temporada {texto_seguro(registro.get('temporada'))}</span></div>"
            "<div class='lpf-hist__match'>"
            f"<span class='lpf-hist__team' title='{texto_seguro(local)}'>"
            f"{team_crest_html(local, 'sm')}{texto_seguro(nombre_corto(local))}</span>"
            "<em>vs</em>"
            f"<span class='lpf-hist__team' title='{texto_seguro(visitante)}'>"
            f"{team_crest_html(visitante, 'sm')}{texto_seguro(nombre_corto(visitante))}</span></div>"
            "<div class='lpf-hist__grid'>"
            f"<div><span>Pronóstico</span><strong>{texto_seguro(etiqueta)}</strong></div>"
            f"<div><span>Marcador Poisson</span><strong>{texto_seguro(marcador)}</strong></div>"
            "</div>"
            "<div class='lpf-hist__foot'>"
            f"<span>Analizado {texto_seguro(formatear_fecha_hora(registro.get('fecha_consulta')))}</span>"
            f"<span>{porcentaje(float(registro.get('prob_marcador') or 0.0), 2)}</span>"
            "</div></article>"
        )

    return f"<div class='lpf-history'>{''.join(tarjetas)}</div>"


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
        + "<div class='lpf-skeleton__card'></div>" * cantidad
        + "</div>"
    )


# ============================================================
# TABLA GENÉRICA
# ============================================================

def data_table_html(encabezados, filas, destacar=None):
    """Tabla simple. filas: listas de textos ya formateados; destacar: índice
    de fila resaltada."""

    cabecera = "".join(
        f"<th class='{'is-team' if i == 0 else ''}'>{texto_seguro(t)}</th>"
        for i, t in enumerate(encabezados)
    )

    cuerpo = []

    for n, fila in enumerate(filas):
        celdas = "".join(
            f"<td class='{'is-team' if i == 0 else ''}'>"
            f"{texto_seguro(valor)}</td>"
            for i, valor in enumerate(fila)
        )
        estilo = " class='is-highlight'" if n == destacar else ""
        cuerpo.append(f"<tr{estilo}>{celdas}</tr>")

    return (
        "<div class='lpf-table-wrap'><table class='lpf-table'>"
        f"<thead><tr>{cabecera}</tr></thead>"
        f"<tbody>{''.join(cuerpo)}</tbody></table></div>"
    )
