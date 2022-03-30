import ujson
import base64
from datetime import datetime
import requests
from src.config import API_TELEGRAM_ACCOUNT_NAME, API_TELEGRAM_ACCOUNT_PASSWORD, URL
from loguru import logger
import urllib.parse


class Token:
    def __init__(self):
        self.token = None

    def is_expired(self):
        if self.token is None:
            return True
        decoded = ujson.loads(base64.b64decode(self.token.split(".")[1] + "=="))
        expire_at = int(decoded["exp"])
        expire_at -= 60  # one minute less for fix internet loading
        expire_time = datetime.fromtimestamp(expire_at)
        return expire_time < datetime.now()

    def update_token(self):
        credentials = {
            "username": API_TELEGRAM_ACCOUNT_NAME,
            "password": API_TELEGRAM_ACCOUNT_PASSWORD,
        }
        credentials = urllib.parse.urlencode(credentials)
        logger.debug(f"{credentials}")
        r = requests.post(
            f"{URL}/api/service/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=credentials,
        )

        logger.debug(f"{r.json()}")
        self.token = r.json()["access_token"]

    def get_token(self):
        if self.is_expired():
            self.update_token()
        return self.token
