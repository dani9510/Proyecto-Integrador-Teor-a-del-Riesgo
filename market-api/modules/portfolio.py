import numpy as np
import pandas as pd

def optimize_portfolio(data_dict, num_portfolios=10000, risk_free_rate=0.04):
    """
    Performs Markowitz Portfolio Optimization using Monte Carlo simulation.
    Finds the Maximum Sharpe Ratio portfolio and the Minimum Volatility portfolio.
    """
    # 1. Gather all log returns into a single DataFrame
    returns_df = pd.DataFrame()
    for ticker, df in data_dict.items():
        if ticker in ["^GSPC", "^IRX"]: continue
        if "log_return" in df.columns:
            returns_df[ticker] = df["log_return"]
    
    if returns_df.empty:
        return None

    # Annualize returns and covariance matrix
    mean_returns = returns_df.mean() * 252
    cov_matrix = returns_df.cov() * 252
    
    num_assets = len(mean_returns)
    results = np.zeros((3 + num_assets, num_portfolios))
    
    # 2. Monte Carlo Simulation
    for i in range(num_portfolios):
        # random weights that sum to 1
        weights = np.random.random(num_assets)
        weights /= np.sum(weights)
        
        # portfolio return, volatility and sharpe ratio
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_std_dev = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        
        results[0,i] = portfolio_return
        results[1,i] = portfolio_std_dev
        results[2,i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
        
        # Store weights
        for j in range(len(weights)):
            results[3+j, i] = weights[j]
            
    # Convert to DataFrame
    columns = ['Return', 'Volatility', 'Sharpe'] + [ticker for ticker in returns_df.columns]
    results_df = pd.DataFrame(results.T, columns=columns)
    
    # 3. Extract Best Portfolios
    max_sharpe_idx = results_df['Sharpe'].idxmax()
    max_sharpe_portfolio = results_df.iloc[max_sharpe_idx]
    
    min_vol_idx = results_df['Volatility'].idxmin()
    min_vol_portfolio = results_df.iloc[min_vol_idx]
    
    return {
        "all_portfolios": results_df,
        "max_sharpe": max_sharpe_portfolio.to_dict(),
        "min_vol": min_vol_portfolio.to_dict(),
        "assets": returns_df.columns.tolist()
    }
