import logging

from app.config import settings


class TradeLogger:
    def __init__(self):
        self.logger = logging.getLogger("trade_logger")
        self.logger.setLevel(logging.INFO)
        self._configure_logger()

    def _configure_logger(self):
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File handler
        file_handler = logging.FileHandler(settings.log_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def log_entry(self, scrip: str, entry_price: float, sl: float, quantity: int):
        message = (
            f"ENTRY SIGNAL - Scrip: {scrip} | "
            f"Entry Price: {entry_price:.2f} | "
            f"SL: {sl:.2f} | "
            f"Qty: {quantity}"
        )
        self.logger.info(message)

    def log_exit(self, scrip: str, exit_price: float, pnl: float, reason: str):
        message = (
            f"EXIT SIGNAL - Scrip: {scrip} | "
            f"Exit Price: {exit_price:.2f} | "
            f"PNL: {pnl:.2f} | "
            f"Reason: {reason}"
        )
        self.logger.info(message)
