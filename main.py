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

        # Flatten multi-index columns
        data.columns = [col[0] for col in data.columns]

        data = data.tail().reset_index()

        # Convert to safe JSON types
        data["Date"] = data["Date"].astype(str)

        return data.to_dict(orient="records")

    except Exception as e:
        return {"error": str(e)}

@app.get("/signal/{symbol}")
def get_signal(symbol: str):
    import yfinance as yf
    import pandas as pd

    data = yf.download(symbol + ".NS", period="6mo")

    if data.empty:
        return {"error": "No data found"}

    # Fix multi-index columns
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Moving averages
    data['SMA_20'] = data['Close'].rolling(20).mean()
    data['SMA_50'] = data['Close'].rolling(50).mean()

    latest = data.iloc[-1]

    # Handle NaN case
    if pd.isna(latest['SMA_20']) or pd.isna(latest['SMA_50']):
        return {"error": "Not enough data"}

    if latest['SMA_20'] > latest['SMA_50']:
        signal = "BUY"
    elif latest['SMA_20'] < latest['SMA_50']:
        signal = "SELL"
    else:
        signal = "HOLD"

    return {
        "symbol": symbol,
        "signal": signal,
        "close": float(latest['Close'])
    }