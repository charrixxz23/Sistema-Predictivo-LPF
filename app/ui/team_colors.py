"""Colores de los clubes SOLO para la presentación (no interviene en los modelos).

Primario y secundario salen de los píxeles reales de cada escudo en app/assets/logos
(k-means en Lab) y fueron curados y aprobados a mano: el blanco no se usa como
secundario porque no se vería sobre el fondo papel.

Reglas de visualización de un partido:
1. Si los primarios de local y visitante se parecen (ΔE < 20, CIE76), el visitante
   usa su secundario; si aun así se parecen, el visitante lleva patrón rayado.
2. En la barra 1X2, el color de un club tampoco puede parecerse al gris del empate
   (ΔE < 20): en ese caso su segmento lleva patrón rayado.
3. El texto sobre el color de un club debe cumplir contraste AA (4,5:1); si ninguna
   tinta lo cumple, el texto va fuera del color.
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
UMBRAL_DE = 20.0
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
    """Diferencia de color CIE76 entre dos colores #RRGGBB."""
    return math.dist(_lab(a), _lab(b))


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


def parecido_al_empate(color):
    return delta_e(color, GRIS_EMPATE) < UMBRAL_DE


def colores_partido(local, visitante):
    """(color_local, color_visitante, rayado) según la regla 1."""
    cl = colores_club(local)["primario"]
    cv = colores_club(visitante)["primario"]

    if delta_e(cl, cv) >= UMBRAL_DE:
        return cl, cv, False

    cv2 = colores_club(visitante)["secundario"]

    if delta_e(cl, cv2) >= UMBRAL_DE:
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
