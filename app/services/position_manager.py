class PositionManager:
    def __init__(self, capital: float, risk_per_trade: float = 0.01):
        self.capital = capital
        self.risk_per_trade = risk_per_trade

    def calculate_position_size(self, entry: float, sl: float) -> int:
        """Calculate position size with risk management"""
        risk_amount = self.capital * self.risk_per_trade
        risk_per_share = entry - sl
        if risk_per_share <= 0:
            return 0
        raw_size = risk_amount / risk_per_share
        return int(0.95 * raw_size)
