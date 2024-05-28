from the_bot.helpers.session import BotSession
from the_bot.api.api import BotApi, InvestOperation
from the_bot.helpers.update_scheduler import update_schedule
import backoff
import os
import time
from random import randrange
from datetime import datetime, timedelta
from aws_lambda_powertools import Logger
from the_bot.services.notification_services import send_msg

logger = Logger(service="Execute oeprations")


class ExecuteOperation:
    MINIMUN_INVESTMENT_PER_COIN = 10

    def __init__(
        self,
        bot_session,
        capital_baseline=os.environ.get("CAPITAL_BASELINE"),
        coins_lock_container={},
        cycle_duration_in_seconds=100 * 100,
        profit_margin=0,
        margin_ratio_percentage=15,
    ) -> None:
        self.bot_session = bot_session
        self.bot_api = BotApi(self.bot_session, coins_lock_container)
        self.current_coin = None
        self.capital_baseline = int(capital_baseline)
        self.cycle_duration_in_seconds = cycle_duration_in_seconds
        self.profit_margin = profit_margin
        self.margin_ratio_percentage = margin_ratio_percentage

    def user_name(self, schedule_name):
        user_info = self.bot_api.user_info()
        if isinstance(user_info, dict):
            logger.info(f"{user_info.get('name')} has initiate session")
            return user_info.get("name")
        if user_info == 403:
            send_msg(f"The user schedule: {schedule_name}, needs new credentials!!!!")

    def user_can_operate(self, arbitrage_balance) -> bool:
        logger.info("Checking if user can operate base on arbitrage balance")
        if arbitrage_balance >= self.capital_baseline:
            return True

    def decrease_profit_margin(self, backoff_event):
        if backoff_event["tries"] >= 4:
            coin_max_profit = self.current_coin.get("max_profit", 0)
            max_loss_accepted = (coin_max_profit * self.margin_ratio_percentage) / 100
            self.profit_margin = coin_max_profit - max_loss_accepted

    def can_invest_in_coin(self, coin) -> dict:
        self.current_coin = coin
        self.profit_margin = coin.get("max_profit", 0)

        @backoff.on_exception(
            backoff.constant,
            Exception,
            on_backoff=self.decrease_profit_margin,
            interval=10,
            max_tries=5,
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

    def execute(self, user_name, context, event, schedule_name):
        arbitrage_balance = self.bot_api.arbitrage_balance()
        user_can_operate = self.user_can_operate(arbitrage_balance)
        if user_can_operate:
            logger.info(
                f"{user_name} balance is enough to operate, arbitrage balance: {arbitrage_balance}"
            )
            send_msg(f"Starting arbritage operation for user: {user_name}.")
            all_coins = self.bot_api.all_coins()
            all_coins = sorted(all_coins, key=lambda d: d["priority"])
            logger.info(f"We has found {len(all_coins)} coins to invest.")
            i = 0
            while True:
                time.sleep(randrange(5, 10))
                arbitrage_balance = self.bot_api.arbitrage_balance()
                if (
                    arbitrage_balance < ExecuteOperation.MINIMUN_INVESTMENT_PER_COIN
                    or len(all_coins) == 0
                ):
                    self.bot_api.reduce_coin_lock()
                    event["coins_lock_container"] = self.bot_api.coins_lock_container
                    next_execution = (
                        datetime.now()
                        + timedelta(seconds=self.cycle_duration_in_seconds)
                    ).strftime("%Y-%m-%dT%H:%M:%S")
                    update_schedule(
                        context.invoked_function_arn,
                        schedule_name,
                        event,
                        f"at({next_execution})",
                    )
                    logger.info(
                        f"End of the cycle for {user_name}, bot will go to sleep for {self.cycle_duration_in_seconds} seconds..."
                    )
                    send_msg(
                        f"The arbritage operation for user: {user_name} has finished, coins in operation: {self.bot_api.pending_operations()}"
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
                    response = invest.submit_suggestion(
                        all_coins[i], buy_id, sell_id, user_name
                    )
                    if not response.get("haserror"):
                        logger.info(
                            f"User {user_name} investment was successfull, adding coin to lock ..."
                        )
                        if all_coins[i].get("abb") != "DOT":
                            self.bot_api.add_coin_lock(all_coins[i])
                        all_coins.pop(i)
                        i = 0
                        continue
                if i < len(all_coins) - 1:
                    i += 1
        else:
            logger.info(
                f"{user_name} balance is not enough to operate, arbitrage balance: {arbitrage_balance}"
            )
            logger.info(f"Updating schedule {schedule_name}")
            next_execution = randrange(8, 15)
            update_schedule(
                context.invoked_function_arn,
                schedule_name,
                event,
                f"rate({next_execution} minutes)",
            )


@logger.inject_lambda_context
def run_the_bot(event, context):
    session = BotSession(event.get("ASPCOOKIE"))
    schedule_name = event.get("schedule_name")
    capital_baseline = event.get("capital_baseline", 0)
    coins_lock_container = event.get("coins_lock_container", {})
    cycle_duration_in_seconds = int(event.get("cycle_duration_in_seconds", 100 * 100))
    bot_session = session.bot_session()
    execute_order = ExecuteOperation(
        bot_session, capital_baseline, coins_lock_container, cycle_duration_in_seconds
    )
    user_name = execute_order.user_name(schedule_name)
    if user_name:
        execute_order.execute(user_name, context, event, schedule_name)
    else:
        update_schedule(
            context.invoked_function_arn,
            schedule_name,
            event,
            "rate(5 minutes)",
        )
