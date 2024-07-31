import time
from datetime import datetime
from app.config import Config


class DhanService:
    def __init__(self, client_id: str, client_secret: str, access_token: str):
        self.base_url = "https://api.dhan.com"  # Base URL for Dhan API
        self.client_id = "<Your Client ID>"
        self.client_secret = "<Your Client Secret>"
        self.access_token = None

    def place_order(self, symbol, quantity, order_type="buy"):
        order = {
            "symbol": symbol,
            "qty": quantity,
            "type": 2,  # Market order
            "side": 1 if order_type == "buy" else -1,  # Buy/Sell
            "productType": "CNC",
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": "False",
            "stopLoss": 0,
            "takeProfit": 0,
        }
        response = self.fyers.place_order(order)
        return response

    def monitor_and_trade(self, breakout_levels):
        while True:
            current_time = datetime.now()
            if current_time.hour >= 9 and current_time.minute >= 30:
                for scrip, levels in breakout_levels.items():
                    high = levels["high"]
                    low = levels["low"]
                    trigger_value = high * 1.0009
                    initial_sl = low * 0.9991

                    data = self.fyers.quotes({"symbols": scrip})
                    ltp = data["d"][0]["v"]["lp"]

                    if ltp > trigger_value:
                        position_size = int(
                            (Config.CAPITAL_AMOUNT * 0.01)
                            / (trigger_value - initial_sl)
                        )
                        quantity = int(0.95 * position_size)
                        response = self.place_order(scrip, quantity)
                        print(f"Order placed for {scrip}: {response}")
                        levels["order_details"] = {
                            "quantity": quantity,
                            "entry_price": trigger_value,
                            "initial_sl": initial_sl,
                        }
                        break

            time.sleep(Config.CHECK_INTERVAL)

    def exit_order(self, symbol, quantity):
        order = {
            "symbol": symbol,
            "qty": quantity,
            "type": 2,  # Market order
            "side": -1,  # Sell
            "productType": "CNC",
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": "False",
            "stopLoss": 0,
            "takeProfit": 0,
        }
        response = self.fyers.place_order(order)
        return response

    def monitor_and_exit(self, breakout_levels):
        while True:
            current_time = datetime.now()
            for scrip, levels in breakout_levels.items():
                if "order_details" in levels:
                    entry_price = levels["order_details"]["entry_price"]
                    initial_sl = levels["order_details"]["initial_sl"]
                    quantity = levels["order_details"]["quantity"]

                    data = self.fyers.quotes({"symbols": scrip})
                    ltp = data["d"][0]["v"]["lp"]

                    if ltp <= initial_sl or (
                        current_time.hour >= 15 and current_time.minute >= 15
                    ):
                        response = self.exit_order(scrip, quantity)
                        print(f"Order exited for {scrip}: {response}")
                        del levels["order_details"]

            time.sleep(Config.CHECK_INTERVAL)
