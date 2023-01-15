# -*- coding: utf-8 -*-

import logging

import telebot

from config import config

telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(config.TOKEN)


from bot.handlers import general_handlers
from bot.handlers import channels_handlers
from bot.handlers import posts_handlers
from bot.handlers import admins_handlers
from bot.handlers import users_handlers

from bot.callbacks.handlers import user_settings
from bot.callbacks.handlers import votes
