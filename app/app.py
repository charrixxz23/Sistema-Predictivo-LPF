"""Pronóstico LPF: punto de entrada y navegación superior.

Este archivo solo configura la página, inyecta el sistema visual y enruta a
las secciones de app/views. La lógica predictiva vive en app/services.
"""

import streamlit as st

from ui.components import brand_bar, footer
from ui.loaders import preparar_base_datos
from ui.styles import inyectar_estilos


st.set_page_config(
    page_title="Pronóstico LPF",
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

brand_bar(db_disponible=preparar_base_datos())

# El pie se crea antes que la página y se coloca al final con CSS (order). Así
# también aparece en las páginas que terminan con st.stop() (estados vacíos o de
# error), tras el cual Streamlit ya no admite nuevos elementos.
footer()

pagina.run()
