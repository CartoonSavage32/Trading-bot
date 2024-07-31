from fastapi import FastAPI
from app.api.v1.api_v1 import api_router
from app.api.services.data_service import DataService
from app.api.services.dhan_service import DhanService
from app.api.strategies.breakout_strategy import BreakoutStrategy

app = FastAPI()

# Initialize Dhan API (update with your actual credentials)
dhan = DhanService(client_id="your-client-id", client_secret="your-secret-key", access_token="your-access-token")


# Initialize services and strategy
data_service = DataService()
breakout_strategy = BreakoutStrategy(data_service)
trading_service = dhan


app.include_router(api_router, prefix="/api/v1")
