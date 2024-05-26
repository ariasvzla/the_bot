from the_bot.constants import bot_domain
from curl_cffi import requests


HTTP_PROTOCOL = "https://"


class BotSession:
    def __init__(self, auth_cookie=None) -> None:
        self.auth_cookie = {".ASPXAUTH": auth_cookie}

    def bot_session(self):
        my_cookies = {**self.auth_cookie}

        session = requests.Session(cookies=my_cookies, impersonate="safari")
        return session

    def send_msg_to_webhook(self, url, data):
        result = requests.post(url, json=data)
        if 200 <= result.status_code < 300:
            return f"Webhook sent {result.status_code}"
        else:
            raise Exception(f"Webhook failed {result.status_code}")
