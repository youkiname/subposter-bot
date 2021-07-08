from bot import bot, admin_required, exception_handler, superuser_required
from telebot.types import Message
from bot.controllers import admins


@bot.message_handler(commands=['add_admin'])
@exception_handler
@superuser_required
def add_new_admin(msg: Message):
    admins.try_add_new_admin(msg)


@bot.message_handler(commands=['admins'])
@exception_handler
@superuser_required
def send_admins_list(msg: Message):
    admins.send_admins_list(msg.chat.id)


@bot.message_handler(commands=['remove_admin'])
@exception_handler
@superuser_required
def delete_admin(msg: Message):
    admins.try_delete_admin(msg)
