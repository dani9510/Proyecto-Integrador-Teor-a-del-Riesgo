import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_data(tickers):

    end_date = datetime.today()
    start_date = end_date - timedelta(days=365*2)

    data = {}

    for ticker in tickers:
        df = yf.download(
            ticker,
            start=start_date,
            end=end_date,
            interval="1d"
        )

        if df.empty:
            continue

        # Aplanar el MultiIndex que introduce la nueva versión de yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [col[0] for col in df.columns]

        # Mantener el DatetimeIndex para que los gráficos usen fechas reales
        df.index.name = "Date"

        data[ticker] = df

    return data