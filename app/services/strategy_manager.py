from abc import ABC, abstractmethod
from typing import Tuple

import pandas as pd


class BaseStrategy(ABC):
    @abstractmethod
    def calculate_entry_levels(self, data: pd.DataFrame) -> Tuple[float, float]:
        pass


class ORBStrategy(BaseStrategy):
    def __init__(self, entry_buffer: float = 0.0009, sl_buffer: float = 0.0009):
        self.entry_buffer = 1 + entry_buffer
        self.sl_buffer = 1 - sl_buffer

    def calculate_entry_levels(self, data: pd.DataFrame) -> Tuple[float, float]:
        """Calculate ORB levels from first 3 5-min candles"""
        if len(data) < 3:
            raise ValueError("Insufficient data for ORB calculation")

        first_3 = data.head(3)
        high = first_3["high"].max()
        low = first_3["low"].min()
        return high * self.entry_buffer, low * self.sl_buffer


class StrategyFactory:
    strategies = {"ORB": ORBStrategy}

    @classmethod
    def create_strategy(cls, strategy_name: str, **kwargs):
        strategy_class = cls.strategies.get(strategy_name)
        if not strategy_class:
            raise ValueError(f"Strategy {strategy_name} not found")
        return strategy_class(**kwargs)
