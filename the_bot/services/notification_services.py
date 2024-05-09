from the_bot.helpers.session import BotSession
import os


def send_msg(msg):
    webhook_session = BotSession().webhook_session()
    discord_webhook = os.environ.get("DISCORD_WEBHOOK")
    if discord_webhook:
        webhook = os.environ.get("DISCORD_WEBHOOK")
        webhook_session.post(webhook, data={"content": msg, "username": "TheTrader"})
    else:
        raise Exception("Discord webhook is not configured")
