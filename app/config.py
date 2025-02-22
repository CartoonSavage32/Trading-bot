from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    fyers_app_id: str
    fyers_secret_key: str
    fyers_client_id: str
    fyers_redirect_uri: str
    fyers_fy_id: str
    fyers_pin: str
    fyers_totp_key: str
    fyers_app_type: str = "100"
    fyers_app_id_type: str = "2"

    model_config = ConfigDict(env_file=".env")

    # test_mode: bool = True  # Set to False for real trading
    # log_file: str = "trading_logs.txt"


settings = Settings()
