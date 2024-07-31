from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from app.api.services.data_service import DataService
from app.api.services.dhan_service import DhanService
from app.api.strategies.breakout_strategy import BreakoutStrategy

router = APIRouter()

def get_data_service():
    return DataService()

def get_trading_service():
    return DhanService(client_id="your-client-id", client_secret="your-secret-key", access_token="your-access-token")

def get_breakout_strategy(data_service: DataService = Depends(get_data_service)):
    return BreakoutStrategy(data_service)

@router.post("/breakout_levels")
def calculate_breakout_levels(
    ticker_symbols: list[str],
    data_service: DataService = Depends(get_data_service),
    strategy: BreakoutStrategy = Depends(get_breakout_strategy)
):
    start_date = datetime.now() - timedelta(days=60)
    end_date = datetime.now()
    breakout_levels = strategy.fetch_and_calculate_levels(ticker_symbols, start_date, end_date)
    return {"breakout_levels": breakout_levels}

@router.post("/monitor_and_trade")
def monitor_and_trade(
    breakout_levels: dict,
    trading_service: DhanService = Depends(get_trading_service)
):
    trading_service.monitor_and_trade(breakout_levels)
    return {"status": "Monitoring and trading started"}

@router.post("/monitor_and_exit")
def monitor_and_exit(
    breakout_levels: dict,
    trading_service: DhanService = Depends(get_trading_service)
):
    trading_service.monitor_and_exit(breakout_levels)
    return {"status": "Monitoring and exiting trades started"}
