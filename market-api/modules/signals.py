import pandas as pd

def compute_signals(data_dict):
    """
    Generates technical signals for each asset based on RSI, MACD and Bollinger Bands.
    """
    signals = {}
    
    for ticker, df in data_dict.items():
        if ticker in ["^GSPC", "^IRX"]: continue
        
        df = df.copy()
        
        # 1. MACD (12, 26, 9)
        k = df['Close'].ewm(span=12, adjust=False).mean()
        d = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = k - d
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # 2. Bollinger Bands
        df['BB_Mid'] = df['Close'].rolling(window=20).mean()
        df['BB_Std'] = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Mid'] + (df['BB_Std'] * 2)
        df['BB_Lower'] = df['BB_Mid'] - (df['BB_Std'] * 2)
        
        # 3. Aggregate Signal Logic
        df['Final_Signal'] = 'HOLD'
        
        # Conditionals
        last_rsi = df['RSI'].iloc[-1] if 'RSI' in df.columns else 50
        last_close = df['Close'].iloc[-1]
        last_bb_lower = df['BB_Lower'].iloc[-1]
        last_bb_upper = df['BB_Upper'].iloc[-1]
        last_macd = df['MACD'].iloc[-1]
        last_macd_sig = df['MACD_Signal'].iloc[-1]
        
        # Simple Buy/Sell Rule
        if last_rsi < 35 or (last_close < last_bb_lower) or (last_macd > last_macd_sig):
            df.loc[df.index[-1], 'Final_Signal'] = 'BUY'
        elif last_rsi > 65 or (last_close > last_bb_upper) or (last_macd < last_macd_sig):
            df.loc[df.index[-1], 'Final_Signal'] = 'SELL'
            
        signals[ticker] = df
        
    return signals
