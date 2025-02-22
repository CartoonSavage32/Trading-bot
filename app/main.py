from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI

from app.services.trading_bot import TradingBot
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize scheduler
    scheduler = AsyncIOScheduler()
    trading_bot = TradingBot()

    # Schedule for Mondays at 9:00 AM
    scheduler.add_job(trading_bot.run, "cron", day_of_week="mon-fri", hour=9, minute=0)

    scheduler.start()
    logger.info("Scheduler started")

    yield

    # Shutdown
    scheduler.shutdown()
    await trading_bot.shutdown()
    logger.info("Scheduler stopped")
