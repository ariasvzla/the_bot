from the_bot.helpers.session import BotSession
import os


def send_msg(msg):
    webhook_session = BotSession().webhook_session()
    discord_webhook = os.environ.get("DISCORD_WEBHOOK")
    if discord_webhook:
        webhook = os.environ.get("DISCORD_WEBHOOK")
        try:
            webhook_session.post(
                webhook, data={"content": msg, "username": "TheTrader"}
            )
        except Exception as e:
            print("The message could not be sent.")
            pass
    else:
        raise Exception("Discord webhook is not configured")
