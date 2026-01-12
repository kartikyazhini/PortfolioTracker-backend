from fastapi import FastAPI, HTTPException
import yfinance as yf

app = FastAPI(title="Stock Price API")

@app.get("/price/{symbol}")
def get_stock_price(symbol: str):
    try:
        # 1. Initialize ticker (Works for AAPL, INTC, and VFIAX)
        ticker = yf.Ticker(symbol)

        # 2. Strategy: Use history with a 5-day window for maximum compatibility
        # Index funds/Mutual funds don't update intraday, so we look at the last few days
        hist = ticker.history(period="5d")

        if hist.empty:
            # Last resort: try to get the 'previousClose' from info if history is empty
            price = ticker.info.get('previousClose')
            currency = ticker.info.get('currency', 'USD')
        else:
            # Get the very last valid closing price in the 5-day window
            price = hist['Close'].iloc[-1]
            currency = ticker.info.get('currency', 'USD')

        if price is None:
            raise HTTPException(status_code=404, detail=f"Data for {symbol} not found")

        return {
            "symbol": symbol.upper(),
            "current_price": round(float(price), 2),
            "currency": currency,
            "type": "Index/Mutual Fund" if len(symbol) == 5 and symbol.endswith('X') else "Stock/ETF"
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)