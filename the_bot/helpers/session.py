from the_bot.constants import bot_domain
import requests.cookies

HTTP_PROTOCOL = "https://"


class BotSession:
    def __init__(self, auth_cookie=None) -> None:
        self.auth_cookie = {".ASPXAUTH": auth_cookie}

    def bot_session(self):
        session = requests.Session()
        session.headers = {
            "Accept": "application/json; charset=utf-8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cookie": f".ASPXAUTH={self.auth_cookie[".ASPXAUTH"]}",
            "Host": bot_domain,
            "Referer": HTTP_PROTOCOL + bot_domain + "arbitrage/manual",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "Trailers",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        }
        my_cookies = {**self.auth_cookie}
        requests.utils.add_dict_to_cookiejar(session.cookies, my_cookies)
        return session

    def send_msg_to_webhook(self, url, data):
        result = requests.post(url, json=data)
        if 200 <= result.status_code < 300:
            return f"Webhook sent {result.status_code}"
        else:
            raise Exception(f"Webhook failed {result.status_code}")
