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

        # 🔥 Modelos Funcionales de Riesgo Financiero (Nivel Senior: Desacoplados)
        # Cada modelo opera sobre los indicadores base de forma independiente
        garch_res = compute_garch(indicators)
        capm_res = compute_capm(indicators)
        var_res = compute_var(indicators)

        # 🔥 Consolidación de Resultados
        # Combinamos las columnas generadas por cada modelo en un solo set de datos
        final_risk_data = {}
        for ticker in indicators.keys():
            df = indicators[ticker].copy()
            
            # Unir columnas de GARCH
            if ticker in garch_res:
                cols_to_add = [c for c in garch_res[ticker].columns if c not in df.columns]
                for col in cols_to_add:
                    df[col] = garch_res[ticker][col]
            
            # Unir columnas de CAPM
            if ticker in capm_res:
                cols_to_add = [c for c in capm_res[ticker].columns if c not in df.columns]
                for col in cols_to_add:
                    df[col] = capm_res[ticker][col]
            
            # Unir columnas de VaR
            if ticker in var_res:
                cols_to_add = [c for c in var_res[ticker].columns if c not in df.columns]
                for col in cols_to_add:
                    df[col] = var_res[ticker][col]
            
            final_risk_data[ticker] = df

        # 🔥 4. Guardar en Google Sheets
        save_to_sheets(final_risk_data)

        return {
            "status": "success",
            "message": "Data updated and sent to Google Sheets with Senior Risk Architecture (Parallel Processing)"
        }

    except Exception as e:
        print("❌ ERROR EN API:", str(e))

        return {
            "status": "error",
            "message": str(e)
        }