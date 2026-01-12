from fastapi import FastAPI, HTTPException
import yfinance as yf

app = FastAPI(title="Stock Price API")

@app.get("/price/{symbol}")
def get_stock_price(symbol: str):
    try:
        ticker = yf.Ticker(symbol)

        # Strategy 1: Attempt to get price from fast_info
        info = ticker.fast_info
        price = None
        if info is not None:
            price = info.get('last_price')
            currency = info.get('currency', 'USD')

        # Strategy 2: Fallback to history if fast_info is empty or None
        if price is None:
            # Download the last 1 day of data
            hist = ticker.history(period="1d")
            if not hist.empty:
                # Get the last closing price from the dataframe
                price = hist['Close'].iloc[-1]
                currency = ticker.info.get('currency', 'USD')

        # Final check if both strategies failed
        if price is None:
            raise HTTPException(status_code=404, detail="Stock symbol not found or price unavailable")

        return {
            "symbol": symbol.upper(),
            "current_price": round(float(price), 2),
            "currency": currency
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)