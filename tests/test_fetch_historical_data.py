import pytest

from app.services.fyers_client import FyersClient


@pytest.fixture
def fyers_client():
    return FyersClient()


def test_fetch_historical_data(fyers_client):
    symbol = "NSE:RELIANCE"
    interval = "D"
    start = "2023-01-01"
    end = "2023-12-31"

    data = fyers_client.get_historical_data(symbol, interval, start, end)

    assert isinstance(data, list)
    if data:
        assert isinstance(data[0], dict)
        assert "timestamp" in data[0]
        assert "open" in data[0]
        assert "high" in data[0]
        assert "low" in data[0]
        assert "close" in data[0]
        assert "volume" in data[0]
