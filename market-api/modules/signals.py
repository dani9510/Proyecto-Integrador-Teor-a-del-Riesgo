def compute_signals(data_dict, rsi_oversold=30, rsi_overbought=70):
    """
    Generates technical trading signals for each asset.
    Combines RSI, MACD, Bollinger Bands, Golden/Death Cross and Stochastic Oscillator.
    Parameters rsi_oversold and rsi_overbought allow configurable thresholds.
    """
    signals = {}

    for ticker, df in data_dict.items():
        if ticker in ["^GSPC", "^IRX"]:
            continue

        df = df.copy()

        # ── MACD (already in technical.py, recalculate if missing) ──
        if "MACD" not in df.columns:
            k = df['Close'].ewm(span=12, adjust=False).mean()
            d = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = k - d
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # ── Bollinger Bands (recalculate if missing) ──
        if "BB_Upper" not in df.columns:
            df['BB_Mid']   = df['Close'].rolling(window=20).mean()
            df['BB_Std']   = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = df['BB_Mid'] + df['BB_Std'] * 2
            df['BB_Lower'] = df['BB_Mid'] - df['BB_Std'] * 2

        # ── Golden / Death Cross (SMA 20 vs SMA 50) ──
        df['SMA_50'] = df['Close'].rolling(50).mean()
        if 'SMA_20' not in df.columns:
            df['SMA_20'] = df['Close'].rolling(20).mean()

        # ── Señal Final ──
        df['Final_Signal'] = 'HOLD'

        # Historial de señales (para gráfico)
        df['Sig_Buy']  = False
        df['Sig_Sell'] = False

        try:
            last_rsi      = float(df['RSI'].iloc[-1])       if 'RSI'      in df.columns else 50.0
            last_close    = float(df['Close'].iloc[-1])
            last_bb_lower = float(df['BB_Lower'].iloc[-1])
            last_bb_upper = float(df['BB_Upper'].iloc[-1])
            last_macd     = float(df['MACD'].iloc[-1])
            last_macd_sig = float(df['MACD_Signal'].iloc[-1])

            # Golden / Death Cross (comparar última vela con la anterior)
            golden_cross = False
            death_cross  = False
            if len(df) >= 2:
                prev_sma20 = float(df['SMA_20'].iloc[-2]) if 'SMA_20' in df.columns else None
                prev_sma50 = float(df['SMA_50'].iloc[-2])
                curr_sma20 = float(df['SMA_20'].iloc[-1]) if 'SMA_20' in df.columns else None
                curr_sma50 = float(df['SMA_50'].iloc[-1])
                if None not in (prev_sma20, prev_sma50, curr_sma20, curr_sma50):
                    golden_cross = (prev_sma20 <= prev_sma50) and (curr_sma20 > curr_sma50)
                    death_cross  = (prev_sma20 >= prev_sma50) and (curr_sma20 < curr_sma50)

            # Estocástico
            stoch_buy  = False
            stoch_sell = False
            if 'STOCH_K' in df.columns and 'STOCH_D' in df.columns and len(df) >= 2:
                k_now  = float(df['STOCH_K'].iloc[-1])
                d_now  = float(df['STOCH_D'].iloc[-1])
                k_prev = float(df['STOCH_K'].iloc[-2])
                d_prev = float(df['STOCH_D'].iloc[-2])
                stoch_buy  = (k_prev <= d_prev) and (k_now > d_now) and k_now < 30
                stoch_sell = (k_prev >= d_prev) and (k_now < d_now) and k_now > 70

            # Lógica de compra / venta combinada
            buy_signals  = sum([
                last_rsi < rsi_oversold,
                last_close < last_bb_lower,
                last_macd > last_macd_sig,
                golden_cross,
                stoch_buy,
            ])
            sell_signals = sum([
                last_rsi > rsi_overbought,
                last_close > last_bb_upper,
                last_macd < last_macd_sig,
                death_cross,
                stoch_sell,
            ])

            if buy_signals > sell_signals:
                df.iat[-1, df.columns.get_loc('Final_Signal')] = 'BUY'
                df.iat[-1, df.columns.get_loc('Sig_Buy')]      = True
            elif sell_signals > buy_signals:
                df.iat[-1, df.columns.get_loc('Final_Signal')] = 'SELL'
                df.iat[-1, df.columns.get_loc('Sig_Sell')]     = True

        except Exception as e:
            print(f"Error procesando señales de {ticker}: {e}")

        signals[ticker] = df

    return signals
