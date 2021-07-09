from bot import bot
from telebot.types import Message
from bot.controllers import users
from bot.middleware import exception_handler


@bot.message_handler(commands=['change_user_rating'])
@exception_handler
@users.admin_required
def change_user_rating(msg: Message):
    users.start_rating_change(msg)


@bot.message_handler(func=users.is_admin_on_rating_change_state)
@exception_handler
@users.admin_required
def continue_rating_change(msg: Message):
    users.continue_rating_change(msg)
