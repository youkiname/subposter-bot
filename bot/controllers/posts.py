import html

from telebot import types

from bot import bot
from bot.controllers import keyboards
from bot.services import channels as channel_services
from bot.services import posts as post_services
from bot.services import users as user_services
from bot.services import votes as votes_services
from bot.services.user_states import UserStates
from models import User, PostData, MediaTypes, Channel, Post


def is_forwarded_from_channel(msg: types.Message) -> bool:
    """Returns true if message was forwarded from saved channel.
    if true and user is admin we can send post info"""
    if not msg.forward_from_chat:
        return False
    channel = Channel.get_or_none(Channel.id == msg.forward_from_chat.id)
    return channel is not None


def start_post_creating(msg: types.Message):
    user = user_services.create_or_update_user(msg.from_user)
    user.state = UserStates.CHANNEL_CHOOSING
    user.save()
    bot.send_message(msg.chat.id, "Начал создание поста. Выбери канал.",
                     reply_markup=keyboards.get_channels())


def continue_post_creating(msg: types.Message):
    user = user_services.create_or_update_user(msg.from_user)
    if user.state == UserStates.CHANNEL_CHOOSING:
        __try_choose_channel(msg, user)
        return
    if msg.text == "Отправить":
        __try_send_post(msg, user)
    elif msg.text == "Превью":
        __try_send_preview(msg, user)
    else:
        __set_new_data_to_post(msg, user)


def send_post_info(msg: types.Message):
    post = Post.get_or_none(Post.id == msg.forward_from_message_id)
    if not post:
        return bot.send_message(msg.chat.id, f"Пост <{msg.message_id}> не найден")
    info = f"Пост <{post.id}>\n" \
           f"Создатель: {post.creator.get_full_name()}\n" \
           f"Лайков: {votes_services.get_post_likes_amount(post.id)}\n" \
           f"Дизлайков {votes_services.get_post_dislikes_amount(post.id)}"
    bot.send_message(msg.chat.id, info)


def __try_choose_channel(msg: types.Message, user: User):
    channel = channel_services.get_by_title(msg.text)
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

    post_services.create_post_data(user.id, channel.id)

    user.state = UserStates.POST_CREATING
    user.save()

    bot.send_message(msg.chat.id, f"Выбрал канал {channel.title}. "
                                  f"Теперь отправь картинку, видео или заголовок поста.",
                     reply_markup=keyboards.get_for_post_creating())


def __set_new_data_to_post(msg: types.Message, user: User):
    post_data = post_services.get_post_data_by_creator_id(user.id)

    if msg.text or msg.caption:
        formatted_text = post_services.FormattedMessageTextData(html.escape(msg.text), msg.caption, msg.entities)
        post_services.replace_text(post_data, formatted_text)

    if msg.content_type != 'text':
        post_services.replace_existing_media_data(post_data, msg)

    post_data.save()
    album_spam_block = post_data.type == 'album' and len(post_data.media) > 1
    if album_spam_block:
        return
    bot.send_message(msg.chat.id, f"Принял {msg.content_type}. Можешь отправить текст, картинку, "
                                  f"видео или гифку, чтобы добавить/изменить содержание поста.\n"
                                  f"Нажми Превью, чтобы посмотреть, как будет выглядеть пост на канале.")


def __check_post_data_validity(chat_id: int, post_data: PostData) -> bool:
    if not post_services.__is_post_data_valid_for_sending(post_data):
        bot.send_message(chat_id, "Не хватает данных для поста. Отправь картинку, видео или гифку.")
        return False
    return True


def __try_send_post(msg: types.Message, user: User):
    post_data = post_services.get_post_data_by_creator_id(user.id)
    if not __check_post_data_validity(msg.chat.id, post_data):
        return

    telegram_message = __send_post(post_data.channel_id, post_data)
    post_services.save_post(post_data, telegram_message.message_id)

    post_data.delete_instance()
    user_services.clear_state(user)

    bot.send_message(msg.chat.id, "Пост отправлен",
                     reply_markup=keyboards.get_main_keyboard())


def __try_send_preview(msg: types.Message, user: User):
    """Preview is a post without keyboard. Creator can check post appearance before sending."""
    post_data = post_services.get_post_data_by_creator_id(user.id)
    if not __check_post_data_validity(msg.chat.id, post_data):
        return
    __send_post(msg.chat.id, post_data, as_preview=True)


def __send_post(chat_id: int, post_data: PostData, as_preview=False):
    """This func is used for preview and sending posts to the channels.
       If is_preview is True post will be sent without keyboard."""
    caption = post_data.text
    user_sign = user_services.get_user_sign(post_data.creator_id)
    keyboard = None
    if not as_preview:
        keyboard = keyboards.get_post_keyboard()
    if user_sign:
        caption += "\n" + user_sign
    if post_data.type == MediaTypes.photo:
        return bot.send_photo(chat_id, post_data.media[0].media_id, caption=caption, reply_markup=keyboard,
                              parse_mode='HTML')
    if post_data.type == MediaTypes.animation:
        return bot.send_animation(chat_id, post_data.media[0].media_id, caption=caption, reply_markup=keyboard,
                                  parse_mode='HTML')
    if post_data.type == MediaTypes.video:
        return bot.send_video(chat_id, post_data.media[0].media_id,
                              caption=caption, reply_markup=keyboard, supports_streaming=True,
                              parse_mode='HTML')
    if post_data.type == MediaTypes.album:
        bot.send_media_group(chat_id, post_services.collect_photo_list(post_data))
        return bot.send_message(chat_id, text=caption or "↑↑↑", reply_markup=keyboard, parse_mode='HTML')
