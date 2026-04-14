import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.api_data import get_data
from modules.returns import calculate_returns
from modules.technical import compute_indicators
from modules.portfolio import optimize_portfolio
from modules.signals import compute_signals
from modules.macro import analyze_macro
from modules.garch import compute_garch, compute_garch_comparison
from modules.capm import compute_capm
from modules.var import compute_var
from scipy import stats
from scipy.signal import find_peaks

# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Teoría del Riesgo · Dashboard Interactivo",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
# PREMIUM DARK THEME CSS
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root variables ── */
:root {
    --bg-primary: #0a0e27;
    --bg-secondary: #111639;
    --bg-card: #161b4a;
    --bg-card-hover: #1c2254;
    --accent-purple: #7c3aed;
    --accent-pink: #ec4899;
    --accent-cyan: #06b6d4;
    --accent-green: #10b981;
    --accent-orange: #f59e0b;
    --accent-red: #ef4444;
    --text-primary: #f1f5f9;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --border-color: #1e2563;
    --gradient-1: linear-gradient(135deg, #7c3aed, #ec4899);
    --gradient-2: linear-gradient(135deg, #06b6d4, #10b981);
    --gradient-3: linear-gradient(135deg, #f59e0b, #ef4444);
}

/* ── Global ── */
html, body, [data-testid="stAppViewContainer"], .main, .block-container {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

.block-container { padding: 2rem 3rem !important; max-width: 1400px !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c1035 0%, #111845 50%, #0f1340 100%) !important;
    border-right: 1px solid var(--border-color) !important;
}
[data-testid="stSidebar"] * { color: var(--text-primary) !important; }
[data-testid="stSidebar"] .stRadio > label { font-size: 11px !important; text-transform: uppercase; letter-spacing: 1.5px; color: var(--text-muted) !important; font-weight: 600 !important; }

[data-testid="stSidebar"] .stRadio > div > label {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 10px 15px !important;
    margin: 2px 0 !important;
    transition: all 0.3s ease !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    border-left: 3px solid transparent !important;
}
[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(124, 58, 237, 0.15) !important;
    border-left: 3px solid var(--accent-purple) !important;
}
[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
[data-testid="stSidebar"] .stRadio > div [data-checked="true"] {
    background: rgba(124, 58, 237, 0.2) !important;
    border-left: 3px solid var(--accent-pink) !important;
    font-weight: 600 !important;
}

/* ── Headers ── */
h1, h2, h3, h4 { color: var(--text-primary) !important; font-family: 'Inter', sans-serif !important; }
h1 { font-size: 2.4rem !important; font-weight: 800 !important; }
h2 { font-size: 1.6rem !important; font-weight: 700 !important; }
h3 { font-size: 1.2rem !important; font-weight: 600 !important; }

/* ── Cards ── */
.risk-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 16px;
    padding: 24px;
    margin: 12px 0;
    transition: all 0.3s ease;
}
.risk-card:hover { transform: translateY(-2px); border-color: var(--accent-purple); box-shadow: 0 8px 30px rgba(124, 58, 237, 0.15); }

/* ── Lesson badge ── */
.lesson-badge {
    display: inline-block;
    background: rgba(124, 58, 237, 0.15);
    color: var(--accent-purple);
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
    border: 1px solid rgba(124, 58, 237, 0.3);
}

/* ── Section title ── */
.section-title {
    font-size: 28px;
    font-weight: 800;
    color: var(--text-primary);
    margin: 5px 0 20px 0;
    padding-bottom: 15px;
    border-bottom: 2px solid var(--border-color);
    position: relative;
}
.section-title::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 60px;
    height: 2px;
    background: var(--gradient-1);
}

/* ── Theory text ── */
.theory-text {
    color: var(--text-secondary);
    font-size: 15px;
    line-height: 1.85;
    margin: 15px 0;
}
.theory-text strong { color: var(--text-primary); }

/* ── Key insight ── */
.key-insight {
    background: linear-gradient(135deg, rgba(124, 58, 237, 0.08), rgba(236, 72, 153, 0.08));
    border-left: 4px solid;
    border-image: var(--gradient-1) 1;
    padding: 18px 22px;
    border-radius: 0 12px 12px 0;
    margin: 20px 0;
    color: var(--text-secondary);
    font-size: 14px;
    line-height: 1.75;
}
.key-insight strong { color: var(--accent-purple); }

/* ── Metric cards ── */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
.metric-value { font-size: 28px; font-weight: 800; margin: 8px 0 4px 0; }
.metric-label { font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
.metric-delta { font-size: 13px; font-weight: 600; }
.delta-up { color: var(--accent-green); }
.delta-down { color: var(--accent-red); }

/* ── Formula box ── */
.formula-box {
    background: rgba(6, 182, 212, 0.06);
    border: 1px solid rgba(6, 182, 212, 0.2);
    border-radius: 12px;
    padding: 18px 22px;
    font-family: 'Courier New', monospace;
    font-size: 15px;
    color: var(--accent-cyan);
    text-align: center;
    margin: 15px 0;
    letter-spacing: 0.5px;
}

/* ── Streamlit widget overrides ── */
.stSelectbox > div > div { background: var(--bg-card) !important; border: 1px solid var(--border-color) !important; border-radius: 10px !important; color: var(--text-primary) !important; }
.stSlider > div > div > div { color: var(--text-primary) !important; }
.stNumberInput > div > div > input { background: var(--bg-card) !important; border: 1px solid var(--border-color) !important; color: var(--text-primary) !important; border-radius: 10px !important; }
.stTextInput > div > div > input { background: var(--bg-card) !important; border: 1px solid var(--border-color) !important; color: var(--text-primary) !important; border-radius: 10px !important; }

.stButton > button {
    background: var(--gradient-1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover { opacity: 0.9 !important; transform: translateY(-1px) !important; box-shadow: 0 5px 20px rgba(124, 58, 237, 0.4) !important; }

/* Metrics override */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
}
[data-testid="stMetric"] label { color: var(--text-muted) !important; font-size: 12px !important; text-transform: uppercase !important; letter-spacing: 1px !important; }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color: var(--text-primary) !important; font-size: 24px !important; font-weight: 700 !important; }

/* Table overrides */
.stTable, table, th, td { background: var(--bg-card) !important; color: var(--text-primary) !important; border-color: var(--border-color) !important; }
thead th { background: var(--bg-secondary) !important; color: var(--accent-cyan) !important; font-weight: 600 !important; text-transform: uppercase !important; font-size: 11px !important; letter-spacing: 1px !important; }
tbody td { font-size: 14px !important; padding: 10px 14px !important; }
tbody tr:hover { background: var(--bg-card-hover) !important; }

/* Dataframe */
[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; }

/* Tabs override */
.stTabs [data-baseweb="tab-list"] { background: var(--bg-secondary) !important; border-radius: 12px !important; padding: 4px !important; gap: 4px !important; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: var(--text-muted) !important; border-radius: 8px !important; font-weight: 500 !important; }
.stTabs [aria-selected="true"] { background: var(--accent-purple) !important; color: white !important; }

/* Expander */
.streamlit-expanderHeader { background: var(--bg-card) !important; border: 1px solid var(--border-color) !important; border-radius: 10px !important; color: var(--text-primary) !important; }
.streamlit-expanderContent { background: var(--bg-secondary) !important; border: 1px solid var(--border-color) !important; color: var(--text-secondary) !important; }

/* Info/Success/Warning/Error boxes */
.stAlert > div { border-radius: 12px !important; }

/* Spinner */
.stSpinner > div { color: var(--accent-purple) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--accent-purple); border-radius: 3px; }

/* ── Divider ── */
.gradient-divider {
    height: 2px;
    background: var(--gradient-1);
    border: none;
    border-radius: 1px;
    margin: 30px 0;
    opacity: 0.5;
}

/* ── Navigation indicator ── */
.nav-counter {
    display: inline-block;
    background: var(--gradient-1);
    color: white;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    text-align: center;
    line-height: 24px;
    font-size: 12px;
    font-weight: 700;
    margin-right: 8px;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# PLOTLY DARK TEMPLATE
# ═══════════════════════════════════════════════════════════════════
PLOT_LAYOUT = dict(
    paper_bgcolor='#111639',
    plot_bgcolor='#0a0e27',
    font=dict(family='Inter', color='#f1f5f9', size=12),
    xaxis=dict(gridcolor='#1e2563', zerolinecolor='#1e2563'),
    yaxis=dict(gridcolor='#1e2563', zerolinecolor='#1e2563'),
    margin=dict(l=40, r=20, t=50, b=40),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(size=11)),
    colorway=['#7c3aed', '#ec4899', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#14b8a6']
)

def styled_fig(fig, title=""):
    fig.update_layout(**PLOT_LAYOUT, title=dict(text=title, font=dict(size=18, color='#f1f5f9')))
    return fig

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR — NAVIGATION & CONTROLS
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="padding: 15px 10px 20px 10px; text-align: center;">
        <div style="font-size: 28px; font-weight: 800; background: linear-gradient(135deg, #7c3aed, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px;">📚 Contenido</div>
        <div style="font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 2px;">Teoría del Riesgo · USTA</div>
    </div>
    """, unsafe_allow_html=True)

    section = st.radio(
        "NAVEGACIÓN",
        [
            "🏠 Dashboard General",
            "📖 Riesgo Sistemático",
            "⚖️ Modelo CAPM",
            "🛡️ Riesgo No Sistemático",
            "📈 Rendimientos",
            "📉 Valor en Riesgo (VaR)",
            "🎰 VaR No Paramétrico",
            "📜 Simulación Histórica",
            "🔄 Simulación Bootstrap",
            "💀 Expected Shortfall (CVaR)",
            "🎲 Simulación Montecarlo",
            "✅ Backtesting del VaR",
            "🌀 Modelo GARCH(1,1)",
            "📊 Indicadores Técnicos",
            "🎯 Portafolio Markowitz",
            "🚦 Señales de Trading",
            "🌍 Análisis Macro",
            "⚠️ Limitaciones y Críticas",
        ],
        label_visibility="collapsed"
    )

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

    st.markdown('<p style="font-size:11px; color:#64748b; text-transform:uppercase; letter-spacing:1.5px; font-weight:600; margin-bottom:8px;">⚙️ Parámetros</p>', unsafe_allow_html=True)
    tickers_input = st.text_input("Activos", value="AVAL, ^GSPC, ETH-USD, IBM, C6L.SI, NTDOY")
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]
    confidence = st.slider("Confianza VaR", 0.90, 0.99, 0.95)
    simulations = st.number_input("Simulaciones", min_value=1000, max_value=20000, value=10000, step=1000)
    refresh_btn = st.button("🔄 Actualizar Datos")

    st.markdown("""
    <div style="position: fixed; bottom: 15px; left: 15px; font-size: 10px; color: #475569;">
        Dashboard v3.0 · Teoría del Riesgo<br>Autor: <b>Paula Español</b>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# DATA LOADING
# ═══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def load_all_data(ticker_list, conf):
    try:
        raw_data = get_data(ticker_list)
        for tk, df in raw_data.items():
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        returns = calculate_returns(raw_data)
        indicators = compute_indicators(returns)
        garch = compute_garch(indicators)
        capm = compute_capm(indicators)
        var = compute_var(indicators, confidence_level=conf)
        signals = compute_signals(indicators)
        return {
            "ind": indicators, "garch": garch, "capm": capm,
            "var": var, "signals": signals, "raw": raw_data
        }
    except Exception as e:
        st.error(f"Error procesando datos: {e}")
        return None

if refresh_btn:
    load_all_data.clear()
    if "cache" in st.session_state:
        del st.session_state.cache

if "cache" not in st.session_state or refresh_btn:
    with st.spinner("⏳ Descargando datos de mercado y construyendo modelos de riesgo..."):
        st.session_state.cache = load_all_data(tickers, confidence)

data_cache = st.session_state.cache

# Helpers
def _to_float(v):
    if isinstance(v, pd.Series): return float(v.iloc[0])
    return float(v) if v is not None and pd.notna(v) else 0.0

def _to_str(v):
    if isinstance(v, pd.Series): return str(v.iloc[0])
    return str(v) if v is not None and pd.notna(v) else 'N/A'

valid_assets = []
if data_cache:
    valid_assets = [t for t in tickers if t not in ['^GSPC', '^IRX'] and t in data_cache["ind"]]

total_sections = 18
section_names = [
    "Dashboard General", "Riesgo Sistemático", "Modelo CAPM", "Riesgo No Sistemático",
    "Rendimientos",
    "Valor en Riesgo (VaR)", "VaR No Paramétrico", "Simulación Histórica", "Simulación Bootstrap",
    "Expected Shortfall (CVaR)", "Simulación Montecarlo", "Backtesting del VaR", "Modelo GARCH(1,1)",
    "Indicadores Técnicos", "Portafolio Markowitz", "Señales de Trading", "Análisis Macro",
    "Limitaciones y Críticas"
]

# Get current section index
current_idx = 0
for i, name in enumerate(section_names):
    if name in section:
        current_idx = i
        break

# ═══════════════════════════════════════════════════════════════════
# SECTION: DASHBOARD GENERAL
# ═══════════════════════════════════════════════════════════════════
if "Dashboard General" in section:
    st.markdown(f'<div class="lesson-badge">📊 Lección 1 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Plataforma Avanzada de Análisis de Riesgo Financiero</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    Bienvenido a la <strong>Plataforma Interactiva de Teoría del Riesgo</strong>, desarrollada como proyecto integrador
    para el análisis cuantitativo de instrumentos financieros. Esta herramienta combina <strong>modelos econométricos avanzados</strong>
    con análisis técnico en tiempo real para un portafolio diversificado de 6 activos internacionales.
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        # Price cards
        cols = st.columns(min(len(valid_assets), 5))
        for idx, t in enumerate(valid_assets[:5]):
            try:
                latest = data_cache["ind"][t].iloc[-1]
                prev = data_cache["ind"][t].iloc[-2]
                price = float(latest['Close'])
                pct = ((price - float(prev['Close'])) / float(prev['Close'])) * 100
                delta_class = "delta-up" if pct >= 0 else "delta-down"
                arrow = "▲" if pct >= 0 else "▼"
                cols[idx].markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">{t}</div>
                    <div class="metric-value" style="background: {'linear-gradient(135deg, #10b981, #06b6d4)' if pct >= 0 else 'linear-gradient(135deg, #ef4444, #f59e0b)'}; -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${price:,.2f}</div>
                    <div class="metric-delta {delta_class}">{arrow} {abs(pct):.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
            except:
                pass

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # Summary table
        st.markdown("### 📋 Resumen del Portafolio")
        summary_rows = []
        for t in valid_assets:
            try:
                df_ind = data_cache["ind"][t]
                df_var_t = data_cache["var"].get(t)
                df_capm_t = data_cache["capm"].get(t)
                df_garch_t = data_cache["garch"].get(t)
                row_data = {"Activo": t}
                row_data["Precio"] = f"${float(df_ind['Close'].iloc[-1]):,.2f}"
                row_data["RSI"] = f"{float(df_ind['RSI'].iloc[-1]):.1f}" if 'RSI' in df_ind.columns else "N/A"
                if df_var_t is not None and 'VaR_95_Hist' in df_var_t.columns:
                    row_data["VaR 95%"] = f"{_to_float(df_var_t['VaR_95_Hist'].iloc[-1])*100:.2f}%"
                else:
                    row_data["VaR 95%"] = "N/A"
                if df_capm_t is not None and 'CAPM_Beta' in df_capm_t.columns:
                    row_data["Beta"] = f"{_to_float(df_capm_t['CAPM_Beta'].iloc[-1]):.2f}"
                else:
                    row_data["Beta"] = "N/A"
                if df_garch_t is not None and 'GARCH_Vol' in df_garch_t.columns:
                    row_data["Vol. GARCH"] = f"{_to_float(df_garch_t['GARCH_Vol'].iloc[-1])*100:.2f}%"
                else:
                    row_data["Vol. GARCH"] = "N/A"
                sig_map = {"BUY": "🟢 COMPRA", "SELL": "🔴 VENTA", "HOLD": "🟡 HOLD"}
                if t in data_cache.get("signals", {}):
                    raw_sig = str(data_cache["signals"][t]['Final_Signal'].iloc[-1])
                    row_data["Señal"] = sig_map.get(raw_sig, "🟡 HOLD")
                else:
                    row_data["Señal"] = "—"
                summary_rows.append(row_data)
            except:
                pass
        if summary_rows:
            st.table(pd.DataFrame(summary_rows))

        st.markdown("""
        <div class="key-insight">
            <strong>💡 Guía de Navegación:</strong> Utiliza el menú lateral para explorar cada concepto teórico junto con su aplicación
            práctica sobre datos reales. Cada sección incluye la <strong>fundamentación teórica</strong>, la <strong>fórmula matemática</strong>,
            y el <strong>análisis aplicado</strong> a nuestro portafolio.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("⏳ Cargando datos... presiona '🔄 Actualizar Datos' en la barra lateral.")

# ═══════════════════════════════════════════════════════════════════
# SECTION: RIESGO SISTEMÁTICO
# ═══════════════════════════════════════════════════════════════════
elif "Riesgo Sistemático" in section:
    st.markdown(f'<div class="lesson-badge">📖 Lección 2 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Riesgo Sistemático</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El <strong>riesgo sistemático</strong>, también conocido como riesgo de mercado o riesgo no diversificable, se refiere a la parte del
    riesgo total de una inversión que está asociada con factores macroeconómicos y que <strong>no se puede eliminar mediante la diversificación</strong>.
    A diferencia del riesgo específico de una empresa o riesgo no sistemático, que puede mitigarse invirtiendo en una variedad de activos,
    el riesgo sistemático afecta a toda la economía o a grandes sectores de ella, y por lo tanto, afecta a casi todas las inversiones en cierta medida.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    Algunos ejemplos de factores que contribuyen al riesgo sistemático incluyen:
    </div>
    """, unsafe_allow_html=True)

    factors = [
        ("1️⃣", "Cambios en las políticas gubernamentales", "Cambios en las tasas de interés, políticas fiscales, o regulaciones que pueden afectar a la economía en general."),
        ("2️⃣", "Inflación", "Las fluctuaciones en los niveles de precios pueden afectar el poder adquisitivo y, por ende, el desempeño económico general."),
        ("3️⃣", "Recesiones económicas", "Períodos de declive económico general afectan a casi todas las empresas y sectores."),
        ("4️⃣", "Guerras y conflictos geopolíticos", "Estos eventos pueden causar incertidumbre en los mercados globales, afectando la economía a gran escala."),
        ("5️⃣", "Desastres naturales", "Aunque su impacto puede ser más localizado, eventos como terremotos, huracanes, o pandemias pueden tener efectos significativos en la economía global."),
    ]

    for num, title, desc in factors:
        st.markdown(f"""
        <div class="risk-card">
            <span style="font-size: 18px;">{num}</span>
            <strong style="color: var(--accent-cyan); margin-left: 8px;">{title}:</strong>
            <span style="color: var(--text-secondary);"> {desc}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="key-insight">
    Debido a que el riesgo sistemático es inherente al mercado en su conjunto, los inversores suelen buscar compensaciones a través de una
    <strong>prima de riesgo</strong>, es decir, esperan obtener un retorno adicional por asumir un mayor nivel de riesgo. La gestión del riesgo
    sistemático a menudo implica estrategias como la <strong>asignación de activos</strong> y el uso de <strong>instrumentos financieros derivados</strong>
    para protegerse contra pérdidas potenciales.
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Análisis Aplicado: Correlación con el Mercado")

        # Correlation analysis
        returns_df = pd.DataFrame()
        for t in valid_assets:
            if t in data_cache["ind"] and 'log_return' in data_cache["ind"][t].columns:
                returns_df[t] = data_cache["ind"][t]["log_return"]
        if '^GSPC' in data_cache["ind"] and 'log_return' in data_cache["ind"]['^GSPC'].columns:
            returns_df["S&P 500"] = data_cache["ind"]["^GSPC"]["log_return"]

        if not returns_df.empty:
            corr = returns_df.corr()
            fig_corr = px.imshow(corr, text_auto='.2f', color_continuous_scale=['#0a0e27', '#7c3aed', '#ec4899'],
                                 title="Matriz de Correlación — Riesgo Sistemático Compartido")
            styled_fig(fig_corr)
            st.plotly_chart(fig_corr, use_container_width=True)

            st.markdown("""
            <div class="key-insight">
            <strong>🔍 Interpretación:</strong> Las correlaciones altas con el S&P 500 indican un mayor <strong>riesgo sistemático</strong>.
            Activos con correlación cercana a 0 o negativa (como las criptomonedas) aportan <strong>diversificación real</strong> al portafolio,
            aunque pueden tener alto riesgo idiosincrático propio.
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: MODELO CAPM
# ═══════════════════════════════════════════════════════════════════
elif "Modelo CAPM" in section:
    st.markdown(f'<div class="lesson-badge">⚖️ Lección 3 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Capital Asset Pricing Model (CAPM)</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El <strong>CAPM</strong> (Capital Asset Pricing Model) es un modelo financiero que establece una relación lineal entre el
    <strong>rendimiento esperado</strong> de un activo y su <strong>riesgo sistemático</strong>, medido por el coeficiente Beta (β).
    Fue desarrollado por William Sharpe (1964), John Lintner (1965) y Jan Mossin (1966).
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        E[Rᵢ] = Rf + βᵢ × (E[Rm] - Rf)
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.markdown("""
    <div class="risk-card">
        <div style="color: var(--accent-cyan); font-weight: 700; margin-bottom: 8px;">📌 E[Rᵢ]</div>
        <div style="color: var(--text-secondary); font-size: 13px;">Rendimiento esperado del activo i</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown("""
    <div class="risk-card">
        <div style="color: var(--accent-green); font-weight: 700; margin-bottom: 8px;">📌 Rf</div>
        <div style="color: var(--text-secondary); font-size: 13px;">Tasa libre de riesgo (T-Bill 13 semanas)</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown("""
    <div class="risk-card">
        <div style="color: var(--accent-pink); font-weight: 700; margin-bottom: 8px;">📌 βᵢ</div>
        <div style="color: var(--text-secondary); font-size: 13px;">Sensibilidad del activo al mercado</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    <strong>Interpretación del Beta:</strong><br>
    • <strong>β > 1:</strong> El activo amplifica los movimientos del mercado (más agresivo).<br>
    • <strong>β = 1:</strong> El activo se mueve exactamente como el mercado.<br>
    • <strong>β < 1:</strong> El activo es más defensivo que el mercado.<br>
    • <strong>β < 0:</strong> El activo se mueve en dirección opuesta al mercado (cobertura natural).
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Análisis CAPM Aplicado a Nuestro Portafolio")

        capm_rows = []
        for v in valid_assets:
            if v in data_cache["capm"] and 'CAPM_Beta' in data_cache["capm"][v].columns:
                row = data_cache["capm"][v].iloc[-1]
                beta = _to_float(row.get('CAPM_Beta', 1.0))
                exp_ret = _to_float(row.get('CAPM_Expected_Return', 0))
                rf = _to_float(row.get('Risk_Free_Rate', 0.04))
                capm_rows.append({
                    "Activo": v,
                    "Beta (β)": round(beta, 4),
                    "Retorno Esperado E[R]": f"{exp_ret*100:.2f}%",
                    "Tasa Rf": f"{rf*100:.2f}%",
                    "Clasificación": "🔴 Agresivo" if beta > 1 else ("🟡 Defensivo" if beta > 0 else "🟢 Cobertura")
                })

        if capm_rows:
            st.table(pd.DataFrame(capm_rows))

            capm_df = pd.DataFrame(capm_rows)
            fig_capm = go.Figure()
            colors = ['#7c3aed' if b > 1 else ('#f59e0b' if b > 0 else '#10b981')
                      for b in [r["Beta (β)"] for r in capm_rows]]
            fig_capm.add_trace(go.Bar(
                x=[r["Activo"] for r in capm_rows],
                y=[r["Beta (β)"] for r in capm_rows],
                marker_color=colors,
                text=[f'β={r["Beta (β)"]:.2f}' for r in capm_rows],
                textposition='outside',
                textfont=dict(color='#f1f5f9')
            ))
            fig_capm.add_hline(y=1, line_dash="dash", line_color="#ef4444", annotation_text="β = 1 (Mercado)")
            fig_capm.add_hline(y=0, line_dash="dot", line_color="#64748b")
            styled_fig(fig_capm, "Coeficiente Beta por Activo — Sensibilidad al Mercado")
            fig_capm.update_layout(yaxis_title="Beta (β)", xaxis_title="Activo")
            st.plotly_chart(fig_capm, use_container_width=True)

            # ── Scatter: retornos activo vs mercado con línea de regresión ──
            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
            st.markdown("### 📈 Diagrama de Dispersión: Retornos del Activo vs S&P 500")

            sel_capm = st.selectbox("Seleccionar activo para scatter CAPM:", valid_assets, key="sel_capm")
            if sel_capm and "^GSPC" in data_cache["ind"] and sel_capm in data_cache["ind"]:
                mkt_ret = data_cache["ind"]["^GSPC"]["log_return"].dropna()
                asset_ret = data_cache["ind"][sel_capm]["log_return"].dropna()
                aligned_capm = pd.concat([asset_ret, mkt_ret], axis=1, join="inner").dropna()
                aligned_capm.columns = ["Asset", "Market"]

                if len(aligned_capm) > 10:
                    slope, intercept, r_value, p_value, _ = stats.linregress(
                        aligned_capm["Market"], aligned_capm["Asset"]
                    )
                    r2 = r_value ** 2
                    x_line = pd.Series([aligned_capm["Market"].min(), aligned_capm["Market"].max()])
                    y_line = intercept + slope * x_line

                    fig_scatter = go.Figure()
                    fig_scatter.add_trace(go.Scatter(
                        x=aligned_capm["Market"] * 100,
                        y=aligned_capm["Asset"] * 100,
                        mode='markers',
                        marker=dict(size=4, color='#7c3aed', opacity=0.5),
                        name='Retornos diarios'
                    ))
                    fig_scatter.add_trace(go.Scatter(
                        x=x_line * 100,
                        y=y_line * 100,
                        mode='lines',
                        line=dict(color='#ec4899', width=2.5),
                        name=f'Regresión OLS (β={slope:.3f})'
                    ))
                    fig_scatter.add_hline(y=0, line_dash="dot", line_color="#475569", line_width=1)
                    fig_scatter.add_vline(x=0, line_dash="dot", line_color="#475569", line_width=1)
                    styled_fig(fig_scatter, f"Scatter CAPM: {sel_capm} vs S&P 500")
                    fig_scatter.update_layout(
                        xaxis_title="Retorno S&P 500 (%)",
                        yaxis_title=f"Retorno {sel_capm} (%)",
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)

                    c_s1, c_s2, c_s3 = st.columns(3)
                    c_s1.metric("Beta (β) OLS", f"{slope:.4f}")
                    c_s2.metric("R² (ajuste)", f"{r2:.4f}")
                    c_s3.metric("p-valor (β)", f"{p_value:.4e}")

                    st.markdown(f"""
                    <div class="key-insight">
                    <strong>🔍 Interpretación — {sel_capm}:</strong><br>
                    β = <strong>{slope:.3f}</strong>: {'amplifica los movimientos del mercado (activo agresivo)' if slope > 1 else ('se mueve en dirección opuesta al mercado (cobertura natural)' if slope < 0 else 'es más defensivo que el mercado')}.<br>
                    R² = <strong>{r2:.3f}</strong>: el S&P 500 explica el <strong>{r2*100:.1f}%</strong> de la variabilidad de los retornos de {sel_capm}.
                    {'El bajo R² confirma que este activo tiene fuerte componente de riesgo idiosincrático.' if r2 < 0.3 else 'El alto R² indica alta correlación con el ciclo de mercado.'}
                    </div>
                    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: RIESGO NO SISTEMÁTICO
# ═══════════════════════════════════════════════════════════════════
elif "Riesgo No Sistemático" in section:
    st.markdown(f'<div class="lesson-badge">🛡️ Lección 4 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Riesgo No Sistemático (Diversificable)</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El <strong>riesgo no sistemático</strong>, también llamado riesgo específico, riesgo diversificable o riesgo idiosincrático,
    es el riesgo que afecta exclusivamente a una empresa, sector o industria particular.
    A diferencia del riesgo sistemático, <strong>puede reducirse o eliminarse mediante la diversificación</strong> del portafolio.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        Riesgo Total = Riesgo Sistemático (β²σ²m) + Riesgo No Sistemático (σ²ε)
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    c1.markdown("""
    <div class="risk-card">
        <div style="color: var(--accent-pink); font-weight: 700; margin-bottom: 10px;">📋 Fuentes de Riesgo No Sistemático</div>
        <div style="color: var(--text-secondary); font-size: 14px; line-height: 1.8;">
        • Gestión de la empresa (fraude, malas decisiones)<br>
        • Cambios regulatorios del sector<br>
        • Innovación disruptiva / obsolescencia<br>
        • Problemas de cadena de suministro<br>
        • Litigios legales específicos
        </div>
    </div>""", unsafe_allow_html=True)
    c2.markdown("""
    <div class="risk-card">
        <div style="color: var(--accent-green); font-weight: 700; margin-bottom: 10px;">🛡️ Mitigación por Diversificación</div>
        <div style="color: var(--text-secondary); font-size: 14px; line-height: 1.8;">
        • Invertir en múltiples sectores (tech, banca, aero)<br>
        • Incluir distintas geografías (USA, Asia, LATAM)<br>
        • Mezclar clases de activos (acciones, cripto)<br>
        • Nuestro portafolio: <strong>6 activos en 4 sectores y 3 continentes</strong>
        </div>
    </div>""", unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Volatilidad Individual vs Diversificada")

        vol_data = []
        for t in valid_assets:
            if 'log_return' in data_cache["ind"][t].columns:
                vol = float(data_cache["ind"][t]["log_return"].std()) * np.sqrt(252) * 100
                vol_data.append({"Activo": t, "Volatilidad Anualizada (%)": round(vol, 2)})

        if vol_data:
            fig_vol = go.Figure()
            fig_vol.add_trace(go.Bar(
                x=[d["Activo"] for d in vol_data],
                y=[d["Volatilidad Anualizada (%)"] for d in vol_data],
                marker=dict(color=[d["Volatilidad Anualizada (%)"] for d in vol_data],
                           colorscale=[[0, '#10b981'], [0.5, '#f59e0b'], [1, '#ef4444']]),
                text=[f'{d["Volatilidad Anualizada (%)"]:.1f}%' for d in vol_data],
                textposition='outside', textfont=dict(color='#f1f5f9')
            ))
            styled_fig(fig_vol, "Volatilidad Anualizada por Activo — Riesgo Individual")
            fig_vol.update_layout(yaxis_title="Volatilidad (%)")
            st.plotly_chart(fig_vol, use_container_width=True)

            st.markdown("""
            <div class="key-insight">
            <strong>💡 Efecto de la Diversificación:</strong> La volatilidad del portafolio diversificado siempre será
            <strong>menor o igual</strong> a la volatilidad promedio de los activos individuales, gracias a las correlaciones
            imperfectas entre ellos. Esto es el principio fundamental detrás de la <strong>Teoría Moderna de Portafolios</strong> de Markowitz.
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: RENDIMIENTOS Y PROPIEDADES EMPÍRICAS
# ═══════════════════════════════════════════════════════════════════
elif "Rendimientos" in section:
    st.markdown(f'<div class="lesson-badge">📈 Lección 5 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Rendimientos y Propiedades Empíricas</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    Los <strong>rendimientos financieros</strong> son la materia prima de todo modelo de riesgo. Antes de ajustar cualquier modelo,
    es esencial caracterizar su distribución: ¿son normales?, ¿tienen colas pesadas?, ¿presentan asimetría?
    Los <strong>hechos estilizados</strong> de los retornos (fat tails, volatility clustering, leptocurtosis) justifican el uso
    de modelos como GARCH y medidas como el CVaR.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        rₜ = ln(Pₜ / Pₜ₋₁) &nbsp;&nbsp;|&nbsp;&nbsp; Retorno simple: rₜ = (Pₜ - Pₜ₋₁) / Pₜ₋₁
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        sel_r = st.selectbox("Seleccione activo:", valid_assets, key="sel_r")
        if sel_r and sel_r in data_cache["ind"]:
            df_r   = data_cache["ind"][sel_r]
            ret    = df_r["log_return"].dropna()
            ret_np = ret.values

            # ── Estadísticas descriptivas ──
            mu    = float(ret.mean())
            sigma = float(ret.std())
            sk    = float(ret.skew())
            ku    = float(ret.kurtosis())

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Media diaria",    f"{mu*100:.4f}%")
            c2.metric("Desv. Estándar",  f"{sigma*100:.4f}%")
            c3.metric("Sesgo",           f"{sk:.4f}")
            c4.metric("Curtosis exceso", f"{ku:.4f}")

            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

            tab1, tab2, tab3 = st.tabs(["📊 Histograma", "📐 Q-Q Plot", "📦 Boxplot"])

            with tab1:
                # Histograma con curva normal superpuesta
                fig_h = go.Figure()
                fig_h.add_trace(go.Histogram(
                    x=ret_np, nbinsx=60, histnorm='probability density',
                    marker_color='#7c3aed', opacity=0.7, name='Retornos observados'
                ))
                x_line = np.linspace(ret.min(), ret.max(), 200)
                pdf    = stats.norm.pdf(x_line, mu, sigma)
                fig_h.add_trace(go.Scatter(
                    x=x_line, y=pdf, mode='lines',
                    line=dict(color='#ec4899', width=2.5), name='Normal teórica'
                ))
                styled_fig(fig_h, f"Distribución de Retornos Logarítmicos — {sel_r}")
                fig_h.update_layout(xaxis_title="Retorno", yaxis_title="Densidad")
                st.plotly_chart(fig_h, use_container_width=True)

            with tab2:
                # Q-Q Plot
                (osm, osr), (slope, intercept, _) = stats.probplot(ret_np, dist="norm")
                fig_qq = go.Figure()
                fig_qq.add_trace(go.Scatter(
                    x=osm, y=osr, mode='markers',
                    marker=dict(color='#7c3aed', size=4, opacity=0.6), name='Cuantiles observados'
                ))
                fig_qq.add_trace(go.Scatter(
                    x=[float(osm[0]), float(osm[-1])],
                    y=[slope*float(osm[0])+intercept, slope*float(osm[-1])+intercept],
                    mode='lines', line=dict(color='#ec4899', width=2), name='Línea normal teórica'
                ))
                styled_fig(fig_qq, f"Q-Q Plot — {sel_r} vs Distribución Normal")
                fig_qq.update_layout(xaxis_title="Cuantiles teóricos", yaxis_title="Cuantiles observados")
                st.plotly_chart(fig_qq, use_container_width=True)
                st.markdown("""
                <div class="key-insight">
                <strong>Lectura del Q-Q Plot:</strong> Si los puntos caen sobre la línea recta, los retornos son normales.
                Las <strong>colas que se alejan hacia arriba/abajo</strong> indican leptocurtosis (eventos extremos más frecuentes de lo normal).
                </div>""", unsafe_allow_html=True)

            with tab3:
                # Boxplot
                fig_box = go.Figure()
                fig_box.add_trace(go.Box(
                    y=ret_np*100, name=sel_r,
                    marker_color='#7c3aed', line_color='#ec4899',
                    boxpoints='outliers', jitter=0.3
                ))
                styled_fig(fig_box, f"Boxplot de Retornos Diarios — {sel_r} (%)")
                fig_box.update_layout(yaxis_title="Retorno (%)")
                st.plotly_chart(fig_box, use_container_width=True)

            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
            st.markdown("### 🧪 Tests de Normalidad")

            jb_stat, jb_p = stats.jarque_bera(ret_np)
            sw_stat, sw_p = stats.shapiro(ret_np[:5000])

            jb_ok = jb_p > 0.05
            sw_ok = sw_p > 0.05

            c1, c2 = st.columns(2)
            c1.markdown(f"""
            <div class="risk-card" style="border-left: 4px solid {'#10b981' if jb_ok else '#ef4444'};">
                <div style="font-weight:700; color:{'#10b981' if jb_ok else '#ef4444'};">Test Jarque-Bera</div>
                <div style="color:var(--text-secondary); font-size:13px; margin-top:6px;">
                Estadístico: <strong>{jb_stat:.4f}</strong><br>
                p-valor: <strong>{jb_p:.4f}</strong><br>
                Resultado: <strong>{'✅ No rechaza normalidad' if jb_ok else '❌ Rechaza normalidad'}</strong>
                </div>
            </div>""", unsafe_allow_html=True)
            c2.markdown(f"""
            <div class="risk-card" style="border-left: 4px solid {'#10b981' if sw_ok else '#ef4444'};">
                <div style="font-weight:700; color:{'#10b981' if sw_ok else '#ef4444'};">Test Shapiro-Wilk</div>
                <div style="color:var(--text-secondary); font-size:13px; margin-top:6px;">
                Estadístico: <strong>{sw_stat:.4f}</strong><br>
                p-valor: <strong>{sw_p:.4f}</strong><br>
                Resultado: <strong>{'✅ No rechaza normalidad' if sw_ok else '❌ Rechaza normalidad'}</strong>
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="key-insight" style="margin-top:16px;">
            <strong>🔍 Hechos Estilizados de {sel_r}:</strong><br>
            {'• <strong>Curtosis = ' + f'{ku:.2f}' + '</strong> > 3 → distribución leptocúrtica (colas más pesadas que la normal). Los eventos extremos son más frecuentes de lo que predice la curva de Gauss.<br>' if ku > 0 else ''}
            {'• <strong>Sesgo negativo (' + f'{sk:.2f}' + ')</strong> → asimetría hacia pérdidas: caídas más severas que subidas equivalentes.<br>' if sk < -0.1 else ('• <strong>Sesgo positivo (' + f'{sk:.2f}' + ')</strong> → distribución sesgada a la derecha.<br>' if sk > 0.1 else '')}
            {'• Ambos tests rechazan normalidad → justifica el uso de GARCH y CVaR sobre el VaR paramétrico normal.' if not jb_ok or not sw_ok else '• Los tests no rechazan normalidad a α=5%, aunque la curtosis sugiere precaución con eventos de cola.'}
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: VALOR EN RIESGO (VaR)
# ═══════════════════════════════════════════════════════════════════
elif "Valor en Riesgo" in section and "No Paramétrico" not in section:
    st.markdown(f'<div class="lesson-badge">📉 Lección 5 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Valor en Riesgo (Value at Risk — VaR)</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El <strong>Valor en Riesgo (VaR)</strong> es una medida estadística que cuantifica la <strong>pérdida máxima esperada</strong>
    de una inversión o portafolio, para un nivel de confianza dado y durante un horizonte temporal específico.
    Es la herramienta estándar de la industria financiera para medir riesgo de mercado.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        VaR(α) = μ - Zα × σ &nbsp;&nbsp;|&nbsp;&nbsp; P(ΔP ≤ -VaR) = 1 - α
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    <strong>Tres metodologías principales:</strong><br><br>
    <strong>1. VaR Paramétrico (Normal):</strong> Asume que los retornos siguen una distribución normal. Usa la media (μ) y desviación estándar (σ)
    de los retornos históricos junto con el z-score correspondiente al nivel de confianza.<br><br>
    <strong>2. VaR Histórico:</strong> No asume ninguna distribución. Ordena los retornos históricos y toma el percentil correspondiente.
    Es más robusto ante distribuciones con colas pesadas.<br><br>
    <strong>3. VaR Monte Carlo:</strong> Simula miles de escenarios posibles usando generación de números aleatorios basados en los parámetros estadísticos
    observados. Nuestro modelo usa 10,000 simulaciones.
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Resultados VaR para Nuestro Portafolio")

        # ── Tabla comparativa: siempre muestra 95% Y 99% ──
        var_data = []
        for v in valid_assets:
            dv = data_cache["var"].get(v)
            if dv is not None and 'VaR_95_Param' in dv.columns:
                row = dv.iloc[-1]
                var_data.append({
                    "Activo": v,
                    "VaR 95% Param.": f"{_to_float(row.get('VaR_95_Param', 0))*100:.2f}%",
                    "VaR 99% Param.": f"{_to_float(row.get('VaR_99_Param', 0))*100:.2f}%",
                    "VaR 95% Hist.":  f"{_to_float(row.get('VaR_95_Hist',  0))*100:.2f}%",
                    "VaR 99% Hist.":  f"{_to_float(row.get('VaR_99_Hist',  0))*100:.2f}%",
                    "VaR 95% MC":     f"{_to_float(row.get('VaR_95_MC',    0))*100:.2f}%",
                    "VaR 99% MC":     f"{_to_float(row.get('VaR_99_MC',    0))*100:.2f}%",
                    "CVaR 95%":       f"{_to_float(row.get('CVaR_95',       0))*100:.2f}%",
                    "CVaR 99%":       f"{_to_float(row.get('CVaR_99',       0))*100:.2f}%",
                })
        if var_data:
            st.markdown("**Tabla comparativa — VaR al 95% y 99% por los tres métodos + CVaR**")
            st.dataframe(pd.DataFrame(var_data), use_container_width=True, hide_index=True)

            # Chart: comparación de métodos al nivel seleccionado en sidebar
            var_chart_data = []
            for v in valid_assets:
                dv = data_cache["var"].get(v)
                if dv is not None and 'VaR_95_Param' in dv.columns:
                    row = dv.iloc[-1]
                    suffix = "99" if confidence >= 0.99 else "95"
                    var_chart_data.append({
                        "Activo": v,
                        "VaR Paramétrico": abs(_to_float(row.get(f'VaR_{suffix}_Param', 0)))*100,
                        "VaR Histórico":   abs(_to_float(row.get(f'VaR_{suffix}_Hist',  0)))*100,
                        "VaR Monte Carlo": abs(_to_float(row.get(f'VaR_{suffix}_MC',    0)))*100,
                    })
            if var_chart_data:
                df_var_chart = pd.DataFrame(var_chart_data)
                fig_var = go.Figure()
                fig_var.add_trace(go.Bar(name='Paramétrico', x=df_var_chart['Activo'], y=df_var_chart['VaR Paramétrico'], marker_color='#7c3aed'))
                fig_var.add_trace(go.Bar(name='Histórico',   x=df_var_chart['Activo'], y=df_var_chart['VaR Histórico'],   marker_color='#ec4899'))
                fig_var.add_trace(go.Bar(name='Monte Carlo', x=df_var_chart['Activo'], y=df_var_chart['VaR Monte Carlo'], marker_color='#06b6d4'))
                fig_var.update_layout(barmode='group')
                styled_fig(fig_var, f"Comparación de Métodos VaR al {confidence*100:.0f}% de Confianza")
                fig_var.update_layout(yaxis_title="Pérdida Máxima Esperada (%)")
                st.plotly_chart(fig_var, use_container_width=True)

        st.markdown("""
        <div class="key-insight">
        <strong>🔍 Interpretación:</strong> Un VaR del -3.80% al 95% significa que, bajo condiciones normales de mercado,
        <strong>solo en 1 de cada 20 días</strong> la pérdida superará ese nivel. El CVaR (Expected Shortfall) mide el promedio de
        pérdidas en ese 5% de peores días, dando una imagen más completa del riesgo de cola.
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: VaR NO PARAMÉTRICO
# ═══════════════════════════════════════════════════════════════════
elif "VaR No Paramétrico" in section:
    st.markdown(f'<div class="lesson-badge">🎰 Lección 6 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">VaR No Paramétrico</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El <strong>VaR No Paramétrico</strong> (o VaR Histórico) es el enfoque más intuitivo y libre de supuestos distributivos.
    En lugar de asumir que los retornos siguen una distribución normal, utiliza directamente la <strong>distribución empírica</strong>
    de los datos observados.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        VaR_hist(α) = Percentil(retornos, (1-α) × 100)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    <strong>Ventajas:</strong><br>
    • No requiere supuestos sobre la forma de la distribución<br>
    • Captura naturalmente las colas pesadas y asimetrías<br>
    • Fácil de implementar y explicar<br><br>
    <strong>Desventajas:</strong><br>
    • Depende de la calidad y cantidad de datos históricos<br>
    • Asume que el pasado es representativo del futuro<br>
    • Sensible a outliers (eventos extremos pasados)
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Distribución de Retornos — Análisis No Paramétrico")

        sel_np = st.selectbox("Seleccione activo:", valid_assets, key="sel_np")
        if sel_np and sel_np in data_cache["ind"]:
            returns = data_cache["ind"][sel_np]["log_return"].dropna()
            var_hist = float(np.percentile(returns, (1 - confidence) * 100))

            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(x=returns, nbinsx=60, marker_color='#7c3aed', opacity=0.7, name='Retornos'))
            fig_hist.add_vline(x=var_hist, line_dash="dash", line_color="#ef4444", line_width=2,
                              annotation_text=f"VaR {confidence*100:.0f}%: {var_hist*100:.2f}%",
                              annotation_font_color="#ef4444")
            styled_fig(fig_hist, f"Distribución de Retornos Logarítmicos — {sel_np}")
            fig_hist.update_layout(xaxis_title="Retorno Logarítmico", yaxis_title="Frecuencia")
            st.plotly_chart(fig_hist, use_container_width=True)

            # Stats
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Media", f"{float(returns.mean())*100:.4f}%")
            c2.metric("Desv. Estándar", f"{float(returns.std())*100:.4f}%")
            c3.metric("Sesgo (Skewness)", f"{float(returns.skew()):.4f}")
            c4.metric("Curtosis", f"{float(returns.kurtosis()):.4f}")

            st.markdown(f"""
            <div class="key-insight">
            <strong>🔍 Análisis de {sel_np}:</strong> La curtosis de <strong>{float(returns.kurtosis()):.2f}</strong>
            {'es superior a 3 (distribución normal), lo que indica <strong>colas pesadas</strong> — los eventos extremos son más frecuentes de lo que predice una distribución normal. Esto justifica el uso de métodos no paramétricos.' if float(returns.kurtosis()) > 3 else 'es cercana a 3, lo que sugiere una distribución aproximadamente normal.'}
            El sesgo de <strong>{float(returns.skew()):.2f}</strong> {'indica asimetría negativa (caídas más severas que alzas).' if float(returns.skew()) < 0 else 'indica asimetría positiva (alzas más frecuentes que caídas extremas).'}
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: SIMULACIÓN HISTÓRICA
# ═══════════════════════════════════════════════════════════════════
elif "Simulación Histórica" in section:
    st.markdown(f'<div class="lesson-badge">📜 Lección 7 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Simulación Histórica</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    La <strong>simulación histórica</strong> es una técnica de valoración de riesgo que utiliza los retornos pasados reales
    para generar una distribución de pérdidas y ganancias potenciales. Se basa en el principio de que
    <strong>los patrones de mercado tienden a repetirse</strong>, y que las distribuciones empíricas contienen
    información valiosa sobre la estructura del riesgo.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    <strong>Procedimiento:</strong><br>
    1. Recopilar una serie temporal de retornos históricos (mínimo 252 días = 1 año bursátil)<br>
    2. Aplicar los retornos históricos al valor actual del portafolio<br>
    3. Ordenar los resultados de menor a mayor para construir la distribución<br>
    4. Extraer el percentil correspondiente al nivel de confianza como VaR
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Ventana Móvil de Retornos Históricos")

        sel_sh = st.selectbox("Seleccione activo:", valid_assets, key="sel_sh")
        if sel_sh and sel_sh in data_cache["ind"]:
            df_sh = data_cache["ind"][sel_sh].copy()
            if 'log_return' in df_sh.columns:
                # Rolling VaR
                rolling_var = df_sh['log_return'].rolling(60).quantile(1 - confidence)
                fig_sh = go.Figure()
                fig_sh.add_trace(go.Scatter(x=df_sh.index, y=df_sh['log_return']*100, mode='lines',
                                           name='Retorno Diario (%)', line=dict(color='#7c3aed', width=1)))
                fig_sh.add_trace(go.Scatter(x=df_sh.index, y=rolling_var*100, mode='lines',
                                           name=f'VaR Histórico Móvil (60d)', line=dict(color='#ef4444', width=2, dash='dash')))
                styled_fig(fig_sh, f"Retornos Diarios vs VaR Histórico Móvil — {sel_sh}")
                fig_sh.update_layout(yaxis_title="Retorno (%)", xaxis_title="Fecha")
                st.plotly_chart(fig_sh, use_container_width=True)

                # Count breaches
                breaches = (df_sh['log_return'] < rolling_var).sum()
                total = len(df_sh['log_return'].dropna())
                st.markdown(f"""
                <div class="key-insight">
                <strong>📊 Brechas del VaR:</strong> En {total} observaciones, el retorno cayó por debajo del VaR histórico
                en <strong>{breaches} días</strong> ({breaches/total*100:.2f}%). El valor esperado teórico es {(1-confidence)*100:.0f}%
                ({total*(1-confidence):.0f} días). {'✅ El modelo es consistente.' if abs(breaches/total - (1-confidence)) < 0.02 else '⚠️ Diferencia detectada — revisar calibración.'}
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: SIMULACIÓN BOOTSTRAP
# ═══════════════════════════════════════════════════════════════════
elif "Simulación Bootstrap" in section:
    st.markdown(f'<div class="lesson-badge">🔄 Lección 8 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Simulación Bootstrap</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El <strong>Bootstrap</strong> es una técnica de remuestreo que consiste en generar múltiples muestras nuevas
    a partir de los datos originales, <strong>con reemplazo</strong>. Cada muestra bootstrap tiene el mismo tamaño
    que los datos originales, pero algunos valores se repiten y otros se omiten.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        VaR_boot = Promedio[ Percentil(muestra_b, α) ] &nbsp;&nbsp; para b = 1, 2, ..., B
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Simulación Bootstrap — Distribución del VaR")

        sel_bs = st.selectbox("Seleccione activo:", valid_assets, key="sel_bs")
        if sel_bs and sel_bs in data_cache["ind"]:
            returns = data_cache["ind"][sel_bs]["log_return"].dropna().values

            n_bootstrap = 5000
            bootstrap_vars = []
            for _ in range(n_bootstrap):
                sample = np.random.choice(returns, size=len(returns), replace=True)
                bootstrap_vars.append(np.percentile(sample, (1 - confidence) * 100))

            bv = np.array(bootstrap_vars) * 100
            mean_var = float(np.mean(bootstrap_vars))
            ic_low  = float(np.percentile(bootstrap_vars, 2.5))
            ic_high = float(np.percentile(bootstrap_vars, 97.5))

            # Número óptimo de bins: regla de Sturges (log2(n)+1) redondeado
            n_bins = max(20, int(np.log2(n_bootstrap) + 1))

            fig_bs = go.Figure()
            fig_bs.add_trace(go.Histogram(
                x=bv, nbinsx=n_bins,
                marker_color='#ec4899', opacity=0.75,
                name=f'Bootstrap VaR ({n_bootstrap:,} muestras)'
            ))
            fig_bs.add_vline(x=mean_var*100, line_dash="dash", line_color="#06b6d4", line_width=2,
                             annotation_text=f"Media: {mean_var*100:.2f}%", annotation_font_color="#06b6d4")
            fig_bs.add_vline(x=ic_low*100,  line_dash="dot", line_color="#f59e0b", line_width=1.5,
                             annotation_text=f"IC inf: {ic_low*100:.2f}%", annotation_font_color="#f59e0b")
            fig_bs.add_vline(x=ic_high*100, line_dash="dot", line_color="#10b981", line_width=1.5,
                             annotation_text=f"IC sup: {ic_high*100:.2f}%", annotation_font_color="#10b981")
            styled_fig(fig_bs, f"Distribución Bootstrap del VaR — {sel_bs} ({n_bootstrap:,} remuestreos)")
            fig_bs.update_layout(xaxis_title="VaR (%)", yaxis_title="Frecuencia")
            st.plotly_chart(fig_bs, use_container_width=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("VaR Promedio Bootstrap", f"{mean_var*100:.4f}%")
            c2.metric("IC 95% Inferior", f"{ic_low*100:.4f}%")
            c3.metric("IC 95% Superior", f"{ic_high*100:.4f}%")

            # Detectar bimodalidad para interpretación
            hist_counts, _ = np.histogram(bv, bins=n_bins)
            peaks, _ = find_peaks(hist_counts, height=n_bootstrap * 0.03)
            bimodal_note = ""
            if len(peaks) >= 2:
                bimodal_note = f"<br><strong>⚠️ Distribución bimodal detectada ({len(peaks)} picos):</strong> el activo {sel_bs} presenta <strong>dos regímenes de volatilidad</strong> en el período analizado — uno de baja volatilidad (VaR ≈ {bv.max():.2f}%) y otro de alta (VaR ≈ {bv.min():.2f}%). Esto es consistente con la presencia de <em>volatility clustering</em> capturado por el modelo GARCH."

            st.markdown(f"""
            <div class="key-insight">
            <strong>🔍 Interpretación:</strong> El intervalo de confianza del 95% para el VaR de <strong>{sel_bs}</strong> va de
            <strong>{ic_low*100:.2f}%</strong> a <strong>{ic_high*100:.2f}%</strong>.
            Esto mide la <strong>incertidumbre estadística</strong> del estimador VaR. Un intervalo ancho indica mayor incertidumbre.{bimodal_note}
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: EXPECTED SHORTFALL (CVaR)
# ═══════════════════════════════════════════════════════════════════
elif "Expected Shortfall" in section:
    st.markdown(f'<div class="lesson-badge">💀 Lección 9 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Expected Shortfall (CVaR — Conditional Value at Risk)</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El <strong>Expected Shortfall (ES)</strong>, también conocido como <strong>CVaR</strong> o <strong>Tail VaR</strong>,
    responde a la pregunta: <strong>"Si las cosas van mal, ¿qué tan mal pueden ir?"</strong>.
    Mide la <strong>pérdida promedio esperada</strong> en los escenarios que superan el VaR, es decir,
    en el peor (1-α)% de los casos.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        ES(α) = E[ L | L > VaR(α) ] = (1/(1-α)) ∫ᵅ¹ VaR(u) du
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    <strong>¿Por qué el CVaR es superior al VaR?</strong><br><br>
    • El VaR solo nos dice <strong>dónde empieza</strong> la zona de peligro<br>
    • El CVaR nos dice <strong>cuánta sangre hay</strong> dentro de esa zona de peligro<br>
    • El CVaR es una medida <strong>coherente de riesgo</strong> (cumple subaditividad), mientras que el VaR no lo es<br>
    • Reguladores como <strong>Basilea III</strong> han adoptado el ES como la medida preferida de riesgo
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Comparación VaR vs CVaR por Activo")

        var_cvar_data = []
        for v in valid_assets:
            if v in data_cache["var"] and 'VaR_95_Hist' in data_cache["var"][v].columns:
                row = data_cache["var"][v].iloc[-1]
                var_val = abs(_to_float(row.get('VaR_95_Hist', 0))) * 100
                cvar_val = abs(_to_float(row.get('CVaR_95', 0))) * 100
                var_cvar_data.append({"Activo": v, "VaR": var_val, "CVaR": cvar_val, "Exceso CVaR": round(cvar_val - var_val, 2)})

        if var_cvar_data:
            fig_cvar = go.Figure()
            fig_cvar.add_trace(go.Bar(name='VaR', x=[d["Activo"] for d in var_cvar_data],
                                     y=[d["VaR"] for d in var_cvar_data], marker_color='#f59e0b'))
            fig_cvar.add_trace(go.Bar(name='CVaR (ES)', x=[d["Activo"] for d in var_cvar_data],
                                     y=[d["CVaR"] for d in var_cvar_data], marker_color='#ef4444'))
            fig_cvar.update_layout(barmode='group')
            styled_fig(fig_cvar, "VaR vs Expected Shortfall — Profundidad del Riesgo de Cola")
            fig_cvar.update_layout(yaxis_title="Pérdida (%)")
            st.plotly_chart(fig_cvar, use_container_width=True)

            st.markdown(f"""
            <div class="key-insight">
            <strong>🔍 Análisis de Colas:</strong> El activo con mayor <strong>riesgo de cola</strong> es
            <strong>{max(var_cvar_data, key=lambda x: x['CVaR'])['Activo']}</strong> con un CVaR de
            <strong>{max(var_cvar_data, key=lambda x: x['CVaR'])['CVaR']:.2f}%</strong>. Esto significa que, en promedio,
            cuando las cosas van mal para este activo, la pérdida esperada alcanza ese nivel.
            El diferencial entre CVaR y VaR indica qué tan <strong>"profundo es el pozo"</strong> más allá del límite de riesgo.
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: SIMULACIÓN MONTECARLO
# ═══════════════════════════════════════════════════════════════════
elif "Simulación Montecarlo" in section:
    st.markdown(f'<div class="lesson-badge">🎲 Lección 10 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Simulación Montecarlo para el Cálculo del VaR</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    La <strong>simulación Monte Carlo</strong> es una técnica computacional que genera miles de escenarios posibles
    para el comportamiento futuro de un activo, basándose en los parámetros estadísticos observados (media y volatilidad).
    Es especialmente útil cuando la distribución de retornos no es normal o cuando el portafolio tiene instrumentos complejos.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        S(t+1) = S(t) × exp[(μ - σ²/2)Δt + σ√Δt × Z] &nbsp;&nbsp; donde Z ~ N(0,1)
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        sel_mc = st.selectbox("Seleccione activo:", valid_assets, key="sel_mc")
        if sel_mc and sel_mc in data_cache["ind"]:
            df_mc = data_cache["ind"][sel_mc]
            returns_mc = df_mc['log_return'].dropna()
            mu = float(returns_mc.mean())
            sigma = float(returns_mc.std())
            last_price = float(df_mc['Close'].iloc[-1])

            # Simulate 30 days ahead, 500 paths
            n_sims = 500
            n_days = 30
            simulated_prices = np.zeros((n_sims, n_days))
            for i in range(n_sims):
                prices = [last_price]
                for d in range(n_days):
                    prices.append(prices[-1] * np.exp(mu + sigma * np.random.randn()))
                simulated_prices[i] = prices[1:]

            fig_mc = go.Figure()
            for i in range(min(100, n_sims)):
                fig_mc.add_trace(go.Scatter(x=list(range(n_days)), y=simulated_prices[i],
                                           mode='lines', opacity=0.15, line=dict(width=1, color='#7c3aed'),
                                           showlegend=False))
            # Mean path
            fig_mc.add_trace(go.Scatter(x=list(range(n_days)), y=np.mean(simulated_prices, axis=0),
                                       mode='lines', line=dict(color='#ec4899', width=3), name='Trayectoria Media'))
            # VaR path
            fig_mc.add_trace(go.Scatter(x=list(range(n_days)), y=np.percentile(simulated_prices, 5, axis=0),
                                       mode='lines', line=dict(color='#ef4444', width=2, dash='dash'), name='Percentil 5% (VaR)'))
            styled_fig(fig_mc, f"Simulación Monte Carlo — {sel_mc} ({n_sims} trayectorias, {n_days} días)")
            fig_mc.update_layout(xaxis_title="Días en el Futuro", yaxis_title="Precio ($)")
            st.plotly_chart(fig_mc, use_container_width=True)

            # Final price distribution
            final_prices = simulated_prices[:, -1]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Precio Actual", f"${last_price:,.2f}")
            c2.metric("Precio Medio (30d)", f"${np.mean(final_prices):,.2f}")
            c3.metric("Peor 5%", f"${np.percentile(final_prices, 5):,.2f}")
            c4.metric("Mejor 5%", f"${np.percentile(final_prices, 95):,.2f}")

# ═══════════════════════════════════════════════════════════════════
# SECTION: BACKTESTING DEL VaR
# ═══════════════════════════════════════════════════════════════════
elif "Backtesting" in section:
    st.markdown(f'<div class="lesson-badge">✅ Lección 11 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Backtesting del VaR — Test de Kupiec</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El <strong>Backtesting</strong> es el proceso de validar la precisión de un modelo de VaR comparando las
    predicciones con los resultados reales. El <strong>Test de Kupiec</strong> (Proportion of Failures — POF)
    evalúa si la proporción de excepciones (días donde la pérdida superó el VaR) es consistente con el nivel de confianza elegido.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        LR_POF = -2ln[(1-p)^(T-N) × p^N] + 2ln[(1-N/T)^(T-N) × (N/T)^N] &nbsp;&nbsp; ~ χ²(1)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    <strong>Criterio de decisión:</strong><br>
    • Si p-value > 0.05: <strong style="color: #10b981;">ACEPTADO</strong> — El modelo es estadísticamente válido<br>
    • Si p-value ≤ 0.05: <strong style="color: #ef4444;">RECHAZADO</strong> — El modelo subestima o sobreestima el riesgo
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📊 Resultados del Test de Kupiec")

        kupiec_data = []
        for v in valid_assets:
            if v in data_cache["var"] and 'Kupiec_Status' in data_cache["var"][v].columns:
                row = data_cache["var"][v].iloc[-1]
                status = _to_str(row.get('Kupiec_Status', 'N/A'))
                exceptions = _to_float(row.get('Kupiec_Exceptions', 0))
                kupiec_data.append({
                    "Activo": v,
                    "Excepciones": int(exceptions),
                    "Status": f"{'✅' if 'Accept' in status else '❌'} {status}",
                    "VaR Histórico": f"{_to_float(row.get('VaR_95_Hist', 0))*100:.2f}%",
                })
        if kupiec_data:
            st.table(pd.DataFrame(kupiec_data))

            all_accepted = all('Accept' in d["Status"] for d in kupiec_data)
            if all_accepted:
                st.markdown("""
                <div class="key-insight">
                <strong>✅ Resultado Global: MODELO VALIDADO</strong><br>
                Todos los activos pasan el Test de Kupiec, lo que significa que nuestro cálculo del VaR es
                <strong>matemáticamente honesto</strong>. No estamos subestimando el riesgo ni generando falsa confianza.
                El modelo proporciona una <strong>capa de protección estadísticamente confiable</strong>.
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="key-insight">
                <strong>⚠️ Atención:</strong> Algunos activos no pasan el test de Kupiec. Se recomienda recalibrar los parámetros
                del VaR o considerar modelos alternativos para esos activos.
                </div>
                """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: MODELO GARCH(1,1)
# ═══════════════════════════════════════════════════════════════════
elif "GARCH" in section:
    st.markdown(f'<div class="lesson-badge">🌀 Lección 12 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Modelo GARCH(1,1) — Volatilidad Condicional</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El modelo <strong>GARCH (Generalized Autoregressive Conditional Heteroskedasticity)</strong> captura una propiedad
    fundamental de los mercados: la <strong>volatilidad no es constante</strong>, sino que se agrupa en clusters.
    Períodos de alta volatilidad tienden a seguir a otros períodos de alta volatilidad (volatility clustering).
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        σ²ₜ = ω + α₁ε²ₜ₋₁ + β₁σ²ₜ₋₁
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.markdown("""
    <div class="risk-card">
        <div style="color: var(--accent-cyan); font-weight: 700;">ω (omega)</div>
        <div style="color: var(--text-secondary); font-size: 13px; margin-top: 6px;">Volatilidad base de largo plazo</div>
    </div>""", unsafe_allow_html=True)
    c2.markdown("""
    <div class="risk-card">
        <div style="color: var(--accent-pink); font-weight: 700;">α₁ (alpha)</div>
        <div style="color: var(--text-secondary); font-size: 13px; margin-top: 6px;">Impacto del shock de ayer</div>
    </div>""", unsafe_allow_html=True)
    c3.markdown("""
    <div class="risk-card">
        <div style="color: var(--accent-green); font-weight: 700;">β₁ (beta)</div>
        <div style="color: var(--text-secondary); font-size: 13px; margin-top: 6px;">Persistencia de la volatilidad</div>
    </div>""", unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        sel_g = st.selectbox("Seleccione activo:", valid_assets, key="sel_g")
        if sel_g and sel_g in data_cache["garch"] and 'GARCH_Vol' in data_cache["garch"][sel_g].columns:
            df_g = data_cache["garch"][sel_g]

            # ── Volatilidad condicional GARCH(1,1) ──
            fig_g = go.Figure()
            fig_g.add_trace(go.Scatter(x=df_g.index, y=df_g['GARCH_Vol']*100, mode='lines',
                                       fill='tozeroy', name='Volatilidad GARCH',
                                       line=dict(color='#7c3aed'), fillcolor='rgba(124,58,237,0.2)'))
            styled_fig(fig_g, f"Volatilidad Condicional GARCH(1,1) — {sel_g}")
            fig_g.update_layout(yaxis_title="Volatilidad (%)", xaxis_title="Fecha")
            st.plotly_chart(fig_g, use_container_width=True)

            last_vol = _to_float(df_g['GARCH_Vol'].iloc[-1]) * 100
            last_aic = _to_float(df_g['GARCH_AIC'].iloc[-1])
            avg_vol  = _to_float(df_g['GARCH_Vol'].mean()) * 100

            c1, c2, c3 = st.columns(3)
            c1.metric("Volatilidad Actual",  f"{last_vol:.2f}%")
            c2.metric("Volatilidad Promedio", f"{avg_vol:.2f}%")
            c3.metric("AIC (Calidad)",        f"{last_aic:.2f}")

            regime = "🔴 Alta Volatilidad" if last_vol > avg_vol * 1.5 else ("🟡 Normal" if last_vol > avg_vol * 0.7 else "🟢 Baja")
            st.markdown(f"""
            <div class="key-insight">
            <strong>🔍 Régimen Actual de {sel_g}: {regime}</strong><br>
            Volatilidad actual ({last_vol:.2f}%) vs promedio histórico ({avg_vol:.2f}%).
            La "memoria de volatilidad" indica que los shocks
            {'<strong>persisten varios días</strong> antes de disiparse.' if last_vol > avg_vol else 'se disipan relativamente rápido.'}
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

            # ── Comparación de modelos ──
            st.markdown("### 📋 Comparación de Especificaciones ARCH/GARCH")
            with st.spinner("Ajustando ARCH(1), GARCH(1,1) y GJR-GARCH(1,1)..."):
                cmp_data, forecast_vol, best_res, best_resid = compute_garch_comparison(
                    data_cache["ind"][sel_g]["log_return"]
                )

            if cmp_data:
                import pandas as _pd
                df_cmp = _pd.DataFrame(cmp_data)[["Modelo", "Log-Likelihood", "AIC", "BIC", "Params", "Mejor"]]
                st.table(df_cmp)
                st.markdown("""
                <div class="key-insight">
                <strong>Criterio de selección:</strong> El modelo con <strong>menor AIC/BIC</strong> ofrece el mejor balance
                entre ajuste y parsimonia. ⭐ marca el modelo óptimo. El <strong>GJR-GARCH</strong> captura el
                <em>efecto apalancamiento</em>: las caídas generan más volatilidad que subidas equivalentes.
                </div>""", unsafe_allow_html=True)

            # ── Diagnóstico de residuos estandarizados ──
            st.markdown("### 🔬 Diagnóstico: Residuos Estandarizados")
            if best_res is not None and best_resid is not None:
                resid_vals = best_resid.values if hasattr(best_resid, 'values') else np.array(best_resid)
                resid_vals = resid_vals[~np.isnan(resid_vals)]

                jb_stat_r, jb_p_r = stats.jarque_bera(resid_vals)

                col1, col2 = st.columns([2, 1])
                with col1:
                    fig_resid = go.Figure()
                    fig_resid.add_trace(go.Scatter(
                        y=resid_vals, mode='lines', line=dict(color='#06b6d4', width=1),
                        name='Residuos Estand.'
                    ))
                    fig_resid.add_hline(y=2,  line_dash="dash", line_color="#f59e0b", opacity=0.6)
                    fig_resid.add_hline(y=-2, line_dash="dash", line_color="#f59e0b", opacity=0.6)
                    styled_fig(fig_resid, "Residuos Estandarizados del Modelo")
                    fig_resid.update_layout(yaxis_title="Residuo / σ")
                    st.plotly_chart(fig_resid, use_container_width=True)
                with col2:
                    jb_ok_r = jb_p_r > 0.05
                    st.markdown(f"""
                    <div class="risk-card" style="margin-top:24px; border-left:4px solid {'#10b981' if jb_ok_r else '#f59e0b'};">
                        <div style="font-weight:700; font-size:14px;">Jarque-Bera (residuos)</div>
                        <div style="color:var(--text-secondary); font-size:13px; margin-top:8px;">
                        Estadístico: <strong>{jb_stat_r:.4f}</strong><br>
                        p-valor: <strong>{jb_p_r:.4f}</strong><br><br>
                        {'✅ Residuos aproximadamente normales' if jb_ok_r else '⚠️ Residuos no normales — el modelo Student-t los maneja correctamente'}
                        </div>
                    </div>""", unsafe_allow_html=True)

            # ── Pronóstico 10 días ──
            if forecast_vol is not None:
                st.markdown("### 🔮 Pronóstico de Volatilidad — 10 Días")
                fig_fc = go.Figure()
                fig_fc.add_trace(go.Scatter(
                    x=list(range(1, 11)), y=forecast_vol * 100,
                    mode='lines+markers',
                    line=dict(color='#10b981', width=2.5),
                    marker=dict(size=8, color='#10b981'),
                    name='Volatilidad pronosticada'
                ))
                fig_fc.add_hline(y=avg_vol, line_dash="dash", line_color="#f59e0b",
                                 annotation_text="Promedio histórico")
                styled_fig(fig_fc, f"Pronóstico de Volatilidad GARCH — {sel_g}")
                fig_fc.update_layout(xaxis_title="Días en el futuro", yaxis_title="Volatilidad (%)")
                st.plotly_chart(fig_fc, use_container_width=True)

                avg_fc = float(np.mean(forecast_vol)) * 100
                st.markdown(f"""
                <div class="key-insight">
                <strong>📅 Pronóstico promedio (próximos 10 días): {avg_fc:.2f}%</strong><br>
                {'La volatilidad pronosticada supera el promedio histórico → entorno de mayor riesgo.' if avg_fc > avg_vol else 'La volatilidad pronosticada está por debajo del promedio → condiciones de mercado estables esperadas.'}
                </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: INDICADORES TÉCNICOS
# ═══════════════════════════════════════════════════════════════════
elif "Indicadores Técnicos" in section:
    st.markdown(f'<div class="lesson-badge">📊 Lección 13 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Indicadores Técnicos</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El <strong>análisis técnico</strong> estudia los patrones de precio y volumen históricos para anticipar movimientos futuros.
    Se implementan los 6 indicadores estándar de la industria:<br><br>
    • <strong>SMA / EMA:</strong> Medias móviles simple y exponencial (tendencia)<br>
    • <strong>RSI:</strong> Oscilador de momentum (sobrecompra/sobreventa)<br>
    • <strong>MACD + Histograma:</strong> Convergencia/divergencia de medias (señal de cruce)<br>
    • <strong>Bandas de Bollinger:</strong> Volatilidad relativa (±2σ)<br>
    • <strong>Oscilador Estocástico (%K / %D):</strong> Posición del precio dentro del rango reciente
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        sel_t = st.selectbox("Seleccione activo:", valid_assets, key="sel_t")
        if sel_t and sel_t in data_cache["ind"]:
            df = data_cache["ind"][sel_t]

            # ── Precio + Medias móviles + Bollinger ──
            fig_tech = go.Figure()
            fig_tech.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Precio', line=dict(color='#f1f5f9', width=1.5)))
            fig_tech.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', line=dict(color='#7c3aed', width=2)))
            fig_tech.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], name='EMA 20', line=dict(color='#ec4899', width=2)))
            if 'BB_Upper' in df.columns:
                fig_tech.add_trace(go.Scatter(x=df.index, y=df['BB_Upper'], name='Bollinger +2σ',
                                              line=dict(color='#06b6d4', width=1, dash='dash'), opacity=0.6))
                fig_tech.add_trace(go.Scatter(x=df.index, y=df['BB_Lower'], name='Bollinger -2σ',
                                              line=dict(color='#06b6d4', width=1, dash='dash'), opacity=0.6,
                                              fill='tonexty', fillcolor='rgba(6,182,212,0.05)'))
            styled_fig(fig_tech, f"Precio · SMA/EMA · Bandas de Bollinger — {sel_t}")
            st.plotly_chart(fig_tech, use_container_width=True)

            # ── RSI ──
            if 'RSI' in df.columns:
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='#06b6d4', width=2)))
                fig_rsi.add_hrect(y0=70, y1=100, fillcolor="rgba(239,68,68,0.1)", line_width=0)
                fig_rsi.add_hrect(y0=0, y1=30, fillcolor="rgba(16,185,129,0.1)", line_width=0)
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ef4444", annotation_text="Sobrecompra (70)")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="#10b981", annotation_text="Sobreventa (30)")
                styled_fig(fig_rsi, f"RSI (14 períodos) — {sel_t}")
                fig_rsi.update_layout(yaxis_title="RSI", yaxis_range=[0, 100])
                st.plotly_chart(fig_rsi, use_container_width=True)

                last_rsi = float(df['RSI'].iloc[-1])
                rsi_status = "🔴 SOBRECOMPRA" if last_rsi > 70 else ("🟢 SOBREVENTA" if last_rsi < 30 else "🟡 NEUTRAL")
                st.markdown(f"""
                <div class="key-insight">
                <strong>RSI Actual {sel_t}: {last_rsi:.1f} — {rsi_status}</strong>
                </div>""", unsafe_allow_html=True)

            # ── MACD con histograma ──
            if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
                fig_macd = go.Figure()
                if 'MACD_Hist' in df.columns:
                    colors_hist = ['#10b981' if v >= 0 else '#ef4444' for v in df['MACD_Hist']]
                    fig_macd.add_trace(go.Bar(x=df.index, y=df['MACD_Hist'], name='Histograma',
                                             marker_color=colors_hist, opacity=0.6))
                fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], name='MACD',
                                             line=dict(color='#7c3aed', width=2)))
                fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], name='Señal',
                                             line=dict(color='#ec4899', width=2)))
                fig_macd.add_hline(y=0, line_color='#64748b', line_width=1)
                styled_fig(fig_macd, f"MACD (12,26,9) con Histograma — {sel_t}")
                st.plotly_chart(fig_macd, use_container_width=True)

            # ── Oscilador Estocástico ──
            if 'STOCH_K' in df.columns and 'STOCH_D' in df.columns:
                fig_stoch = go.Figure()
                fig_stoch.add_trace(go.Scatter(x=df.index, y=df['STOCH_K'], name='%K',
                                              line=dict(color='#f59e0b', width=2)))
                fig_stoch.add_trace(go.Scatter(x=df.index, y=df['STOCH_D'], name='%D',
                                              line=dict(color='#ef4444', width=2, dash='dash')))
                fig_stoch.add_hrect(y0=80, y1=100, fillcolor="rgba(239,68,68,0.1)", line_width=0)
                fig_stoch.add_hrect(y0=0,  y1=20,  fillcolor="rgba(16,185,129,0.1)", line_width=0)
                fig_stoch.add_hline(y=80, line_dash="dash", line_color="#ef4444", annotation_text="Sobrecompra (80)")
                fig_stoch.add_hline(y=20, line_dash="dash", line_color="#10b981", annotation_text="Sobreventa (20)")
                styled_fig(fig_stoch, f"Oscilador Estocástico (%K/%D, 14 períodos) — {sel_t}")
                fig_stoch.update_layout(yaxis_title="%K / %D", yaxis_range=[0, 100])
                st.plotly_chart(fig_stoch, use_container_width=True)

                k_now = float(df['STOCH_K'].iloc[-1])
                d_now = float(df['STOCH_D'].iloc[-1])
                st.markdown(f"""
                <div class="key-insight">
                <strong>Estocástico actual: %K={k_now:.1f} / %D={d_now:.1f}</strong><br>
                {'🔴 Zona de sobrecompra — el precio está cerca del máximo reciente.' if k_now > 80
                else ('🟢 Zona de sobreventa — el precio está cerca del mínimo reciente.' if k_now < 20
                else '🟡 Zona neutral — sin señal extrema.')}
                {'  Un cruce de %K por encima de %D en zona baja genera señal de <strong>COMPRA</strong>.' if k_now < 30 else ''}
                </div>""", unsafe_allow_html=True)
            else:
                st.info("ℹ️ El Oscilador Estocástico requiere columnas High/Low. Verifica que los datos incluyan OHLC completo.")

# ═══════════════════════════════════════════════════════════════════
# SECTION: PORTAFOLIO MARKOWITZ
# ═══════════════════════════════════════════════════════════════════
elif "Portafolio Markowitz" in section:
    st.markdown(f'<div class="lesson-badge">🎯 Lección 14 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Optimización de Portafolio — Frontera Eficiente de Markowitz</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    La <strong>Teoría Moderna de Portafolios</strong> (Harry Markowitz, 1952) establece que un inversor racional
    busca maximizar el retorno esperado para un nivel dado de riesgo. La <strong>frontera eficiente</strong> es la
    curva que contiene todos los portafolios óptimos posibles.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        max SR = (E[Rp] - Rf) / σp &nbsp;&nbsp; sujeto a: Σwᵢ = 1, wᵢ ≥ 0
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        with st.spinner(f"⏳ Optimizando {simulations:,} portafolios aleatorios..."):
            opt_res = optimize_portfolio(data_cache["ind"], num_portfolios=simulations)

        if opt_res:
            fig_ef = go.Figure()
            fig_ef.add_trace(go.Scatter(
                x=opt_res["all_portfolios"]['Volatility']*100,
                y=opt_res["all_portfolios"]['Return']*100,
                mode='markers',
                marker=dict(size=3, color=opt_res["all_portfolios"]['Sharpe'],
                           colorscale=[[0, '#0a0e27'], [0.5, '#7c3aed'], [1, '#ec4899']], showscale=True,
                           colorbar=dict(title=dict(text="Sharpe", font=dict(color='#f1f5f9')), tickfont=dict(color='#f1f5f9'))),
                name='Portafolios', showlegend=False
            ))
            fig_ef.add_trace(go.Scatter(
                x=[opt_res["max_sharpe"]["Volatility"]*100],
                y=[opt_res["max_sharpe"]["Return"]*100],
                mode='markers', marker=dict(color='#10b981', size=18, symbol='star', line=dict(width=2, color='white')),
                name=f'⭐ Max Sharpe ({opt_res["max_sharpe"]["Sharpe"]:.2f})'
            ))
            fig_ef.add_trace(go.Scatter(
                x=[opt_res["min_vol"]["Volatility"]*100],
                y=[opt_res["min_vol"]["Return"]*100],
                mode='markers', marker=dict(color='#06b6d4', size=15, symbol='diamond', line=dict(width=2, color='white')),
                name='💎 Min Volatilidad'
            ))
            styled_fig(fig_ef, f"Frontera Eficiente de Markowitz ({simulations:,} simulaciones)")
            fig_ef.update_layout(xaxis_title="Volatilidad (%)", yaxis_title="Retorno Esperado (%)")
            st.plotly_chart(fig_ef, use_container_width=True)

            # Weights
            st.markdown("### 📋 Asignación Óptima del Portafolio")
            c1, c2 = st.columns([1, 1])
            with c1:
                w = {k: v for k, v in opt_res["max_sharpe"].items() if k not in ['Return', 'Volatility', 'Sharpe']}
                w_df = pd.DataFrame(list(w.items()), columns=['Activo', 'Peso (%)'])
                w_df['Peso (%)'] = (w_df['Peso (%)'] * 100).round(2)
                w_df = w_df.sort_values(by='Peso (%)', ascending=False)
                st.table(w_df)

            with c2:
                fig_pie = go.Figure(data=[go.Pie(
                    labels=w_df['Activo'], values=w_df['Peso (%)'],
                    hole=0.5, marker=dict(colors=['#7c3aed', '#ec4899', '#06b6d4', '#10b981', '#f59e0b', '#ef4444']),
                    textinfo='label+percent', textfont=dict(color='#f1f5f9')
                )])
                styled_fig(fig_pie, "Distribución de Pesos")
                st.plotly_chart(fig_pie, use_container_width=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("Retorno Esperado", f"{opt_res['max_sharpe']['Return']*100:.2f}%")
            c2.metric("Volatilidad", f"{opt_res['max_sharpe']['Volatility']*100:.2f}%")
            c3.metric("Ratio de Sharpe", f"{opt_res['max_sharpe']['Sharpe']:.2f}")

            # ── Selector de retorno objetivo ──
            st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
            st.markdown("### 🎯 Portafolio por Retorno Objetivo")
            all_p = opt_res["all_portfolios"]
            ret_min = float(all_p["Return"].min() * 100)
            ret_max = float(all_p["Return"].max() * 100)
            target_ret = st.slider(
                "Retorno anualizado objetivo (%)",
                min_value=round(ret_min, 1),
                max_value=round(ret_max, 1),
                value=round((ret_min + ret_max) / 2, 1),
                step=0.1,
                key="target_ret"
            )
            # Filtrar portafolios eficientes (mayor Sharpe por nivel de retorno)
            ef_portfolios = all_p.sort_values("Sharpe", ascending=False).drop_duplicates(subset=["Return"])
            closest = all_p.iloc[(all_p["Return"] * 100 - target_ret).abs().argsort()[:1]]
            if not closest.empty:
                cp = closest.iloc[0]
                st.markdown(f"""
                <div class="risk-card" style="border-color:#7c3aed;">
                <strong style="color:#7c3aed;">Portafolio más cercano al objetivo:</strong>
                Retorno ≈ <strong>{cp['Return']*100:.2f}%</strong> · Volatilidad: <strong>{cp['Volatility']*100:.2f}%</strong> · Sharpe: <strong>{cp['Sharpe']:.2f}</strong>
                </div>
                """, unsafe_allow_html=True)
                asset_cols = [c for c in all_p.columns if c not in ['Return', 'Volatility', 'Sharpe']]
                w_target = pd.DataFrame({"Activo": asset_cols, "Peso (%)": [round(cp[a]*100, 2) for a in asset_cols]})
                w_target = w_target.sort_values("Peso (%)", ascending=False)
                st.dataframe(w_target, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: SEÑALES DE TRADING
# ═══════════════════════════════════════════════════════════════════
elif "Señales de Trading" in section:
    st.markdown(f'<div class="lesson-badge">🚦 Lección 15 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Motor de Señales de Trading</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El sistema de señales combina múltiples indicadores técnicos para generar recomendaciones de
    <strong style="color:#10b981;">COMPRA</strong>, <strong style="color:#ef4444;">VENTA</strong> o
    <strong style="color:#f59e0b;">MANTENER</strong>. La lógica integra RSI, MACD y Bandas de Bollinger
    para reducir señales falsas.
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        sel_s = st.selectbox("Ver Señales de:", valid_assets, key="sel_s")

        # ── Umbrales configurables del RSI ──
        st.markdown("**Umbrales RSI configurables:**")
        col_rsi1, col_rsi2 = st.columns(2)
        with col_rsi1:
            rsi_oversold_ui = st.slider("RSI Sobreventa (BUY)", min_value=10, max_value=45, value=30, step=1, key="rsi_os")
        with col_rsi2:
            rsi_overbought_ui = st.slider("RSI Sobrecompra (SELL)", min_value=55, max_value=90, value=70, step=1, key="rsi_ob")

        if sel_s and sel_s in data_cache["ind"]:
            # Recompute signals on-the-fly with user thresholds
            df_recomputed = compute_signals(
                {sel_s: data_cache["ind"][sel_s]},
                rsi_oversold=rsi_oversold_ui,
                rsi_overbought=rsi_overbought_ui
            )
            df_s = df_recomputed[sel_s]
            curr_sig = str(df_s['Final_Signal'].iloc[-1])

            if curr_sig == 'BUY':
                st.markdown('<div class="risk-card" style="border-color: #10b981; background: rgba(16,185,129,0.1);"><span style="font-size:24px;">🟢</span> <strong style="color:#10b981; font-size:18px;">SEÑAL ACTIVA: COMPRA</strong></div>', unsafe_allow_html=True)
            elif curr_sig == 'SELL':
                st.markdown('<div class="risk-card" style="border-color: #ef4444; background: rgba(239,68,68,0.1);"><span style="font-size:24px;">🔴</span> <strong style="color:#ef4444; font-size:18px;">SEÑAL ACTIVA: VENTA</strong></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="risk-card" style="border-color: #f59e0b; background: rgba(245,158,11,0.1);"><span style="font-size:24px;">🟡</span> <strong style="color:#f59e0b; font-size:18px;">SEÑAL ACTIVA: NEUTRAL / MANTENER</strong></div>', unsafe_allow_html=True)

            # Signal vote breakdown
            last_rsi = float(df_s['RSI'].iloc[-1]) if 'RSI' in df_s.columns else 50.0
            last_close = float(df_s['Close'].iloc[-1])
            last_bb_lower = float(df_s['BB_Lower'].iloc[-1]) if 'BB_Lower' in df_s.columns else last_close
            last_bb_upper = float(df_s['BB_Upper'].iloc[-1]) if 'BB_Upper' in df_s.columns else last_close
            last_macd = float(df_s['MACD'].iloc[-1]) if 'MACD' in df_s.columns else 0
            last_macd_sig = float(df_s['MACD_Signal'].iloc[-1]) if 'MACD_Signal' in df_s.columns else 0

            vote_data = {
                "Indicador": ["RSI", "Precio vs BB", "MACD vs Señal", "Golden/Death Cross", "Estocástico"],
                "Valor": [
                    f"{last_rsi:.1f}",
                    f"{last_close:.2f}",
                    f"{last_macd:.4f}",
                    "—",
                    "—",
                ],
                "Voto": [
                    "🟢 BUY" if last_rsi < rsi_oversold_ui else ("🔴 SELL" if last_rsi > rsi_overbought_ui else "⬛ NEUTRAL"),
                    "🟢 BUY" if last_close < last_bb_lower else ("🔴 SELL" if last_close > last_bb_upper else "⬛ NEUTRAL"),
                    "🟢 BUY" if last_macd > last_macd_sig else "🔴 SELL",
                    "—",
                    "—",
                ],
            }
            st.dataframe(pd.DataFrame(vote_data), use_container_width=True, hide_index=True)

            fig_sig = go.Figure()
            fig_sig.add_trace(go.Scatter(x=df_s.index, y=df_s['Close'], name='Precio', line=dict(color='#f1f5f9', width=1.5)))
            if 'BB_Upper' in df_s.columns:
                fig_sig.add_trace(go.Scatter(x=df_s.index, y=df_s['BB_Upper'], name='Bollinger +2σ', line=dict(color='#7c3aed', width=1, dash='dash'), opacity=0.5))
                fig_sig.add_trace(go.Scatter(x=df_s.index, y=df_s['BB_Lower'], name='Bollinger -2σ', line=dict(color='#7c3aed', width=1, dash='dash'), opacity=0.5,
                                            fill='tonexty', fillcolor='rgba(124,58,237,0.05)'))

            b = df_s[df_s['Final_Signal'] == 'BUY']
            s = df_s[df_s['Final_Signal'] == 'SELL']
            fig_sig.add_trace(go.Scatter(x=b.index, y=b['Close'], mode='markers', marker=dict(symbol='triangle-up', size=14, color='#10b981'), name='🟢 Buy'))
            fig_sig.add_trace(go.Scatter(x=s.index, y=s['Close'], mode='markers', marker=dict(symbol='triangle-down', size=14, color='#ef4444'), name='🔴 Sell'))
            styled_fig(fig_sig, f"Precio con Señales de Trading — {sel_s}")
            st.plotly_chart(fig_sig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════
# SECTION: ANÁLISIS MACRO
# ═══════════════════════════════════════════════════════════════════
elif "Análisis Macro" in section:
    st.markdown(f'<div class="lesson-badge">🌍 Lección 16 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Análisis Macro — Benchmark vs Portafolio</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="theory-text">
    El análisis macro compara el rendimiento de nuestro <strong>portafolio optimizado</strong> contra el
    <strong>S&P 500</strong> (^GSPC), el benchmark más utilizado para medir el desempeño del mercado norteamericano.
    El objetivo es generar <strong>Alfa (α)</strong>: retorno excedente ajustado por riesgo.
    </div>
    """, unsafe_allow_html=True)

    if data_cache and valid_assets:
        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        # ── Panel de Indicadores Macroeconómicos ──
        st.markdown("### 🌐 Indicadores Macroeconómicos en Tiempo Real")
        # Tasa libre de riesgo desde ^IRX (ya descargada en el pipeline)
        rf_current = 0.04  # fallback
        if "^IRX" in data_cache["ind"] and 'Close' in data_cache["ind"]["^IRX"].columns:
            try:
                rf_current = float(data_cache["ind"]["^IRX"]["Close"].dropna().iloc[-1]) / 100
            except:
                pass
        elif valid_assets and data_cache["capm"].get(valid_assets[0]) is not None:
            try:
                rf_current = float(data_cache["capm"][valid_assets[0]]["Risk_Free_Rate"].iloc[-1])
            except:
                pass

        # S&P 500 último valor y retorno YTD
        sp500_price = None
        sp500_ytd = None
        if "^GSPC" in data_cache["ind"]:
            sp_df = data_cache["ind"]["^GSPC"]
            try:
                sp500_price = float(sp_df["Close"].iloc[-1])
                first_close = float(sp_df["Close"].iloc[0])
                sp500_ytd = (sp500_price - first_close) / first_close
            except:
                pass

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric(
            "Tasa Libre de Riesgo (^IRX)",
            f"{rf_current*100:.2f}%",
            help="T-Bill 13 semanas EE.UU. obtenida automáticamente vía Yahoo Finance"
        )
        if sp500_price:
            mc2.metric("S&P 500 (último cierre)", f"{sp500_price:,.2f}")
        if sp500_ytd is not None:
            mc3.metric(
                "Retorno S&P 500 (período)",
                f"{sp500_ytd*100:.2f}%",
                delta=f"{sp500_ytd*100:.2f}%",
                delta_color="normal"
            )

        st.markdown("""
        <div class="theory-text" style="margin-top:8px; font-size:13px;">
        <strong>Nota sobre inflación:</strong> El análisis utiliza la tasa del T-Bill (^IRX) como proxy de la tasa libre de riesgo nominal.
        La inflación implícita puede estimarse como la diferencia entre la tasa nominal y la tasa real (TIPS). Para datos de inflación CPI
        en tiempo real, se recomienda consumir la <a href="https://fred.stlouisfed.org/series/CPIAUCSL" target="_blank" style="color:#7c3aed;">API FRED (serie CPIAUCSL)</a>.
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

        try:
            opt_res = optimize_portfolio(data_cache["ind"], num_portfolios=simulations)
            if opt_res:
                macro_weights = {k: v for k, v in opt_res["max_sharpe"].items() if k not in ['Return', 'Volatility', 'Sharpe']}
                m_res = analyze_macro(data_cache["ind"], macro_weights)
                if m_res:
                    df_m = pd.DataFrame({
                        'Mi Portafolio': m_res["portfolio_cumulative"],
                        'S&P 500': m_res["benchmark_cumulative"]
                    }).dropna()

                    fig_macro = go.Figure()
                    fig_macro.add_trace(go.Scatter(x=df_m.index, y=df_m['Mi Portafolio'], name='📈 Mi Portafolio',
                                                   line=dict(color='#7c3aed', width=2.5), fill='tozeroy',
                                                   fillcolor='rgba(124,58,237,0.1)'))
                    fig_macro.add_trace(go.Scatter(x=df_m.index, y=df_m['S&P 500'], name='📊 S&P 500',
                                                   line=dict(color='#ec4899', width=2.5)))
                    styled_fig(fig_macro, "Rendimiento Acumulado: Portafolio Optimizado vs S&P 500")
                    st.plotly_chart(fig_macro, use_container_width=True)

                    alfa = opt_res['max_sharpe']['Return'] - (m_res['benchmark_sharpe'] * opt_res['max_sharpe']['Volatility'])
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Alfa (α)", f"{alfa:.2%}")
                    c2.metric("Sharpe Portafolio", f"{opt_res['max_sharpe']['Sharpe']:.2f}")
                    c3.metric("Sharpe S&P 500", f"{m_res['benchmark_sharpe']:.2f}")

                    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

                    # ── Métricas adicionales de gestión activa ──
                    c4, c5, c6 = st.columns(3)
                    te = m_res.get("tracking_error", 0)
                    ir = m_res.get("information_ratio", 0)
                    md = m_res.get("max_drawdown", 0)
                    port_ann = m_res.get("port_ann_return", 0)
                    bench_ann = m_res.get("bench_ann_return", 0)

                    c4.metric("Tracking Error (anual)", f"{te:.2%}",
                              help="Desviación estándar anualizada del exceso de retorno del portafolio vs benchmark.")
                    c5.metric("Information Ratio", f"{ir:.2f}",
                              help="Retorno activo anual dividido entre el Tracking Error. IR > 0.5 se considera bueno.")
                    c6.metric("Máximo Drawdown", f"{md:.2%}",
                              help="Mayor caída desde un máximo en el período analizado.")

                    c7, c8 = st.columns(2)
                    c7.metric("Retorno Anualizado Portafolio", f"{port_ann:.2%}")
                    c8.metric("Retorno Anualizado S&P 500", f"{bench_ann:.2%}")

                    st.markdown("""
                    <div class="theory-text" style="margin-top:12px;">
                    <strong>Interpretación:</strong>
                    <ul>
                    <li><strong>Tracking Error:</strong> mide cuánto se desvía el portafolio del índice. Un TE bajo indica gestión pasiva; uno alto indica apuestas activas.</li>
                    <li><strong>Information Ratio:</strong> premia el exceso de retorno obtenido por unidad de riesgo activo. IR &gt; 0.5 es considerado competitivo en la industria.</li>
                    <li><strong>Máximo Drawdown:</strong> la mayor pérdida desde pico hasta valle en el período. Captura el riesgo de cola que el VaR no siempre muestra.</li>
                    </ul>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="key-insight">
                    <strong>{'✅ Alfa Positivo — Portafolio SUPERA al mercado' if alfa > 0 else '⚠️ Alfa Negativo — Portafolio NO supera al mercado'}</strong><br>
                    {'Nuestro modelo de optimización ha demostrado generar valor real por encima del benchmark. La estrategia de diversificación con activos de bajo beta y alta Sharpe está funcionando.' if alfa > 0 else 'El portafolio actual no genera exceso de retorno sobre el S&P 500. Se recomienda rebalancear los pesos hacia activos con mejor relación riesgo-retorno.'}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No se pudo optimizar el portafolio.")
        except Exception as e:
            st.error(f"Error: {e}")

# ═══════════════════════════════════════════════════════════════════
# SECTION: LIMITACIONES Y CRÍTICAS
# ═══════════════════════════════════════════════════════════════════
elif "Limitaciones" in section:
    st.markdown(f'<div class="lesson-badge">⚠️ Lección 17 de {total_sections}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Limitaciones y Críticas al VaR</div>', unsafe_allow_html=True)

    limitations = [
        ("1️⃣", "Supuesto de Normalidad", "El VaR Paramétrico asume que los retornos siguen una distribución normal, pero en la realidad los mercados financieros exhiben colas pesadas (leptocurtosis) y asimetrías que hacen que los eventos extremos sean más frecuentes de lo predicho.", "#ef4444"),
        ("2️⃣", "No captura el riesgo de cola", "El VaR solo dice dónde empieza el peligro, no qué tan profundo es. El CVaR (Expected Shortfall) soluciona parcialmente esto, pero aún depende de los datos históricos disponibles.", "#f59e0b"),
        ("3️⃣", "Horizonte temporal fijo", "El VaR se calcula para un horizonte específico (1 día, 10 días, etc.). En crisis prolongadas, las pérdidas pueden acumularse mucho más allá de lo que un solo VaR diario predice.", "#ec4899"),
        ("4️⃣", "No es subaditivo", "El VaR no cumple la propiedad de subaditividad: VaR(A+B) ≤ VaR(A) + VaR(B) no siempre se cumple. Esto significa que diversificar un portafolio podría, paradójicamente, aumentar el VaR medido.", "#7c3aed"),
        ("5️⃣", "Dependencia de datos históricos", "Todos los modelos retroalimentan datos del pasado para predecir el futuro. Eventos de 'cisne negro' (crisis 2008, COVID) rompen los patrones históricos y generan pérdidas no anticipadas.", "#06b6d4"),
        ("6️⃣", "Falsa sensación de seguridad", "Un VaR del 95% puede dar la impresión de que se está 'protegido'. En realidad, el 5% restante puede contener pérdidas catastróficas. El VaR es una herramienta, no un escudo.", "#10b981"),
    ]

    for num, title, desc, color in limitations:
        st.markdown(f"""
        <div class="risk-card" style="border-left: 4px solid {color};">
            <span style="font-size: 16px;">{num}</span>
            <strong style="color: {color}; margin-left: 6px; font-size: 15px;">{title}</strong>
            <div style="color: var(--text-secondary); font-size: 14px; margin-top: 10px; line-height: 1.75;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="key-insight">
    <strong>💡 Conclusión Académica:</strong> El VaR y sus métricas asociadas son herramientas valiosas pero imperfectas.
    La mejor práctica es combinar múltiples metodologías (paramétrica + histórica + simulación),
    validar con backtesting riguroso (Kupiec), y complementar con métricas de cola como el CVaR.
    <strong>Ningún modelo puede predecir el futuro con certeza</strong> — pero un buen modelo nos prepara para lo peor con inteligencia estadística.
    </div>
    """, unsafe_allow_html=True)

# ── Footer ──
st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 20px; color: #475569; font-size: 12px;">
    <strong>Proyecto Integrador — Teoría del Riesgo</strong> · Universidad Santo Tomás<br>
    Autora: Paula Español · Construido con Streamlit + Plotly + Python<br>
    <span style="color: #7c3aed;">Dashboard v3.0</span> · Modelos: CAPM, GARCH(1,1), VaR, CVaR, Markowitz, Monte Carlo
</div>
""", unsafe_allow_html=True)
