from the_bot.helpers.session import BotSession
from the_bot.api.api import BotApi, InvestOperation
from schedule import run_pending
import schedule
import backoff
from the_bot.helpers.logging_helper import log_setup
import os
import time


logger = log_setup(__name__)


class ExecuteOperation:
    MINIMUN_INVESTMENT_PER_COIN = 10

    def __init__(
        self,
        bot_session,
        capital_baseline=500,
        profit_margin=0,
        margin_ratio_percentage=10,
    ) -> None:
        self.bot_session = bot_session
        self.bot_api = BotApi(self.bot_session)
        self.current_coin = None
        self.capital_baseline = capital_baseline
        self.profit_margin = profit_margin
        self.margin_ratio_percentage = margin_ratio_percentage

    def validate_user(self):
        user_info = self.bot_api.user_info()
        logger.info(f"{user_info.get('name')} has initiate session")

    def user_can_operate(self):
        logger.info("Checking if user can operate base on arbitrage balance")
        if (
            self.bot_api.arbitrage_balance() > self.capital_baseline
            and self.bot_api.balance_in_operation() == 0
        ):
            logger.info(
                f"User balance is enough to operate, arbitrage balance: {self.bot_api.arbitrage_balance()}"
            )
            return True

    def increase_profit_margin(self, backoff_event):
        if backoff_event["tries"] >= 3:
            coin_max_profit = self.current_coin.get("max_profit", 0)
            max_loss_accepted = (coin_max_profit * self.margin_ratio_percentage) / 100
            self.profit_margin = coin_max_profit - max_loss_accepted

    def can_invest_in_coin(self, coin) -> dict:

        @backoff.on_exception(
            backoff.constant,
            Exception,
            on_backoff=self.increase_profit_margin,
            interval=10,
            max_tries=6,
            logger=logger,
            raise_on_giveup=False,
        )
        def calculate_coin_profit() -> dict:
            self.current_coin = coin
            bot_suggestion = self.bot_api.solesbot_suggestion_for_coin(coin.get("id"))
            logger.info(f"Checking if {coin.get('abb')} is profitable...")
            coin_profit = float(bot_suggestion.get("profit", 0))
            logger.info(f"Profit of {coin.get('abb')} is {coin_profit}")
            logger.info(f"profit acceptable: {self.profit_margin}")
            if coin_profit >= self.profit_margin:
                return bot_suggestion
            else:
                raise Exception(f"{coin.get('abb')} is not profitable, trying again...")

        return calculate_coin_profit()

    def execute(self):
        if self.user_can_operate():
            arbitrage_balance = self.bot_api.arbitrage_balance()
            while arbitrage_balance >= ExecuteOperation.MINIMUN_INVESTMENT_PER_COIN:
                time.sleep(30)
                all_coins = self.bot_api.all_coins()
                for coin in all_coins:
                    time.sleep(10)
                    self.profit_margin = 0
                    arbitrage_balance = self.bot_api.arbitrage_balance()
                    coin_to_invest: dict = self.can_invest_in_coin(coin)
                    if coin_to_invest:
                        logger.info(f"{coin.get('abb')} is profitable, investing...")
                        buy_id = int(coin_to_invest.get("buy", {}).get("id"))
                        sell_id = int(coin_to_invest.get("sell", {}).get("id"))
                        if coin.get("max_to_invest", 0) <= arbitrage_balance:
                            logger.info(
                                f"Investing {coin.get("max_to_invest", 0)} in {coin.get('abb')}..."
                            )
                            invest = InvestOperation(
                                amount=coin.get("max_to_invest", 0),
                                bot_api=self.bot_api,
                            )
                            invest.submit_suggestion(coin.get("id"), buy_id, sell_id)
                        else:
                            logger.info(
                                f"Investing {arbitrage_balance} in {coin.get('abb')}..."
                            )
                            invest = InvestOperation(
                                amount=arbitrage_balance, bot_api=self.bot_api
                            )
                            invest.submit_suggestion(coin.get("id"), buy_id, sell_id)
        else:
            logger.info(
                f"User balance is not enough to operate, arbitrage balance: {self.bot_api.arbitrage_balance()}, operation balance: {self.bot_api.balance_in_operation()}"
            )


def run_the_bot():
    session = BotSession(os.environ.get("ASPCOOKIE"))
    bot_session = session.bot_session()
    execute_order = ExecuteOperation(bot_session)
    execute_order.execute()


if __name__ == "__main__":
    schedule.every(2).minutes.do(run_the_bot)
    while True:
        run_pending()
        time.sleep(1)
