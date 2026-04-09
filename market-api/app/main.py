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
from modules.garch import compute_garch
from modules.capm import compute_capm
from modules.var import compute_var

# --- PAGE CONFIG ---
st.set_page_config(page_title="Risk & Portfolio Dashboard", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🚀 Inversión Senior")
tickers_input = st.sidebar.text_input("Lista de Activos", value="AVAL, ^GSPC, ETH-USD, IBM, C6L.SI, NTDOY")
tickers = [t.strip() for t in tickers_input.split(",")]

confidence = st.sidebar.slider("Nivel de Confianza VaR", 0.90, 0.99, 0.95)
simulations = st.sidebar.number_input("Simulaciones Markowitz", min_value=1000, max_value=20000, value=10000, step=1000)
refresh_btn = st.sidebar.button("🔄 Actualizar Datos")

# --- DATA ORCHESTRATION ---
@st.cache_data(ttl=300)
def load_all_data(ticker_list, conf):
    try:
        raw_data = get_data(ticker_list)
        
        # FIX EXTREMO: Aplanar MultiIndex directamente en la orquestación central 
        # esto evita cualquier falla si Python no refrescó el módulo api_data.py en memoria.
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
            "var": var, "signals": signals
        }
    except Exception as e:
         st.error(f"Error procesando datos: {e}")
         return None

if refresh_btn:
    load_all_data.clear()
    if "cache" in st.session_state:
        del st.session_state.cache

if "cache" not in st.session_state or refresh_btn:
    with st.spinner("Construyendo modelos matemáticos..."):
        st.session_state.cache = load_all_data(tickers, confidence)

data_cache = st.session_state.cache

st.title("📈 Plataforma Avanzada de Riesgo & Portafolios")
st.markdown("*Autor:* **Paula Español**")

if not data_cache:
    st.stop()

# --- TABS ---
t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
    "1. Overview", "2. Indicadores Técnicos", "3. Riesgo (VaR/CVaR)", 
    "4. GARCH", "5. CAPM", "6. Portafolio Markowitz", "7. Señales", "8. Macro"
])

valid_assets = [t for t in tickers if t not in ['^GSPC', '^IRX'] and t in data_cache["ind"]]

# 1. OVERVIEW
with t1:
    st.header("📝 Overview del Mercado")
    if valid_assets:
        cols = st.columns(len(valid_assets[:4]))
        for idx, t in enumerate(valid_assets[:4]):
            try:
                latest = data_cache["ind"][t].iloc[-1]
                prev = data_cache["ind"][t].iloc[-2]
                pct_change = ((float(latest['Close']) - float(prev['Close'])) / float(prev['Close'])) * 100
                cols[idx].metric(f"{t} Precio", f"${float(latest['Close']):.2f}", f"{pct_change:.2f}%")
            except:
                pass
        st.info("💡 **Interpretación Automática:** Los activos muestran la última cotización procesada. Valores negativos fuertes indican corrección, ideales para analizar entradas en la pestaña de Señales.")

# 2. INDICADORES TÉCNICOS
with t2:
    st.header("📊 Indicadores Técnicos")
    sel_t2 = st.selectbox("Activo a analizar:", valid_assets, key="sel_t2")
    if sel_t2:
        try:
            df = data_cache["ind"][sel_t2]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Precio'))
            fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20'))
            fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], name='EMA 20'))
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error gráfico: {e}")

# 3. RIESGO VaR / CVaR
with t3:
    st.header("📉 Análisis de Riesgo Extremo")
    try:
        var_data = []
        
        # Helperes para forzar siempre escalares y reventar la caché de Series
        def _to_float(v):
            if isinstance(v, pd.Series): return float(v.iloc[0])
            return float(v) if pd.notna(v) else 0.0
            
        def _to_str(v):
            if isinstance(v, pd.Series): return str(v.iloc[0])
            return str(v) if pd.notna(v) else 'N/A'

        for v in valid_assets:
            if v in data_cache["var"]:
                row = data_cache["var"][v].iloc[-1]
                var_data.append({
                    "Activo": v,
                    "VaR Paramétrico": f"{_to_float(row.get('VaR_95_Param', 0))*100:.2f}%",
                    "VaR Histórico": f"{_to_float(row.get('VaR_95_Hist', 0))*100:.2f}%",
                    "VaR Monte Carlo": f"{_to_float(row.get('VaR_95_MC', 0))*100:.2f}%",
                    "CVaR (Expected Shortfall)": f"{_to_float(row.get('CVaR_95', 0))*100:.2f}%",
                    "Kupiec Status": _to_str(row.get('Kupiec_Status', 'N/A')),
                    "Kupiec P-Value": f"{_to_float(row.get('Kupiec_PValue', 0)):.4f}"
                })
        st.table(pd.DataFrame(var_data))
        st.info("💡 **Interpretación Automática:** El CVaR siempre debe ser mayor (en magnitud de pérdida) que el VaR, pues representa el promedio de pérdidas en el peor de los escenarios. Kupiec Status 'Accepted' indica que el modelo es estadísticamente válido y protege ante pánicos.")
    except Exception as e:
        st.error(f"Error cargando VaR: {e}")

# 4. GARCH
with t4:
    st.header("🌀 Volatilidad Condicional (GARCH 1,1)")
    try:
        sel_t4 = st.selectbox("Seleccione Activo:", valid_assets, key="sel_t4")
        if sel_t4 and sel_t4 in data_cache["garch"]:
            df_g = data_cache["garch"][sel_t4]
            fig = px.line(df_g, x=df_g.index, y='GARCH_Vol', title=f"Volatilidad Estocástica Diaria - {sel_t4}")
            st.plotly_chart(fig, use_container_width=True)
            last_aic = float(df_g['GARCH_AIC'].iloc[-1])
            st.metric("Calidad del Modelo (Akaike IC)", f"{last_aic:.2f}")
    except Exception as e:
        st.error(f"Error GARCH: {e}")

