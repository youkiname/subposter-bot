from bot import bot
from telebot.types import Message
from bot.controllers import admins, users
from bot.middleware import exception_handler


@bot.message_handler(commands=['add_admin'])
@exception_handler
@users.superuser_required
def add_new_admin(msg: Message):
    admins.try_add_new_admin(msg)


@bot.message_handler(commands=['admins'])
@exception_handler
@users.superuser_required
def send_admins_list(msg: Message):
    admins.send_admins_list(msg.chat.id)


@bot.message_handler(commands=['remove_admin'])
@exception_handler
@users.superuser_required
def delete_admin(msg: Message):
    admins.try_delete_admin(msg)
