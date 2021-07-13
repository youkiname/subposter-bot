from bot import bot
from telebot.types import Message
from bot.controllers import users
from bot.middleware import exception_handler


@bot.message_handler(commands=['change_rating'])
@exception_handler
@users.admin_required
def change_user_rating(msg: Message):
    users.start_rating_change(msg)


@bot.message_handler(func=users.is_admin_on_rating_change_state)
@exception_handler
@users.admin_required
def continue_rating_change(msg: Message):
    users.continue_rating_change(msg)


@bot.message_handler(commands=['change_post_limit'])
@exception_handler
@users.admin_required
def change_user_daily_posts_limit(msg: Message):
    users.start_daily_post_limit_change(msg)


@bot.message_handler(func=users.is_admin_on_daily_posts_limit_change_state)
@exception_handler
@users.admin_required
def continue_user_daily_posts_limit(msg: Message):
    users.continue_daily_post_limit_change(msg)
