"""Pruebas de los colores de club: CIEDE2000, cruces y contraste.

Ejecutar desde la carpeta app:  python test_colores.py
"""

import itertools
import sys

from services.team_assets import EQUIPOS_ACTIVOS
from ui import team_colors as T
from ui.components import es_parejo, frase_pronostico

ok = True


def chk(titulo, condicion):
    global ok
    ok &= bool(condicion)
    print(("OK    " if condicion else "FALLO ") + titulo)


def de00_lab(lab1, lab2):
    """ΔE2000 entre dos colores dados directamente en CIELAB."""

    original = T._lab
    valores = iter([lab1, lab2])
    T._lab = lambda _c: next(valores)

    try:
        return T.delta_e00("#000000", "#000000")
    finally:
        T._lab = original


# Pares de referencia de Sharma, Wu y Dalal (2005), «The CIEDE2000 color-difference formula»
for lab1, lab2, esperado in [
    ((50.0, 2.6772, -79.7751), (50.0, 0.0, -82.7485), 2.0425),
    ((50.0, 3.1571, -77.2803), (50.0, 0.0, -82.7485), 2.8615),
    ((50.0, 2.5, 0.0), (50.0, 0.0, -2.5), 4.3065),
    ((60.2574, -34.0099, 36.2677), (60.4626, -34.1751, 39.4387), 1.2644),
    ((2.0776, 0.0795, -1.1350), (0.9033, -0.0636, -0.5514), 0.9082),
]:
    chk(f"CIEDE2000 = {esperado} (par de Sharma {lab1[:2]})", abs(de00_lab(lab1, lab2) - esperado) < 1e-3)

chk("Simetría y color idéntico: ΔE2000(a, a) = 0", T.delta_e00("#17304F", "#17304F") < 1e-9)

# El caso que CIE76 no detectaba
chk("Plaza Amador y Veraguas (azules oscuros): CIE76 los daba distintos, CIEDE2000 los marca parecidos",
    T.delta_e("#17304F", "#021F65") > 20 and T.se_parecen("#17304F", "#021F65"))

# Ningún cruce deja dos primarios parecidos en la barra sin remedio (secundario o rayado)
parecidos = 0
for a, b in itertools.permutations(EQUIPOS_ACTIVOS, 2):
    (cl, _), (cv, rv) = T.colores_barra(a, b)

    if T.se_parecen(cl, cv) and not rv:
        parecidos += 1

chk("Los 132 cruces: ninguno muestra dos colores parecidos sin rayado", parecidos == 0)

(_, _), (cv, rv) = T.colores_barra("Plaza Amador", "Veraguas")
chk("Plaza Amador vs Veraguas: el visitante cambia a su color secundario", cv == T.TEAM_COLORS["Veraguas"]["secundario"] and not rv)

# Gris del empate
chk("Los secundarios grises (Tauro, CAI, Unión Coclé) se parecen al gris del empate",
    all(T.parecido_al_empate(T.TEAM_COLORS[e]["secundario"]) for e in ("Tauro", "CA Independiente de La Chorrera", "Unión Coclé")))
chk("Celeste de UMECIT (cromático) no se confunde con el gris del empate", not T.parecido_al_empate(T.TEAM_COLORS["UMECIT"]["primario"]))

# Contraste AA de las letras de la forma (G blanco sobre verde, E oscuro sobre gris, P blanco sobre rojo)
for fondo, tinta, nombre in [("#1B7A4B", "#FFFFFF", "G"), ("#8A8F96", "#17181A", "E"), ("#B3211F", "#FFFFFF", "P")]:
    chk(f"Forma {nombre}: contraste {T.contraste(fondo, tinta):.1f}:1 (AA = 4,5)", T.contraste(fondo, tinta) >= 4.5)

# Pronóstico: lenguaje prudente
chk("Partido parejo: 36/32/32 difieren menos de 5 puntos", es_parejo({"L": .32, "E": .32, "V": .36}))
chk("No parejo: 48/27/25", not es_parejo({"L": .48, "E": .27, "V": .25}))
chk("Frase: «Más probable: victoria de Plaza Amador (48 %)»",
    frase_pronostico({"L": .48, "E": .27, "V": .25}, "Plaza Amador", "Veraguas") == "Más probable: victoria de Plaza Amador (48 %)")
chk("Frase: empate más probable",
    frase_pronostico({"L": .30, "E": .45, "V": .25}, "Alianza", "Tauro") == "Más probable: empate (45 %)")
chk("Frase: «Partido parejo» cuando los dos primeros difieren menos de 5 puntos",
    frase_pronostico({"L": .36, "E": .32, "V": .32}, "San Francisco FC", "Árabe Unido") == "Partido parejo")

print("RESULTADO:", "OK" if ok else "FALLO")
sys.exit(0 if ok else 1)
