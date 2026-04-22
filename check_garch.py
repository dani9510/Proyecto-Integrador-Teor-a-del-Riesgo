import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px

# Mantener tu configuración de path
sys.path.append('market-api')

from data.api_data import get_data
from modules.returns import calculate_returns
from modules.technical import compute_indicators
from modules.garch import compute_garch

# Configuración de la página de Streamlit
st.set_page_config(page_title="Check GARCH - IBM & AVAL", layout="wide")
st.title("📊 Verificación de Modelo GARCH")

# --- LÓGICA ORIGINAL (SIN QUITAR NADA) ---
raw = get_data(['IBM','AVAL'])
for tk, df in raw.items():
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

ret = calculate_returns(raw)
ind = compute_indicators(ret)
g = compute_garch(ind)

# --- VISUALIZACIÓN EN STREAMLIT ---
for ticker in ['IBM', 'AVAL']:
    st.header(f"Activo: {ticker}")
    
    if ticker in g and 'GARCH_Vol' in g[ticker].columns:
        vol = g[ticker]['GARCH_Vol'].dropna()
        
        # 1. Gráfica de Volatilidad (Nueva función para la web)
        fig = px.line(vol, title=f"Volatilidad Condicional GARCH - {ticker}", 
                     labels={'value': 'Volatilidad', 'Date': 'Fecha'})
        st.plotly_chart(fig, use_container_width=True)

        # 2. Reemplazo de tus 'print' por bloques de texto en Streamlit
        # Usamos st.code para mantener el formato de consola que tenías
        output_console = (
            f'=== {ticker} GARCH ===\n'
            f'Length: {len(vol)}\n'
            f'First 5: {[round(x,6) for x in vol.head().tolist()]}\n'
            f'Last 5:  {[round(x,6) for x in vol.tail().tolist()]}\n'
            f'Min: {vol.min():.6f}  Max: {vol.max():.6f}  Mean: {vol.mean():.6f}\n'
            f'Nunique: {vol.nunique()}\n'
            f'Std of vol: {vol.std():.6f}\n'
            f'Index dtype: {idx.dtype if "idx" in locals() else "datetime"}\n'
            f'Index first 3: {vol.index[:3].tolist()}\n'
        )
        
        st.subheader("Estadísticas Técnicas (Consola)")
        st.code(output_console)
        
        # También imprimimos en la consola del servidor por si acaso
        print(output_console)
        
    else:
        st.error(f"No se encontraron datos GARCH para {ticker}")
        print(f"Error: No se encontraron datos GARCH para {ticker}")

st.success("Análisis finalizado correctamente.")
