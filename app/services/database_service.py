from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import sqlite3


ROOT = Path(__file__).resolve().parents[2]

DB_DIR = ROOT / "database"

DB_PATH = DB_DIR / "lpf_predictive.db"


CREATE_PREDICCIONES_TABLE = """
CREATE TABLE IF NOT EXISTS predicciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_consulta TEXT,
    temporada TEXT,
    fecha_partido TEXT,
    equipo_local TEXT,
    equipo_visitante TEXT,
    prob_local REAL,
    prob_empate REAL,
    prob_visitante REAL,
    resultado_predicho TEXT,
    lambda_local REAL,
    lambda_visitante REAL,
    marcador_local INTEGER,
    marcador_visitante INTEGER,
    prob_marcador REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
"""


@contextmanager
def _abrir_conexion(db_path=DB_PATH):
    ruta_db = Path(db_path)
    ruta_db.parent.mkdir(parents=True, exist_ok=True)

    conexion = sqlite3.connect(ruta_db)
    conexion.row_factory = sqlite3.Row

    try:
        yield conexion
    finally:
        conexion.close()


def inicializar_base_datos(db_path=DB_PATH):
    with _abrir_conexion(db_path) as conexion:
        conexion.execute(CREATE_PREDICCIONES_TABLE)
        conexion.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_predicciones_created_at
            ON predicciones(created_at DESC)
            """
        )
        conexion.commit()


def guardar_prediccion(
    *,
    temporada,
    fecha_partido,
    equipo_local,
    equipo_visitante,
    prob_local,
    prob_empate,
    prob_visitante,
    resultado_predicho,
    lambda_local,
    lambda_visitante,
    marcador_local,
    marcador_visitante,
    prob_marcador,
    fecha_consulta=None,
    db_path=DB_PATH,
):
    inicializar_base_datos(db_path)

    fecha_consulta = (
        fecha_consulta
        or datetime.now().isoformat(timespec="seconds")
    )

    with _abrir_conexion(db_path) as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO predicciones (
                fecha_consulta,
                temporada,
                fecha_partido,
                equipo_local,
                equipo_visitante,
                prob_local,
                prob_empate,
                prob_visitante,
                resultado_predicho,
                lambda_local,
                lambda_visitante,
                marcador_local,
                marcador_visitante,
                prob_marcador
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(fecha_consulta),
                str(temporada),
                str(fecha_partido),
                str(equipo_local),
                str(equipo_visitante),
                float(prob_local),
                float(prob_empate),
                float(prob_visitante),
                str(resultado_predicho),
                float(lambda_local),
                float(lambda_visitante),
                int(marcador_local),
                int(marcador_visitante),
                float(prob_marcador),
            ),
        )
        conexion.commit()

        return int(cursor.lastrowid)


def obtener_ultimas_predicciones(limite=5, db_path=DB_PATH):
    inicializar_base_datos(db_path)
    limite = max(1, int(limite))

    with _abrir_conexion(db_path) as conexion:
        cursor = conexion.execute(
            """
            SELECT
                id,
                fecha_consulta,
                temporada,
                fecha_partido,
                equipo_local,
                equipo_visitante,
                prob_local,
                prob_empate,
                prob_visitante,
                resultado_predicho,
                lambda_local,
                lambda_visitante,
                marcador_local,
                marcador_visitante,
                prob_marcador,
                created_at
            FROM predicciones
            ORDER BY id DESC
            LIMIT ?
            """,
            (limite,),
        )

        return [
            dict(fila)
            for fila in cursor.fetchall()
        ]


def limpiar_historial(db_path=DB_PATH):
    inicializar_base_datos(db_path)

    with _abrir_conexion(db_path) as conexion:
        conexion.execute("DELETE FROM predicciones")
        conexion.commit()
