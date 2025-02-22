from typing import Dict, List

from fyers_apiv3 import fyersModel

from app.config import settings
from app.services.auth_manager import FyersAuthManager
from app.utils.logger import logger


class FyersClient:
    """FYERS API client with auto-login capability"""

    def __init__(self):
        self._client = None
        self._initialize_client()
        self.logger = logger

    def _initialize_client(self):
        """Initialize authenticated client"""
        auth_manager = FyersAuthManager()
        success, auth_code = auth_manager.login()

        if not success:
            raise ConnectionError(f"Login failed: {auth_code}")

        session = fyersModel.SessionModel(
            client_id=settings.fyers_client_id,
            secret_key=settings.fyers_secret_key,
            redirect_uri=settings.fyers_redirect_uri,
            response_type="code",
            grant_type="authorization_code",
        )

        session.set_token(auth_code)
        response = session.generate_token()

        if response.get("s") == "error":
            raise ConnectionError(f"Token generation failed: {response.get('message')}")

        self._client = fyersModel.FyersModel(
            client_id=settings.fyers_client_id,
            token=response["access_token"],
            log_path="/logs",
            is_async=False,
        )

    @property
    def client(self):
        """Get authenticated client instance"""
        if not self._client:
            self._initialize_client()
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
