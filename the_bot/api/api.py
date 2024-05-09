from the_bot.constants import bot_domain, coins
import backoff
from the_bot.helpers.logging_helper import log_setup
import os

logger = log_setup(os.path.basename(__file__))
HTTP_PROTOCOL = "https://"


class BotApi:
    def __init__(self, session) -> None:
        self.known_coins = coins
        self.bot_session = session

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=10, logger=logger, raise_on_giveup=False
    )
    def _bot_coins(self):
        return self.bot_session.get(f"{HTTP_PROTOCOL}{bot_domain}/robot/getCoins")

    @backoff.on_exception(
        backoff.expo, Exception, max_tries=10, logger=logger, raise_on_giveup=False
    )
    def all_coins(self) -> list:
        bot_coins = self._bot_coins().json()
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
        return self.bot_session.get(f"{HTTP_PROTOCOL}{bot_domain}/home/dataHome").json()

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

    def submit_suggestion(self, coin_id: int, buy_id: int, sell_id: int, user: str):

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
                    "coin": coin_id,
                    "idbuy": buy_id,
                    "idsell": sell_id,
                    "sug": True,
                }
                logger.info(
                    f"{user} is about to invest in, investment details: {sug_data}"
                )

                response = self.bot_session.post(
                    f"{HTTP_PROTOCOL}{bot_domain}/robot/submitsuggestion", data=sug_data
                ).json()

                logger.info(f"{user}, investment results: {response}")

                error = response if "haserror" in response else False

                if error:
                    if not error["error"].startswith("You can only execute"):
                        raise Exception(response["error"])
            except Exception as e:
                raise Exception(e)

        return submit()
