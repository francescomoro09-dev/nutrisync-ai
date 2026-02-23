"""
NutriSync AI -- Shared UI Components & Theme

Black & yellow only. No icons. No color variety.
"""

import html as html_mod
import json
import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# GLOBAL CSS
# ============================================================

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --ns-bg:         #000000;
    --ns-bg2:        #0A0A0A;
    --ns-bg3:        #141414;
    --ns-border:     #1F1F1F;
    --ns-border-hover: #2A2A2A;
    --ns-text:       #F5F5F5;
    --ns-text2:      #737373;
    --ns-text3:      #525252;
    --ns-yellow:     #FACC15;
    --ns-yellow-dim: #EAB308;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

header[data-testid="stHeader"] {
    background: rgba(0, 0, 0, 0.85) !important;
    backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--ns-border);
}

section[data-testid="stSidebar"] {
    background: var(--ns-bg2) !important;
    border-right: 1px solid var(--ns-border) !important;
}

a[data-testid="stSidebarNavLink"] {
    border-radius: 8px !important;
    transition: background 0.15s ease !important;
    margin-bottom: 2px !important;
}
a[data-testid="stSidebarNavLink"]:hover {
    background: var(--ns-bg3) !important;
}
a[data-testid="stSidebarNavLink"][aria-current="page"] {
    background: rgba(250, 204, 21, 0.08) !important;
    border-left: 3px solid var(--ns-yellow) !important;
}

div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
    background: var(--ns-bg2) !important;
    border: 1px solid var(--ns-border) !important;
    border-radius: 12px !important;
    padding: 1.25rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"]:hover {
    border-color: var(--ns-border-hover) !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.5) !important;
}

div[data-testid="stMetric"] {
    background: var(--ns-bg2);
    border: 1px solid var(--ns-border);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
}
div[data-testid="stMetric"] label {
    color: var(--ns-text2) !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 700 !important;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
    color: var(--ns-text2) !important;
    font-size: 0.75rem !important;
}

div[data-testid="stProgress"] > div {
    background-color: var(--ns-border) !important;
    border-radius: 6px !important;
    height: 8px !important;
}
div[data-testid="stProgress"] > div > div {
    border-radius: 6px !important;
    background: var(--ns-yellow) !important;
    height: 8px !important;
    transition: width 0.5s ease;
}

button[data-testid="stBaseButton-primary"] {
    background: var(--ns-yellow) !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    letter-spacing: 0.02em !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
}
button[data-testid="stBaseButton-primary"]:hover {
    background: var(--ns-yellow-dim) !important;
    box-shadow: 0 4px 14px rgba(250, 204, 21, 0.3) !important;
    transform: translateY(-1px) !important;
}

