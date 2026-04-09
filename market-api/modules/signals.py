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
        
        try:
            # Extracción estricta de variables escalares
            last_rsi = float(df['RSI'].iloc[-1]) if 'RSI' in df.columns else 50.0
            last_close = float(df['Close'].iloc[-1])
            last_bb_lower = float(df['BB_Lower'].iloc[-1])
            last_bb_upper = float(df['BB_Upper'].iloc[-1])
            last_macd = float(df['MACD'].iloc[-1])
            last_macd_sig = float(df['MACD_Signal'].iloc[-1])
            
            # Simple Buy/Sell Rule (Scalar validation to avoid pandas ambiguity)
            is_buy = (last_rsi < 30) or (last_close < last_bb_lower) or (last_macd > last_macd_sig)
            is_sell = (last_rsi > 70) or (last_close > last_bb_upper) or (last_macd < last_macd_sig)
            
            if is_buy and not is_sell:
                df.iat[-1, df.columns.get_loc('Final_Signal')] = 'BUY'
            elif is_sell and not is_buy:
                df.iat[-1, df.columns.get_loc('Final_Signal')] = 'SELL'
                
        except Exception as e:
            print(f"Error procesando señales de {ticker}: {e}")
            
        signals[ticker] = df
        
    return signals
