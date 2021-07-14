from bot import bot
from bot.controllers import keyboards
from telebot.types import Message
from models import PostData, MediaTypes, PostDataMedia, Post
from bot.services import users as user_services
import html


def check_posts_limit(user_id: int, channel_id: int) -> bool:
    """:returns true if user can send post"""
    sent_posts_amount = user_services.get_daily_posts_amount(user_id, channel_id)
    post_limit = user_services.get_daily_posts_limit(user_id, channel_id)
    return post_limit > sent_posts_amount


def send_post(chat_id: int, post_data: PostData, as_preview=False):
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


def replace_text(post_data: PostData, msg: Message):
    if msg.caption:
        post_data.text = __apply_entities(html.escape(msg.caption), msg.entities)
    elif msg.text:
        post_data.text = __apply_entities(html.escape(msg.text), msg.entities)


def replace_existing_media_data(post_data: PostData, msg: Message):
    """User can send another photo while post creating. Caption will be saved, but post will get new image."""
    __remove_media_data(post_data)
    if msg.content_type == MediaTypes.photo:
        __attach_photo_to_post(post_data, msg.photo[-1].file_id)
    elif msg.content_type == MediaTypes.video:
        __attach_video_to_post(post_data, msg.video.file_id)
    elif msg.content_type == MediaTypes.animation:
        __attach_animation_to_post(post_data, msg.animation.file_id)


def save_post(post_data: PostData, telegram_message_id: int):
    Post.create(id=telegram_message_id, creator_id=post_data.creator_id,
                channel_id=post_data.channel_id, type=post_data.type,
                text=post_data.text)


def delete_temp_post_data(user_id: int):
    PostData.delete().where(PostData.creator_id == user_id).execute()


def __is_post_data_valid_for_sending(post_data: PostData) -> bool:
    """If post data type was initialized User already send allowed media. This is enough to create post."""
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


