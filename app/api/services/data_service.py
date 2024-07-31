import os
import yfinance as yf
import pandas as pd

class DataService:
    def fetch_historical_data(self, ticker_symbol, start_date, end_date, interval="5m"):
        """Fetch historical data for a given ticker symbol from Yahoo Finance."""
        data = yf.download(
            tickers=ticker_symbol,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval=interval,
        )
        if data.empty:
            print(f"No data found for {ticker_symbol}")
            return None
        return data


    def determine_breakout_levels(self, data):
        """Determine breakout levels based on high and low prices."""
        high = data["high"].max()
        low = data["low"].min()
        return high, low


    def save_to_csv(self, data, filename):
        """Save the given data to a CSV file."""
        data.to_csv(filename, index=False)
        print(f"Saved {filename}")
        
    def download_and_save_historical_data(self, ticker_symbols, save_dir="."):
        """Download and save historical data for a list of ticker symbols."""
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.DateOffset(days=59)

        for ticker_symbol in ticker_symbols:
            data = self.fetch_historical_data(ticker_symbol, start_date, end_date)
            if data is not None:
                csv_filename = os.path.join(
                    save_dir, f"{ticker_symbol}_historical_data.csv"
                )
                self.save_to_csv(data, csv_filename)


    # List of ticker symbols to process with NSE suffix
    TICKER_SYMBOLS = [
        "CDSL.NS",
        "BLUESTARCO.NS",
        "FINCABLES.NS",
        "CAMS.NS",
        "GLENMARK.NS",
        "NCC.NS",
        "NH.NS",
        "HFCL.NS",
        "INDIAMART.NS",
        "SONATSOFTW.NS",
        "BSOFT.NS",
        "CROMPTON.NS",
        "AARTIIND.NS",
        "GSPL.NS",
        "NATCOPHARM.NS",
        "HAPPSTMNDS.NS",
        "CENTURYTEX.NS",
        "TANLA.NS",
        "NATIONALUM.NS",
        "MGL.NS",
        "CASTROLIND.NS",
        "RKFORGE.NS",
        "ZENSARTECH.NS",
        "EXIDEIND.NS",
        "APARINDS.NS",
        "CYIENT.NS",
        "NAVINFLUOR.NS",
    ]
