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
                mu = returns.mean()
                sigma = returns.std()
                simulated_returns = np.random.normal(mu, sigma, 10000)

                # Siempre calcular al 95% Y al 99%
                for cl, suffix in [(0.95, "95"), (0.99, "99")]:
                    a = 1 - cl
                    z = norm.ppf(cl)
                    vp = mu - z * sigma
                    vh = np.percentile(returns, a * 100)
                    vm = np.percentile(simulated_returns, a * 100)
                    losses = returns[returns <= vh]
                    cv = losses.mean() if len(losses) > 0 else vh

                    df[f"VaR_{suffix}_Param"] = vp
                    df[f"VaR_{suffix}_Hist"]  = vh
                    df[f"VaR_{suffix}_MC"]    = vm
                    df[f"CVaR_{suffix}"]       = cv

                # Columnas al nivel configurado (para compatibilidad con otras secciones)
                z_score = norm.ppf(confidence_level)
                var_param = mu - z_score * sigma
                var_hist = np.percentile(returns, alpha * 100)
                var_mc = np.percentile(simulated_returns, alpha * 100)
                losses_below_var = returns[returns <= var_hist]
                cvar = losses_below_var.mean() if len(losses_below_var) > 0 else var_hist

                df["VaR_Param"] = var_param
                df["VaR_Hist"]  = var_hist
                df["VaR_MC"]    = var_mc
                df["CVaR"]      = cvar

                # Test de Kupiec sobre VaR histórico al nivel configurado
                kupiec_res = kupiec_test(returns, var_hist, confidence_level)
                df["Kupiec_Exceptions"] = kupiec_res["Exceptions"]
                df["Kupiec_Status"]     = kupiec_res["Status"]

        results[ticker] = df
        
    for ticker in data_dict:
        if ticker not in results:
            results[ticker] = data_dict[ticker]
            
    return results
