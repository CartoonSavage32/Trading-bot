from datetime import datetime
from typing import Dict, List

from app.services.auth_manager import FyersAuthManager
from app.utils.logger import logger


class FyersClient:
    """FYERS API client with auto-login capability"""

    def __init__(self):
        self._client = None
        self._token_expiry = None
        self._initialize_client()
        self.logger = logger

    def _initialize_client(self):
        """Initialize authenticated client"""
        auth_manager = FyersAuthManager()
        profile = auth_manager.login()

        if profile["s"] != "ok":
            raise ConnectionError(f"Login failed: {profile['message']}")

    def _refresh_token_if_needed(self):
        """Refresh the token if it has expired"""
        if datetime.now() >= self._token_expiry:
            self._initialize_client()

    @property
    def client(self):
        """Get authenticated client instance"""
        self._refresh_token_if_needed()
        return self._client

    def get_historical_data(
        self, symbol: str, interval: str, start: str, end: str
    ) -> List[Dict]:
        """Fetch historical candle data from FYERS"""
        try:
            data = self.client.history(
                symbol=symbol,
                resolution=interval,
                date_format="1",
                range_from=start,
                range_to=end,
            )
            return data.get("candles", [])
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            return []

    def place_order(self, order_data: Dict) -> Dict:
        """Generic order placement method"""
        try:
            return self.client.place_order(order_data)
        except Exception as e:
            self.logger.error(f"Order placement failed: {e}")
            return {"status": "error", "message": str(e)}
