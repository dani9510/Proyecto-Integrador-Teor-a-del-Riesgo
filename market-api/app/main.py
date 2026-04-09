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

# --- PAGE CONFIG ---
st.set_page_config(page_title="Risk & Portfolio Dashboard", page_icon="📈", layout="wide")

# Custom CSS for a premium look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🚀 Inversión Senior")
st.sidebar.markdown("---")
tickers_input = st.sidebar.text_input("Lista de Activos (TICKERS)", value="AVAL, ^GSPC, ETH-USD, IBM, C6L.SI, NTDOY")
tickers = [t.strip() for t in tickers_input.split(",")]

st.sidebar.markdown("### Configuración")
confidence = st.sidebar.slider("Nivel de Confianza VaR", 0.90, 0.99, 0.95)
simulations = st.sidebar.number_input("Simulaciones Markowitz", 1000, 20000, 10000)

refresh_btn = st.sidebar.button("🔄 Actualizar Datos en Tiempo Real")

# --- DATA ORCHESTRATION ---
@st.cache_data(ttl=300) # Cache for 5 minutes
def load_all_data(ticker_list):
    raw_data = get_data(ticker_list)
    returns = calculate_returns(raw_data)
    indicators = compute_indicators(returns)
    return indicators

if "data" not in st.session_state or refresh_btn:
    with st.spinner("Descargando información financiera..."):
        st.session_state.data = load_all_data(tickers)
        st.success("¡Datos actualizados exitosamente!")

data = st.session_state.data

# --- HEADER ---
st.title("📈 Dashboard de Riesgo & Optimización de Portafolio")
st.markdown(f"*Autor:* **Paula Español** | *Estado:* **Actualizado en tiempo real**")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Optimización Markowitz", "🚦 Señales de Trading", "🌍 Análisis Macro"])

# --- TAB 1: PORTFOLIO ---
with tab1:
    st.header("🏁 Frontera Eficiente de Markowitz")
    
    with st.spinner("Ejecutando simulaciones de Monte Carlo..."):
        opt_res = optimize_portfolio(data, num_portfolios=simulations)
        
    if opt_res:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            all_ports = opt_res["all_portfolios"]
            fig = px.scatter(all_ports, x='Volatility', y='Return', color='Sharpe',
                             title=f"Simulación de {simulations} Portafolios",
                             labels={'Volatility': 'Riesgo (Volatilidad)', 'Return': 'Retorno Esperado'},
                             color_continuous_scale='Viridis')
            
            # Highlight Max Sharpe
            fig.add_trace(go.Scatter(x=[opt_res["max_sharpe"]["Volatility"]], 
                                     y=[opt_res["max_sharpe"]["Return"]],
                                     mode='markers', marker=dict(color='red', size=15, symbol='star'),
                                     name='Max Sharpe'))
            
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("💡 Asignación Óptima")
            st.info("Basado en el portafolio con mayor Ratio de Sharpe.")
            
            weights = {k: v for k, v in opt_res["max_sharpe"].items() if k not in ['Return', 'Volatility', 'Sharpe']}
            weights_df = pd.DataFrame(list(weights.items()), columns=['Activo', 'Peso (%)'])
            weights_df['Peso (%)'] = (weights_df['Peso (%)'] * 100).round(2)
            
            st.table(weights_df.sort_values(by='Peso (%)', ascending=False))
            
            st.metric("Ratio de Sharpe Máximo", f"{opt_res['max_sharpe']['Sharpe']:.2f}")
            st.metric("Retorno Esperado Anual", f"{opt_res['max_sharpe']['Return'] * 100:.2f}%")

# --- TAB 2: SIGNALS ---
with tab2:
    st.header("🚦 Estrategia de Señales Técnicas")
    asset_to_viz = st.selectbox("Selecciona un activo para ver señales:", [t for t in tickers if t != '^GSPC'])
    
    signals_res = compute_signals(data)
    
    if asset_to_viz in signals_res:
        df_sig = signals_res[asset_to_viz]
        
        # Plot price with Bollinger Bands
        fig_price = go.Figure()
        fig_price.add_trace(go.Scatter(x=df_sig.index, y=df_sig['Close'], name='Precio'))
        fig_price.add_trace(go.Scatter(x=df_sig.index, y=df_sig['BB_Upper'], line=dict(dash='dash'), name='BB Superior', opacity=0.3))
        fig_price.add_trace(go.Scatter(x=df_sig.index, y=df_sig['BB_Lower'], line=dict(dash='dash'), name='BB Inferior', opacity=0.3))
        
        # Add Buy/Sell Markers
        buys = df_sig[df_sig['Final_Signal'] == 'BUY']
        sells = df_sig[df_sig['Final_Signal'] == 'SELL']
        
        fig_price.add_trace(go.Scatter(x=buys.index, y=buys['Close'], mode='markers', 
                                       marker=dict(symbol='triangle-up', size=12, color='green'), name='Compra'))
        fig_price.add_trace(go.Scatter(x=sells.index, y=sells['Close'], mode='markers', 
                                       marker=dict(symbol='triangle-down', size=12, color='red'), name='Venta'))
        
        st.plotly_chart(fig_price, use_container_width=True)
        
        # Latest Signal Alert
        latest_sig = df_sig['Final_Signal'].iloc[-1]
        if latest_sig == 'BUY':
            st.success(f"🔥 SEÑAL ACTUAL PARA {asset_to_viz}: COMPRA FUERTE")
        elif latest_sig == 'SELL':
            st.error(f"⚠️ SEÑAL ACTUAL PARA {asset_to_viz}: VENTA / TOMA DE UTILIDADES")
        else:
            st.warning(f"⚖️ SEÑAL ACTUAL PARA {asset_to_viz}: NEUTRAL / HOLD")

# --- TAB 3: MACRO ---
with tab3:
    st.header("🌍 Comparativa vs Benchmarks")
    
    if opt_res:
        weights = {k: v for k, v in opt_res["max_sharpe"].items() if k not in ['Return', 'Volatility', 'Sharpe']}
        macro_res = analyze_macro(data, weights)
        
        if macro_res:
            st.subheader("Crecimiento Acumulado: Portafolio vs S&P 500")
            
            comp_df = pd.DataFrame({
                'Portafolio Optimizado': macro_res["portfolio_cumulative"],
                'S&P 500 (Market)': macro_res["benchmark_cumulative"]
            })
            
            fig_macro = px.line(comp_df, title="Rentabilidad Acumulada (Normalizada)")
            st.plotly_chart(fig_macro, use_container_width=True)
            
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Sharpe Portafolio", f"{opt_res['max_sharpe']['Sharpe']:.2f}")
            col_m2.metric("Sharpe Mercado (^GSPC)", f"{macro_res['benchmark_sharpe']:.2f}")
            
            alfa = opt_res['max_sharpe']['Return'] - (macro_res['benchmark_sharpe'] * opt_res['max_sharpe']['Volatility'])
            st.write(f"**Alfa Generado (Exceso de retorno):** {alfa:.4%}")