button[data-testid="stBaseButton-secondary"],
button[data-testid="stBaseButton-minimal"] {
    background: transparent !important;
    border: 1px solid var(--ns-border) !important;
    border-radius: 8px !important;
    color: var(--ns-text2) !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
button[data-testid="stBaseButton-secondary"]:hover,
button[data-testid="stBaseButton-minimal"]:hover {
    border-color: var(--ns-text2) !important;
    color: var(--ns-text) !important;
    background: var(--ns-bg3) !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stDateInput"] input,
div[data-testid="stTimeInput"] input {
    background: var(--ns-bg) !important;
    border: 1px solid var(--ns-border) !important;
    border-radius: 8px !important;
    color: var(--ns-text) !important;
    transition: border-color 0.2s ease !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: var(--ns-yellow) !important;
    box-shadow: 0 0 0 3px rgba(250, 204, 21, 0.12) !important;
}

div[data-testid="stSelectbox"] > div > div {
    background: var(--ns-bg) !important;
    border: 1px solid var(--ns-border) !important;
    border-radius: 8px !important;
}

details[data-testid="stExpander"] {
    background: var(--ns-bg2) !important;
    border: 1px solid var(--ns-border) !important;
    border-radius: 10px !important;
}
details[data-testid="stExpander"] summary {
    color: var(--ns-text2) !important;
    font-weight: 500 !important;
}
details[data-testid="stExpander"][open] summary {
    color: var(--ns-text) !important;
}

hr {
    border-color: var(--ns-border) !important;
    opacity: 0.5;
}

div[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 4px !important;
}

table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    width: 100% !important;
}
table th {
    background: var(--ns-bg3) !important;
    color: var(--ns-text2) !important;
    font-weight: 600 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    padding: 0.75rem 1rem !important;
    border-bottom: 1px solid var(--ns-border) !important;
}
table td {
    padding: 0.6rem 1rem !important;
    border-bottom: 1px solid var(--ns-border) !important;
    color: var(--ns-text) !important;
    font-size: 0.85rem !important;
}
table tr:last-child td { border-bottom: none !important; }
table tr:hover td { background: var(--ns-bg3) !important; }

h1 { font-weight: 700 !important; letter-spacing: -0.03em !important; }
h2 { color: var(--ns-text) !important; font-weight: 700 !important; letter-spacing: -0.02em !important; }
h3 { color: var(--ns-text) !important; font-weight: 600 !important; }

div[data-testid="stForm"] {
    background: var(--ns-bg2) !important;
    border: 1px solid var(--ns-border) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
}

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--ns-bg); }
::-webkit-scrollbar-thumb { background: var(--ns-border); border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #2A2A2A; }
</style>
"""


# ============================================================
# STYLED METRIC CARD -- yellow only
# ============================================================

def styled_metric(label, value, subtitle=""):
    """Render a metric card. Always yellow accent."""
    sub_html = ""
    if subtitle:
        sub_html = f"<div style='color:#737373;font-size:0.75rem;margin-top:0.25rem;'>{html_mod.escape(str(subtitle))}</div>"

    st.markdown(f"""
    <div style="
        background:#0A0A0A;
        border:1px solid #1F1F1F;
        border-left:3px solid #FACC15;
        border-radius:10px;
        padding:1rem 1.25rem;
    ">
        <div style="color:#737373;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.35rem;">
            {html_mod.escape(label)}
        </div>
        <div style="color:#FACC15;font-size:1.6rem;font-weight:700;line-height:1.2;letter-spacing:-0.02em;">
            {html_mod.escape(str(value))}
        </div>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# STYLED PROGRESS BAR -- yellow only
# ============================================================

def styled_progress(value, max_val, height="8px"):
    """Render a progress bar. Yellow fill, red when over."""
    pct = min(value / max_val, 1.0) * 100 if max_val > 0 else 0
    over = value > max_val and max_val > 0
    fill = "#EF4444" if over else "#FACC15"

    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:0.75rem;margin:0.3rem 0 0.6rem 0;">
        <div style="flex:1;background:#1F1F1F;border-radius:6px;height:{height};overflow:hidden;">
            <div style="width:{pct:.1f}%;height:100%;background:{fill};border-radius:6px;transition:width 0.5s ease;"></div>
        </div>
        <span style="color:{'#EF4444' if over else '#737373'};font-size:0.75rem;font-weight:600;min-width:3rem;text-align:right;">{pct:.0f}%</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# SIDEBAR BRAND HEADER -- no icon
# ============================================================

def sidebar_brand():
    """Render the branded sidebar header."""
    st.sidebar.markdown("""
    <div style="padding:0.25rem 0 1rem 0;margin-bottom:0.5rem;border-bottom:1px solid #1F1F1F;">
        <div style="font-size:1.35rem;font-weight:700;letter-spacing:-0.03em;color:#FACC15;margin-bottom:0.1rem;">
            NutriSync AI
        </div>
        <div style="color:#525252;font-size:0.7rem;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;">
            Intelligent Nutrition Tracking
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE HEADER -- no icon
# ============================================================

def page_header(title, subtitle=""):
    """Render a styled page header."""
    sub_html = ""
    if subtitle:
        sub_html = f"<p style='color:#737373;font-size:0.88rem;margin:0;'>{html_mod.escape(subtitle)}</p>"

    st.markdown(f"""
    <div style="margin-bottom:1.5rem;">
        <h1 style="font-size:2rem;font-weight:700;letter-spacing:-0.03em;color:#FACC15;margin-bottom:0.2rem;line-height:1.2;">
            {html_mod.escape(title)}
        </h1>
        {sub_html}
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# SECTION HEADER -- no icon
# ============================================================

def section_header(title):
    """Render a styled section divider."""
    st.markdown(f"""
    <div style="margin:1.5rem 0 1rem 0;padding-bottom:0.5rem;border-bottom:1px solid #1F1F1F;">
        <span style="color:#F5F5F5;font-size:1.1rem;font-weight:700;letter-spacing:-0.01em;">{html_mod.escape(title)}</span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# MEAL CARD HEADER -- no icon
# ============================================================

def meal_card_header(label, time_str, raw_input):
    """Render the header section of a meal card."""
    st.markdown(f"""
    <div style="margin-bottom:0.5rem;">
        <div style="display:flex;align-items:center;gap:0.6rem;">
            <span style="background:rgba(250,204,21,0.12);color:#FACC15;font-size:0.7rem;font-weight:700;padding:0.2rem 0.6rem;border-radius:20px;text-transform:uppercase;letter-spacing:0.05em;">
                {html_mod.escape(label)}
            </span>
            <span style="color:#525252;font-size:0.8rem;">{html_mod.escape(time_str)}</span>
        </div>
        <div style="color:#737373;font-size:0.82rem;font-style:italic;margin-top:0.3rem;">
            &ldquo;{html_mod.escape(raw_input)}&rdquo;
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# CONFIDENCE BADGE -- yellow only
# ============================================================

def confidence_badge(level):
    """Render a pill badge for confidence level. Always yellow."""
    st.markdown(f"""
    <span style="background:rgba(250,204,21,0.12);color:#FACC15;font-size:0.7rem;font-weight:700;padding:0.2rem 0.6rem;border-radius:20px;text-transform:uppercase;letter-spacing:0.05em;">
        {html_mod.escape(level)}
    </span>
    """, unsafe_allow_html=True)


# ============================================================
# VEGA-LITE CHART RENDERER
# ============================================================

VEGA_THEME_CONFIG = {
    "background": "transparent",
    "axis": {
        "labelColor": "#737373",
        "titleColor": "#737373",
        "gridColor": "#1F1F1F",
        "domainColor": "#1F1F1F",
        "tickColor": "#1F1F1F",
        "labelFont": "Space Grotesk, sans-serif",
        "titleFont": "Space Grotesk, sans-serif",
        "labelFontSize": 11,
        "titleFontSize": 12,
        "titleFontWeight": 600,
    },
    "legend": {
        "labelColor": "#737373",
        "titleColor": "#737373",
        "labelFont": "Space Grotesk, sans-serif",
        "titleFont": "Space Grotesk, sans-serif",
        "labelFontSize": 11,
    },
    "title": {
        "color": "#F5F5F5",
        "font": "Space Grotesk, sans-serif",
        "fontWeight": 700,
    },
    "view": {
        "stroke": "transparent",
    },
}


def render_vega_chart(spec, height=350):
    """Render a Vega-Lite chart with theme applied."""
    spec["$schema"] = "https://vega.github.io/schema/vega-lite/v5.json"
    spec["background"] = "transparent"

    if "config" not in spec:
        spec["config"] = {}
    for key, val in VEGA_THEME_CONFIG.items():
        if key == "background":
            continue
        if key not in spec["config"]:
            spec["config"][key] = val
        elif isinstance(val, dict):
            spec["config"][key] = {**val, **spec["config"].get(key, {})}

    spec_json = json.dumps(spec)
    chart_html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <div id="vis" style="width:100%;"></div>
    <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
    <script>
        vegaEmbed('#vis', {spec_json}, {{actions: false, theme: 'dark', renderer: 'svg'}}).catch(console.error);
    </script>
    """
    components.html(chart_html, height=height)
