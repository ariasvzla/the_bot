import pytest
from the_bot.services.execute_operations import ExecuteOperation, run_the_bot
from aws_lambda_powertools.utilities.typing import LambdaContext
import os 

os.environ["DISCORD_WEBHOOK"] = "test_discord_webhook"

test_coins = [{"id":1,"title":"CAKE","abb":"CAKE"},{"id":2,"title":"Arbitrum","abb":"ARB"},{"id":5,"title":"VeChain","abb":"VET"},{"id":6,"title":"Lido","abb":"LDO"},{"id":8,"title":"Cosmos","abb":"ATOM"},{"id":9,"title":"Filecoin","abb":"FIL"},{"id":10,"title":"Fantom","abb":"FTM"},{"id":11,"title":"Polkadot","abb":"DOT"}]

def test_execution_order_with_polkadot(mocker):
    
    user_call_mock = mocker.patch("the_bot.services.execute_operations.ExecuteOperation.user_name", return_value="test_user")
    arbi_balance_mock = mocker.patch("the_bot.api.api.BotApi.arbitrage_balance", return_value=500)
    balance_in_ops_mock = mocker.patch("the_bot.api.api.BotApi.balance_in_operation", return_value=0)
    get_coins_mock = mocker.patch("the_bot.api.api.BotApi.get_coins", return_value=test_coins)
    current_ops_mock = mocker.patch("the_bot.api.api.BotApi.all_current_operations", return_value={"result":[{"ID":29213020,"Key":"C7CIRZYQQ448185815","Date":"06/06/2024","Hour":"13:50","Exchanges":"Kucoin | Binance","Prices":"7,17492284 | 7,24008359","Amount":"223.37000000","Percent":"0,91","percentwin":"0,55","Transaction":"","Situation":"Pending","Coin":"Polkadot/USDT","IDSituacao":1,"link":"https://bscscan.com/tx/"},{"ID":29047038,"Key":"CPI3MT0RWQLY185815","Date":"06/06/2024","Hour":"10:25","Exchanges":"Coinbase | Binance","Prices":"7,12162356 | 7,18630026","Amount":"220.67000000","Percent":"0,91","percentwin":"0,55","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28927029,"Key":"PZLZGIRCS535185815","Date":"06/06/2024","Hour":"07:12","Exchanges":"Coinbase | Binance","Prices":"7,09207465 | 7,15648300","Amount":"219.26000000","Percent":"0,91","percentwin":"0,55","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28820482,"Key":"P76IAK0JMPMP185815","Date":"06/06/2024","Hour":"04:01","Exchanges":"Bybit | Binance","Prices":"7,15165772 | 7,20933238","Amount":"216.50000000","Percent":"0,81","percentwin":"0,49","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28672878,"Key":"FGDXYR7GMCU9185815","Date":"06/06/2024","Hour":"00:49","Exchanges":"Bybit | Binance","Prices":"7,19181064 | 7,24615682","Amount":"114.94000000","Percent":"0,76","percentwin":"0,46","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28672415,"Key":"J9TDKWBUXG9B185815","Date":"06/06/2024","Hour":"00:48","Exchanges":"Coinbase | Binance","Prices":"0,81710844 | 0,82997302","Amount":"100.00000000","Percent":"1,57","percentwin":"0,94","Transaction":"","Situation":"Executed","Coin":"Fantom/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28522934,"Key":"EVGILPTS8DEG185815","Date":"05/06/2024","Hour":"21:40","Exchanges":"Bybit | Binance","Prices":"7,19848371 | 7,26019537","Amount":"213.93000000","Percent":"0,86","percentwin":"0,52","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28373188,"Key":"83PYTKYXHXB4185815","Date":"05/06/2024","Hour":"18:35","Exchanges":"Kraken | Binance","Prices":"7,20002272 | 7,26541142","Amount":"212.08000000","Percent":"0,91","percentwin":"0,55","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28228685,"Key":"JB3DMSYMQCEZ185815","Date":"05/06/2024","Hour":"15:28","Exchanges":"Coinbase | Binance","Prices":"7,15983466 | 7,21393920","Amount":"110.18000000","Percent":"0,76","percentwin":"0,46","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28228355,"Key":"1CQY6197LRVO185815","Date":"05/06/2024","Hour":"15:28","Exchanges":"Coinbase | Binance","Prices":"0,82182981 | 0,84231235","Amount":"100.00000000","Percent":"2,49","percentwin":"1,49","Transaction":"","Situation":"Executed","Coin":"Fantom/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"}],"totals":87})
    sug_mock = mocker.patch("the_bot.api.api.BotApi.solesbot_suggestion_for_coin", return_value={"buy":{"id":4,"icon":"null","name":"Coinbase","pricebtc":0,"priceeth":0,"price":7.21345375},"sell":{"id":1,"icon":"null","name":"Binance","pricebtc":0,"priceeth":0,"price":7.27896443},"profit":0.91,"pair":"Polkadot"})
    submit_mock = mocker.patch("the_bot.api.api.InvestOperation.submit_suggestion", return_value={})
    send_mdg_mock = mocker.patch("the_bot.helpers.session.BotSession.send_msg_to_webhook", return_value="Staring operation")
    schedu_call_mock = mocker.patch("boto3.client")
    
    test_event = {"ASPCOOKIE": "test_cookie", "schedule_name": "test_schedule_name", "capital_baseline": 500, "coins_lock_container": {},"user_strategy": [{"abb": "DOT", "max_profit": 0.91, "max_to_invest": 500}]}
    run_the_bot(test_event, LambdaContext)

    user_call_mock.assert_called()
    arbi_balance_mock.assert_called()
    balance_in_ops_mock.assert_called()
    get_coins_mock.assert_called()
    current_ops_mock.assert_called()
    sug_mock.assert_called()
    submit_mock.assert_called()
    send_mdg_mock.assert_called()
    schedu_call_mock.assert_called()


