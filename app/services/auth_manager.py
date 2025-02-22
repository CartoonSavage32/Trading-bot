from typing import Tuple
from urllib import parse

import pyotp
import requests

from app.config import settings
from app.utils.logger import logger


class FyersAuthManager:
    """Handles FYERS authentication workflow with auto-login capabilities"""

    BASE_URL = "https://api-t2.fyers.in/vagator/v2"
    BASE_URL_V3 = "https://api-t1.fyers.in/api/v3"

    def __init__(self):
        self.session = requests.Session()
        self.access_token = None

    def _send_login_otp(self) -> Tuple[bool, str]:
        """Send login OTP to registered mobile/email"""
        try:
            response = self.session.post(
                f"{self.BASE_URL}/send_login_otp",
                json={
                    "fy_id": settings.fyers_fy_id,
                    "app_id": settings.fyers_app_id_type,
                },
            )
            response.raise_for_status()
            return True, response.json()["request_key"]
        except Exception as e:
            logger.error(f"OTP send failed: {str(e)}")
            return False, str(e)

    def _generate_totp(self) -> str:
        """Generate TOTP using secret key"""
        return pyotp.TOTP(settings.fyers_totp_key).now()

    def _verify_totp(self, request_key: str, totp: str) -> Tuple[bool, str]:
        """Verify TOTP with FYERS API"""
        try:
            response = self.session.post(
                f"{self.BASE_URL}/verify_otp",
                json={"request_key": request_key, "otp": totp},
            )
            response.raise_for_status()
            return True, response.json()["request_key"]
        except Exception as e:
            logger.error(f"TOTP verification failed: {str(e)}")
            return False, str(e)

    def _verify_pin(self, request_key: str) -> Tuple[bool, str]:
        """Verify trading PIN"""
        try:
            response = self.session.post(
                f"{self.BASE_URL}/verify_pin",
                json={
                    "request_key": request_key,
                    "identity_type": "pin",
                    "identifier": settings.fyers_pin,
                },
            )
            response.raise_for_status()
            return True, response.json()["data"]["access_token"]
        except Exception as e:
            logger.error(f"PIN verification failed: {str(e)}")
            return False, str(e)

    def _get_auth_code(self, access_token: str) -> Tuple[bool, str]:
        """Get authorization code"""
        try:
            response = self.session.post(
                f"{self.BASE_URL_V3}/token",
                json={
                    "fyers_id": settings.fyers_fy_id,
                    "app_id": settings.fyers_app_id,
                    "redirect_uri": settings.fyers_redirect_uri,
                    "appType": settings.fyers_app_type,
                    "code_challenge": "",
                    "state": "auto_login",
                    "scope": "",
                    "nonce": "",
                    "response_type": "code",
                    "create_cookie": True,
                },
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            url = response.json()["Url"]
            return True, parse.parse_qs(parse.urlparse(url).query)["auth_code"][0]
        except Exception as e:
            logger.error(f"Auth code fetch failed: {str(e)}")
            return False, str(e)

    def login(self) -> Tuple[bool, str]:
        """Complete login flow"""
        # Step 1: Send login OTP
        success, request_key = self._send_login_otp()
        if not success:
            return False, "OTP send failed"

        # Step 2: Generate and verify TOTP
        totp = self._generate_totp()
        success, new_request_key = self._verify_totp(request_key, totp)
        if not success:
            return False, "TOTP verification failed"

        # Step 3: Verify PIN
        success, access_token = self._verify_pin(new_request_key)
        if not success:
            return False, "PIN verification failed"

        # Step 4: Get auth code
        success, auth_code = self._get_auth_code(access_token)
        if not success:
            return False, "Auth code fetch failed"

        return True, auth_code
