"""Pruebas del desempate oficial de la clasificación (Reglamento LPF, Anexo II, art. 11).

Ejecutar desde la carpeta app:  python test_desempate.py
Cada caso es un mini-torneo sintético con un solo criterio decisivo. Los equipos del
grupo se pasan en orden alfabético inverso a propósito: así el orden alfabético
(el que se usaba antes) nunca coincide por casualidad con el resultado esperado.

El criterio 5 (puntos de juego limpio) no se prueba: los datos traen cantidad de
tarjetas pero no su tipo (amarilla, doble amarilla, roja directa), así que no
se calcula y el empate se marca como «sin resolver».
"""

import sys

import pandas as pd

from services import liga_service as L

ok = True


def chk(titulo, condicion):
    global ok
    ok &= bool(condicion)
    print(("OK    " if condicion else "FALLO ") + titulo)


def orden(partidos, equipos):
    return clasificar(partidos, equipos)["equipo"].tolist()


def clasificar(partidos, equipos):
    return L.clasificar_grupo(partidos, equipos)


# Tuplas: (local, visitante, goles_local, goles_visitante). X e Y son rivales ajenos al grupo.

# --- Puntos: primer orden de la tabla, sin desempate
t = clasificar([("B", "X", 1, 0), ("A", "Y", 0, 0)], ["B", "A"])
chk("Puntos: quien suma más va primero, sin invocar desempate", t["equipo"].tolist() == ["B", "A"] and t["desempate"].isna().all())

# --- Criterio 1: diferencia de goles
p = [("A", "X", 3, 0), ("B", "Y", 1, 0)]
t = clasificar(p, ["B", "A"])
chk("Criterio 1: diferencia de goles (A +3 antes que B +1, mismos puntos)", t["equipo"].tolist() == ["A", "B"] and t.iloc[0]["desempate"] == "diferencia de goles")

# --- Criterio 2: goles a favor (misma diferencia)
p = [("A", "X", 3, 2), ("B", "Y", 1, 0)]
t = clasificar(p, ["B", "A"])
chk("Criterio 2: goles a favor (A 3 GF antes que B 1 GF, misma diferencia +1)", t["equipo"].tolist() == ["A", "B"] and t.iloc[0]["desempate"] == "goles a favor")

# --- Criterio 3: marcadores directos entre los empatados (mismos puntos, DG y GF)
# A: gana a B 1-0 y pierde 0-1 en casa de X.  B: pierde con A y gana 1-0 a Y.  Ambos: 3 pts, GF 1, GC 1.
p = [("A", "B", 1, 0), ("X", "A", 1, 0), ("B", "Y", 1, 0)]
t = clasificar(p, ["B", "A"])
chk("Criterio 3: marcador directo (A venció a B; mismos puntos, DG y GF)", t["equipo"].tolist() == ["A", "B"] and t.iloc[0]["desempate"] == "marcadores directos entre los empatados")
tot = L._totales(p, ["A", "B"])
chk("Criterio 3: los totales de A y B sí eran idénticos (puntos, DG, GF)", all(tot["A"][k] == tot["B"][k] for k in ("pts", "dg", "gf")))

# --- Criterio 4: goles como visitante (directos igualados 1-0 y 0-1 en ida y vuelta)
# A: gana en casa a B 1-0, pierde 0-1 en casa de B, gana 1-0 en casa de X.
# B: pierde en casa de A, gana en casa a A, gana 1-0 en casa a Y. Ambos: 6 pts, GF 2, GC 1; directos iguales.
p = [("A", "B", 1, 0), ("B", "A", 1, 0), ("X", "A", 0, 1), ("B", "Y", 1, 0)]
t = clasificar(p, ["B", "A"])
tot = L._totales(p, ["A", "B"])
chk("Criterio 4: goles de visitante (A 1 frente a B 0; puntos, DG, GF y directos iguales)",
    t["equipo"].tolist() == ["A", "B"] and t.iloc[0]["desempate"] == "goles como visitante"
    and tot["A"]["gf_visita"] == 1 and tot["B"]["gf_visita"] == 0)

