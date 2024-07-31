import os
import unittest
from app.api.services.data_service import download_and_save_historical_data, TICKER_SYMBOLS

class TestHistoricalData(unittest.TestCase):

    def setUp(self):
        self.ticker_symbols = TICKER_SYMBOLS
        self.test_dir = 'test_data'
        os.makedirs(self.test_dir, exist_ok=True)
        print(f"Test data directory: {os.path.abspath(self.test_dir)}")

    def tearDown(self):
        for file_name in os.listdir(self.test_dir):
            file_path = os.path.join(self.test_dir, file_name)
            os.remove(file_path)
        os.rmdir(self.test_dir)

    def test_download_and_save_multiple_symbols(self):
        download_and_save_historical_data(self.ticker_symbols, save_dir=self.test_dir)

        for symbol in self.ticker_symbols:
            expected_file_path = os.path.join(self.test_dir, f"{symbol}_historical_data.csv")
            self.assertTrue(
                os.path.isfile(expected_file_path),
                f"The file {expected_file_path} was not found."
            )

if __name__ == "__main__":
    unittest.main()
