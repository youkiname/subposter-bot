from bot import bot
from bot.controllers import users, keyboards
from telebot import types
from models import User, PostData, Channel, MediaTypes, PostDataMedia, Post
import html


def start_post_creating(msg: types.Message):
    user = users.get_or_create_user(msg.from_user)
    user.state = users.States.CHANNEL_CHOOSING
    user.save()
    bot.send_message(msg.chat.id, "Начал создание поста. Выбери канал.",
                     reply_markup=keyboards.get_channels())


def try_choose_channel(msg: types.Message, user: User):
    channel = Channel.get_or_none(title=msg.text)
    if channel is None:
        bot.send_message(msg.chat.id, "Такой канал не зарегистрирован.\n"
                                      "Выбери канал, нажав на нужную кнопку.")
        return

    if channel.frozen:
        bot.send_message(msg.chat.id, f"Канал {channel.title} временно заморожен.")
        return

    if not __check_posts_limit(user.id, channel.id):
        bot.send_message(msg.chat.id, "У вас достиг суточный лимит постов на этом канале.")
        return

    PostData.create(creator_id=user.id, channel_id=channel.id).save()

    user.state = users.States.POST_CREATING
    user.save()

    bot.send_message(msg.chat.id, f"Выбрал канал {channel.title}. "
                                  f"Теперь отправь картинку, видео или заголовок поста.",
                     reply_markup=keyboards.get_for_post_creating())


def continue_post_creating(msg: types.Message, user: User):
    post_data = PostData.get(PostData.creator_id == user.id)

    __replace_text(post_data, msg)

    if msg.content_type not in ['text', MediaTypes.album]:
        __replace_existing_media_data(post_data, msg)

    post_data.save()
    bot.send_message(msg.chat.id, f"Принял {msg.content_type}. Можешь отправить текст, картинку, "
                                  f"видео или гифку, чтобы добавить/изменить содержание поста.\n"
                                  f"Нажми Превью, чтобы посмотреть, как будет выглядеть пост на канале.")


def try_send_post(msg: types.Message, user: User):
    post_data = PostData.get(PostData.creator_id == user.id)
    if __notify_about_post_data_readiness(msg.chat.id, post_data):
        return

    telegram_message = __send_post(post_data.channel_id, post_data)
    post_data.delete_instance()

    __save_post(post_data, telegram_message.message_id)
    bot.send_message(msg.chat.id, "Пост отправлен",
                     reply_markup=keyboards.get_main_keyboard())


def try_send_preview(msg: types.Message, user: User):
    """Preview is a post without keyboard. Creator can check post appearance before sending."""
    post_data = PostData.get(PostData.creator_id == user.id)
    if __notify_about_post_data_readiness(msg.chat.id, post_data):
        return
    __send_post(msg.chat.id, post_data, as_preview=True)


def __check_posts_limit(user_id: int, channel_id: int) -> bool:
    """:returns true if user can send post"""
    posts_limit = users.get_or_create_user_post_limit(user_id, channel_id)
    sent_posts_amount = users.get_daily_posts_amount(user_id, channel_id)
    return posts_limit.posts_limit > sent_posts_amount


def __send_post(chat_id: int, post_data: PostData, as_preview=False):
    """This func is used for preview and sending posts to the channels.
       If is_preview is True post will be sent without keyboard."""
    caption = post_data.text
    user_sign = users.get_user_sign(post_data.creator_id)
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


def __notify_about_post_data_readiness(chat_id: int, post_data: PostData) -> bool:
    """:returns true if post_data is not valid to sending and notification was sent."""
    if not __is_post_data_valid(post_data):
        bot.send_message(chat_id, "Не хватает данных для отправки поста.")
        return True
    return False


def __is_post_data_valid(post_data: PostData) -> bool:
    """:returns True if post_data is valid to sending.
       If post data type was initialized User already send allowed media. This is enough to create post."""
    return post_data.type is not None


def __apply_entities(text: str, entities: list) -> str:
    """Apply telegram native text formatting. Converts entities to html tags."""
    if not entities:
        return text

    html_tags_templates = {
        "bold": "<b>{}</b>",
        "italic": "<i>{}</i>",
        "underline": "<u>{}</u>",
        "strikethrough": "<s>{}</s>",
        "code": "<code>{}</code>",
        "text_link": "<a href='{}'>{}</a>"
    }

    global_offset = 0
    for entity in entities:
        if entity.type not in html_tags_templates.keys():
            continue
        start = entity.offset + global_offset
        end = start + entity.length
        entity_text = text[start:end]
        if entity.type == 'text_link':
            template = html_tags_templates[entity.type].format(entity.url, entity_text)
        else:
            template = html_tags_templates[entity.type].format(entity_text)
        global_offset += len(template) - len(entity_text)
        text = "".join((text[:start], template, text[end:]))

    return text


def __replace_text(post_data: PostData, msg: types.Message):
    if msg.caption:
        post_data.text = __apply_entities(html.escape(msg.caption), msg.entities)
    elif msg.text:
        post_data.text = __apply_entities(html.escape(msg.text), msg.entities)


def __replace_existing_media_data(post_data: PostData, msg: types.Message):
    """User can send another photo while post creating. Caption will be saved, but post will get new image."""
    __remove_media_data(post_data)
    if msg.content_type == MediaTypes.photo:
        __attach_photo_to_post(post_data, msg.photo[-1].file_id)
    elif msg.content_type == MediaTypes.video:
        __attach_video_to_post(post_data, msg.video.file_id)
    elif msg.content_type == MediaTypes.animation:
        __attach_animation_to_post(post_data, msg.animation.file_id)


def __remove_media_data(post_data: PostData):
    PostDataMedia.delete().where(PostDataMedia.post_data_id == post_data.id).execute()


def __attach_photo_to_post(post_data: PostData, photo_id):
    post_data.type = MediaTypes.photo
    PostDataMedia.create(type=MediaTypes.photo,
                         post_data_id=post_data.id,
                         media_id=photo_id)


def __attach_video_to_post(post_data: PostData, video_id):
    post_data.type = MediaTypes.video
    PostDataMedia.create(type=MediaTypes.video,
                         post_data_id=post_data.id,
                         media_id=video_id)


def __attach_animation_to_post(post_data: PostData, animation_id):
    post_data.type = MediaTypes.animation
    PostDataMedia.create(type=MediaTypes.animation,
                         post_data_id=post_data.id,
                         media_id=animation_id)


def __save_post(post_data: PostData, telegram_message_id: int):
    Post.create(id=telegram_message_id, creator_id=post_data.creator_id,
                channel_id=post_data.channel_id, type=post_data.type,
                text=post_data.text)
