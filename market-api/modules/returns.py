import numpy as np

def calculate_returns(data_dict):
    results = {}

    for ticker, df in data_dict.items():
        df = df.copy()

        df["return"] = df["Close"].pct_change()
        df["log_return"] = np.log(df["Close"] / df["Close"].shift(1))

        df = df.dropna()

        results[ticker] = df

    return results