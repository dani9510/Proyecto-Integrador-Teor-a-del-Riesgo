import requests
import pandas as pd

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbwE11WuYvb-AWf2upc5zWOtHOuHM-Usoer13Egx80mHwGkK-cJ22dq0Y_TvMeBcFa3c/exec"


def clean_dataframe(df, ticker):
    df = df.copy()

    # 🔥 Limitar a últimos 200 registros
    df = df.tail(200)

    # 🔥 Reset index (evita problemas con fechas como índice)
    df = df.reset_index()

    # 🔥 Agregar ticker
    df["ticker"] = ticker

    # 🔥 Convertir TODO a string (evita problemas JSON)
    for col in df.columns:
        df[col] = df[col].astype(str)

    return df.to_dict(orient="records")


def save_to_sheets(data_dict):
    all_data = []

    for ticker, df in data_dict.items():

        # 🔥 Si columnas son MultiIndex (tuplas) → convertir a string
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = ['_'.join(map(str, col)) for col in df.columns]

        clean_records = clean_dataframe(df, ticker)

        all_data.extend(clean_records)

    try:
        response = requests.post(WEBHOOK_URL, json=all_data)

        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        if response.status_code != 200:
            raise Exception(response.text)

    except Exception as e:
        print("❌ ERROR ENVIANDO A SHEETS:", str(e))
        raise