# 5. CAPM
with t5:
    st.header("⚖️ Capital Asset Pricing Model (CAPM)")
    try:
        capm_df = pd.DataFrame()
        for v in valid_assets:
            if v in data_cache["capm"]:
                row = data_cache["capm"][v].iloc[-1]
                capm_df = pd.concat([capm_df, pd.DataFrame([{
                    "Activo": v,
                    "Beta": float(row.get('CAPM_Beta', 1.0)),
                    "Retorno Esperado": float(row.get('CAPM_Expected_Return', 0))
                }])], ignore_index=True)
                
        fig_capm = px.bar(capm_df, x='Activo', y='Beta', color='Retorno Esperado', title="Sensibilidad vs Retorno")
        st.plotly_chart(fig_capm, use_container_width=True)
        st.info("💡 **Interpretación Automática:** Betas > 1 hiperamplifican el movimiento del mercado. Activos con beta negativo funcionan como seguro contra caídas sistémicas.")
    except Exception as e:
        st.error(f"Error CAPM: {e}")

# 6. PORTAFOLIO MARKOWITZ
with t6:
    st.header("🎯 Frontera Eficiente de Markowitz")
    try:
        with st.spinner("Optimizando portafolios (10k)..."):
            opt_res = optimize_portfolio(data_cache["ind"], num_portfolios=simulations)
            
        if opt_res:
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = px.scatter(opt_res["all_portfolios"], x='Volatility', y='Return', color='Sharpe')
                fig.add_trace(go.Scatter(x=[opt_res["max_sharpe"]["Volatility"]], y=[opt_res["max_sharpe"]["Return"]],
                                         mode='markers', marker=dict(color='red', size=15, symbol='star'), name='Max Sharpe'))
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                w = {k: v for k, v in opt_res["max_sharpe"].items() if k not in ['Return', 'Volatility', 'Sharpe']}
                w_df = pd.DataFrame(list(w.items()), columns=['Activo', 'Peso (%)'])
                w_df['Peso (%)'] = (w_df['Peso (%)'] * 100).round(2)
                st.dataframe(w_df.sort_values(by='Peso (%)', ascending=False), hide_index=True)
                st.metric("Ratio de Sharpe (Max)", f"{opt_res['max_sharpe']['Sharpe']:.2f}")
    except Exception as e:
        st.error(f"Error Portafolio: {e}")

# 7. SEÑALES TÉCNICAS
with t7:
    st.header("🚦 Engine de Trading")
    try:
        sel_t7 = st.selectbox("Ver Señales de:", valid_assets, key="sel_t7")
        if sel_t7 and sel_t7 in data_cache["signals"]:
            df_s = data_cache["signals"][sel_t7]
            curr_sig = str(df_s['Final_Signal'].iloc[-1])
            
            if curr_sig == 'BUY': st.success("🔥 SEÑAL: COMPRA FUERTE")
            elif curr_sig == 'SELL': st.error("⚠️ SEÑAL: VENTA")
            else: st.warning("⚖️ SEÑAL: NEUTRAL")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_s.index, y=df_s['Close'], name='Price'))
            fig.add_trace(go.Scatter(x=df_s.index, y=df_s['BB_Upper'], line=dict(dash='dash'), opacity=0.3, name='BB+'))
            fig.add_trace(go.Scatter(x=df_s.index, y=df_s['BB_Lower'], line=dict(dash='dash'), opacity=0.3, name='BB-'))
            
            b = df_s[df_s['Final_Signal'] == 'BUY']
            s = df_s[df_s['Final_Signal'] == 'SELL']
            
            fig.add_trace(go.Scatter(x=b.index, y=b['Close'], mode='markers', marker=dict(symbol='triangle-up', size=12, color='green'), name='Buy'))
            fig.add_trace(go.Scatter(x=s.index, y=s['Close'], mode='markers', marker=dict(symbol='triangle-down', size=12, color='red'), name='Sell'))
            
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error Señales: {e}")

# 8. MACRO
with t8:
    st.header("🌍 Benchmark & Desempeño Acumulado")
    try:
        if "opt_res" in locals() and opt_res:
            macro_weights = {k: v for k, v in opt_res["max_sharpe"].items() if k not in ['Return', 'Volatility', 'Sharpe']}
            # Ensure analyze_macro is properly called (it was imported at the top)
            m_res = analyze_macro(data_cache["ind"], macro_weights)
            if m_res:
                df_m = pd.DataFrame({'Mi Portafolio': m_res["portfolio_cumulative"], 'S&P 500': m_res["benchmark_cumulative"]})
                st.plotly_chart(px.line(df_m, title="Crecimiento Acumulado: Nosotros vs Wall Street"), use_container_width=True)
                
                alfa = opt_res['max_sharpe']['Return'] - (m_res['benchmark_sharpe'] * opt_res['max_sharpe']['Volatility'])
                st.metric("Alfa (Exceso de Retorno vs Index)", f"{alfa:.2%}")
                st.info("💡 **Interpretación Automática:** Si el Alfa es positivo, tu modelo logró superar estadísticamente al S&P 500.")
        else:
            st.warning("⚠️ Primero optimiza el portafolio.")
    except Exception as e:
        st.error(f"Error Análisis Macro: {e}")

