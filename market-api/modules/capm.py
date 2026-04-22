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

    # 1. Extracción oculta de la Tasa Libre de Riesgo (13 Week Treasury Bill)
    current_rf_annual = 0.04  # Paracaídas dictatorial del 4%
    try:
        if rf_ticker in data_dict:
            current_rf_annual = data_dict[rf_ticker]["Close"].dropna().iloc[-1] / 100
        else:
            end_date = datetime.today()
            start_date = end_date - timedelta(days=20) 
            # Descarga con timeout muy corto para no colgar la demo
            rf_df = yf.download(rf_ticker, start=start_date, end=end_date, interval="1d", progress=False, timeout=5)
            
            if not rf_df.empty:
               if isinstance(rf_df.columns, pd.MultiIndex):
                   rf_df.columns = [col[0] for col in rf_df.columns]
               current_rf_annual = rf_df["Close"].dropna().iloc[-1] / 100
    except Exception as e:
        print(f"[WARN] CAPM: Tasa Risk-Free inalcanzable. Usando fallback 4%. Detalle: {e}")

    # 2. Retorno empírico del benchmark y Varianza (Con Fallback para la Demo)
    has_market = False
    if market_ticker in data_dict and "return" in data_dict[market_ticker].columns:
        market_returns = data_dict[market_ticker]["return"].dropna()
        if len(market_returns) > 0:
            market_var = market_returns.var()
            annual_market_return = market_returns.mean() * 252
            has_market = True
            
    if not has_market:
        print("⚠️ Aviso (CAPM): Falla en el Benchmark de Mercado. Activando modo Demo-Fallback.")
        market_var = 0.0001
        annual_market_return = 0.10 # Asume rentabilidad del mercado del 10% estándar

    # 3. Cálculo activo por activo del CAPM
    for ticker, df in data_dict.items():
        if ticker in [market_ticker, rf_ticker]:
            continue
            
        df = df.copy()
        
        if "return" in df.columns:
            asset_returns = df["return"].dropna()
            
            # Valores por defecto para fallback de seguridad
            beta = 1.0 # Si algo falla, asume la volatilidad idéntica al mercado
            
            if has_market:
                aligned = pd.concat([asset_returns, market_returns], axis=1, join="inner")
                aligned.columns = ["Asset", "Market"]
                if not aligned.empty and market_var != 0:
                    covariance = aligned.cov().iloc[0, 1]
                    beta = covariance / market_var
            
            # Formula E[R] matemáticamente definida en CAPM aplicada en ambos casos reales o fallbacks
            expected_return = current_rf_annual + beta * (annual_market_return - current_rf_annual)
            
            df["CAPM_Beta"] = beta
            df["CAPM_Expected_Return"] = expected_return
            df["Risk_Free_Rate"] = current_rf_annual
                
        results[ticker] = df
        
    for ticker in data_dict:
        if ticker not in results:
            results[ticker] = data_dict[ticker]
            
    return results
