from fastapi import FastAPI
from data.api_data import get_data
from modules.returns import calculate_returns
from modules.technical import compute_indicators
from services.sheets import save_to_sheets

app = FastAPI()

TICKERS = ["AVAL", "^GSPC", "ETH-USD", "IBM", "C6L.SI","NTDOY"]


@app.get("/")
def home():
    return {"status": "API running"}


@app.post("/update-market-data")
def update_data():
    try:
        # 🔥 1. Obtener data
        data = get_data(TICKERS)

        # 🔥 2. Calcular retornos
        returns = calculate_returns(data)

        # 🔥 3. Indicadores técnicos
        indicators = compute_indicators(returns)

        # 🔥 4. Guardar en Google Sheets
        save_to_sheets(indicators)

        return {
            "status": "success",
            "message": "Data updated and sent to Google Sheets"
        }

    except Exception as e:
        print("❌ ERROR EN API:", str(e))

        return {
            "status": "error",
            "message": str(e)
        }