import logging

logging.basicConfig(
    filename="bot_logs.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)


def log_setup(name):
    return logging.getLogger(name)
