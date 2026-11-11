"""Sistema visual de Pronóstico LPF: UN solo módulo de CSS.

Paleta «Claro y verde» (base: FotMob), tipografía Barlow Condensed (cifras y
títulos) y Barlow (texto), diseño plano: sin degradados de fondo ni brillos.
Los colores base coinciden con .streamlit/config.toml. Ninguna página ni
componente define estilos propios: todo vive aquí y se inyecta una vez desde
app.py mediante ``inyectar_estilos()``.

Las fuentes están en app/static/fonts y se sirven con enableStaticServing
(ver .streamlit/config.toml), de modo que la app funciona sin internet.
"""

import streamlit as st


CSS = """
/* =========================================================
   1. Fuentes locales (OFL) y tokens
========================================================= */
@font-face { font-family: "Barlow"; font-weight: 400; font-style: normal; font-display: swap; src: url("/app/static/fonts/Barlow-400.woff2") format("woff2"); }
@font-face { font-family: "Barlow"; font-weight: 500; font-style: normal; font-display: swap; src: url("/app/static/fonts/Barlow-500.woff2") format("woff2"); }
@font-face { font-family: "Barlow"; font-weight: 600; font-style: normal; font-display: swap; src: url("/app/static/fonts/Barlow-600.woff2") format("woff2"); }
@font-face { font-family: "Barlow"; font-weight: 700; font-style: normal; font-display: swap; src: url("/app/static/fonts/Barlow-700.woff2") format("woff2"); }
@font-face { font-family: "Barlow Condensed"; font-weight: 500; font-style: normal; font-display: swap; src: url("/app/static/fonts/BarlowCondensed-500.woff2") format("woff2"); }
@font-face { font-family: "Barlow Condensed"; font-weight: 600; font-style: normal; font-display: swap; src: url("/app/static/fonts/BarlowCondensed-600.woff2") format("woff2"); }
@font-face { font-family: "Barlow Condensed"; font-weight: 700; font-style: normal; font-display: swap; src: url("/app/static/fonts/BarlowCondensed-700.woff2") format("woff2"); }

:root {
    /* Paleta B · Claro y verde (contrastes WCAG AA verificados) */
    --bg: #F3F4F5;
    --surface: #FFFFFF;
    --surface2: #EBEDEF;
    --line: #DADDE1;

    --text: #1F2328;
    --muted: #4D5965;
    --dim: #58646F;

    --brand: #00875A;
    --brand-ink: #FFFFFF;
    --brand-text: #007049;
    --brand-soft: #E3F3EC;

    --local: #7048D8;
    --draw: #7C8793;
    --away: #D9730D;

    --hit: #2F6FDB;
    --hit-bg: #E6EEFB;
    --hit-text: #1E58B8;
    --miss: #D3302F;
    --miss-bg: #FBE7E6;
    --miss-text: #B3211F;

    --nav-bg: #FFFFFF;
    --nav-text: #1F2328;

    /* Escala tipográfica en rem (raíz 16 px): base 17 px, formularios 16 px,
       etiquetas auxiliares 14 px; ningún texto por debajo de 13 px. */
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

    --r: 10px;
}

/* En pantallas grandes se escala la raíz para que el texto siga legible */
@media (min-width: 1700px) { html { font-size: 112.5%; } }
@media (min-width: 2300px) { html { font-size: 125%; } }


/* =========================================================
   2. Base de la aplicación
========================================================= */
.stApp {
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-ui);
    font-size: var(--fs-base);
}

.stApp [data-testid="stMainBlockContainer"],
.stApp .block-container {
    max-width: 96rem;
    padding: 5rem 1.5rem 2.5rem;
}

.stApp h1, .stApp h2, .stApp h3 {
    font-family: var(--font-display);
    color: var(--text);
    letter-spacing: 0;
}

.stApp p, .stApp li { font-family: var(--font-ui); font-size: var(--fs-base); }
.stApp [data-testid="stCaptionContainer"],
.stApp [data-testid="stCaptionContainer"] p { font-size: 0.9375rem; color: var(--muted); }

footer:not(.lpf-footer), #MainMenu { visibility: hidden; }

/* Los bloques <style> que inyectamos no deben ocupar espacio */
.stElementContainer:has(style) { display: none; }

*:focus-visible { outline: 3px solid var(--brand); outline-offset: 2px; }


/* =========================================================
   3. Navegación superior (st.navigation, position="top")
========================================================= */
header[data-testid="stHeader"] {
    background: var(--nav-bg);
    border-bottom: 1px solid var(--line);
}

header[data-testid="stHeader"] a[data-testid="stTopNavLink"] { border-radius: 8px; }

/* Texto de cada enlace (los iconos Material conservan su propia fuente) */
header[data-testid="stHeader"] a[data-testid="stTopNavLink"] span:not([data-testid="stIconMaterial"]) {
    font-family: var(--font-display) !important;
    font-weight: 600;
    font-size: var(--fs-md);
    letter-spacing: 0;
    color: var(--nav-text) !important;
}

header[data-testid="stHeader"] a[data-testid="stTopNavLink"] [data-testid="stIconMaterial"] { color: var(--muted) !important; }

/* Pestaña activa */
header[data-testid="stHeader"] a[aria-current="page"] { background: var(--brand-soft); }
header[data-testid="stHeader"] a[aria-current="page"] span:not([data-testid="stIconMaterial"]),
header[data-testid="stHeader"] a[aria-current="page"] [data-testid="stIconMaterial"] { color: var(--brand-text) !important; }


/* =========================================================
   4. Widgets de Streamlit
========================================================= */
.stApp [data-testid="stWidgetLabel"] p,
.stApp label p { font-size: var(--fs-sm); font-weight: 600; color: var(--text); }

.stApp div[data-baseweb="select"] > div,
.stApp .stDateInput div[data-baseweb="input"],
.stApp .stDateInput input {
    background: var(--surface);
    border-color: var(--line);
    border-radius: 8px;
    font-size: var(--fs-sm);
    min-height: 2.75rem;
}

.stApp div[data-baseweb="select"] *,
.stApp .stDateInput input { font-size: var(--fs-base); color: var(--text); }

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
.stApp .stDownloadButton > button {
    border-radius: 8px;
    font-weight: 600;
    min-height: 2.75rem;
}

.stApp .stButton > button p,
.stApp .stDownloadButton > button p { font-size: var(--fs-sm); font-weight: 600; }

.stApp .stButton > button[kind="primary"] {
    background: var(--brand);
    border-color: var(--brand);
    color: var(--brand-ink);
}

.stApp .stButton > button[kind="primary"] p { color: var(--brand-ink); font-size: var(--fs-md); }

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

.st-key-match-controls { background: var(--surface); border-radius: var(--r); }


/* =========================================================
   5. Marca, encabezado de página y pie
========================================================= */
.lpf-brand {
    display: flex;
    align-items: baseline;
    flex-wrap: wrap;
    gap: .25rem 1rem;
    margin-bottom: 1rem;
}

.lpf-brand__name { font-family: var(--font-display); font-weight: 700; font-size: var(--fs-lg); color: var(--text); }
.lpf-brand__name b { color: var(--brand-text); }
.lpf-brand__tag { color: var(--muted); font-size: var(--fs-sm); }
.lpf-brand__status { margin-left: auto; }

.lpf-header {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
    margin: 0 0 1.25rem;
    padding-bottom: .75rem;
    border-bottom: 1px solid var(--line);
}

.lpf-header__title {
    margin: 0;
    font-family: var(--font-display);
    font-size: var(--fs-2xl);
    line-height: 1.05;
    font-weight: 700;
    color: var(--text);
}

.lpf-header__subtitle { margin: .35rem 0 0; color: var(--muted); font-size: var(--fs-base); max-width: 70ch; }
.lpf-header__chips { display: flex; flex-wrap: wrap; gap: .5rem; }

.lpf-footer {
    margin-top: 3rem;
    padding: 1.25rem 0 .5rem;
    border-top: 1px solid var(--line);
    color: var(--muted);
    font-size: 0.9375rem;
    text-align: center;
}


/* =========================================================
   6. Chips
========================================================= */
.lpf-chip {
    display: inline-flex;
    align-items: center;
    gap: .3rem;
    padding: .15rem .65rem;
    border-radius: 6px;
    font-size: var(--fs-aux);
    font-weight: 600;
    background: var(--surface2);
    color: var(--muted);
    border: 1px solid var(--line);
    white-space: nowrap;
}

.lpf-chip--brand { background: var(--brand-soft); color: var(--brand-text); border-color: transparent; }
.lpf-chip--pending { background: transparent; color: var(--brand-text); border-color: var(--brand-text); }
.lpf-chip--hit { background: var(--hit-bg); color: var(--hit-text); border-color: transparent; }
.lpf-chip--hit::before { content: "\\2713"; }
.lpf-chip--miss { background: var(--miss-bg); color: var(--miss-text); border-color: transparent; }
.lpf-chip--miss::before { content: "\\2715"; }


/* =========================================================
   7. Secciones y tarjetas de métrica
========================================================= */
.lpf-section {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: .75rem;
    margin: 2rem 0 .85rem;
}

.lpf-section__title { margin: 0; font-family: var(--font-display); font-size: var(--fs-xl); font-weight: 700; color: var(--text); }
.lpf-section__hint { color: var(--muted); font-size: var(--fs-sm); }
.lpf-hint-gap { margin-top: 1rem; }

.lpf-metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); gap: .75rem; }

.lpf-metric {
    padding: .85rem 1.1rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-left: 4px solid var(--line);
    border-radius: var(--r);
}

.lpf-metric--brand { border-left-color: var(--brand); }
.lpf-metric__label { color: var(--muted); font-size: var(--fs-sm); font-weight: 600; }
.lpf-metric__value { margin-top: .1rem; font-family: var(--font-display); font-size: var(--fs-xl); font-weight: 700; line-height: 1.1; color: var(--text); }
.lpf-metric--brand .lpf-metric__value { color: var(--brand-text); }
.lpf-metric__hint { margin-top: .15rem; color: var(--dim); font-size: var(--fs-aux); }

.lpf-note {
    display: flex;
    flex-direction: column;
    gap: .15rem;
    margin: 0 0 .85rem;
    padding: .7rem 1rem;
    border-left: 4px solid var(--brand);
    border-radius: 8px;
    background: var(--brand-soft);
    color: var(--muted);
    font-size: var(--fs-sm);
}

.lpf-note strong { color: var(--brand-text); font-size: var(--fs-base); }


/* =========================================================
   8. Escudos
========================================================= */
.lpf-crest {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    border-radius: 50%;
    background: #F4F6FA;
    border: 1px solid var(--line);
    overflow: hidden;
}

.lpf-crest img { width: 84%; height: 84%; object-fit: contain; }
.lpf-crest--sm { width: 1.75rem; height: 1.75rem; }
.lpf-crest--md { width: 2.25rem; height: 2.25rem; }
.lpf-crest--lg { width: 6rem; height: 6rem; }

.lpf-crest--fallback { background: var(--surface2); color: var(--muted); font-family: var(--font-display); font-weight: 700; }
.lpf-crest--sm.lpf-crest--fallback { font-size: 0.8125rem; }
.lpf-crest--md.lpf-crest--fallback { font-size: var(--fs-aux); }
.lpf-crest--lg.lpf-crest--fallback { font-size: var(--fs-lg); }


/* =========================================================
   9. Calendario y tarjeta de partido (compacta)
========================================================= */
.lpf-day {
    display: flex;
    align-items: center;
    gap: .75rem;
    margin: 1.25rem 0 .65rem;
    font-family: var(--font-display);
    font-size: var(--fs-lg);
    font-weight: 600;
    color: var(--text);
}

.lpf-day::after { content: ""; flex: 1; height: 1px; background: var(--line); }

.lpf-matches { display: grid; gap: .75rem; grid-template-columns: repeat(auto-fill, minmax(min(100%, 26rem), 1fr)); }

.lpf-match {
    display: flex;
    flex-direction: column;
    gap: .6rem;
    padding: .8rem 1rem;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--r);
}

.lpf-match__meta { display: flex; align-items: center; justify-content: space-between; gap: .5rem; color: var(--dim); font-size: var(--fs-aux); }
.lpf-match__venue { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }

.lpf-match__teams { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: .6rem; min-height: 2.75rem; }
.lpf-team { display: flex; align-items: center; gap: .5rem; min-width: 0; text-align: left; }
.lpf-team--away { flex-direction: row-reverse; text-align: right; }
.lpf-team__name { font-weight: 600; font-size: var(--fs-base); line-height: 1.1; color: var(--text); }

.lpf-match__center { display: flex; flex-direction: column; align-items: center; min-width: 4.5rem; }
.lpf-match__time, .lpf-match__score { font-family: var(--font-display); font-weight: 700; font-size: var(--fs-xl); line-height: 1; color: var(--text); }
.lpf-match__tag { margin-top: .15rem; color: var(--dim); font-size: var(--fs-aux); white-space: nowrap; }

.lpf-pred { display: flex; flex-direction: column; gap: .45rem; padding-top: .6rem; border-top: 1px solid var(--line); }
.lpf-bar { display: flex; height: 6px; border-radius: 3px; overflow: hidden; gap: 2px; background: var(--surface2); }
.lpf-bar__seg { min-width: 4px; }
.lpf-bar__seg--L { background: var(--local); }
.lpf-bar__seg--E { background: var(--draw); }
.lpf-bar__seg--V { background: var(--away); }

.lpf-odds { display: grid; grid-template-columns: repeat(3, 1fr); gap: .4rem; }
.lpf-odd { display: flex; align-items: baseline; justify-content: center; gap: .4rem; padding: .25rem .3rem; border-radius: 6px; background: var(--surface2); border: 2px solid transparent; color: var(--muted); font-size: var(--fs-aux); white-space: nowrap; }
.lpf-odd strong { font-family: var(--font-display); font-size: var(--fs-lg); line-height: 1; color: var(--text); }
.lpf-odd--L.is-pick { border-color: var(--local); }
.lpf-odd--E.is-pick { border-color: var(--draw); }
.lpf-odd--V.is-pick { border-color: var(--away); }

.lpf-pred__foot { display: flex; align-items: center; justify-content: space-between; gap: .5rem; font-size: var(--fs-sm); color: var(--muted); min-height: 1.5rem; }
.lpf-pred__foot strong { color: var(--text); }
.lpf-pred__pick { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }

.lpf-link { color: var(--brand-text) !important; font-weight: 600; font-size: var(--fs-sm); text-decoration: none !important; white-space: nowrap; flex: 0 0 auto; }
.lpf-link:hover { text-decoration: underline !important; }


/* =========================================================
   10. Clasificación y tablas
========================================================= */
.lpf-table-wrap { overflow-x: auto; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); }
.lpf-table { width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }
.lpf-table th { padding: .55rem .55rem; color: var(--dim); font-size: var(--fs-aux); font-weight: 600; text-align: center; border-bottom: 1px solid var(--line); white-space: nowrap; }
.lpf-table td { padding: .45rem .55rem; text-align: center; border-bottom: 1px solid var(--line); color: var(--muted); font-size: var(--fs-base); }
.lpf-table tr:last-child td { border-bottom: none; }
.lpf-table tbody tr:hover td { background: var(--bg); }
.lpf-table .is-team, .lpf-table th.is-team { text-align: left; }
.lpf-table .is-pts { color: var(--text); font-family: var(--font-display); font-size: var(--fs-lg); font-weight: 700; }
/* Variante compacta (portada): oculta las columnas de detalle */
.lpf-table--compact .hide-sm { display: none; }
.lpf-table tr.is-highlight td { background: var(--brand-soft); color: var(--text); }

.lpf-team-cell { display: flex; align-items: center; gap: .6rem; color: var(--text); font-weight: 600; font-size: var(--fs-md); white-space: nowrap; }

.lpf-pos { display: inline-flex; align-items: center; justify-content: center; width: 1.75rem; height: 1.75rem; border-radius: 6px; font-family: var(--font-display); font-weight: 700; font-size: var(--fs-md); color: var(--muted); background: var(--surface2); }
.lpf-pos--first { background: var(--brand); color: var(--brand-ink); }

.lpf-form { display: inline-flex; gap: .25rem; }
.lpf-form span { width: 1.6rem; height: 1.6rem; border-radius: 5px; display: inline-flex; align-items: center; justify-content: center; font-size: var(--fs-aux); font-weight: 700; }
.lpf-form .G { background: var(--hit-bg); color: var(--hit-text); }
.lpf-form .E { background: var(--surface2); color: var(--muted); }
.lpf-form .P { background: var(--miss-bg); color: var(--miss-text); }


/* =========================================================
   11. Predicciones: equipos y panel de resultados
========================================================= */
.lpf-versus { padding: 1.25rem 1.25rem 1.5rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); }
.lpf-versus__meta { display: flex; justify-content: center; flex-wrap: wrap; gap: .5rem; margin-bottom: 1rem; }
.lpf-versus .lpf-chip { font-size: var(--fs-sm); padding: .25rem .85rem; }
.lpf-versus__teams { display: grid; grid-template-columns: 1fr auto 1fr; align-items: center; gap: 1rem; }
.lpf-versus__team { display: flex; flex-direction: column; align-items: center; gap: .5rem; text-align: center; min-width: 0; }
.lpf-versus__role { color: var(--brand-text); font-size: var(--fs-sm); font-weight: 700; letter-spacing: .08em; }
.lpf-versus__name { font-family: var(--font-display); font-size: var(--fs-xl); font-weight: 700; line-height: 1.05; color: var(--text); }
.lpf-versus__code { color: var(--muted); font-size: var(--fs-sm); font-weight: 600; letter-spacing: .06em; }
.lpf-versus__vs { font-family: var(--font-display); font-size: var(--fs-xl); font-weight: 700; color: var(--dim); text-align: center; }

.lpf-panel { margin-top: 1rem; padding: 1.25rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); }
.lpf-panel__head { margin-bottom: 1rem; }
.lpf-panel__kicker { color: var(--brand-text); font-size: var(--fs-sm); font-weight: 700; }
.lpf-panel__title { margin: .1rem 0 0; font-family: var(--font-display); font-size: var(--fs-xl); font-weight: 700; color: var(--text); }

.lpf-probs { display: grid; grid-template-columns: repeat(3, 1fr); gap: .75rem; }
.lpf-prob { container-type: inline-size; padding: .9rem 1rem; border-radius: var(--r); background: var(--surface2); border: 2px solid transparent; display: flex; flex-direction: column; gap: .35rem; }
.lpf-prob__role { color: var(--dim); font-size: var(--fs-aux); font-weight: 600; }
.lpf-prob__name { font-weight: 600; font-size: var(--fs-md); color: var(--text); }
.lpf-prob__value { font-family: var(--font-display); font-size: clamp(2rem, 24cqw, 3rem); font-weight: 700; line-height: 1; color: var(--text); white-space: nowrap; }
.lpf-prob__track { height: 6px; border-radius: 3px; background: var(--bg); overflow: hidden; }
.lpf-prob__fill { display: block; height: 100%; }
.lpf-prob--L .lpf-prob__fill { background: var(--local); }
.lpf-prob--E .lpf-prob__fill { background: var(--draw); }
.lpf-prob--V .lpf-prob__fill { background: var(--away); }
.lpf-prob--L.is-pick { border-color: var(--local); }
.lpf-prob--E.is-pick { border-color: var(--draw); }
.lpf-prob--V.is-pick { border-color: var(--away); }
.lpf-prob small { color: var(--muted); font-size: var(--fs-sm); }

.lpf-pick { margin-top: .9rem; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: .5rem; padding: .7rem 1rem; border-radius: var(--r); background: var(--surface2); color: var(--muted); font-size: var(--fs-base); }
.lpf-pick strong { font-family: var(--font-display); font-size: var(--fs-lg); color: var(--text); }

.lpf-xg { display: grid; grid-template-columns: repeat(3, 1fr); gap: .75rem; }
.lpf-xg__card { container-type: inline-size; padding: .9rem 1rem; border-radius: var(--r); background: var(--surface2); display: flex; flex-direction: column; gap: .2rem; }
.lpf-xg__card span { color: var(--muted); font-size: var(--fs-base); }
.lpf-xg__card strong { font-family: var(--font-display); font-size: clamp(2rem, 26cqw, 3rem); line-height: 1; color: var(--text); white-space: nowrap; }
.lpf-xg__card small { color: var(--dim); font-size: var(--fs-sm); }
.lpf-xg__card--main { border: 2px solid var(--brand); }

.lpf-scores { display: flex; flex-wrap: wrap; gap: .5rem; margin-top: .6rem; }
.lpf-score { display: inline-flex; align-items: baseline; gap: .5rem; padding: .3rem .8rem; border-radius: 8px; background: var(--surface2); }
.lpf-score strong { font-family: var(--font-display); font-size: var(--fs-lg); }
.lpf-score span { color: var(--muted); font-size: var(--fs-sm); }


/* =========================================================
   12. Historial
========================================================= */
.lpf-history { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 22rem), 1fr)); gap: .75rem; }
.lpf-hist { padding: .85rem 1rem; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r); display: flex; flex-direction: column; gap: .6rem; }
.lpf-hist__meta { display: flex; justify-content: space-between; gap: .5rem; color: var(--dim); font-size: var(--fs-aux); }
.lpf-hist__match { display: flex; align-items: center; gap: .5rem; flex-wrap: wrap; font-weight: 700; font-size: var(--fs-md); }
.lpf-hist__team { display: inline-flex; align-items: center; gap: .4rem; }
.lpf-hist__match em { color: var(--dim); font-style: normal; font-weight: 500; font-size: var(--fs-sm); }
.lpf-hist__grid { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; }
.lpf-hist__grid span { display: block; color: var(--dim); font-size: var(--fs-aux); }
.lpf-hist__grid strong { font-size: var(--fs-base); }
.lpf-hist__foot { display: flex; justify-content: space-between; color: var(--dim); font-size: var(--fs-aux); padding-top: .5rem; border-top: 1px solid var(--line); }


/* =========================================================
   13. Estados: vacío, error y carga
========================================================= */
.lpf-state { display: flex; flex-direction: column; align-items: center; text-align: center; gap: .4rem; padding: 2.5rem 1.5rem; background: var(--surface); border: 1px dashed var(--line); border-radius: var(--r); color: var(--muted); }
.lpf-state__icon { width: 3rem; height: 3rem; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: var(--fs-lg); background: var(--brand-soft); color: var(--brand-text); }
.lpf-state__title { margin: .4rem 0 0; font-family: var(--font-display); font-size: var(--fs-lg); color: var(--text); }
.lpf-state__text { margin: 0; max-width: 50ch; font-size: var(--fs-base); }
.lpf-state__detail { margin-top: .5rem; font-size: var(--fs-aux); color: var(--dim); font-family: ui-monospace, Consolas, monospace; }
.lpf-state--error { border-color: var(--miss); }
.lpf-state--error .lpf-state__icon { color: var(--miss-text); background: var(--miss-bg); }

.lpf-skeleton { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 26rem), 1fr)); gap: .75rem; }
.lpf-skeleton__card { height: 12rem; border-radius: var(--r); background: var(--surface2); animation: lpf-pulse 1.2s ease-in-out infinite; }

@keyframes lpf-pulse { 0%, 100% { opacity: 1; } 50% { opacity: .55; } }

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}


/* =========================================================
   14. Pantallas pequeñas
========================================================= */
@media (max-width: 760px) {
    .stApp [data-testid="stMainBlockContainer"],
    .stApp .block-container { padding: 4.5rem 1rem 2rem; }

    .lpf-header__title { font-size: var(--fs-xl); }
    .lpf-versus__teams { grid-template-columns: 1fr; gap: .5rem; }
    .lpf-versus__name { font-size: var(--fs-lg); }
    .lpf-probs, .lpf-xg { grid-template-columns: 1fr; }
    .lpf-prob__value, .lpf-xg__card strong { font-size: 2.5rem; }
    .lpf-table { min-width: 0; }
    .lpf-table th, .lpf-table td { padding: .45rem .35rem; }
    .lpf-table .hide-sm { display: none; }
    .lpf-metrics { grid-template-columns: repeat(2, 1fr); }
    .lpf-brand__tag { display: none; }
}
"""


def inyectar_estilos():
    """Inyecta el CSS global. Llamar una vez por ejecución desde app.py."""

    # st.html con solo <style> va al contenedor de eventos y no sobrevive a
    # st.navigation; st.markdown inserta el bloque en la página de forma fiable.
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
