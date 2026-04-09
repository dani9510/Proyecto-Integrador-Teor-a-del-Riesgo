import pandas as pd
from arch import arch_model

def compute_garch(data_dict):
    """
    Computes GARCH(1,1) conditional volatility for items in the dictionary.
    Also provides a diagnostic metric (AIC).
    """
    results = {}
    
    for ticker, df in data_dict.items():
        if ticker in ["^IRX"]:
            continue
            
        df = df.copy()
        
        if "log_return" in df.columns:
            # Multiplicamos por 100 para facilitar la convergencia del optimizador MLE interno en arch_model
            returns = df["log_return"].dropna() * 100
            
            try:
                # Definir y ajustar el modelo GARCH(1,1) asumiendo media constante
                model = arch_model(returns, mean='Constant', vol="Garch", p=1, q=1, rescale=False)
                res = model.fit(disp="off")
                
                # Volatilidad condicional diaria esperada (se regresa a la escala original)
                df["GARCH_Vol"] = res.conditional_volatility / 100
                
                # Diagnóstico GARCH: Akaike Information Criterion (Se añade como constante en la serie)
                df["GARCH_AIC"] = res.aic
                
                # Mejora nivel top: Residuos Estandarizados para validar modelo y normalidad
                df["GARCH_Std_Resid"] = res.resid / res.conditional_volatility
                
            except Exception as e:
                print(f"❌ Error estimando GARCH para {ticker}: {e}")
                df["GARCH_Vol"] = None
                df["GARCH_AIC"] = None
                
        results[ticker] = df
        
    # Preservar tickers que hayan sido omitidos intencionalmente
    for ticker in data_dict:
        if ticker not in results:
            results[ticker] = data_dict[ticker]
            
    return results
