from the_bot.constants import bot_domain
from curl_cffi import requests
from the_bot.helpers.browser_actions import BrowserActions
from the_bot.helpers.read_parameters_for_users import get_user_credentials

HTTP_PROTOCOL = "https://"


class BotSession:
    def __init__(self, schedule_name = None) -> None:
        self.schedule_name = schedule_name

    def bot_session(self):
        act = BrowserActions(None)
        user_credentials = get_user_credentials(self.schedule_name)
        cookiejar = act.automatic_login(user_credentials.get("username"), user_credentials.get("password"))
        if cookiejar:
            session = requests.Session(cookies=cookiejar, impersonate="chrome")
            return session

    def send_msg_to_webhook(self, url, data):
        result = requests.post(url, json=data)
        if 200 <= result.status_code < 300:
            return f"Webhook sent {result.status_code}"
        else:
            raise Exception(f"Webhook failed {result.status_code}")
