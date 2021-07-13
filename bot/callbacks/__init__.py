from telebot.types import CallbackQuery
from bot import bot
from config import config
import logging


class CallbackCommands:
    POST_LIKE = '0'
    POST_DISLIKE = '1'
    SET_SHOW_USERNAME = '2'
    SET_SHOW_NAME = '3'


def callback_exception_handler(handler):
    def wrapper_accepting_arguments(callback: CallbackQuery):
        try:
            handler(callback)
        except Exception as e:
            bot.answer_callback_query(callback.id, "Произошла ошибка: {}.".format(type(e).__name__), show_alert=True)
            if config.EXCEPTION_LOG_CHAT_ID:
                bot.send_message(config.EXCEPTION_LOG_CHAT_ID, "Поймано исключение {} в {}:\n"
                                                               "{}".format(type(e).__name__, handler.__name__, e))
            logging.exception(e)
    return wrapper_accepting_arguments
