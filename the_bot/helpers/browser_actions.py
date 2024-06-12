import mechanize
from the_bot.api.api import BotApi
import backoff
from aws_lambda_powertools import Logger

from the_bot.constants import bot_domain
from curl_cffi import requests

logger = Logger(service="Browser Actions")
class BrowserActions:
    def __init__(self, bot_api: BotApi):
        self.browser = mechanize.Browser()
        self.browser.addheaders = [
            (
                "User-agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            )
        ]
        self.bot_api = bot_api

    def _set_cookies(self, cookies):
        cookie_jar = mechanize.CookieJar()
        self.browser.set_cookiejar(cookies)

    def _set_form(self):
        self.browser.select_form(nr=0)
        self.browser.form.set_all_readonly(False)

    def _submit_form(self):
        return self.browser.submit()
    
    @backoff.on_exception(backoff.expo, Exception, max_tries=10, logger=logger, raise_on_giveup=False)
    def automatic_login(self, email, password):
        self.browser.open("https://bot.solesbot.ai/dashboard")
        self._set_form()
        self.browser.form["Email"] = email
        self.browser.form["Password"] = password
        self._submit_form()
        if self.browser.response().code == 200:
            return self.browser.cookiejar
     
    @backoff.on_exception(backoff.expo, Exception, max_tries=10, logger=logger, raise_on_giveup=False)
    def transfer_from_spot_to_arbritage(self, amount_to_transfer, cookies):
        self._set_cookies(cookies)
        self.browser.open("https://bot.solesbot.ai/wallet/transfer")
        self._set_form()
        self.browser.form["wallet"] = "usdt"
        self.browser.form["amount"] = amount_to_transfer.replace(".", ",")
        self.browser.form["fromWalletvl"] = "spot"
        self.browser.form["toWalletvl"] = "arbitrage"
        self._submit_form()
        if self.browser.response().code == 200:
            return True

    def withdraw_money(self):
        pass