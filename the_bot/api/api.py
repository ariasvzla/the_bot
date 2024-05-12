from the_bot.constants import bot_domain, coins
import backoff
from the_bot.helpers.logging_helper import log_setup
import os
import re
import json

logger = log_setup(os.path.basename(__file__))
HTTP_PROTOCOL = "https://"


class BotApi:
    def __init__(self, session) -> None:
        self.known_coins = coins
        self.bot_session = session
        self.coins_lock_container = json.loads(os.environ.get("COINS_LOCKED", "{}"))

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=10, logger=logger, raise_on_giveup=False
    )
    def _bot_coins(self):
        response = self.bot_session.get(f"{HTTP_PROTOCOL}{bot_domain}/robot/getCoins")
        filtered_coins = []
        if 200 <= response.status_code < 300:
            bot_coins = response.json()
            filtered_coins = [
                coin
                for coin in bot_coins
                if not self.coins_lock_container.get(
                    coin.get("abb", "no_coin_found"), 0
                )
            ]
        return filtered_coins

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=10, logger=logger, raise_on_giveup=False
    )
    def all_coins(self) -> list:
        bot_coins = self._bot_coins()
        for coin in bot_coins:
            for known_coin in self.known_coins:
                if coin.get("abb") == known_coin.get("abb"):
                    coin.update(known_coin)
        logger.info(f"Bot coins: {bot_coins}")
        return bot_coins

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=10, logger=logger, raise_on_giveup=False
    )
    def solesbot_suggestion_for_coin(self, coin_id: int) -> dict:
        response = self.bot_session.get(
            f"{HTTP_PROTOCOL}{bot_domain}/robot/suggestionManual/?coin={coin_id}"
        )
        return response.json()

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=10, logger=logger, raise_on_giveup=False
    )
    def user_info(self) -> dict:
        response = self.bot_session.get(f"{HTTP_PROTOCOL}{bot_domain}/home/dataHome")
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            logger.error(f"User info failed {response.status_code}, {response.reason}")
            response.raise_for_status()

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=10, logger=logger, raise_on_giveup=False
    )
    def balance_in_operation(self) -> float:
        response = self.bot_session.get(
            f"{HTTP_PROTOCOL}{bot_domain}/robot/getBalanceInOperation"
        )
        return float(response.json().get("balance", 0))

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=10, logger=logger, raise_on_giveup=False
    )
    def date_in_operation(self):
        return self.bot_session.get(
            f"{HTTP_PROTOCOL}{bot_domain}/robot/getDateInOperation"
        ).json()

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=10, logger=logger, raise_on_giveup=False
    )
    def arbitrage_balance(self) -> float:
        response = self.bot_session.get(
            f"{HTTP_PROTOCOL}{bot_domain}/wallet/getbalancesopman"
        )
        return float(response.json().get("usdt", 0))

    def add_coin_lock(self, coin):
        logger.info(f"Adding coin lock for {coin.get('abb')}")
        self.coins_lock_container[coin.get("abb")] = 3
        os.environ["COINS_LOCKED"] = json.dumps(self.coins_lock_container)

    def reduce_coin_lock(self):
        for k, v in self.coins_lock_container.items():
            if v > 0:
                logger.info(f"Reducing coin lock for {k} by 1")
                self.coins_lock_container[k] = v - 1
        os.environ["COINS_LOCKED"] = json.dumps(self.coins_lock_container)


class InvestOperation:
    def __init__(self, arbitrage_balance, coin_max_investment, bot_api: BotApi) -> None:
        self.bot_api = bot_api
        self.bot_session = bot_api.bot_session
        self.coin_max_investment = coin_max_investment
        self.decrease_amount_to_invest_ratio = 0.1
        self.money_to_invest = arbitrage_balance

    @property
    def money_to_invest(self):
        return self._money_to_invest

    @money_to_invest.setter
    def money_to_invest(self, arbitrage_balance):
        if self.coin_max_investment <= arbitrage_balance:
            self._money_to_invest = self.coin_max_investment
        else:
            self._money_to_invest = arbitrage_balance

    def reduce_amount_to_invest(self, backoff_event):
        if backoff_event["tries"] == 3:
            logger.info(
                f"Reducing amount to invest by {self.decrease_amount_to_invest_ratio}..."
            )
            self.money_to_invest = (
                self.money_to_invest - self.decrease_amount_to_invest_ratio
            )

    def submit_suggestion(self, coin: int, buy_id: int, sell_id: int, user: str):

        @backoff.on_exception(
            backoff.constant,
            Exception,
            on_backoff=self.reduce_amount_to_invest,
            interval=10,
            max_tries=5,
            logger=logger,
            raise_on_giveup=False,
        )
        def submit():
            try:
                sug_data = {
                    "amount": str(self.money_to_invest).replace(".", ","),
                    "coin": coin.get("id"),
                    "idbuy": buy_id,
                    "idsell": sell_id,
                    "sug": True,
                }
                logger.info(
                    f"{user} is about to invest in, investment details: {sug_data}"
                )

                response = self.bot_session.post(
                    f"{HTTP_PROTOCOL}{bot_domain}/robot/submitsuggestion", json=sug_data
                )

                if 200 <= response.status_code < 300:
                    response = response.json()

                    error = response.get("error")

                    if error:
                        match_error = re.match(
                            "You can only execute another transaction in.*",
                            error,
                        )
                        if not match_error:
                            raise Exception(error)
                    else:
                        logger.info(
                            f"{user} investment done successfully, results: {response}"
                        )
                        self.bot_api.add_coin_lock(coin)
                    return response
                else:
                    response.raise_for_status()
            except Exception as e:
                raise Exception(e)

        return submit()
