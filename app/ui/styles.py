"""Sistema visual de LPF Predictive Center: UN solo módulo de CSS.

Los colores base coinciden con .streamlit/config.toml. Ninguna página ni
componente define estilos propios: todo vive aquí y se inyecta una vez desde
app.py mediante ``inyectar_estilos()``.
"""

import streamlit as st


CSS = """
/* =========================================================
   1. Tokens
========================================================= */
:root {
    --lpf-bg: #0A1224;
    --lpf-bg-2: #0E1830;
    --lpf-surface: #111C33;
    --lpf-surface-2: #16233F;
    --lpf-line: #25324D;
    --lpf-line-soft: rgba(148, 163, 184, 0.14);

    --lpf-text: #E8EEF8;
    --lpf-muted: #9AA8C2;
    --lpf-dim: #6F7F9E;

    --lpf-accent: #2DD4A7;
    --lpf-accent-ink: #04241B;
    --lpf-accent-soft: rgba(45, 212, 167, 0.14);
    --lpf-gold: #F5C451;
    --lpf-gold-soft: rgba(245, 196, 81, 0.14);
    --lpf-draw: #7C8AA5;
    --lpf-danger: #F87171;
    --lpf-danger-soft: rgba(248, 113, 113, 0.14);

    --lpf-font-ui: "Segoe UI Variable Text", "Segoe UI", system-ui, -apple-system,
        "Helvetica Neue", Arial, sans-serif;
    --lpf-font-display: "Bahnschrift", "DIN Alternate", "Roboto Condensed",
        "Arial Narrow", "Segoe UI", system-ui, sans-serif;

    --lpf-s1: 4px;
    --lpf-s2: 8px;
    --lpf-s3: 12px;
    --lpf-s4: 16px;
    --lpf-s5: 24px;
    --lpf-s6: 32px;
    --lpf-s7: 48px;

    --lpf-r-sm: 10px;
    --lpf-r-md: 14px;
    --lpf-r-lg: 20px;

    --lpf-shadow: 0 10px 30px rgba(2, 6, 18, 0.35);
}


/* =========================================================
   2. Base de la aplicación
========================================================= */
.stApp {
    font-family: var(--lpf-font-ui);
    color: var(--lpf-text);
    background:
        radial-gradient(900px 420px at 85% -10%, rgba(45, 212, 167, 0.10), transparent 60%),
        radial-gradient(700px 380px at 0% 0%, rgba(56, 120, 248, 0.10), transparent 55%),
        var(--lpf-bg);
}

.stApp [data-testid="stMainBlockContainer"],
.stApp .block-container {
    max-width: 1240px;
    padding: 84px var(--lpf-s5) 72px;
}

.stApp h1, .stApp h2, .stApp h3 {
    font-family: var(--lpf-font-display);
    letter-spacing: 0.01em;
    color: var(--lpf-text);
}

.stApp p, .stApp label, .stApp button, .stApp input, .stApp li {
    font-family: var(--lpf-font-ui);
}

footer, #MainMenu { visibility: hidden; }

/* Los bloques <style> que inyectamos no deben ocupar espacio */
.stElementContainer:has(> .stMarkdown > div > style),
.stElementContainer:has(style) { display: none; }

*:focus-visible {
    outline: 2px solid var(--lpf-accent);
    outline-offset: 2px;
}


/* =========================================================
   3. Navegación superior (st.navigation, position="top")
========================================================= */
header[data-testid="stHeader"] {
    background: rgba(10, 18, 36, 0.86);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--lpf-line-soft);
}

header[data-testid="stHeader"] a,
header[data-testid="stHeader"] button {
    font-family: var(--lpf-font-display);
    letter-spacing: 0.04em;
    text-transform: uppercase;
    font-size: 0.86rem;
}


/* =========================================================
   4. Widgets de Streamlit (selectores, botones, pills, tabs)
========================================================= */
.stApp div[data-baseweb="select"] > div,
.stApp .stDateInput div[data-baseweb="input"] {
    background: var(--lpf-surface-2);
    border: 1px solid var(--lpf-line);
    border-radius: var(--lpf-r-sm);
}

.stApp .stButton > button,
.stApp .stDownloadButton > button {
    border-radius: var(--lpf-r-sm);
    font-weight: 600;
    letter-spacing: 0.02em;
    transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
}

.stApp .stButton > button:hover { transform: translateY(-1px); }

.stApp .stButton > button[kind="primary"] {
    background: var(--lpf-accent);
    color: var(--lpf-accent-ink);
    border: none;
    box-shadow: 0 8px 22px rgba(45, 212, 167, 0.28);
}

.stApp .stButton > button[kind="primary"] p { color: var(--lpf-accent-ink); font-weight: 700; }

.stApp [data-testid="stTabs"] [role="tab"] { font-weight: 600; }

/* Selector de jornada: una fila desplazable en pantallas estrechas */
.st-key-jornada-selector [data-testid="stButtonGroup"] {
    flex-wrap: nowrap;
    overflow-x: auto;
    scrollbar-width: thin;
    padding-bottom: var(--lpf-s1);
}

.st-key-jornada-selector [data-testid="stButtonGroup"] button { flex: 0 0 auto; }

.st-key-jornada-selector button[kind="secondary"],
.st-key-jornada-nav button {
    border-radius: var(--lpf-r-sm);
}


/* =========================================================
   5. Encabezado de página
========================================================= */
.lpf-header {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-end;
    justify-content: space-between;
    gap: var(--lpf-s4);
    padding: var(--lpf-s3) 0 var(--lpf-s5);
    border-bottom: 1px solid var(--lpf-line-soft);
    margin-bottom: var(--lpf-s5);
}

.lpf-header__kicker {
    color: var(--lpf-accent);
    font-family: var(--lpf-font-display);
    font-size: 0.8rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
}

.lpf-header__title {
    margin: var(--lpf-s1) 0 0;
    font-family: var(--lpf-font-display);
    font-size: clamp(1.9rem, 4.4vw, 3rem);
    line-height: 1.05;
    font-weight: 700;
    color: var(--lpf-text);
}

.lpf-header__subtitle {
    margin: var(--lpf-s2) 0 0;
    color: var(--lpf-muted);
    font-size: 1rem;
    max-width: 62ch;
}

.lpf-header__chips { display: flex; flex-wrap: wrap; gap: var(--lpf-s2); }


/* =========================================================
   6. Chips y etiquetas
========================================================= */
.lpf-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.74rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: var(--lpf-muted);
    background: var(--lpf-surface-2);
    border: 1px solid var(--lpf-line);
    white-space: nowrap;
}

.lpf-chip--accent { color: var(--lpf-accent); background: var(--lpf-accent-soft); border-color: transparent; }
.lpf-chip--gold   { color: var(--lpf-gold);   background: var(--lpf-gold-soft);   border-color: transparent; }
.lpf-chip--danger { color: var(--lpf-danger); background: var(--lpf-danger-soft); border-color: transparent; }

.lpf-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--lpf-accent);
    box-shadow: 0 0 0 4px var(--lpf-accent-soft);
}


/* =========================================================
   7. Secciones y tarjetas de métrica
========================================================= */
.lpf-section {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: var(--lpf-s3);
    margin: var(--lpf-s6) 0 var(--lpf-s4);
}

.lpf-section__title {
    margin: 0;
    font-family: var(--lpf-font-display);
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}

.lpf-section__hint { color: var(--lpf-muted); font-size: 0.88rem; }

.lpf-metrics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: var(--lpf-s4);
}

.lpf-metric {
    position: relative;
    padding: var(--lpf-s4) var(--lpf-s5);
    background: var(--lpf-surface);
    border: 1px solid var(--lpf-line-soft);
    border-radius: var(--lpf-r-md);
    overflow: hidden;
}

.lpf-metric::before {
    content: "";
    position: absolute; inset: 0 auto 0 0; width: 3px;
    background: var(--lpf-line);
}

.lpf-metric--accent::before { background: var(--lpf-accent); }
.lpf-metric--gold::before   { background: var(--lpf-gold); }

.lpf-metric__label {
    color: var(--lpf-muted);
    font-size: 0.74rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.lpf-metric__value {
    margin-top: var(--lpf-s1);
    font-family: var(--lpf-font-display);
    font-size: 2.2rem;
    font-weight: 700;
    line-height: 1.1;
    color: var(--lpf-text);
}

.lpf-metric--accent .lpf-metric__value { color: var(--lpf-accent); }
.lpf-metric--gold .lpf-metric__value   { color: var(--lpf-gold); }

.lpf-metric__hint { margin-top: var(--lpf-s1); color: var(--lpf-dim); font-size: 0.82rem; }


/* =========================================================
   8. Escudos
========================================================= */
.lpf-crest {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    border-radius: 50%;
    background: #F3F6FB;
    overflow: hidden;
}

.lpf-crest img { width: 82%; height: 82%; object-fit: contain; }

.lpf-crest--sm { width: 28px; height: 28px; }
.lpf-crest--md { width: 44px; height: 44px; }
.lpf-crest--lg { width: 88px; height: 88px; }

.lpf-crest--fallback {
    background: var(--lpf-surface-2);
    border: 1px solid var(--lpf-line);
    color: var(--lpf-muted);
    font-family: var(--lpf-font-display);
    font-weight: 700;
    letter-spacing: 0.04em;
}

.lpf-crest--sm.lpf-crest--fallback { font-size: 0.6rem; }
.lpf-crest--md.lpf-crest--fallback { font-size: 0.8rem; }
.lpf-crest--lg.lpf-crest--fallback { font-size: 1.5rem; }


/* =========================================================
   9. Calendario y tarjeta de partido
========================================================= */
.lpf-day {
    display: flex;
    align-items: center;
    gap: var(--lpf-s3);
    margin: var(--lpf-s6) 0 var(--lpf-s3);
    color: var(--lpf-muted);
    font-family: var(--lpf-font-display);
    font-size: 0.95rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.lpf-day::after { content: ""; flex: 1; height: 1px; background: var(--lpf-line-soft); }

.lpf-day__date { color: var(--lpf-text); }

.lpf-matches {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(min(100%, 360px), 1fr));
    gap: var(--lpf-s4);
}

.lpf-match {
    display: flex;
    flex-direction: column;
    gap: var(--lpf-s4);
    padding: var(--lpf-s4) var(--lpf-s5) var(--lpf-s4);
    background: var(--lpf-surface);
    border: 1px solid var(--lpf-line-soft);
    border-radius: var(--lpf-r-lg);
    box-shadow: var(--lpf-shadow);
    transition: border-color 0.15s ease, transform 0.15s ease;
}

.lpf-match:hover { border-color: var(--lpf-line); transform: translateY(-2px); }

.lpf-match__meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--lpf-s2);
    color: var(--lpf-dim);
    font-size: 0.78rem;
}

.lpf-match__venue {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
}

.lpf-match__teams {
    min-height: 124px;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: var(--lpf-s3);
}

.lpf-team {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--lpf-s2);
    min-width: 0;
    text-align: center;
}

.lpf-team__name {
    font-weight: 600;
    font-size: 0.9rem;
    line-height: 1.2;
    overflow-wrap: anywhere;
}

.lpf-match__center {
    display: flex;
    flex-direction: column;
    align-items: center;
    min-width: 64px;
}

.lpf-match__time,
.lpf-match__score {
    font-family: var(--lpf-font-display);
    font-weight: 700;
    line-height: 1;
    color: var(--lpf-text);
}

.lpf-match__time  { font-size: 1.5rem; }
.lpf-match__score { font-size: 1.9rem; letter-spacing: 0.04em; }
.lpf-match__tag   { margin-top: var(--lpf-s1); color: var(--lpf-dim); font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; }

.lpf-pred {
    display: flex;
    flex-direction: column;
    gap: var(--lpf-s2);
    padding-top: var(--lpf-s3);
    border-top: 1px dashed var(--lpf-line);
}

.lpf-pred__title {
    display: flex;
    justify-content: space-between;
    gap: var(--lpf-s2);
    color: var(--lpf-dim);
    font-size: 0.68rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.lpf-bar {
    display: flex;
    height: 10px;
    border-radius: 999px;
    overflow: hidden;
    background: var(--lpf-surface-2);
    gap: 2px;
}

.lpf-bar__seg { min-width: 4px; }
.lpf-bar__seg--L { background: var(--lpf-accent); }
.lpf-bar__seg--E { background: var(--lpf-draw); }
.lpf-bar__seg--V { background: var(--lpf-gold); }

.lpf-odds {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--lpf-s2);
}

.lpf-odd {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 6px 4px;
    border-radius: var(--lpf-r-sm);
    background: var(--lpf-bg-2);
    border: 1px solid transparent;
    color: var(--lpf-muted);
    font-size: 0.7rem;
    letter-spacing: 0.08em;
}

.lpf-odd strong {
    font-family: var(--lpf-font-display);
    font-size: 1.1rem;
    color: var(--lpf-text);
    letter-spacing: 0;
}

.lpf-odd.is-pick { border-color: var(--lpf-accent); background: var(--lpf-accent-soft); }
.lpf-odd.is-pick strong { color: var(--lpf-accent); }

.lpf-pred__foot {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: var(--lpf-s2);
    font-size: 0.82rem;
    color: var(--lpf-muted);
}

.lpf-pred__foot strong { color: var(--lpf-text); }

.lpf-link {
    color: var(--lpf-accent) !important;
    font-weight: 600;
    font-size: 0.82rem;
    text-decoration: none !important;
}

.lpf-link:hover { text-decoration: underline !important; }


/* =========================================================
   10. Clasificación
========================================================= */
.lpf-table-wrap {
    overflow-x: auto;
    background: var(--lpf-surface);
    border: 1px solid var(--lpf-line-soft);
    border-radius: var(--lpf-r-lg);
}

.lpf-table {
    width: 100%;
    min-width: 520px;
    border-collapse: collapse;
    font-variant-numeric: tabular-nums;
}

.lpf-table th {
    padding: var(--lpf-s3) var(--lpf-s3);
    color: var(--lpf-dim);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    text-align: center;
    border-bottom: 1px solid var(--lpf-line);
    white-space: nowrap;
}

.lpf-table td {
    padding: 10px var(--lpf-s3);
    text-align: center;
    border-bottom: 1px solid var(--lpf-line-soft);
    color: var(--lpf-muted);
}

.lpf-table tr:last-child td { border-bottom: none; }
.lpf-table tbody tr:hover td { background: var(--lpf-surface-2); }

.lpf-table .is-team { text-align: left; }
.lpf-table th.is-team { text-align: left; }

.lpf-table .is-pts { color: var(--lpf-text); font-family: var(--lpf-font-display); font-size: 1.1rem; font-weight: 700; }

.lpf-team-cell { display: flex; align-items: center; gap: var(--lpf-s3); color: var(--lpf-text); font-weight: 600; }

.lpf-pos {
    display: inline-flex; align-items: center; justify-content: center;
    width: 26px; height: 26px; border-radius: 8px;
    font-weight: 700; color: var(--lpf-muted); background: var(--lpf-surface-2);
}

.lpf-pos--first { background: var(--lpf-accent); color: var(--lpf-accent-ink); }

.lpf-form { display: inline-flex; gap: 4px; }

.lpf-form span {
    width: 20px; height: 20px; border-radius: 6px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.66rem; font-weight: 700; color: var(--lpf-accent-ink);
}

.lpf-form .G { background: var(--lpf-accent); }
.lpf-form .E { background: var(--lpf-draw); }
.lpf-form .P { background: var(--lpf-danger); }


.lpf-note {
    display: flex;
    flex-direction: column;
    gap: 2px;
    margin: 0 0 var(--lpf-s3);
    padding: var(--lpf-s3) var(--lpf-s4);
    border-left: 3px solid var(--lpf-gold);
    border-radius: var(--lpf-r-sm);
    background: var(--lpf-gold-soft);
    color: var(--lpf-muted);
    font-size: 0.85rem;
}

.lpf-note strong { color: var(--lpf-gold); font-size: 0.9rem; letter-spacing: 0.02em; }


/* =========================================================
   11. Predicción de partido (Match Center)
========================================================= */
.lpf-versus {
    margin-top: var(--lpf-s4);
    margin-bottom: var(--lpf-s4);
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: var(--lpf-s5);
    padding: var(--lpf-s6) var(--lpf-s5);
    background:
        linear-gradient(180deg, rgba(45, 212, 167, 0.06), transparent 60%),
        var(--lpf-surface);
    border: 1px solid var(--lpf-line-soft);
    border-radius: var(--lpf-r-lg);
}

.lpf-versus__team { display: flex; flex-direction: column; align-items: center; gap: var(--lpf-s3); text-align: center; min-width: 0; }
.lpf-versus__role { color: var(--lpf-accent); font-size: 0.7rem; letter-spacing: 0.2em; }
.lpf-versus__name { font-family: var(--lpf-font-display); font-size: 1.5rem; font-weight: 700; overflow-wrap: anywhere; }
.lpf-versus__code { color: var(--lpf-dim); font-size: 0.8rem; letter-spacing: 0.2em; }
.lpf-versus__vs   { font-family: var(--lpf-font-display); font-size: 2.2rem; color: var(--lpf-dim); }
.lpf-versus__meta { display: flex; gap: var(--lpf-s2); justify-content: center; margin-top: var(--lpf-s2); }

.lpf-panel {
    margin-top: var(--lpf-s5);
    padding: var(--lpf-s5);
    background: var(--lpf-surface);
    border: 1px solid var(--lpf-line-soft);
    border-radius: var(--lpf-r-lg);
    animation: lpf-rise 0.35s ease both;
}

.lpf-panel__head { margin-bottom: var(--lpf-s4); }
.lpf-panel__kicker { color: var(--lpf-accent); font-size: 0.72rem; letter-spacing: 0.2em; text-transform: uppercase; }
.lpf-panel__title { margin: var(--lpf-s1) 0 0; font-family: var(--lpf-font-display); font-size: 1.4rem; font-weight: 700; }

.lpf-probs { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--lpf-s4); }

.lpf-prob {
    padding: var(--lpf-s4);
    border-radius: var(--lpf-r-md);
    background: var(--lpf-bg-2);
    border: 1px solid var(--lpf-line-soft);
    display: flex; flex-direction: column; gap: var(--lpf-s2);
}

.lpf-prob.is-pick { border-color: var(--lpf-accent); background: var(--lpf-accent-soft); }

.lpf-prob__role { color: var(--lpf-dim); font-size: 0.68rem; letter-spacing: 0.16em; }
.lpf-prob__name { font-weight: 600; overflow-wrap: anywhere; }
.lpf-prob__value { font-family: var(--lpf-font-display); font-size: 2.2rem; font-weight: 700; line-height: 1; }
.lpf-prob.is-pick .lpf-prob__value { color: var(--lpf-accent); }
.lpf-prob__track { height: 6px; border-radius: 999px; background: var(--lpf-surface-2); overflow: hidden; }
.lpf-prob__fill  { display: block; height: 100%; border-radius: 999px; background: var(--lpf-muted); }
.lpf-prob.is-pick .lpf-prob__fill { background: var(--lpf-accent); }
.lpf-prob small { color: var(--lpf-muted); }

.lpf-pick {
    margin-top: var(--lpf-s4);
    display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: var(--lpf-s2);
    padding: var(--lpf-s3) var(--lpf-s4);
    border-radius: var(--lpf-r-md);
    background: var(--lpf-gold-soft);
    color: var(--lpf-muted);
}

.lpf-pick strong { font-family: var(--lpf-font-display); font-size: 1.15rem; color: var(--lpf-gold); letter-spacing: 0.04em; }

.lpf-xg { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--lpf-s4); }

.lpf-xg__card {
    padding: var(--lpf-s4);
    border-radius: var(--lpf-r-md);
    background: var(--lpf-bg-2);
    border: 1px solid var(--lpf-line-soft);
    display: flex; flex-direction: column; gap: var(--lpf-s1);
}

.lpf-xg__card span  { color: var(--lpf-muted); font-size: 0.85rem; }
.lpf-xg__card strong { font-family: var(--lpf-font-display); font-size: 2rem; line-height: 1.1; }
.lpf-xg__card small { color: var(--lpf-dim); }
.lpf-xg__card--main { border-color: var(--lpf-gold); background: var(--lpf-gold-soft); }
.lpf-xg__card--main strong { color: var(--lpf-gold); font-size: 2.4rem; }

.lpf-scores { display: flex; flex-wrap: wrap; gap: var(--lpf-s2); margin-top: var(--lpf-s4); }

.lpf-score {
    display: inline-flex; align-items: baseline; gap: var(--lpf-s2);
    padding: 6px 12px; border-radius: var(--lpf-r-sm);
    background: var(--lpf-bg-2); border: 1px solid var(--lpf-line-soft);
}

.lpf-score strong { font-family: var(--lpf-font-display); font-size: 1.1rem; }
.lpf-score span   { color: var(--lpf-muted); font-size: 0.8rem; }


/* =========================================================
   12. Historial
========================================================= */
.lpf-history { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 300px), 1fr)); gap: var(--lpf-s4); }

.lpf-hist {
    padding: var(--lpf-s4);
    background: var(--lpf-surface);
    border: 1px solid var(--lpf-line-soft);
    border-radius: var(--lpf-r-md);
    display: flex; flex-direction: column; gap: var(--lpf-s3);
}

.lpf-hist__meta { display: flex; justify-content: space-between; gap: var(--lpf-s2); color: var(--lpf-dim); font-size: 0.76rem; }
.lpf-hist__match { display: flex; align-items: center; gap: var(--lpf-s2); flex-wrap: wrap; font-weight: 700; }
.lpf-hist__match em { color: var(--lpf-dim); font-style: normal; font-weight: 400; font-size: 0.8rem; }
.lpf-hist__grid { display: grid; grid-template-columns: 1fr 1fr; gap: var(--lpf-s3); }
.lpf-hist__grid span { display: block; color: var(--lpf-dim); font-size: 0.7rem; letter-spacing: 0.1em; text-transform: uppercase; }
.lpf-hist__grid strong { font-size: 0.95rem; }
.lpf-hist__foot { display: flex; justify-content: space-between; color: var(--lpf-dim); font-size: 0.74rem; padding-top: var(--lpf-s2); border-top: 1px solid var(--lpf-line-soft); }


/* =========================================================
   13. Estados: vacío, error y carga
========================================================= */
.lpf-state {
    display: flex; flex-direction: column; align-items: center; text-align: center;
    gap: var(--lpf-s2);
    padding: var(--lpf-s7) var(--lpf-s5);
    background: var(--lpf-surface);
    border: 1px dashed var(--lpf-line);
    border-radius: var(--lpf-r-lg);
    color: var(--lpf-muted);
}

.lpf-state__icon {
    width: 52px; height: 52px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; background: var(--lpf-surface-2); color: var(--lpf-accent);
}

.lpf-state__title { margin: var(--lpf-s2) 0 0; font-family: var(--lpf-font-display); font-size: 1.3rem; color: var(--lpf-text); }
.lpf-state__text  { margin: 0; max-width: 46ch; }
.lpf-state__detail { margin-top: var(--lpf-s2); font-size: 0.78rem; color: var(--lpf-dim); font-family: ui-monospace, Consolas, monospace; }

.lpf-state--error { border-color: rgba(248, 113, 113, 0.4); }
.lpf-state--error .lpf-state__icon { color: var(--lpf-danger); background: var(--lpf-danger-soft); }

.lpf-skeleton { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 360px), 1fr)); gap: var(--lpf-s4); }

.lpf-skeleton__card {
    height: 230px;
    border-radius: var(--lpf-r-lg);
    background: linear-gradient(100deg, var(--lpf-surface) 30%, var(--lpf-surface-2) 50%, var(--lpf-surface) 70%);
    background-size: 220% 100%;
    animation: lpf-shimmer 1.4s linear infinite;
}


/* =========================================================
   14. Marca (franja bajo la navegación)
========================================================= */
.lpf-brand {
    display: flex;
    align-items: center;
    gap: var(--lpf-s3);
    margin-bottom: var(--lpf-s4);
}

.lpf-brand__logo { height: 44px; width: auto; padding: 4px 6px; border-radius: var(--lpf-r-sm); background: #F3F6FB; }
.lpf-brand__kicker { color: var(--lpf-dim); font-size: 0.66rem; letter-spacing: 0.22em; text-transform: uppercase; }
.lpf-brand__name { font-family: var(--lpf-font-display); font-size: 1.05rem; font-weight: 700; letter-spacing: 0.04em; }
.lpf-brand__status { margin-left: auto; }

.lpf-table tr.is-highlight td { background: var(--lpf-accent-soft); color: var(--lpf-text); }


/* =========================================================
   15. Animaciones
========================================================= */
@keyframes lpf-rise {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes lpf-shimmer {
    from { background-position: 120% 0; }
    to   { background-position: -120% 0; }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation: none !important; transition: none !important; }
}


/* =========================================================
   16. Responsive
========================================================= */
@media (max-width: 760px) {
    .stApp [data-testid="stMainBlockContainer"],
    .stApp .block-container { padding: 76px 16px 56px; }

    .lpf-header { padding-bottom: var(--lpf-s4); }
    .lpf-versus { grid-template-columns: 1fr; padding: var(--lpf-s5) var(--lpf-s4); gap: var(--lpf-s3); }
    .lpf-versus__vs { font-size: 1.4rem; }
    .lpf-probs, .lpf-xg { grid-template-columns: 1fr; }
    .lpf-table { min-width: 0; }
    .lpf-table th, .lpf-table td { padding: 8px 6px; }
    .lpf-table .hide-sm { display: none; }
    .lpf-team-cell { gap: var(--lpf-s2); font-size: 0.9rem; }
    .lpf-metrics { grid-template-columns: repeat(2, 1fr); gap: var(--lpf-s3); }
    .lpf-metric { padding: var(--lpf-s3) var(--lpf-s4); }
    .lpf-metric__value { font-size: 1.5rem; overflow-wrap: anywhere; }
    .lpf-match { padding: var(--lpf-s4); }
}
"""


def inyectar_estilos():
    """Inyecta el CSS global. Llamar una vez por ejecución desde app.py."""

    # st.html con solo <style> va al contenedor de eventos y no sobrevive a
    # st.navigation; st.markdown inserta el bloque en la página de forma fiable.
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
