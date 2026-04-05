def compute_indicators(data_dict):
    results = {}

    for ticker, df in data_dict.items():
        df = df.copy()

        df["SMA_20"] = df["Close"].rolling(20).mean()
        df["EMA_20"] = df["Close"].ewm(span=20).mean()

        # RSI
        delta = df["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        df = df.dropna()

        results[ticker] = df

    return results