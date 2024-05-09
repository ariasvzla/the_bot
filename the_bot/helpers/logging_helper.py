import logging
from the_bot.services.notification_services import send_msg


def log_setup(name):
    logging.basicConfig(
        filename="bot_logs.log",
        filemode="a",
        level=logging.DEBUG,
    )
    logger = logging.getLogger(name)
    custom_handler = RequestsHandler()
    formatter = FormatterLogger(logger)
    custom_handler.setFormatter(formatter)
    logger.addHandler(custom_handler)

    return logger


class RequestsHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)
        return send_msg(log_entry)


class FormatterLogger(logging.Formatter):
    def __init__(self, task_name=None):

        super(FormatterLogger, self).__init__()

    def format(self, record):
        data = f"{record.msg}, funcName: {record.funcName}, lineno: {record.lineno}."
        return data
