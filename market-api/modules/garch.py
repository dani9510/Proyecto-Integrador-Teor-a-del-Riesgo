import pandas as pd
import numpy as np
from arch import arch_model

def compute_garch(data_dict):
    """
    Computes GARCH(1,1) conditional volatility for the pipeline.
    Uses Student-t distribution and explicit starting values to avoid
    alpha collapsing to zero (local minimum issue with some assets).
    """
    results = {}

    for ticker, df in data_dict.items():
        if ticker in ["^IRX"]:
            continue

        df = df.copy()

        if "log_return" in df.columns:
            log_ret = df["log_return"].dropna()
            returns = log_ret * 100

            try:
                model = arch_model(
                    returns, mean='Zero', vol='Garch', p=1, q=1,
                    rescale=False, dist='t'
                )
                var_est = float(returns.var())
                omega_start = max(var_est * (1 - 0.10 - 0.85), 1e-4)
                starting_values = np.array([omega_start, 0.10, 0.85, 8.0])

                res = model.fit(
                    disp='off',
                    starting_values=starting_values,
                    options={'maxiter': 500}
                )

                params = res.params
                alpha_key = [k for k in params.index if 'alpha' in k.lower()]
                beta_key  = [k for k in params.index if 'beta'  in k.lower()]

                if alpha_key and beta_key:
                    alpha_val = params[alpha_key[0]]
                    if alpha_val < 1e-6:
                        print(f"[WARN] GARCH({ticker}): alpha colapso, reintentando con rescale=True...")
                        model2 = arch_model(returns, mean='Zero', vol='Garch', p=1, q=1,
                                            rescale=True, dist='t')
                        res = model2.fit(disp='off', options={'maxiter': 500})

                cond_vol = res.conditional_volatility.values / 100
                vol_series = pd.Series(np.nan, index=df.index)
                vol_series.loc[log_ret.index] = cond_vol
                df["GARCH_Vol"] = vol_series
                df["GARCH_AIC"] = res.aic

                std_resid_vals = (res.resid / res.conditional_volatility).values
                resid_series = pd.Series(np.nan, index=df.index)
                resid_series.loc[log_ret.index] = std_resid_vals
                df["GARCH_Std_Resid"] = resid_series

            except Exception as e:
                print(f"[ERROR] GARCH para {ticker}: {e}")
                df["GARCH_Vol"] = None
                df["GARCH_AIC"] = None

        results[ticker] = df

    for ticker in data_dict:
        if ticker not in results:
            results[ticker] = data_dict[ticker]

    return results


def compute_garch_comparison(returns_series):
    """
    Fits ARCH(1), GARCH(1,1) and GJR-GARCH(1,1) with Student-t distribution.
    Returns:
        comparison: list of dicts with model metrics (Log-Likelihood, AIC, BIC)
        forecast_vol: array of 10-day ahead conditional volatility forecast (decimal)
        best_res: fitted result object of the best model (lowest AIC)
        resid_series: standardized residuals of the best model
    """
    returns = returns_series.dropna() * 100

    var_est = float(returns.var())
    omega_start = max(var_est * (1 - 0.10 - 0.85), 1e-4)

    specs = [
        ("ARCH(1)",        arch_model(returns, mean='Zero', vol='ARCH', p=1,
                                      rescale=False, dist='t')),
        ("GARCH(1,1)",     arch_model(returns, mean='Zero', vol='Garch', p=1, q=1,
                                      rescale=False, dist='t')),
        ("GJR-GARCH(1,1)", arch_model(returns, mean='Zero', vol='GARCH', p=1, q=1, o=1,
                                      rescale=False, dist='t')),
    ]

    comparison = []
    best_res   = None
    best_aic   = np.inf
    best_resid = None

    for name, model in specs:
        try:
            if "GARCH(1,1)" in name:
                sv = np.array([omega_start, 0.10, 0.85, 8.0])
                res = model.fit(disp='off', starting_values=sv, options={'maxiter': 500})
            else:
                res = model.fit(disp='off', options={'maxiter': 500})

            comparison.append({
                "Modelo":           name,
                "Log-Likelihood":   round(res.loglikelihood, 2),
                "AIC":              round(res.aic, 2),
                "BIC":              round(res.bic, 2),
                "Params":           len(res.params),
            })
            if res.aic < best_aic:
                best_aic   = res.aic
                best_res   = res
                best_resid = res.resid / res.conditional_volatility

        except Exception as e:
            comparison.append({
                "Modelo": name,
                "Log-Likelihood": "Error",
                "AIC": "Error",
                "BIC": "Error",
                "Params": "-",
            })

    # Marcar el mejor modelo
    best_name = min(
        [c for c in comparison if isinstance(c["AIC"], float)],
        key=lambda x: x["AIC"],
        default={}
    ).get("Modelo", "")
    for c in comparison:
        c["Mejor"] = "⭐" if c["Modelo"] == best_name else ""

    # Pronóstico 10 días del mejor modelo
    forecast_vol = None
    if best_res is not None:
        try:
            fc = best_res.forecast(horizon=10)
            forecast_vol = np.sqrt(fc.variance.values[-1]) / 100  # a decimal
        except Exception:
            forecast_vol = None

    return comparison, forecast_vol, best_res, best_resid
