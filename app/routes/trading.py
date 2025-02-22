from fastapi import APIRouter, BackgroundTasks, Depends

from app.models.schemas import BotConfig
from app.services.trading_bot import TradingBot

router = APIRouter(prefix="/api/trading")


@router.post("/start-bot")
async def start_bot(
    config: BotConfig,
    background_tasks: BackgroundTasks,
    trading_bot: TradingBot = Depends(TradingBot),
):
    if trading_bot.is_running:
        return {"status": "error", "message": "Bot already running"}

    background_tasks.add_task(trading_bot.run, config)
    return {"status": "success", "message": "Bot started"}


@router.post("/stop-bot")
async def stop_bot(trading_bot: TradingBot = Depends(TradingBot)):
    trading_bot.stop()
    return {"status": "success", "message": "Bot stopping"}


@router.get("/status")
async def get_status(trading_bot: TradingBot = Depends(TradingBot)):
    return {"is_running": trading_bot.is_running}
