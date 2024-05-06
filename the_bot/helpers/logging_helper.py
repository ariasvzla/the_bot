import logging
from the_bot.helpers.session import BotSession
from the_bot.api.api import BotApi, InvestOperation
import os


def log_setup(name):
    session = BotSession(os.environ.get("ASPCOOKIE"))
    bot_session = session.bot_session()
    bot_api = BotApi(bot_session)
    user_info = bot_api.user_info()
    username = user_info.get('name').replace(" ", "_")
    
    logging.basicConfig(
        filename=f"{username}_bot_logs.log",
        filemode="a",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )
    return logging.getLogger(name)
