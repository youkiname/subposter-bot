from bot import bot
from bot.controllers import users, keyboards
from telebot import types
from models import User, PostData, Channel, MediaTypes
from bot.services import posts as post_services
from bot.services import users as user_services
from bot.services.user_states import UserStates


def start_post_creating(msg: types.Message):
    user = users.get_or_create_user(msg.from_user)
    user.state = UserStates.CHANNEL_CHOOSING
    user.save()
    bot.send_message(msg.chat.id, "Начал создание поста. Выбери канал.",
                     reply_markup=keyboards.get_channels())


def continue_post_creating(msg: types.Message):
    user = users.get_or_create_user(msg.from_user)
    if user.state == UserStates.CHANNEL_CHOOSING:
        __try_choose_channel(msg, user)
        return
    if msg.text == "Отправить":
        __try_send_post(msg, user)
    elif msg.text == "Превью":
        __try_send_preview(msg, user)
    else:
        __set_new_data_to_post(msg, user)


def __try_choose_channel(msg: types.Message, user: User):
    channel = Channel.get_or_none(title=msg.text)
    if channel is None:
        bot.send_message(msg.chat.id, "Такой канал не зарегистрирован.\n"
                                      "Выбери канал, нажав на нужную кнопку.")
        return

    if channel.frozen:
        bot.send_message(msg.chat.id, f"Канал {channel.title} временно заморожен.")
        return

    if not post_services.check_posts_limit(user.id, channel.id):
        bot.send_message(msg.chat.id, "У вас достиг суточный лимит постов на этом канале.")
        return

    PostData.create(creator_id=user.id, channel_id=channel.id).save()

    user.state = UserStates.POST_CREATING
    user.save()

    bot.send_message(msg.chat.id, f"Выбрал канал {channel.title}. "
                                  f"Теперь отправь картинку, видео или заголовок поста.",
                     reply_markup=keyboards.get_for_post_creating())


def __set_new_data_to_post(msg: types.Message, user: User):
    post_data = PostData.get(PostData.creator_id == user.id)

    post_services.replace_text(post_data, msg)

    if msg.content_type not in ['text', MediaTypes.album]:
        post_services.replace_existing_media_data(post_data, msg)

    post_data.save()
    bot.send_message(msg.chat.id, f"Принял {msg.content_type}. Можешь отправить текст, картинку, "
                                  f"видео или гифку, чтобы добавить/изменить содержание поста.\n"
                                  f"Нажми Превью, чтобы посмотреть, как будет выглядеть пост на канале.")


def __check_post_data_validity(chat_id: int, post_data: PostData) -> bool:
    if not post_services.__is_post_data_valid_for_sending(post_data):
        bot.send_message(chat_id, "Не хватает данных для поста. Отправь картинку, видео или гифку.")
        return False
    return True


def __try_send_post(msg: types.Message, user: User):
    post_data = PostData.get(PostData.creator_id == user.id)
    if not __check_post_data_validity(msg.chat.id, post_data):
        return

    telegram_message = post_services.send_post(post_data.channel_id, post_data)
    post_services.save_post(post_data, telegram_message.message_id)

    post_data.delete_instance()
    user_services.clear_state(user)

    bot.send_message(msg.chat.id, "Пост отправлен",
                     reply_markup=keyboards.get_main_keyboard())


def __try_send_preview(msg: types.Message, user: User):
    """Preview is a post without keyboard. Creator can check post appearance before sending."""
    post_data = PostData.get(PostData.creator_id == user.id)
    if not __check_post_data_validity(msg.chat.id, post_data):
        return
    post_services.send_post(msg.chat.id, post_data, as_preview=True)
