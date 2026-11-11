"""Colores de los clubes SOLO para la presentación (no interviene en los modelos).

Primario y secundario salen de los píxeles reales de cada escudo en app/assets/logos
(k-means en Lab) y fueron curados y aprobados a mano: el blanco no se usa como
secundario porque no se vería sobre el fondo papel.

Reglas de visualización de un partido:
1. Si los primarios de local y visitante se parecen (ΔE2000 < UMBRAL_DE00), el
   visitante usa su secundario; si aun así se parecen, el visitante lleva patrón
   rayado.
2. En la barra 1X2, el color de un club tampoco puede parecerse al gris del empate:
   en ese caso su segmento lleva patrón rayado.
3. El texto sobre el color de un club debe cumplir contraste AA (4,5:1); si ninguna
   tinta lo cumple, el texto va fuera del color.

La diferencia de color es CIEDE2000. CIE76 sobreestimaba la distancia entre azules
oscuros (Plaza Amador y Veraguas: ΔE76 = 29,5 frente a ΔE2000 = 8,1) y no detectaba
que se vieran casi iguales.
"""

import math

TEAM_COLORS = {
    "Alianza":                         {"primario": "#139A4C", "secundario": "#1A1A1A"},
    "CA Independiente de La Chorrera": {"primario": "#1A1A1A", "secundario": "#A5A7AB"},
    "Herrera":                         {"primario": "#FEE31D", "secundario": "#1243BB"},
    "Plaza Amador":                    {"primario": "#17304F", "secundario": "#F9B326"},
    "San Francisco FC":                {"primario": "#EB1A24", "secundario": "#1A1A1A"},
    "Sporting San Miguelito":          {"primario": "#C21D24", "secundario": "#221E20"},
    "Tauro":                           {"primario": "#1A1A1A", "secundario": "#838383"},
    "UMECIT":                          {"primario": "#07A4D6", "secundario": "#1B4168"},
    "Universitario":                   {"primario": "#0246B8", "secundario": "#CD9918"},
    "Unión Coclé":                     {"primario": "#E81819", "secundario": "#5F5F5F"},
    "Veraguas":                        {"primario": "#021F65", "secundario": "#48CBE0"},
    "Árabe Unido":                     {"primario": "#020193", "secundario": "#1A1A1A"},
}

# Color de un equipo desconocido (neutro)
NEUTRO = {"primario": "#7C8793", "secundario": "#B5BCC4"}

GRIS_EMPATE = "#8A8F96"

# Umbrales (CIEDE2000). Dos colores con ΔE2000 menor que UMBRAL_DE00 se confunden
# como segmentos contiguos de una barra delgada. Para el gris del empate hay una
# segunda condición: un color casi sin croma (neutro) se confunde con él hasta
# UMBRAL_GRIS_NEUTRO, porque solo difiere en luminosidad; uno cromático (el celeste
# de UMECIT, ΔE2000 = 19,9) no.
UMBRAL_DE00 = 12.0
UMBRAL_GRIS_NEUTRO = 25.0
CROMA_NEUTRO = 12.0

TINTA_CLARA, TINTA_OSCURA = "#FFFFFF", "#141517"


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _rgb(hex_):
    hex_ = hex_.lstrip("#")
    return tuple(int(hex_[i:i + 2], 16) for i in (0, 2, 4))


def luminancia(hex_):
    r, g, b = map(_lin, _rgb(hex_))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = luminancia(a), luminancia(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _lab(hex_):
    r, g, b = map(_lin, _rgb(hex_))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def delta_e(a, b):
    """Diferencia de color CIE76 entre dos colores #RRGGBB (solo referencia)."""
    return math.dist(_lab(a), _lab(b))


def delta_e00(a, b):
    """Diferencia de color CIEDE2000 (Sharma, Wu y Dalal, 2005) entre dos #RRGGBB."""

    l1, a1, b1 = _lab(a)
    l2, a2, b2 = _lab(b)

    c1, c2 = math.hypot(a1, b1), math.hypot(a2, b2)
    cm = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt(cm ** 7 / (cm ** 7 + 25 ** 7)))

    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360

    dl, dc = l2 - l1, c2p - c1p

    if c1p * c2p == 0:
        dh = 0.0
    else:
        d = h2p - h1p
        dh = d if abs(d) <= 180 else d - 360 * (1 if d > 0 else -1)

    dhh = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dh / 2))

    lm, cmp_ = (l1 + l2) / 2, (c1p + c2p) / 2

    if c1p * c2p == 0:
        hm = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hm = (h1p + h2p) / 2
    else:
        hm = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2

    t = (
        1
        - 0.17 * math.cos(math.radians(hm - 30))
        + 0.24 * math.cos(math.radians(2 * hm))
        + 0.32 * math.cos(math.radians(3 * hm + 6))
        - 0.20 * math.cos(math.radians(4 * hm - 63))
    )
    dtheta = 30 * math.exp(-(((hm - 275) / 25) ** 2))
    rc = 2 * math.sqrt(cmp_ ** 7 / (cmp_ ** 7 + 25 ** 7))
    sl = 1 + 0.015 * (lm - 50) ** 2 / math.sqrt(20 + (lm - 50) ** 2)
    sc = 1 + 0.045 * cmp_
    sh = 1 + 0.015 * cmp_ * t
    rt = -math.sin(math.radians(2 * dtheta)) * rc

    return math.sqrt(
        (dl / sl) ** 2
        + (dc / sc) ** 2
        + (dhh / sh) ** 2
        + rt * (dc / sc) * (dhh / sh)
    )


def croma(color):
    """Croma (saturación percibida) de un color #RRGGBB en CIELAB."""
    _, a, b = _lab(color)
    return math.hypot(a, b)


def mezclar(a, b, t):
    """Mezcla lineal de dos colores #RRGGBB (t=0 -> a, t=1 -> b)."""
    ra, rb = _rgb(a), _rgb(b)
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(ra, rb))


def colores_club(equipo):
    return TEAM_COLORS.get(equipo, NEUTRO)


def tinta_sobre(color):
    """(tinta, cumple_AA). Si ninguna tinta llega a 4,5:1 el texto debe ir FUERA del color."""
    mejor = max((TINTA_CLARA, TINTA_OSCURA), key=lambda t: contraste(color, t))
    return mejor, contraste(color, mejor) >= 4.5


def se_parecen(a, b):
    """True si dos colores se confunden como segmentos contiguos de una barra."""
    return delta_e00(a, b) < UMBRAL_DE00


def parecido_al_empate(color):
    d = delta_e00(color, GRIS_EMPATE)

    return d < UMBRAL_DE00 or (croma(color) < CROMA_NEUTRO and d < UMBRAL_GRIS_NEUTRO)


def colores_partido(local, visitante):
    """(color_local, color_visitante, rayado) según la regla 1."""
    cl = colores_club(local)["primario"]
    cv = colores_club(visitante)["primario"]

    if not se_parecen(cl, cv):
        return cl, cv, False

    cv2 = colores_club(visitante)["secundario"]

    if not se_parecen(cl, cv2):
        return cl, cv2, False

    return cl, cv, True


def colores_barra(local, visitante):
    """Colores y rayados de la barra 1X2: ((local, rayado), (visitante, rayado)).

    Aplica la regla 1 (pareja) y la regla 2 (parecido al gris del empate).
    """
    cl, cv, rayado_pareja = colores_partido(local, visitante)

    return (
        (cl, parecido_al_empate(cl)),
        (cv, rayado_pareja or parecido_al_empate(cv)),
    )
