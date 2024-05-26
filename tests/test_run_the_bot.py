import pytest
from the_bot.services.execute_operations import ExecuteOperation, run_the_bot
from aws_lambda_powertools.utilities.typing import LambdaContext
import os 

os.environ["DISCORD_WEBHOOK"] = "test_discord_webhook"

test_coins = [{"id":1,"title":"CAKE","abb":"CAKE"},{"id":2,"title":"Arbitrum","abb":"ARB"},{"id":5,"title":"VeChain","abb":"VET"},{"id":6,"title":"Lido","abb":"LDO"},{"id":8,"title":"Cosmos","abb":"ATOM"},{"id":9,"title":"Filecoin","abb":"FIL"},{"id":10,"title":"Fantom","abb":"FTM"},{"id":11,"title":"Polkadot","abb":"DOT"}]

def test_execution_order(mocker):
    mocker.patch("the_bot.services.execute_operations.ExecuteOperation.user_name", return_value="test_user")
    mocker.patch("the_bot.api.api.BotApi.arbitrage_balance", return_value=500)
    mocker.patch("the_bot.api.api.BotApi.get_coins", return_value=test_coins)
    mocker.patch("the_bot.helpers.session.BotSession.send_msg_to_webhook", return_value="Staring operation")
    test_event = {"ASPCOOKIE": "test_cookie", "schedule_name": "test_schedule_name", "capital_baseline": 500, "coins_lock_container": {}}
    assert run_the_bot(test_event, LambdaContext)
