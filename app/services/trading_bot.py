import asyncio
from datetime import datetime, time

from app.config import settings
from app.services.fyers_client import FyersClient
from app.services.position_manager import PositionManager
from app.services.strategy_manager import StrategyFactory
from app.services.test_logger import TradeLogger
from app.utils.logger import logger


class TradingBot:
    def __init__(self):
        self.is_running = False
        self.fyers = FyersClient().client
        self.position_manager = PositionManager(
            settings.capital_amount, settings.risk_per_trade
        )
        self.logger = TradeLogger() if self.test_mode else None

    async def run(self, config):
        self.is_running = True
        strategy = StrategyFactory.create_strategy(config.strategy_name)

        while self.is_running:
            await self.check_market(strategy, config.scrips)
            await asyncio.sleep(1)

    async def check_market(self, strategy, scrips):
        current_time = datetime.now().time()
        if time(9, 30) <= current_time <= time(15, 15):
            for scrip in scrips:
                await self.process_scrip(strategy, scrip)

    async def process_scrip(self, strategy, scrip):
        try:
            data = self.fyers.get_historical_data(scrip, "5", "today", "now")
            if not data:
                return

            entry, sl = strategy.calculate_entry_levels(data)
            ltp = self.get_current_price(scrip)

            if ltp >= entry:
                position_size = self.position_manager.calculate_position_size(entry, sl)

                if self.test_mode:
                    self.logger.log_entry(
                        scrip=scrip, entry_price=entry, sl=sl, quantity=position_size
                    )
                    # Store virtual position for exit logging
                    self.virtual_positions[scrip] = {
                        "entry_price": entry,
                        "sl": sl,
                        "quantity": position_size,
                    }
                else:
                    self.place_real_order(scrip, position_size, entry, sl)

        except Exception as e:
            logger.error(f"Error processing {scrip}: {str(e)}")

    async def monitor_exits(self):
        while True:
            if self.test_mode:
                await self.check_virtual_exits()
            else:
                await self.check_real_exits()
            await asyncio.sleep(5)

    async def check_virtual_exits(self):
        current_time = datetime.now().time()
        for scrip, position in self.virtual_positions.items():
            ltp = self.get_current_price(scrip)
            exit_reason = None

            # Check SL hit
            if ltp <= position["sl"]:
                exit_reason = "SL Triggered"

            # Check time exit
            elif current_time >= time(15, 15):
                exit_reason = "Time Exit"

            if exit_reason:
                pnl = (ltp - position["entry_price"]) * position["quantity"]
                self.logger.log_exit(
                    scrip=scrip, exit_price=ltp, pnl=pnl, reason=exit_reason
                )
                del self.virtual_positions[scrip]

    def stop(self):
        self.is_running = False
