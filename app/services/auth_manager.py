import sys
import time
from urllib import parse

import pyotp
import requests
from fyers_apiv3 import fyersModel

from app.config import settings
from app.utils.logger import logger


class FyersAuthManager:
    # API endpoints as class constants
    BASE_URL = "https://api-t2.fyers.in/vagator/v2"
    BASE_URL_2 = "https://api-t1.fyers.in/api/v3"
    URL_SEND_LOGIN_OTP = BASE_URL + "/send_login_otp"
    URL_VERIFY_TOTP = BASE_URL + "/verify_otp"
    URL_VERIFY_PIN = BASE_URL + "/verify_pin"
    URL_TOKEN = BASE_URL_2 + "/token"
    URL_VALIDATE_AUTH_CODE = BASE_URL_2 + "/validate-authcode"

    SUCCESS = 1
    ERROR = -1

    def __init__(self):
        """
        Initialize the FyersAuth instance by reading configuration from settings.py.
        """
        self.fy_id = settings.fyers_fy_id
        self.app_id = settings.fyers_app_id
        self.totp_key = settings.fyers_totp_key
        self.pin = settings.fyers_pin
        self.client_id = settings.fyers_client_id
        self.secret_key = settings.fyers_secret_key
        self.redirect_uri = settings.fyers_redirect_uri
        self.app_type = settings.fyers_app_type

        self.session = requests.Session()
        self.fyers_session = None  # This will be an instance of fyersModel.SessionModel
        self.logger = logger

    def send_login_otp(self):
        """Call send_login_otp API to get the request key."""
        try:
            response = self.session.post(
                url=self.URL_SEND_LOGIN_OTP,
                json={"fy_id": self.fy_id, "app_id": self.app_id},
            )
            if response.status_code != 200:
                return [self.ERROR, response.text]
            result = response.json()
            request_key = result.get("request_key")
            return [self.SUCCESS, request_key]
        except Exception as e:
            return [self.ERROR, e]

    def generate_totp(self):
        """Generate a TOTP using the provided secret key."""
        try:
            totp = pyotp.TOTP(self.totp_key).now()
            return [self.SUCCESS, totp]
        except Exception as e:
            return [self.ERROR, e]

    def verify_totp(self, request_key, totp):
        """Verify the TOTP using the verify_otp API."""
        self.logger.debug("6 digits >>>", totp)
        self.logger.debug("Request key >>>", request_key)
        try:
            response = self.session.post(
                url=self.URL_VERIFY_TOTP,
                json={"request_key": request_key, "otp": totp},
            )
            if response.status_code != 200:
                return [self.ERROR, response.text]
            result = response.json()
            new_request_key = result.get("request_key")
            return [self.SUCCESS, new_request_key]
        except Exception as e:
            return [self.ERROR, e]

    def verify_pin(self, request_key):
        """Verify the PIN using the verify_pin API to get an access token."""
        try:
            payload = {
                "request_key": request_key,
                "identity_type": "pin",
                "identifier": self.pin,
            }
            response = self.session.post(url=self.URL_VERIFY_PIN, json=payload)
            if response.status_code != 200:
                return [self.ERROR, response.text]
            result = response.json()
            access_token = result.get("data", {}).get("access_token")
            return [self.SUCCESS, access_token]
        except Exception as e:
            return [self.ERROR, e]

    def get_auth_code(self, access_token):
        """
        Get the auth code for the API V2 App by calling the token API.
        Expect a 308 redirect response.
        """
        try:
            payload = {
                "fyers_id": self.fy_id,
                "app_id": self.app_id,
                "redirect_uri": self.redirect_uri,
                "appType": "100",
                "code_challenge": "",
                "state": "sample_state",
                "scope": "",
                "nonce": "",
                "response_type": "code",
                "create_cookie": True,
            }
            headers = {"Authorization": f"Bearer {access_token}"}
            response = self.session.post(
                url=self.URL_TOKEN, json=payload, headers=headers
            )
            if response.status_code != 308:
                return [self.ERROR, response.text]
            result = response.json()
            url_val = result.get("Url")
            auth_code = parse.parse_qs(parse.urlparse(url_val).query)["auth_code"][0]
            return [self.SUCCESS, auth_code]
        except Exception as e:
            return [self.ERROR, e]

    def login(self):
        """
        Perform the entire authentication flow:
          1. Initialize the Fyers session and log activation URL.
          2. Send login OTP.
          3. Generate and verify TOTP (with up to two attempts).
          4. Verify PIN to get the trade access token.
          5. Retrieve the auth code.
          6. Generate the final access token.
          7. Get the user profile.
        """
        # Step 1: Initialize Fyers session and log activation URL.
        self.logger.debug("Initializing Fyers Session")
        self.fyers_session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=self.secret_key,
            redirect_uri=self.redirect_uri,
            response_type="code",
            grant_type="authorization_code",
        )
        auth_url = self.fyers_session.generate_authcode()
        self.logger.debug(f"URL to activate APP: {auth_url}")

        # Step 2: Send login OTP.
        send_otp_result = self.send_login_otp()
        if send_otp_result[0] != self.SUCCESS:
            self.logger.debug(f"send_login_otp failure: {send_otp_result[1]}")
            sys.exit(1)
        self.logger.debug("send_login_otp success")

        # Step 3: Generate TOTP.
        totp_result = self.generate_totp()
        if totp_result[0] != self.SUCCESS:
            self.logger.debug(f"generate_totp failure: {totp_result[1]}")
            sys.exit(1)
        self.logger.debug("generate_totp success")
        totp = totp_result[1]
        request_key = send_otp_result[1]

        # Step 4: Verify TOTP (attempt twice if needed).
        verify_totp_result = None
        for attempt in range(2):
            verify_totp_result = self.verify_totp(request_key, totp)
            if verify_totp_result[0] == self.SUCCESS:
                self.logger.debug(f"verify_totp success on attempt {attempt + 1}")
                break
            else:
                self.logger.debug(
                    f"verify_totp failure on attempt {attempt + 1}: {verify_totp_result[1]}"
                )
                time.sleep(1)
        if verify_totp_result[0] != self.SUCCESS:
            sys.exit(1)

        # Step 5: Verify PIN.
        new_request_key = verify_totp_result[1]
        verify_pin_result = self.verify_pin(new_request_key)
        if verify_pin_result[0] != self.SUCCESS:
            self.logger.debug(f"verify_pin failure: {verify_pin_result[1]}")
            sys.exit(1)
        self.logger.debug("verify_pin success")
        access_token = verify_pin_result[1]
        self.session.headers.update({"authorization": f"Bearer {access_token}"})

        # Step 6: Get auth code.
        token_result = self.get_auth_code(access_token)
        if token_result[0] != self.SUCCESS:
            self.logger.debug(f"get_auth_code failure: {token_result[1]}")
            sys.exit(1)
        self.logger.debug("get_auth_code success")
        auth_code = token_result[1]

        # Step 7: Set the auth code in the Fyers session and generate the final token.
        self.fyers_session.set_token(auth_code)
        token_response = self.fyers_session.generate_token()
        if token_response.get("s") == "ERROR":
            self.logger.debug("\nCannot Login. Check your credentials thoroughly!")
            sys.exit(1)
        access_token_final = token_response.get("access_token")
        self.logger.debug("Access token:", access_token_final)

        # Step 8: Initialize FyersModel and retrieve the user profile.
        fyers_instance = fyersModel.FyersModel(
            client_id=self.client_id, is_async=False, token=access_token_final
        )
        profile = fyers_instance.get_profile()
        self.logger.debug("User Profile:", profile)
        return profile
