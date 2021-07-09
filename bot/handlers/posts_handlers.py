from bot import bot
from telebot.types import Message
from bot.controllers import posts, users
from bot.middleware import exception_handler


@bot.message_handler(regexp="Создать пост")
@exception_handler
def start_post_creating(msg: Message):
    posts.start_post_creating(msg)


@bot.message_handler(func=users.is_user_creating_post, content_types=['text', 'animation', 'video', 'photo'])
@exception_handler
def continue_post_creating(msg: Message):
    user = users.get_or_create_user(msg.from_user)
    if user.state == users.States.CHANNEL_CHOOSING:
        posts.try_choose_channel(msg, user)
        return
    if msg.text == "Отправить":
        posts.try_send_post(msg, user)
    elif msg.text == "Превью":
        posts.try_send_preview(msg, user)
    else:
        posts.continue_post_creating(msg, user)
