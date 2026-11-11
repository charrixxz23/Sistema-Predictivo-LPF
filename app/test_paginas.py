"""Prueba de humo de la interfaz: las seis páginas se dibujan sin excepciones.

Ejecutar desde la raíz del proyecto:  python app/test_paginas.py
Usa el marco de pruebas de Streamlit (AppTest); no abre un servidor ni pulsa
«Analizar partido», por lo que no escribe en la base de datos local.
"""

import sys
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parent / "app.py"

PAGINAS = [
    "views/inicio.py",
    "views/calendario.py",
    "views/predicciones.py",
    "views/clasificacion.py",
    "views/historial.py",
    "views/modelos.py",
]

PIE = "No está afiliado a la Liga Panameña de Fútbol."


def texto(at):
    partes = []

    for elemento in at.get("html"):
        partes.append(str(getattr(elemento, "value", None) or ""))

    partes += [str(m.value) for m in at.markdown]

    return "\n".join(partes)


def main():
    at = AppTest.from_file(str(APP), default_timeout=240).run()
    ok = True

    for pagina in PAGINAS:
        at.switch_page(pagina).run()
        correcta = not at.exception and PIE in texto(at)
        ok &= correcta
        print(("OK    " if correcta else "FALLO ") + pagina)

        for excepcion in at.exception:
            print("      ", str(excepcion.value)[:200])

    print("RESULTADO:", "OK" if ok else "FALLO")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
