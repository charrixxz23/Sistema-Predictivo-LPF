"""Sistema visual de Pronóstico LPF: UN solo módulo de CSS.

Concepto: la interfaz es neutra (papel cálido, texto casi negro, verde solo como
acento) y el color lo ponen los clubes (ui/team_colors.py). Sin tarjetas, sin
sombras, sin cajas con borde de color: el orden lo dan el espacio, las líneas
finas y la jerarquía tipográfica.

Los colores base coinciden con .streamlit/config.toml. Las fuentes (Barlow
Condensed y Barlow, OFL) están en app/static/fonts y se sirven con
enableStaticServing, de modo que la app funciona sin internet.

Los ``linear-gradient`` con cortes duros solo dibujan formas planas (la línea de
bandera, la diagonal de la cabecera y el rayado); no hay degradados visuales.
"""

import streamlit as st


CSS = """
/* =========================================================
   1. Fuentes locales y tokens
========================================================= */
@font-face { font-family: "Barlow"; font-weight: 400; font-style: normal; font-display: swap; src: url("/app/static/fonts/Barlow-400.woff2") format("woff2"); }
@font-face { font-family: "Barlow"; font-weight: 500; font-style: normal; font-display: swap; src: url("/app/static/fonts/Barlow-500.woff2") format("woff2"); }
@font-face { font-family: "Barlow"; font-weight: 600; font-style: normal; font-display: swap; src: url("/app/static/fonts/Barlow-600.woff2") format("woff2"); }
@font-face { font-family: "Barlow"; font-weight: 700; font-style: normal; font-display: swap; src: url("/app/static/fonts/Barlow-700.woff2") format("woff2"); }
@font-face { font-family: "Barlow Condensed"; font-weight: 500; font-style: normal; font-display: swap; src: url("/app/static/fonts/BarlowCondensed-500.woff2") format("woff2"); }
@font-face { font-family: "Barlow Condensed"; font-weight: 600; font-style: normal; font-display: swap; src: url("/app/static/fonts/BarlowCondensed-600.woff2") format("woff2"); }
@font-face { font-family: "Barlow Condensed"; font-weight: 700; font-style: normal; font-display: swap; src: url("/app/static/fonts/BarlowCondensed-700.woff2") format("woff2"); }

:root {
    --paper: #FBF8F2;
    --paper2: #F3EEE4;
    --ink: #17181A;
    --muted: #57534B;
    --dim: #6A665D;
    --line: #E4DED2;
    --line-strong: #C9C2B3;

    --accent: #00875A;
    --accent-text: #007049;
    --accent-soft: #E3F3EC;

    --draw: #8A8F96;
    --hit-text: #1E58B8;
    --miss-text: #B3211F;

    /* Escala tipográfica en rem (raíz 16 px): base 17 px, formularios 16 px o más,
       etiquetas auxiliares 14 px; ningún texto por debajo de 14 px. */
    --fs-aux: 0.875rem;
    --fs-sm: 1rem;
    --fs-base: 1.0625rem;
    --fs-md: 1.1875rem;
    --fs-lg: 1.5rem;
    --fs-xl: 2rem;
    --fs-2xl: 2.5rem;
    --fs-3xl: 3rem;

    --font-ui: "Barlow", "Segoe UI", system-ui, sans-serif;
    --font-display: "Barlow Condensed", "Arial Narrow", "Segoe UI", sans-serif;
}

/* En pantallas grandes se escala la raíz para que el texto siga legible */
@media (min-width: 1700px) { html { font-size: 112.5%; } }
@media (min-width: 2300px) { html { font-size: 125%; } }


/* =========================================================
   2. Base de la aplicación
========================================================= */
.stApp {
    background: var(--paper);
    color: var(--ink);
    font-family: var(--font-ui);
    font-size: var(--fs-base);
}

.stApp [data-testid="stMainBlockContainer"],
.stApp .block-container {
    max-width: 96rem;
    padding: 5rem 2rem 2.5rem;
}

.stApp h1, .stApp h2, .stApp h3 {
    font-family: var(--font-display);
    color: var(--ink);
    letter-spacing: 0;
}

.stApp p, .stApp li { font-family: var(--font-ui); font-size: var(--fs-base); }
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stCaptionContainer"] p { font-size: 0.9375rem; color: var(--muted); }

footer:not(.lpf-footer), #MainMenu { visibility: hidden; }

/* Los bloques <style> que inyectamos no deben ocupar espacio */
.stElementContainer:has(style) { display: none; }

*:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }


/* =========================================================
   3. Navegación superior y línea de bandera
========================================================= */
header[data-testid="stHeader"] {
    background: var(--paper);
    border-bottom: 0;
}

/* Línea fina continua: mitad azul, mitad roja (colores de la bandera de Panamá) */
header[data-testid="stHeader"]::after {
    content: "";
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 3px;
    background: linear-gradient(to right, #005293 0 50%, #D21034 50% 100%);
}

header[data-testid="stHeader"] a[data-testid="stTopNavLink"] { border-radius: 6px; }

/* Texto de cada enlace (los iconos Material conservan su propia fuente) */
header[data-testid="stHeader"] a[data-testid="stTopNavLink"] span:not([data-testid="stIconMaterial"]) {
    font-family: var(--font-display) !important;
    font-weight: 600;
    font-size: var(--fs-md);
    letter-spacing: 0;
    color: var(--ink) !important;
}

header[data-testid="stHeader"] a[data-testid="stTopNavLink"] [data-testid="stIconMaterial"] { color: var(--muted) !important; }

/* Pestaña activa */
header[data-testid="stHeader"] a[aria-current="page"] { background: var(--accent-soft); }
header[data-testid="stHeader"] a[aria-current="page"] span:not([data-testid="stIconMaterial"]),
header[data-testid="stHeader"] a[aria-current="page"] [data-testid="stIconMaterial"] { color: var(--accent-text) !important; }


/* =========================================================
   4. Widgets de Streamlit
========================================================= */
.stApp [data-testid="stWidgetLabel"] p,
.stApp label p { font-size: var(--fs-sm); font-weight: 600; color: var(--ink); }

.stApp div[data-baseweb="select"] > div,
.stApp .stDateInput div[data-baseweb="input"],
.stApp .stDateInput input {
    background: #FFFFFF;
    border-color: var(--line-strong);
    border-radius: 6px;
    min-height: 2.75rem;
}

.stApp div[data-baseweb="select"] *,
.stApp .stDateInput input { font-size: var(--fs-base); color: var(--ink); }

/* Valores de formularios: 16 px o más (Streamlit fija 14 px en el campo del selector) */
.stApp input,
.stApp [data-baseweb="select"] input,
.stApp [data-baseweb="input"] input { font-size: var(--fs-base) !important; }

/* Campo de fecha: Streamlit lo compone con segmentos de 14 px */
.stApp [data-testid="stDateInput"] * { font-size: var(--fs-base) !important; }

/* Opciones desplegables y avisos */
[data-baseweb="popover"] li,
[data-baseweb="popover"] [role="option"],
[data-baseweb="menu"] li { font-size: var(--fs-base) !important; }
.stApp [data-testid="stAlert"] p { font-size: var(--fs-base); }

.stApp .stButton > button,
.stApp .stDownloadButton > button { border-radius: 6px; font-weight: 600; min-height: 2.75rem; }

.stApp .stButton > button p,
.stApp .stDownloadButton > button p { font-size: var(--fs-sm); font-weight: 600; }

.stApp .stButton > button[kind="primary"] { background: var(--accent); border-color: var(--accent); color: #FFFFFF; }
.stApp .stButton > button[kind="primary"] p { color: #FFFFFF; font-size: var(--fs-md); }

.stApp [data-testid="stTabs"] [role="tab"] p { font-size: var(--fs-base); font-weight: 600; }

/* Selector de jornada: una fila desplazable en pantallas estrechas */
.st-key-jornada-selector [data-testid="stButtonGroup"] {
    flex-wrap: nowrap;
    overflow-x: auto;
    scrollbar-width: thin;
    padding-bottom: 4px;
}

.st-key-jornada-selector [data-testid="stButtonGroup"] button { flex: 0 0 auto; }
.st-key-jornada-selector [data-testid="stButtonGroup"] button p { font-family: var(--font-display); font-size: var(--fs-md); font-weight: 600; }


/* =========================================================
   5. Marca, encabezado de página y pie
========================================================= */
.lpf-brand { display: flex; align-items: baseline; flex-wrap: wrap; gap: .25rem 1rem; margin-bottom: 1.25rem; }
.lpf-brand__name { font-family: var(--font-display); font-weight: 700; font-size: var(--fs-lg); color: var(--ink); }
.lpf-brand__name b { color: var(--accent-text); }
.lpf-brand__tag { color: var(--muted); font-size: var(--fs-sm); }
.lpf-brand__aviso { margin-left: auto; color: var(--miss-text); font-weight: 600; font-size: var(--fs-sm); }

.lpf-header { margin: 0 0 1rem; }
.lpf-header__title { margin: 0; font-family: var(--font-display); font-size: var(--fs-2xl); line-height: 1.05; font-weight: 700; color: var(--ink); }
.lpf-header__subtitle { margin: .3rem 0 0; color: var(--muted); font-size: var(--fs-base); max-width: 75ch; }

.lpf-footer {
    margin-top: 3rem;
    padding: 1.25rem 0 .5rem;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 0.9375rem;
    text-align: center;
}

.lpf-section { display: flex; align-items: baseline; justify-content: space-between; gap: .75rem; margin: 2.25rem 0 .5rem; }
.lpf-section__title { margin: 0; font-family: var(--font-display); font-size: var(--fs-xl); font-weight: 700; color: var(--ink); }
.lpf-section__hint { color: var(--muted); font-size: var(--fs-sm); }
.lpf-subseccion { margin: 1.25rem 0 .25rem; font-family: var(--font-display); font-size: var(--fs-lg); font-weight: 700; }

.lpf-datos { display: flex; flex-wrap: wrap; gap: .25rem 1.75rem; margin: .5rem 0 1.25rem; color: var(--muted); font-size: var(--fs-base); }
.lpf-datos b { color: var(--ink); font-weight: 700; }

.lpf-nota-pie { margin: .6rem 0 0; color: var(--dim); font-size: var(--fs-sm); font-style: italic; }


/* =========================================================
   6. Escudos
========================================================= */
.lpf-crest { display: inline-flex; align-items: center; justify-content: center; flex: 0 0 auto; border-radius: 50%; background: #FFFFFF; border: 1px solid var(--line); overflow: hidden; }
.lpf-crest img { width: 84%; height: 84%; object-fit: contain; }
.lpf-crest--sm { width: 1.75rem; height: 1.75rem; }
.lpf-crest--md { width: 2.25rem; height: 2.25rem; }
.lpf-crest--lg { width: 7rem; height: 7rem; }
.lpf-crest--fallback { background: var(--paper2); color: var(--muted); font-family: var(--font-display); font-weight: 700; }
.lpf-crest--sm.lpf-crest--fallback { font-size: var(--fs-aux); }
.lpf-crest--lg.lpf-crest--fallback { font-size: var(--fs-lg); }


/* =========================================================
   7. Partidos: fecha y filas de duelo (una columna)
========================================================= */
.lpf-dia { margin: 1.5rem 0 .25rem; padding-bottom: .25rem; font-family: var(--font-display); font-size: var(--fs-lg); font-weight: 600; border-bottom: 1px solid var(--line-strong); }
.lpf-duelos { display: block; }

.lpf-duelo, .lpf-hist { padding: .7rem 0 .75rem; border-bottom: 1px solid var(--line); }
.lpf-duelo__banda { display: flex; height: 4px; margin-bottom: .55rem; }
.lpf-duelo__banda i { flex: 1; background: var(--c1); }
.lpf-duelo__banda i + i { background: var(--c2); }

.lpf-duelo__linea { display: grid; grid-template-columns: 5.5rem minmax(0, 1fr) 3.5rem minmax(0, 1fr); align-items: center; gap: .6rem; }
.lpf-duelo__cuando { display: flex; flex-direction: column; line-height: 1.1; }
.lpf-duelo__cuando b { font-family: var(--font-display); font-size: var(--fs-xl); font-weight: 700; }
.lpf-duelo__cuando span { font-size: var(--fs-aux); color: var(--dim); }
.lpf-duelo__local, .lpf-duelo__visita { display: flex; align-items: center; gap: .55rem; min-width: 0; }
.lpf-duelo__local { justify-content: flex-end; text-align: right; }
.lpf-duelo__n { font-weight: 600; font-size: var(--fs-md); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.lpf-duelo__marcador { text-align: center; font-family: var(--font-display); font-weight: 700; font-size: var(--fs-xl); line-height: 1; white-space: nowrap; }
.lpf-duelo__marcador.vs { font-size: var(--fs-md); color: var(--dim); font-weight: 600; }

.lpf-duelo__pred { display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 1.5rem; align-items: end; margin-top: .55rem; }
.lpf-duelo__lado { text-align: right; font-size: var(--fs-sm); color: var(--muted); line-height: 1.35; }
.lpf-duelo__lado strong { color: var(--ink); }
.lpf-duelo__pie { display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; margin-top: .25rem; color: var(--dim); font-size: var(--fs-sm); }
.lpf-duelo__pie span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }

/* Barra 1X2: color del local, gris del empate y color del visitante.
   El segmento de un club parecido al gris (o a su rival) lleva rayado. */
.lpf-1x2, .lpf-prob3__barra { display: flex; gap: 2px; }
.lpf-1x2 { height: 6px; margin-bottom: .25rem; }
.lpf-1x2 i, .lpf-prob3__barra i { display: block; min-width: 4px; }
.lpf-1x2 .u, .lpf-prob3__barra .u { background: var(--c1); }
.lpf-1x2 .x, .lpf-prob3__barra .x { background: var(--draw); }
.lpf-1x2 .d, .lpf-prob3__barra .d { background: var(--c2); }
.lpf-1x2 .u.rayado, .lpf-prob3__barra .u.rayado { background: repeating-linear-gradient(135deg, var(--c1) 0 4px, var(--paper) 4px 8px); }
.lpf-1x2 .d.rayado, .lpf-prob3__barra .d.rayado { background: repeating-linear-gradient(135deg, var(--c2) 0 4px, var(--paper) 4px 8px); }
.lpf-1x2__n { display: grid; grid-template-columns: repeat(3, 1fr); font-size: var(--fs-sm); color: var(--muted); font-variant-numeric: tabular-nums; }
.lpf-1x2__n span:nth-child(2) { text-align: center; }
.lpf-1x2__n span:nth-child(3) { text-align: right; }
.lpf-1x2__n b { font-weight: 700; color: var(--ink); }

.lpf-enlace { color: var(--accent-text) !important; font-weight: 600; text-decoration: none !important; white-space: nowrap; flex: 0 0 auto; }
.lpf-enlace:hover { text-decoration: underline !important; }
.lpf-marca-ok { color: var(--hit-text); font-weight: 600; }
.lpf-marca-no { color: var(--miss-text); font-weight: 600; }
.lpf-marca-neutra { color: var(--dim); }


/* =========================================================
   8. Clasificación y tablas
========================================================= */
.lpf-tabla-wrap { overflow-x: auto; }
.lpf-tabla { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
.lpf-tabla th { padding: .45rem .5rem; color: var(--dim); font-size: var(--fs-aux); font-weight: 600; text-align: center; border-bottom: 1px solid var(--line-strong); white-space: nowrap; }
.lpf-tabla td { padding: .4rem .5rem; text-align: center; border-bottom: 1px solid var(--line); color: var(--muted); font-size: var(--fs-base); }
.lpf-tabla .e, .lpf-tabla th.e { text-align: left; }
.lpf-tabla td.club { border-left: 6px solid var(--club); padding-left: .75rem; color: var(--dim); font-family: var(--font-display); font-weight: 700; font-size: var(--fs-md); width: 2.5rem; }
.lpf-tabla .eq { display: flex; align-items: center; gap: .6rem; color: var(--ink); font-weight: 600; font-size: var(--fs-md); white-space: nowrap; }
.lpf-tabla .pts { color: var(--ink); font-family: var(--font-display); font-size: var(--fs-lg); font-weight: 700; }
.lpf-tabla .forma { display: inline-flex; gap: .2rem; }
.lpf-tabla .forma i { width: 1.15rem; height: .35rem; border-radius: 2px; display: inline-block; }
.lpf-tabla .forma .G { background: var(--hit-text); }
.lpf-tabla .forma .E { background: var(--draw); }
.lpf-tabla .forma .P { background: var(--miss-text); }
.lpf-tabla .oculta { display: none; }

/* Tabla de datos (Modelos): sin franja de club */
.lpf-tabla--datos td.e { color: var(--ink); font-weight: 600; }
.lpf-tabla--datos tr.is-destacada td { background: var(--accent-soft); color: var(--ink); font-weight: 600; }
.lpf-tabla--datos tr.is-destacada td.e { border-left: 6px solid var(--accent); }


/* =========================================================
   9. Predicciones: cabecera en diagonal, probabilidades y matriz
========================================================= */
.lpf-versus { margin-top: 1rem; }
.lpf-vs { position: relative; display: grid; grid-template-columns: 1fr 1fr; min-height: 15rem; background: linear-gradient(105deg, var(--c1) 0 49.6%, var(--paper) 49.6% 50.4%, var(--c2) 50.4% 100%); }
.lpf-vs__lado { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .4rem; padding: 1.5rem 1rem; text-align: center; color: var(--tinta); min-width: 0; }
.lpf-vs__rol { font-size: var(--fs-sm); font-weight: 700; letter-spacing: .08em; }
.lpf-vs__nombre { font-family: var(--font-display); font-size: var(--fs-xl); font-weight: 700; line-height: 1.05; }
.lpf-vs__abrev { font-size: var(--fs-sm); font-weight: 600; letter-spacing: .06em; }
.lpf-vs__centro { position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%); width: 3.25rem; height: 3.25rem; border-radius: 50%; background: var(--paper); display: flex; align-items: center; justify-content: center; font-family: var(--font-display); font-weight: 700; font-size: var(--fs-md); color: var(--ink); }
.lpf-vs__fuera { display: grid; grid-template-columns: 1fr 1fr; text-align: center; padding-top: .35rem; font-family: var(--font-display); font-size: var(--fs-xl); font-weight: 700; line-height: 1.05; }
.lpf-vs__fuera small { display: block; font-family: var(--font-ui); font-size: var(--fs-sm); font-weight: 700; letter-spacing: .08em; color: var(--muted); }
.lpf-vs__fuera span:empty { visibility: hidden; }
.lpf-vs__meta { margin: .6rem 0 0; color: var(--muted); }

.lpf-prob3__barra { height: 12px; gap: 3px; margin-top: .75rem; }
.lpf-prob3__cols { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; margin-top: .75rem; }
.lpf-prob3__col small { display: block; color: var(--dim); font-size: var(--fs-sm); }
.lpf-prob3__col b { display: block; font-family: var(--font-display); font-size: var(--fs-3xl); line-height: 1; font-weight: 700; white-space: nowrap; }
.lpf-prob3__col span { color: var(--muted); font-size: var(--fs-base); }
.lpf-prob3__col.pick { border-top: 3px solid var(--ink); margin-top: -3px; }
.lpf-prob3__col:not(.pick) b { color: var(--muted); }
.lpf-prob3__pick { margin: 1rem 0 0; color: var(--muted); }
.lpf-prob3__pick strong { color: var(--ink); font-family: var(--font-display); font-size: var(--fs-lg); }

.lpf-poisson { display: grid; grid-template-columns: minmax(0, 1.25fr) minmax(0, 1fr); gap: 3rem; align-items: start; margin-top: .5rem; }
.lpf-mapa-caja { width: 100%; }
.lpf-mapa__eje { display: flex; justify-content: center; font-family: var(--font-display); font-weight: 700; font-size: var(--fs-md); padding: 0 0 .4rem 2.6rem; }
.lpf-mapa__eje span { padding-bottom: .15rem; border-bottom: 4px solid transparent; }
.lpf-mapa__fila { display: flex; }
.lpf-mapa__v { writing-mode: vertical-rl; transform: rotate(180deg); font-family: var(--font-display); font-weight: 700; font-size: var(--fs-md); text-align: center; padding-right: .3rem; border-right: 4px solid transparent; }
.lpf-mapa { flex: 1; border-collapse: separate; border-spacing: 2px; font-variant-numeric: tabular-nums; table-layout: fixed; }
.lpf-mapa th { font-weight: 600; color: var(--dim); font-size: var(--fs-sm); padding: .2rem; }
.lpf-mapa td { text-align: center; font-size: var(--fs-aux); font-weight: 500; padding: .6rem .1rem; border-radius: 2px; }
.lpf-mapa td.max { outline: 3px solid var(--ink); outline-offset: -1px; font-weight: 700; }
.lpf-mapa-pie { margin: .6rem 0 0; color: var(--dim); font-size: var(--fs-sm); }

.lpf-xg3 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.lpf-xg3 div { padding-bottom: .5rem; border-bottom: 4px solid var(--c); }
.lpf-xg3 small { display: block; color: var(--muted); font-size: var(--fs-base); }
.lpf-xg3 b { font-family: var(--font-display); font-size: var(--fs-3xl); line-height: 1; font-weight: 700; white-space: nowrap; }
.lpf-top { margin: 0; padding: 0; list-style: none; }
.lpf-top li { display: flex; justify-content: space-between; align-items: baseline; padding: .3rem 0; border-bottom: 1px solid var(--line); font-size: var(--fs-base); color: var(--muted); }
.lpf-top li b { font-family: var(--font-display); font-size: var(--fs-lg); color: var(--ink); }


/* =========================================================
   10. Historial
========================================================= */
.lpf-hist__linea { display: grid; grid-template-columns: 9rem minmax(0, 1.6fr) minmax(0, 1fr) minmax(0, .8fr) minmax(0, 1fr); align-items: center; gap: 1rem; }
.lpf-hist__cuando b { display: block; font-family: var(--font-display); font-size: var(--fs-lg); line-height: 1.1; }
.lpf-hist__cuando span { color: var(--dim); font-size: var(--fs-aux); }
.lpf-hist__partido { display: flex; flex-wrap: wrap; align-items: center; gap: .4rem .6rem; font-weight: 600; font-size: var(--fs-md); }
.lpf-hist__eq { display: inline-flex; align-items: center; gap: .4rem; white-space: nowrap; }
.lpf-hist__partido em { color: var(--dim); font-style: normal; font-weight: 500; font-size: var(--fs-sm); }
.lpf-hist__dato small { display: block; color: var(--dim); font-size: var(--fs-aux); }
.lpf-hist__dato b { font-size: var(--fs-base); font-weight: 600; }
.lpf-hist__dato--fin { text-align: right; }


/* =========================================================
   11. Modelos: ficha técnica y gráfico por fold
========================================================= */
.lpf-ficha { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 3rem; margin: .5rem 0 0; }
.lpf-ficha div { display: grid; grid-template-columns: 9rem minmax(0, 1fr); gap: 1rem; padding: .5rem 0; border-bottom: 1px solid var(--line); }
.lpf-ficha dt { color: var(--dim); font-weight: 600; font-size: var(--fs-sm); }
.lpf-ficha dd { margin: 0; color: var(--ink); font-size: var(--fs-base); }

.lpf-fold-caja { overflow-x: auto; }
.lpf-fold { display: block; width: 100%; min-width: 540px; height: auto; }

.lpf-explica { max-width: 78ch; margin: .75rem 0 0; color: var(--ink); font-size: var(--fs-base); line-height: 1.55; }


/* =========================================================
   12. Estados: vacío, error y carga
========================================================= */
.lpf-state { display: flex; flex-direction: column; align-items: center; text-align: center; gap: .4rem; padding: 2.5rem 1.5rem; border-top: 1px solid var(--line-strong); border-bottom: 1px solid var(--line-strong); color: var(--muted); }
.lpf-state__icon { width: 3rem; height: 3rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: var(--fs-lg); background: var(--accent-soft); color: var(--accent-text); }
.lpf-state__title { margin: .4rem 0 0; font-family: var(--font-display); font-size: var(--fs-lg); color: var(--ink); }
.lpf-state__text { margin: 0; max-width: 50ch; font-size: var(--fs-base); }
.lpf-state__detail { margin-top: .5rem; font-size: var(--fs-aux); color: var(--dim); font-family: ui-monospace, Consolas, monospace; }
.lpf-state--error .lpf-state__icon { color: var(--miss-text); background: #FBE7E6; }
.lpf-state--error .lpf-state__title { color: var(--miss-text); }

.lpf-skeleton { display: block; }
.lpf-skeleton__fila { height: 5.5rem; margin-bottom: .75rem; background: var(--paper2); animation: lpf-pulse 1.2s ease-in-out infinite; }

@keyframes lpf-pulse { 0%, 100% { opacity: 1; } 50% { opacity: .55; } }

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}


/* =========================================================
   13. Pantallas pequeñas
========================================================= */
@media (max-width: 900px) {
    .lpf-poisson { grid-template-columns: 1fr; gap: 1.5rem; }
    .lpf-ficha { grid-template-columns: 1fr; }
    .lpf-hist__linea { grid-template-columns: 1fr 1fr; gap: .6rem 1rem; }
    .lpf-hist__partido { grid-column: 1 / -1; }
    .lpf-hist__dato--fin { text-align: left; }
}

@media (max-width: 760px) {
    .stApp [data-testid="stMainBlockContainer"],
    .stApp .block-container { padding: 4.5rem 1rem 2rem; }

    .lpf-header__title { font-size: var(--fs-xl); }
    .lpf-brand__tag { display: none; }

    /* Local y visitante apilados: cada nombre se ve completo, sin truncar */
    .lpf-duelo__linea {
        grid-template-columns: 4.2rem minmax(0, 1fr) auto;
        grid-template-areas: "cuando local marcador" "cuando visita marcador";
        gap: .3rem .6rem;
    }
    .lpf-duelo__cuando { grid-area: cuando; align-self: start; }
    .lpf-duelo__cuando b { font-size: var(--fs-lg); }
    .lpf-duelo__local { grid-area: local; justify-content: flex-end; text-align: left; flex-direction: row-reverse; }
    .lpf-duelo__visita { grid-area: visita; }
    .lpf-duelo__marcador { grid-area: marcador; font-size: var(--fs-lg); }
    .lpf-duelo__n { font-size: var(--fs-md); overflow: visible; text-overflow: clip; }
    .lpf-duelo__pred { grid-template-columns: 1fr; gap: .4rem; }
    .lpf-duelo__lado { text-align: left; }

    .lpf-vs { min-height: 12rem; }
    .lpf-crest--lg { width: 4.75rem; height: 4.75rem; }
    .lpf-vs__nombre, .lpf-vs__fuera { font-size: var(--fs-lg); }
    .lpf-vs__lado { padding: 1rem .5rem; }
    .lpf-vs__centro { width: 2.5rem; height: 2.5rem; font-size: var(--fs-sm); }

    .lpf-prob3__cols { gap: .75rem; }
    .lpf-prob3__col b, .lpf-xg3 b { font-size: 2.25rem; }
    .lpf-mapa td { padding: .45rem 0; }

    .lpf-tabla th, .lpf-tabla td { padding: .4rem .3rem; }
    .lpf-tabla .hide-sm { display: none; }
    .lpf-tabla td.club { padding-left: .5rem; }
}
"""


def inyectar_estilos():
    """Inyecta el CSS global. Llamar una vez por ejecución desde app.py."""

    # st.html con solo <style> va al contenedor de eventos y no sobrevive a
    # st.navigation; st.markdown inserta el bloque en la página de forma fiable.
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