def test_execution_order_with_all_coins(mocker):
    
    user_call_mock = mocker.patch("the_bot.services.execute_operations.ExecuteOperation.user_name", return_value="test_user")
    arbi_balance_mock = mocker.patch("the_bot.api.api.BotApi.arbitrage_balance", return_value=500)
    balance_in_ops_mock = mocker.patch("the_bot.api.api.BotApi.balance_in_operation", return_value=0)
    get_coins_mock = mocker.patch("the_bot.api.api.BotApi.get_coins", return_value=test_coins)
    current_ops_mock = mocker.patch("the_bot.api.api.BotApi.all_current_operations", return_value={"result":[{"ID":29213020,"Key":"C7CIRZYQQ448185815","Date":"06/06/2024","Hour":"13:50","Exchanges":"Kucoin | Binance","Prices":"7,17492284 | 7,24008359","Amount":"223.37000000","Percent":"0,91","percentwin":"0,55","Transaction":"","Situation":"Pending","Coin":"Polkadot/USDT","IDSituacao":1,"link":"https://bscscan.com/tx/"},{"ID":29047038,"Key":"CPI3MT0RWQLY185815","Date":"06/06/2024","Hour":"10:25","Exchanges":"Coinbase | Binance","Prices":"7,12162356 | 7,18630026","Amount":"220.67000000","Percent":"0,91","percentwin":"0,55","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28927029,"Key":"PZLZGIRCS535185815","Date":"06/06/2024","Hour":"07:12","Exchanges":"Coinbase | Binance","Prices":"7,09207465 | 7,15648300","Amount":"219.26000000","Percent":"0,91","percentwin":"0,55","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28820482,"Key":"P76IAK0JMPMP185815","Date":"06/06/2024","Hour":"04:01","Exchanges":"Bybit | Binance","Prices":"7,15165772 | 7,20933238","Amount":"216.50000000","Percent":"0,81","percentwin":"0,49","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28672878,"Key":"FGDXYR7GMCU9185815","Date":"06/06/2024","Hour":"00:49","Exchanges":"Bybit | Binance","Prices":"7,19181064 | 7,24615682","Amount":"114.94000000","Percent":"0,76","percentwin":"0,46","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28672415,"Key":"J9TDKWBUXG9B185815","Date":"06/06/2024","Hour":"00:48","Exchanges":"Coinbase | Binance","Prices":"0,81710844 | 0,82997302","Amount":"100.00000000","Percent":"1,57","percentwin":"0,94","Transaction":"","Situation":"Executed","Coin":"Fantom/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28522934,"Key":"EVGILPTS8DEG185815","Date":"05/06/2024","Hour":"21:40","Exchanges":"Bybit | Binance","Prices":"7,19848371 | 7,26019537","Amount":"213.93000000","Percent":"0,86","percentwin":"0,52","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28373188,"Key":"83PYTKYXHXB4185815","Date":"05/06/2024","Hour":"18:35","Exchanges":"Kraken | Binance","Prices":"7,20002272 | 7,26541142","Amount":"212.08000000","Percent":"0,91","percentwin":"0,55","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28228685,"Key":"JB3DMSYMQCEZ185815","Date":"05/06/2024","Hour":"15:28","Exchanges":"Coinbase | Binance","Prices":"7,15983466 | 7,21393920","Amount":"110.18000000","Percent":"0,76","percentwin":"0,46","Transaction":"","Situation":"Executed","Coin":"Polkadot/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"},{"ID":28228355,"Key":"1CQY6197LRVO185815","Date":"05/06/2024","Hour":"15:28","Exchanges":"Coinbase | Binance","Prices":"0,82182981 | 0,84231235","Amount":"100.00000000","Percent":"2,49","percentwin":"1,49","Transaction":"","Situation":"Executed","Coin":"Fantom/USDT","IDSituacao":5,"link":"https://bscscan.com/tx/"}],"totals":87})
    sug_mock = mocker.patch("the_bot.api.api.BotApi.solesbot_suggestion_for_coin", return_value={"buy":{"id":4,"icon":"null","name":"Coinbase","pricebtc":0,"priceeth":0,"price":7.21345375},"sell":{"id":1,"icon":"null","name":"Binance","pricebtc":0,"priceeth":0,"price":7.27896443},"profit":0.91,"pair":"Polkadot"})
    submit_mock = mocker.patch("the_bot.api.api.InvestOperation.submit_suggestion", return_value={"haserror": False})
    send_mdg_mock = mocker.patch("the_bot.helpers.session.BotSession.send_msg_to_webhook", return_value="Staring operation")
    schedu_call_mock = mocker.patch("boto3.client")

    test_event = {"ASPCOOKIE": "test_cookie", "schedule_name": "test_schedule_name", "capital_baseline": 500, "coins_lock_container": {} }
    run_the_bot(test_event, LambdaContext)

    user_call_mock.assert_called()
    arbi_balance_mock.assert_called()
    balance_in_ops_mock.assert_called()
    get_coins_mock.assert_called()
    current_ops_mock.assert_called()
    sug_mock.assert_called()
    submit_mock.assert_called()
    send_mdg_mock.assert_called()
    schedu_call_mock.assert_called()