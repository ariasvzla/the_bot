from the_bot.constants import bot_domain, coins
import backoff
import re
import re
from aws_lambda_powertools import Logger
import re

logger = Logger(service="Bot API")
HTTP_PROTOCOL = "https://"


class BotApi:
    def __init__(self, session, coins_lock_container={}) -> None:
        self.known_coins = coins
        self.bot_session = session
        self.coins_lock_container = coins_lock_container

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=5, logger=logger, raise_on_giveup=False
    )
    def get_amount_in_spot(self):
        response = self.bot_session.get(
            f"{HTTP_PROTOCOL}{bot_domain}/wallet/getbalancescoin?coin=usdt&from=spot"
        )
        if 200 <= response.status_code < 300:
            return response.json()

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=5, logger=logger, raise_on_giveup=False
    )
    def all_current_operations(self):
        response = self.bot_session.post(
            f"{HTTP_PROTOCOL}{bot_domain}/robot/getManualOperation?p=0&period=7"
        )
        if 200 <= response.status_code < 300:
            return response.json()

    def pending_operations(self):
        all_current_operations = self.all_current_operations()
        if all_current_operations:
            results = all_current_operations.get("result")
            return [
                {
                    "Amount": float(operation.get("Amount").replace(",", "")),
                    "Coin": operation.get("Coin"),
                    "NetROI": float(operation.get("percentwin").replace(",", ".")),
                }
                for operation in results
                if operation.get("Situation") == "Pending"
            ]

    @backoff.on_exception(backoff.expo, Exception, max_tries=5, logger=logger)
    def get_coins(self):
        response = self.bot_session.get(f"{HTTP_PROTOCOL}{bot_domain}/robot/getCoins")
        if 200 <= response.status_code < 300:
            return response.json()

    def _bot_coins(self):
        coins = self.get_coins()
        logger.info(f"current coins in the lock container: {self.coins_lock_container}")

        filtered_coins = [
            coin
            for coin in coins
            if not self.coins_lock_container.get(coin.get("abb", "no_coin_found"), 0)
        ]
        return filtered_coins

    def all_coins(self, user_strategy) -> list:
        bot_coins = self._bot_coins()
        desired_coins_to_invest = user_strategy if user_strategy else self.known_coins
        coins_to_invest = []
        for desired_coin in desired_coins_to_invest:
            for bot_coin in bot_coins:
                if bot_coin.get("abb") == desired_coin.get("abb"):
                    bot_coin.update(desired_coin)
                    coins_to_invest.append(bot_coin)
        logger.info(f"Bot coins: {coins_to_invest}")
        return coins_to_invest

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=5, logger=logger, raise_on_giveup=False
    )
    def solesbot_suggestion_for_coin(self, coin_id: int) -> dict:
        response = self.bot_session.get(
            f"{HTTP_PROTOCOL}{bot_domain}/robot/suggestionManual/?coin={coin_id}"
        )
        return response.json()

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=5, logger=logger, raise_on_giveup=False
    )
    def user_info(self) -> dict:
        response = self.bot_session.get(f"{HTTP_PROTOCOL}{bot_domain}/home/dataHome")
        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except Exception as e:
                logger.error(f"Response is not a JSON response, actual response: {e}")
                if (
                    re.search("/login?ReturnUrl=", response.text)
                    or "returnUrl" in response.text
                ):
                    return 403
                raise Exception(f"Returned content invalid. Content: {response.text}")
        if response.status_code == 403:
            logger.error(f"User info failed {response.status_code}, {response.reason}")
            return response.status_code

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=5, logger=logger, raise_on_giveup=False
    )
    def balance_in_operation(self) -> float:
        response = self.bot_session.get(
            f"{HTTP_PROTOCOL}{bot_domain}/robot/getBalanceInOperation"
        )
        if 200 <= response.status_code < 300:
            resp_to_json = response.json()
            balance = resp_to_json.get("balance", 0)
            return int(balance)

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=5, logger=logger, raise_on_giveup=False
    )
    def date_in_operation(self):
        return self.bot_session.get(
            f"{HTTP_PROTOCOL}{bot_domain}/robot/getDateInOperation"
        ).json()

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=5, logger=logger, raise_on_giveup=False
    )
    def arbitrage_balance(self) -> float:
        response = self.bot_session.get(
            f"{HTTP_PROTOCOL}{bot_domain}/wallet/getbalancesopman"
        )
        if 200 <= response.status_code < 300:
            resp_to_json = response.json()
            balance = resp_to_json.get("usdt", 0)
            return float(balance.replace(",", ""))

    def add_coin_lock(self, coin):
        logger.info(f"Adding coin lock for {coin.get('abb')}")
        self.coins_lock_container[coin.get("abb")] = 3

    def reduce_coin_lock(self):
        for k, v in self.coins_lock_container.items():
            if v > 0:
                logger.info(f"Reducing coin lock for {k} by 1")
                self.coins_lock_container[k] = v - 1


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
                    return response
                else:
                    response.raise_for_status()
            except Exception as e:
                raise Exception(e)

        return submit()
