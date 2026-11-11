"""Verifica la integridad de los modelos y los datos con sumas SHA-256.

Uso (desde la raíz del proyecto):
    python scripts/verificar_hashes.py            # compara con docs/hashes_sha256.json
    python scripts/verificar_hashes.py --generar  # reescribe docs/hashes_sha256.json

Cubre los modelos serializados (models/*.joblib) y todos los CSV de data/. En los
CSV se normalizan los finales de línea (CRLF -> LF) antes de calcular la suma, para
que el resultado no dependa de la configuración core.autocrlf de Git.
Solo lee archivos; no modifica modelos ni datos.
"""

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MANIFIESTO = RAIZ / "docs" / "hashes_sha256.json"


def archivos_a_verificar():
    return sorted(
        list((RAIZ / "models").glob("*.joblib")) + list((RAIZ / "data").rglob("*.csv"))
    )


def suma(ruta):
    contenido = ruta.read_bytes()

    if ruta.suffix == ".csv":
        contenido = contenido.replace(b"\r\n", b"\n")

    return hashlib.sha256(contenido).hexdigest()


def calcular():
    return {ruta.relative_to(RAIZ).as_posix(): suma(ruta) for ruta in archivos_a_verificar()}


def main():
    actuales = calcular()

    if "--generar" in sys.argv:
        MANIFIESTO.parent.mkdir(exist_ok=True)
        MANIFIESTO.write_text(
            json.dumps(actuales, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print(f"Manifiesto escrito: {MANIFIESTO.relative_to(RAIZ)} ({len(actuales)} archivos)")
        return 0

    esperados = json.loads(MANIFIESTO.read_text(encoding="utf-8"))

    distintos = [k for k in esperados if actuales.get(k) != esperados[k]]
    faltantes = [k for k in esperados if k not in actuales]
    nuevos = [k for k in actuales if k not in esperados]

    print(f"Archivos verificados: {len(esperados)}")

    for etiqueta, lista in (
        ("Modificados", distintos), ("Ausentes", faltantes), ("Sin registrar", nuevos)
    ):
        for k in lista:
            print(f"  {etiqueta}: {k}")

    if distintos or faltantes:
        print("RESULTADO: FALLO (hay archivos modificados o ausentes)")
        return 1

    print("RESULTADO: OK (todos los archivos coinciden con el manifiesto)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
