import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

def compute_capm(data_dict, market_ticker="^GSPC", rf_ticker="^IRX"):
    """
    Computes BETA and CAPM Expected Return for all assets relative to a benchmark.
    Downloads the Risk Free Rate intrinsically so we do not modify the core API logic.
    """
    results = {}
    
    # Verificación estricta de la presencia del Benchmark
    if market_ticker not in data_dict:
        return data_dict

    market_df = data_dict[market_ticker]
    
    # 1. Extracción oculta de la Tasa Libre de Riesgo (13 Week Treasury Bill)
    current_rf_annual = 0.04  # Paracaídas del 4% en caso de fallas de fetch
    try:
        if rf_ticker in data_dict:
            current_rf_annual = data_dict[rf_ticker]["Close"].dropna().iloc[-1] / 100
        else:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=20) 
            rf_df = yf.download(rf_ticker, start=start_date, end=end_date, interval="1d", progress=False)
            
            if not rf_df.empty:
               # Limpiar multi-index si yfinance lo arroja
               if isinstance(rf_df.columns, pd.MultiIndex):
                   rf_df.columns = [col[0] for col in rf_df.columns]
               current_rf_annual = rf_df["Close"].dropna().iloc[-1] / 100
    except Exception as e:
        print(f"⚠️ Aviso (CAPM): Tasa Risk-Free dinámica inalcanzable. Retornando The default 4%. Detalle: {e}")

    # 2. Retorno empírico del benchmark y Varianza
    if "return" in market_df.columns:
        market_returns = market_df["return"].dropna()
        market_var = market_returns.var()
        annual_market_return = market_returns.mean() * 252
    else:
        return data_dict 

    # 3. Cálculo activo por activo del CAPM
    for ticker, df in data_dict.items():
        if ticker in [market_ticker, rf_ticker]:
            continue
            
        df = df.copy()
        
        if "return" in df.columns:
            asset_returns = df["return"].dropna()
            
            # Alinear asincronías combinando marcos de fecha
            aligned = pd.concat([asset_returns, market_returns], axis=1, join="inner")
            aligned.columns = ["Asset", "Market"]
            
            if not aligned.empty and market_var != 0:
                covariance = aligned.cov().iloc[0, 1]
                beta = covariance / market_var
                
                # Formula E[R] matemáticamente definida en CAPM
                expected_return = current_rf_annual + beta * (annual_market_return - current_rf_annual)
                
                df["CAPM_Beta"] = beta
                df["CAPM_Expected_Return"] = expected_return
                df["Risk_Free_Rate"] = current_rf_annual
        
        results[ticker] = df
        
    for ticker in data_dict:
        if ticker not in results:
            results[ticker] = data_dict[ticker]
            
    return results
