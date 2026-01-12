from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app

client = TestClient(app)

def test_get_stock_price_success():
    """Test a successful stock price retrieval with mocking."""
    # We patch 'yfinance.Ticker' to avoid making a real network call
    with patch("yfinance.Ticker") as mock_ticker:
        # Setup the mock to return a fake price and currency
        mock_instance = MagicMock()
        mock_instance.fast_info = {
            "last_price": 150.00,
            "currency": "USD"
        }
        mock_ticker.return_value = mock_instance

        response = client.get("/price/AAPL")

        assert response.status_code == 200
        assert response.json() == {
            "symbol": "AAPL",
            "current_price": 150.0,
            "currency": "USD"
        }

def test_get_stock_price_not_found():
    """Test behavior when the stock price is missing."""
    with patch("yfinance.Ticker") as mock_ticker:
        mock_instance = MagicMock()
        mock_instance.fast_info = {"last_price": None}
        mock_ticker.return_value = mock_instance

        response = client.get("/price/INVALID")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]