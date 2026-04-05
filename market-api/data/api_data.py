import yfinance as yf
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

        df = df.reset_index()

        data[ticker] = df

    return data