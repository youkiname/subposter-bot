from bot import bot
import logging
from config import config


def exception_handler(handler):
    def wrapper_accepting_arguments(msg):
        try:
            handler(msg)
        except Exception as e:
            bot.send_message(msg.chat.id, "Произошла ошибка: {}.".format(type(e).__name__))
            bot.send_message(config.EXCEPTION_LOG_CHAT_ID, "Поймано исключение {} в {}:\n"
                                                           "{}".format(type(e).__name__, handler.__name__, e))
            logging.exception(e)
    return wrapper_accepting_arguments
