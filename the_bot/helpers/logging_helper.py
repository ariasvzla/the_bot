import logging


def log_setup(name):
    logging.basicConfig(
        filename="bot_logs.log",
        filemode="a",
        format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        level=logging.DEBUG,
    )
    return logging.getLogger(name)
