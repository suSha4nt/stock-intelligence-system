from fastapi import FastAPI
import yfinance as yf

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Stock ML Service Running"}


@app.get("/stock/{symbol}")
def get_stock(symbol: str):
    try:
        data = yf.download(symbol + ".NS", period="5d", progress=False)

        if data is None or data.empty:
            return {"error": "No data found"}

        # 🔥 FIX: Flatten multi-index columns
        data.columns = [col[0] for col in data.columns]

        data = data.tail().reset_index()

        # Convert to safe JSON types
        data["Date"] = data["Date"].astype(str)

        return data.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}