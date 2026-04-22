import pandas as pd
import numpy as np

def analyze_macro(data_dict, max_sharpe_weights, benchmark_ticker="^GSPC"):
    """
    Compares the optimized portfolio performance against the market benchmark.
    Calculates Alpha, Tracking Error, Information Ratio and Max Drawdown.
    """
    if benchmark_ticker not in data_dict:
        return None

    benchmark_df = data_dict[benchmark_ticker]
    bm_returns = benchmark_df["log_return"].dropna()
    bm_cumulative = (1 + bm_returns).cumprod()

    # Portfolio weighted returns
    assets_returns_df = pd.DataFrame()
    for ticker, weight in max_sharpe_weights.items():
        if ticker in data_dict:
            assets_returns_df[ticker] = data_dict[ticker]["log_return"] * weight

    port_returns = assets_returns_df.sum(axis=1)
    port_cumulative = (1 + port_returns).cumprod()

    # Alinear índices para métricas comparativas
    common_idx = port_returns.index.intersection(bm_returns.index)
    p = port_returns[common_idx].dropna()
    b = bm_returns[common_idx].dropna()
    common_idx = p.index.intersection(b.index)
    p = p[common_idx]
    b = b[common_idx]

    # Sharpe del benchmark
    rf_daily = 0.04 / 252
    bm_sharpe = (b.mean() - rf_daily) / b.std() * np.sqrt(252) if b.std() != 0 else 0

    # Tracking Error (desviación estándar del exceso de retorno, anualizado)
    active_returns = p - b
    tracking_error = active_returns.std() * np.sqrt(252) if len(active_returns) > 1 else 0

    # Information Ratio
    active_return_annual = active_returns.mean() * 252
    information_ratio = active_return_annual / tracking_error if tracking_error != 0 else 0

    # Máximo Drawdown del portafolio
    cum_p = (1 + p).cumprod()
    rolling_max = cum_p.cummax()
    drawdown = (cum_p - rolling_max) / rolling_max
    max_drawdown = float(drawdown.min())

    # Retorno anualizado portafolio vs benchmark
    port_ann_return  = p.mean() * 252
    bench_ann_return = b.mean() * 252

    return {
        "portfolio_cumulative":  port_cumulative,
        "benchmark_cumulative":  bm_cumulative,
        "benchmark_sharpe":      bm_sharpe,
        "benchmark_ticker":      benchmark_ticker,
        "tracking_error":        tracking_error,
        "information_ratio":     information_ratio,
        "max_drawdown":          max_drawdown,
        "port_ann_return":       port_ann_return,
        "bench_ann_return":      bench_ann_return,
    }
