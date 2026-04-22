def compute_indicators(data_dict):
    results = {}

    for ticker, df in data_dict.items():
        df = df.copy()

        df["SMA_20"] = df["Close"].rolling(20).mean()
        df["EMA_20"] = df["Close"].ewm(span=20).mean()

        # RSI (14 períodos)
        delta = df["Close"].diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()
        rs = gain / loss
        df["RSI"] = 100 - (100 / (1 + rs))

        # MACD (12, 26, 9)
        ema12 = df["Close"].ewm(span=12, adjust=False).mean()
        ema26 = df["Close"].ewm(span=26, adjust=False).mean()
        df["MACD"] = ema12 - ema26
        df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
        df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]

        # Bandas de Bollinger (20, ±2σ)
        df["BB_Mid"] = df["Close"].rolling(20).mean()
        bb_std = df["Close"].rolling(20).std()
        df["BB_Upper"] = df["BB_Mid"] + 2 * bb_std
        df["BB_Lower"] = df["BB_Mid"] - 2 * bb_std

        # Oscilador Estocástico (%K y %D, 14 períodos)
        if "Low" in df.columns and "High" in df.columns:
            low_14  = df["Low"].rolling(14).min()
            high_14 = df["High"].rolling(14).max()
            denom = high_14 - low_14
            df["STOCH_K"] = 100 * (df["Close"] - low_14) / denom.replace(0, float("nan"))
            df["STOCH_D"] = df["STOCH_K"].rolling(3).mean()

        df = df.dropna()
        results[ticker] = df

    return results