# --- Empate sin resolver
p = [("A", "X", 1, 0), ("B", "Y", 1, 0)]
t = clasificar(p, ["B", "A"])
chk("Sin resolver: empate total marcado, cada equipo señala al otro", t["sin_resolver"].all() and set(t.iloc[0]["empatado_con"]) | {t.iloc[0]["equipo"]} == {"A", "B"})
chk("Sin resolver: no se inventa un ganador (el orden mostrado es provisional)", len(t) == 2 and t["sin_resolver"].tolist() == [True, True])

# --- Tres empatados: cada criterio solo vuelve a aplicarse a los que siguen empatados
# A +3 se separa por DG; B y C quedan empatados en DG (+1) y se separan por GF.
p = [("A", "X", 3, 0), ("B", "Y", 2, 1), ("C", "X", 1, 0)]
t = clasificar(p, ["C", "B", "A"])
chk("Tres empatados: DG separa a A; entre B y C decide GF (B 2 frente a C 1)", t["equipo"].tolist() == ["A", "B", "C"]
    and t.iloc[0]["desempate"] == "diferencia de goles" and t.iloc[1]["desempate"] == "goles a favor")

# --- Marcadores directos entre tres empatados usan SOLO los partidos entre ellos
# Mini-liga A, B, C con ciclo de 1-0 (A>B, B>C, C>A): todo igual -> sin resolver.
p = [("A", "B", 1, 0), ("B", "C", 1, 0), ("C", "A", 1, 0)]
t = clasificar(p, ["C", "B", "A"])
chk("Ciclo A>B>C>A: ningún criterio rompe el empate de tres equipos (3 sin resolver)", t["sin_resolver"].all() and len(t) == 3)

# --- Los puntos mandan sobre cualquier criterio
p = [("A", "X", 5, 0), ("B", "Y", 1, 0), ("B", "Y", 1, 0)]
t = clasificar(p, ["A", "B"])
chk("Más puntos antes que mejor diferencia (B 6 pts frente a A 3 pts con DG +5)", t["equipo"].tolist() == ["B", "A"])

# --- Forma: letras de los últimos 5, del más antiguo al más reciente
p = [("A", "X", 1, 0), ("A", "X", 0, 0), ("A", "X", 0, 1), ("A", "X", 2, 0), ("A", "X", 0, 3), ("A", "X", 1, 0)]
chk("Forma: últimos 5 como G/E/P, del más antiguo al más reciente", clasificar(p, ["A"]).iloc[0]["forma"] == ["E", "P", "G", "P", "G"])

# --- Configuración por temporada
for temp in ("2026", "2026/2027"):
    chk(f"Config: la temporada {temp} tiene conferencias y nombre de torneo", L.tiene_conferencias(temp) and L.nombre_torneo(temp))
for temp in ("2025", "2024/2025", "2014/2015", "2019"):
    chk(f"Config: la temporada {temp} NO tiene conferencias (no se adivinan)", not L.tiene_conferencias(temp) and L.nombre_torneo(temp) is None)

chk("Nombres: «Apertura 2026 (temporada 2026/2027)» y «Clausura 2026 (temporada 2026)»",
    L.nombre_torneo("2026/2027") == "Apertura 2026 (temporada 2026/2027)" and L.nombre_torneo("2026") == "Clausura 2026 (temporada 2026)")

cfg = L.config_temporada("2026/2027")["conferencias"]
chk("Conferencias: 6 + 6 clubes sin repetir, tal como el art. 8", len(cfg["Este"]) == 6 and len(cfg["Oeste"]) == 6 and not set(cfg["Este"]) & set(cfg["Oeste"]))
chk("Conferencias: Este = Alianza, Plaza Amador, UMECIT, Sporting San Miguelito, Tauro, Árabe Unido",
    set(cfg["Este"]) == {"Alianza", "Plaza Amador", "UMECIT", "Sporting San Miguelito", "Tauro", "Árabe Unido"})
