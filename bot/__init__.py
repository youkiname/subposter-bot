# -*- coding: utf-8 -*-

import telebot

from config import config
import logging
from bot.controllers import users

telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(config.TOKEN)


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


def superuser_required(handler):
    def wrapper_accepting_arguments(msg):
        if users.is_superuser(msg.from_user.id):
            handler(msg)
        else:
            bot.send_message(msg.chat.id, "Недостаточно полномочий")
    return wrapper_accepting_arguments


def admin_required(handler):
    def wrapper_accepting_arguments(msg):
        if users.is_admin(msg.from_user.id):
            handler(msg)
        else:
            bot.send_message(msg.chat.id, "Недостаточно полномочий")
    return wrapper_accepting_arguments


from bot.handlers import general_handlers
from bot.handlers import channels_handlers
from bot.handlers import posts_handlers
from bot.handlers import admins_handler

from bot.callbacks.handlers import user_settings
from bot.callbacks.handlers import votes
