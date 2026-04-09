import pandas as pd
import numpy as np

def analyze_macro(data_dict, max_sharpe_weights, benchmark_ticker="^GSPC"):
    """
    Compares the optimized portfolio performance against the market benchmark.
    Calculates Alpha and relative performance.
    """
    if benchmark_ticker not in data_dict:
        return None
        
    benchmark_df = data_dict[benchmark_ticker]
    bm_returns = benchmark_df["log_return"].dropna()
    bm_cumulative = (1 + bm_returns).cumprod()
    
    # Calculate portfolio cumulative returns
    # We use the returns of the assets and apply the weights
    assets_returns_df = pd.DataFrame()
    for ticker, weight in max_sharpe_weights.items():
        if ticker in data_dict:
            assets_returns_df[ticker] = data_dict[ticker]["log_return"] * weight
            
    port_returns = assets_returns_df.sum(axis=1)
    port_cumulative = (1 + port_returns).cumprod()
    
    # Metrics
    bm_sharpe = (bm_returns.mean() * 252 - 0.04) / (bm_returns.std() * np.sqrt(252))
    
    return {
        "portfolio_cumulative": port_cumulative,
        "benchmark_cumulative": bm_cumulative,
        "benchmark_sharpe": bm_sharpe,
        "benchmark_ticker": benchmark_ticker
    }