chk("Etiquetas de partido: Este / Oeste / Interconferencia",
    L.etiqueta_conferencia("Alianza", "Tauro", "2026/2027") == "Este"
    and L.etiqueta_conferencia("Herrera", "Veraguas", "2026/2027") == "Oeste"
    and L.etiqueta_conferencia("Alianza", "Herrera", "2026/2027") == "Interconferencia"
    and L.etiqueta_conferencia("Alianza", "Herrera", "2025") is None)
chk("Zonas: 1.º semifinal, 2.º y 3.º playoff, 4.º a 6.º eliminado",
    [L.zona_de_posicion(i) for i in range(1, 7)] == ["semifinal", "playoff", "playoff", "eliminado", "eliminado", "eliminado"])

# --- Fase de clasificación: excluye partidos tras los 16 por equipo
f = pd.DataFrame({
    "fecha_partido": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"]),
    "registro_id": [1, 2, 3, 4],
    "home_team_name": ["A", "A", "B", "A"], "away_team_name": ["B", "B", "A", "B"],
})
chk("Fase de clasificación: con tope de 2 partidos por equipo, el 3.º y 4.º cruce quedan fuera", len(L.fase_clasificacion(f, 2)) == 2)

# --- Datos reales
from services.feature_service import cargar_historico  # noqa: E402

h = cargar_historico()
for temp, n in (("2026", 96), ("2026/2027", 48)):
    t = L.construir_clasificacion_oficial(h, temp)
    chk(f"Real {temp}: {n} partidos en la fase de clasificación y 12 clubes", t["partidos"] == n and len(t["General"]) == 12)
    chk(f"Real {temp}: Este y Oeste con 6 clubes y el General contiene a los 12", len(t["Este"]) == 6 and len(t["Oeste"]) == 6 and set(t["General"]["equipo"]) == set(t["Este"]["equipo"]) | set(t["Oeste"]["equipo"]))
    chk(f"Real {temp}: puntos ordenados de mayor a menor en cada tabla", all(t[k]["pts"].is_monotonic_decreasing for k in ("Este", "Oeste", "General")))
    chk(f"Real {temp}: goles a favor = goles en contra en el General", t["General"]["gf"].sum() == t["General"]["gc"].sum())
    chk(f"Real {temp}: cada equipo con PJ = G + E + P y PTS = 3G + E",
        all((t[k]["pj"] == t[k]["g"] + t[k]["e"] + t[k]["p"]).all() and (t[k]["pts"] == 3 * t[k]["g"] + t[k]["e"]).all() for k in ("Este", "Oeste", "General")))

t26 = L.construir_clasificacion_oficial(h, "2026")
chk("Real 2026: la fase de clasificación quedó completa (16 PJ por equipo)", t26["completa"])
c = L.cruces_si_terminara_hoy(t26)
# En mayo de 2026 los datos traen los cruces reales de playoff: Alianza-CAI y Unión Coclé-UMECIT.
chk("Real 2026: cruces de playoff coinciden con los partidos de fase final que traen los datos (Alianza-CAI, Unión Coclé-UMECIT)",
    {(x["local"], x["visitante"]) for x in c["playoff"]} == {("Alianza", "CA Independiente de La Chorrera"), ("Unión Coclé", "UMECIT")})
chk("Real 2026: el segundo de cada conferencia juega de local (art. 12)", all(x["local_pos"] == 2 and x["visitante_pos"] == 3 for x in c["playoff"]))
chk("Real 2026: sin empates sin resolver entre los cuatro primeros", c["incierto"] is False)
chk("Sin conferencias: construir_clasificacion_oficial devuelve None", L.construir_clasificacion_oficial(h, "2025") is None)

print("RESULTADO:", "OK" if ok else "FALLO")
sys.exit(0 if ok else 1)
