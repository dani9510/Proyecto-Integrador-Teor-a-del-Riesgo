import pandas as pd
import numpy as np
from scipy.stats import norm, chi2

def kupiec_test(returns, var_forecast, alpha):
    """ Backtesting matemático de la ventana VaR (Kupiec's POF Test / Proportion of Failures) """
    exceptions = sum(returns < -abs(var_forecast))
    T = len(returns)
    p = 1 - alpha # Por ejemplo 5% de que falle
    
    if T == 0 or exceptions == 0:
        return {"Exceptions": int(exceptions), "Status": "Accepted"}

    fail_rate = exceptions / T
    
    try:
        lr_pof = -2 * (exceptions * np.log(p) + (T - exceptions) * np.log(1 - p)) + \
                  2 * (exceptions * np.log(fail_rate) + (T - exceptions) * np.log(1 - fail_rate))
        
        p_value = 1 - chi2.cdf(lr_pof, 1) # Un grado de libertad
        status = "Accepted" if p_value > 0.05 else "Rejected"
    except:
        status = "Error"

    return {"Exceptions": int(exceptions), "Status": status}

def compute_var(data_dict, confidence_level=0.95):
    """
    Computes 3 types of VaR, the Conditional VaR (CVaR) and applies the Kupiec Test.
    """
    results = {}
    alpha = 1 - confidence_level

    for ticker, df in data_dict.items():
        if ticker in ["^IRX"]:
            continue
            
        df = df.copy()
        
        if "log_return" in df.columns:
            returns = df["log_return"].dropna()
            
            if len(returns) > 0:
                # 1. VaR Paramétrico (Distribución Normal)
                mu = returns.mean()
                sigma = returns.std()
                z_score = norm.ppf(confidence_level)
                var_param = mu - z_score * sigma
                
                # 2. VaR Histórico (Basado en datos fácticos reales)
                var_hist = np.percentile(returns, alpha * 100)
                
                # 3. VaR Monte Carlo (Distribución Estocástica simulada)
                simulations = 10000
                simulated_returns = np.random.normal(mu, sigma, simulations)
                var_mc = np.percentile(simulated_returns, alpha * 100)
                
                # 4. CVaR - Conditional Value at Risk (Expected Shortfall) de la cola
                losses_below_var = returns[returns <= var_hist]
                cvar = losses_below_var.mean() if len(losses_below_var) > 0 else var_hist
                
                # Guardar salidas en DataFrame
                df["VaR_95_Param"] = var_param
                df["VaR_95_Hist"] = var_hist
                df["VaR_95_MC"] = var_mc
                df["CVaR_95"] = cvar
                
                # 5. BONUS: Test de Kupiec para asertividad del VaR Histórico
                kupiec_res = kupiec_test(returns, var_hist, confidence_level)
                df["Kupiec_Exceptions"] = kupiec_res["Exceptions"]
                df["Kupiec_Status"] = kupiec_res["Status"]

        results[ticker] = df
        
    for ticker in data_dict:
        if ticker not in results:
            results[ticker] = data_dict[ticker]
            
    return results
