import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px

# 1. Mantener tu configuración de rutas y módulos
sys.path.append('market-api')

from data.api_data import get_data
from modules.returns import calculate_returns
from modules.technical import compute_indicators
from modules.garch import compute_garch

# 2. Configuración de la interfaz web
st.set_page_config(page_title="Check GARCH - IBM & AVAL", layout="wide")
st.title("📊 Validación de Volatilidad GARCH")

# --- TU LÓGICA ORIGINAL (SIN CAMBIOS) ---
raw = get_data(['IBM','AVAL'])
for tk, df in raw.items():
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

ret = calculate_returns(raw)
ind = compute_indicators(ret)
g = compute_garch(ind)

# --- INTEGRACIÓN CON STREAMLIT ---
for ticker in ['IBM', 'AVAL']:
    st.header(f"Resultados para {ticker}")
    
    if ticker in g and 'GARCH_Vol' in g[ticker].columns:
        vol = g[ticker]['GARCH_Vol'].dropna()
        idx = g[ticker].index
        
        # A. Visualización Gráfica (Para que la página no esté en blanco)
        fig = px.line(vol, title=f"Volatilidad Condicional - {ticker}", 
                     labels={'value': 'Sigma', 'Date': 'Fecha'})
        st.plotly_chart(fig, use_container_width=True)

        # B. Bloque de Consola (Tus prints originales tal cual)
        # Creamos un string con exactamente lo que imprimías
        console_output = (
            f'=== {ticker} GARCH ===\n'
            f'Length: {len(vol)}\n'
            f'First 5: {[round(x,6) for x in vol.head().tolist()]}\n'
            f'Last 5:  {[round(x,6) for x in vol.tail().tolist()]}\n'
            f'Min: {vol.min():.6f}  Max: {vol.max():.6f}  Mean: {vol.mean():.6f}\n'
            f'Nunique: {vol.nunique()}\n'
            f'Std of vol: {vol.std():.6f}\n'
            f'Index dtype: {idx.dtype}\n'
            f'Index first 3: {idx[:3].tolist()}\n'
        )
        
        # Mostramos tus prints en un bloque de código para que se vea igual a la terminal
        st.subheader(f"Log de Verificación: {ticker}")
        st.code(console_output)
        
        # Mantener los prints originales por si revisas los logs de la nube
        print(console_output)
    else:
        st.warning(f"No se detectaron datos GARCH para {ticker}")

st.success("Cálculos completados exitosamente.")
