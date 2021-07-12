from telebot import types
from bot import bot
from models import User, Channel, Admin


USER_COMMANDS_HELP_MESSAGE = ("Действия с пользователем:\n"
                              "/change_rating <username or id>\n"
                              "/change_post_limit <username or id> <channel_title>\n"
                              "/add_admin <username or id>\n"
                              "/delete_admin <username or id>\n"
                              "<username or id> - имя пользователя или id\n"
                              "<channel title> - название сохраненного канала")


USERDATA_INDEX_IN_MESSAGE_TEXT = 1
CHANNEL_TITLE_INDEX_IN_MESSAGE_TEXT = 2


def __try_get_word_from_message_text_by_index(msg: types.Message, index: int) -> str or None:
    try:
        word = msg.text.split(' ')[index]
    except (ValueError, IndexError):
        bot.send_message(msg.chat.id, USER_COMMANDS_HELP_MESSAGE)
        return None
    return word


def get_username_from_message_text(msg: types.Message) -> str or None:
    """example: /command <username>"""
    return __try_get_word_from_message_text_by_index(msg, USERDATA_INDEX_IN_MESSAGE_TEXT)


def try_get_user_from_message_text(msg: types.Message) -> User or None:
    """example: /command <username or id>"""
    username = get_username_from_message_text(msg)
    if username is None:
        return None
    user = None
    if username.isnumeric():
        user_id = int(username)
        user = User.get_or_none(User.id == user_id)
    else:
        user = User.get_or_none(User.username == username)
    if user is None:
        bot.send_message(msg.chat.id, f"Пользователь {username} не найден")
    return user


def try_get_admin_from_message_text(msg: types.Message) -> Admin or None:
    username = get_username_from_message_text(msg)
    if username is None:
        return None
    return Admin.get_or_none(Admin.username == username)


def try_get_channel_from_message_text(msg: types.Message) -> Channel or None:
    """example: /command <username or id> <channel title>"""
    channel_title = __try_get_word_from_message_text_by_index(msg, CHANNEL_TITLE_INDEX_IN_MESSAGE_TEXT)
    if channel_title is None:
        return None
    channel = Channel.get_or_none(Channel.title == channel_title)
    if channel is None:
        bot.send_message(msg.chat.id, f"Канал {channel_title} не зарегистрирован у бота.\n"
                                      f"/add_channel - добавить канал.\n"
                                      f"/channels - список каналов.")
    return channel