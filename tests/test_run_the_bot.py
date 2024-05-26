import pytest
from the_bot.services.execute_operations import ExecuteOperation, run_the_bot
from aws_lambda_powertools.utilities.typing import LambdaContext
import os 

os.environ["DISCORD_WEBHOOK"] = "test_discord_webhook"

test_coins = [
    {"abb": "ARB", "max_profit": 0.86, "max_to_invest": 300},
    {"abb": "VET", "max_profit": 0.60, "max_to_invest": 300},
    {"abb": "VET1", "max_profit": 0.60, "max_to_invest": 300},
    {"abb": "LDO", "max_profit": 0.65, "max_to_invest": 300},
    {"abb": "FTM", "max_profit": 1.68, "max_to_invest": 100},
    {"abb": "CAKE", "max_profit": 1.86, "max_to_invest": 30},
    {"abb": "FIL", "max_profit": 0.60, "max_to_invest": 1000},
]

def test_execution_order(mocker):
    mocker.patch("the_bot.services.execute_operations.ExecuteOperation.user_name", return_value="test_user")
    mocker.patch("the_bot.api.api.BotApi.arbitrage_balance", return_value=500)
    mocker.patch("the_bot.api.api.BotApi.get_coins", return_value=test_coins)
    mocker.patch("the_bot.helpers.session.BotSession.send_msg_to_webhook", return_value="Staring operation")
    test_event = {"ASPCOOKIE": "test_cookie", "schedule_name": "test_schedule_name", "capital_baseline": 500, "coins_lock_container": {}}
    assert run_the_bot(test_event, LambdaContext)
