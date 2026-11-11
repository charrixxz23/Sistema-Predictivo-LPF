"""LPF Predictive Center: punto de entrada y navegación superior.

Este archivo solo configura la página, inyecta el sistema visual y enruta a
las secciones de app/views. La lógica predictiva vive en app/services.
"""

from pathlib import Path

import streamlit as st

from ui.components import brand_bar
from ui.loaders import preparar_base_datos
from ui.styles import inyectar_estilos


APP_DIR = Path(__file__).resolve().parent

LPF_LOGO = APP_DIR / "assets" / "logos" / "lpf.png"


st.set_page_config(
    page_title="LPF Predictive Center",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="collapsed",
)

inyectar_estilos()


paginas = [
    st.Page(
        "views/inicio.py",
        title="Inicio",
        icon=":material/home:",
        url_path="inicio",
        default=True,
    ),
    st.Page(
        "views/calendario.py",
        title="Calendario",
        icon=":material/calendar_month:",
        url_path="calendario",
    ),
    st.Page(
        "views/predicciones.py",
        title="Predicciones",
        icon=":material/analytics:",
        url_path="predicciones",
    ),
    st.Page(
        "views/clasificacion.py",
        title="Clasificación",
        icon=":material/leaderboard:",
        url_path="clasificacion",
    ),
    st.Page(
        "views/historial.py",
        title="Historial",
        icon=":material/history:",
        url_path="historial",
    ),
    st.Page(
        "views/modelos.py",
        title="Modelos",
        icon=":material/model_training:",
        url_path="modelos",
    ),
]

pagina = st.navigation(paginas, position="top")

brand_bar(LPF_LOGO, db_disponible=preparar_base_datos())

pagina.run()
