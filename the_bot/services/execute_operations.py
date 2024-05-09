from the_bot.helpers.session import BotSession
from the_bot.api.api import BotApi, InvestOperation
from schedule import run_pending
import schedule
import backoff
from the_bot.helpers.logging_helper import log_setup
import os
import time
from the_bot.services.notification_services import send_msg


logger = log_setup(os.path.basename(__file__))


class ExecuteOperation:
    MINIMUN_INVESTMENT_PER_COIN = 10

    def __init__(
        self,
        bot_session,
        capital_baseline=570,
        profit_margin=0,
        margin_ratio_percentage=11,
    ) -> None:
        self.bot_session = bot_session
        self.bot_api = BotApi(self.bot_session)
        self.current_coin = None
        self.capital_baseline = capital_baseline
        self.profit_margin = profit_margin
        self.margin_ratio_percentage = margin_ratio_percentage

    def user_info(self):
        user_info = self.bot_api.user_info()
        logger.info(f"{user_info.get('name')} has initiate session")
        return user_info.get("name")

    def user_can_operate(self, arbitrage_balance) -> bool:
        logger.info("Checking if user can operate base on arbitrage balance")
        if arbitrage_balance > self.capital_baseline:
            return True

    def decrease_profit_margin(self, backoff_event):
        if backoff_event["tries"] >= 4:
            coin_max_profit = self.current_coin.get("max_profit", 0)
            max_loss_accepted = (coin_max_profit * self.margin_ratio_percentage) / 100
            self.profit_margin = coin_max_profit - max_loss_accepted
            self.margin_ratio_percentage += 1

    def can_invest_in_coin(self, coin) -> dict:
        self.current_coin = coin
        self.profit_margin = coin.get("max_profit", 0)

        @backoff.on_exception(
            backoff.constant,
            Exception,
            on_backoff=self.decrease_profit_margin,
            interval=10,
            max_tries=6,
            logger=logger,
            raise_on_giveup=False,
        )
        def calculate_coin_profit() -> dict:
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

    def execute(self, user):
        arbitrage_balance = self.bot_api.arbitrage_balance()
        user_can_operate = self.user_can_operate(arbitrage_balance)
        if user_can_operate:
            logger.info(
                f"{user} balance is enough to operate, arbitrage balance: {arbitrage_balance}"
            )
            all_coins = self.bot_api.all_coins()
            i = 0
            while True:
                time.sleep(10)
                arbitrage_balance = self.bot_api.arbitrage_balance()

                if (
                    arbitrage_balance < ExecuteOperation.MINIMUN_INVESTMENT_PER_COIN
                    or len(all_coins) == 0
                ):
                    logger.info(
                        f"End of the cycle for {user}, bot will go to sleep for 2 minutes..."
                    )
                    break

                self.profit_margin = all_coins[i].get("max_profit", 0)

                coin_to_invest: dict = self.can_invest_in_coin(all_coins[i])
                if coin_to_invest:
                    logger.info(
                        f"{all_coins[i].get('abb')} is profitable, investing..."
                    )
                    invest = InvestOperation(
                        arbitrage_balance=arbitrage_balance,
                        coin_max_investment=all_coins[i].get("max_to_invest", 100),
                        bot_api=self.bot_api,
                    )
                    buy_id = int(coin_to_invest.get("buy", {}).get("id"))
                    sell_id = int(coin_to_invest.get("sell", {}).get("id"))
                    invest.submit_suggestion(all_coins[i].get("id"), buy_id, sell_id, user)
                    del all_coins[i]
                    i = 0
                    continue
                if i < len(all_coins) - 1:
                    i += 1
        else:
            logger.info(
                f"{user} balance is not enough to operate, arbitrage balance: {arbitrage_balance}"
            )


def run_the_bot():
    session = BotSession(os.environ.get("ASPCOOKIE"))
    bot_session = session.bot_session()
    execute_order = ExecuteOperation(bot_session)
    user = execute_order.user_info()
    execute_order.execute(user)


if __name__ == "__main__":
    schedule.every(2).minutes.do(run_the_bot)
    while True:
        run_pending()
        time.sleep(1)
