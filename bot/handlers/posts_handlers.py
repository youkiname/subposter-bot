from bot import bot, exception_handler
from telebot.types import Message
from bot.controllers import posts, users, keyboards


@bot.message_handler(regexp="Создать пост")
@exception_handler
def start_post_creating(msg: Message):
    user = users.get_or_create_user(msg.from_user)
    posts.start_post_creating(user)
    bot.send_message(msg.chat.id, "Начал создание поста. Выбери канал.",
                     reply_markup=keyboards.get_channels())


@bot.message_handler(func=users.is_user_creating_post, content_types=['text', 'animation', 'video', 'photo'])
@exception_handler
def continue_post_creating(msg: Message):
    user = users.get_or_create_user(msg.from_user)
    if user.state == users.States.CHANNEL_CHOOSING:
        posts.choose_channel(msg, user)
        return
    if msg.text == "Отправить":
        posts.try_send_post(msg, user)
    elif msg.text == "Превью":
        posts.try_send_preview(msg, user)
    else:
        posts.continue_post_creating(msg, user)
