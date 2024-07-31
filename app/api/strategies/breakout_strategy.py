from app.api.services.data_service import DataService


class BreakoutStrategy:
    def __init__(self, data_service: DataService):
        self.data_service = data_service

    def fetch_and_calculate_levels(self, ticker_symbols, start_date, end_date):
        breakout_levels = {}
        for symbol in ticker_symbols:
            data = self.data_service.fetch_historical_data(symbol, start_date, end_date)
            if data is not None:
                high, low = self.data_service.determine_breakout_levels(data)
                breakout_levels[symbol] = {"high": high, "low": low}
        return breakout_levels
