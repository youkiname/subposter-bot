from bot import bot
from telebot.types import Message
from bot.controllers import posts, users
from bot.middleware import exception_handler
from models import MediaTypes


@bot.message_handler(func=users.is_user_creating_post, content_types=['text', 'animation', 'video', 'photo'])
@exception_handler
def continue_post_creating(msg: Message):
    if msg.media_group_id:
        # I don't use pyTelegramBotAPI middleware for this.
        # When use_class_middlewares is enabled bot can't receive a pack of photo and gives me only one.
        # Maybe its pyTelegramBotAPI bug, idk ¯\_(ツ)_/¯
        msg.content_type = MediaTypes.album

    posts.continue_post_creating(msg)


@bot.message_handler(regexp="Создать пост")
@exception_handler
def start_post_creating(msg: Message):
    posts.start_post_creating(msg)
