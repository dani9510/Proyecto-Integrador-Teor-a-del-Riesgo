from fastapi import FastAPI
from data.api_data import get_data
from modules.returns import calculate_returns
from modules.technical import compute_indicators
from services.sheets import save_to_sheets

# Importación de Módulos de Riesgo
from modules.garch import compute_garch
from modules.capm import compute_capm
from modules.var import compute_var

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

        # 🔥 Modelos Funcionales de Riesgo Financiero
        garch_data = compute_garch(indicators)
        capm_data = compute_capm(garch_data)
        final_risk_data = compute_var(capm_data)

        # 🔥 4. Guardar en Google Sheets
        save_to_sheets(final_risk_data)

        return {
            "status": "success",
            "message": "Data updated and sent to Google Sheets with Risk Metrics"
        }

    except Exception as e:
        print("❌ ERROR EN API:", str(e))

        return {
            "status": "error",
            "message": str(e)
        }