from the_bot.helpers.session import BotSession
import os
from aws_lambda_powertools import Logger

logger = Logger(service="Notifications")


def send_msg(msg):
    data = {"content": msg, "username": "TheTrader"}
    discord_webhook = os.environ.get("DISCORD_WEBHOOK")
    bot_session = BotSession()
    if discord_webhook:
        try:
            bot_session.send_msg_to_webhook(discord_webhook, data)
        except Exception as e:
            print(e)
    else:
        raise Exception("Discord webhook is not configured")
