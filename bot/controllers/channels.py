from models import Channel, ChannelPostsLimit
from telebot.types import Message
from bot import bot


class ChannelStatusAction:
    freeze = True
    unfreeze = False

    @staticmethod
    def to_text(status: bool):
        if status == ChannelStatusAction.freeze:
            return "заморожен"
        return "разморожен"


def process_channel_addition(msg: Message):
    channel_data = __try_get_channel_data(msg)
    if channel_data is None:
        return
    channel_id, title = channel_data
    add_new(channel_id, title)
    bot.send_message(msg.chat.id, f"Канал {title} успешно добавлен.\n"
                                  f"/channels - список каналов.")


def process_channel_deleting(msg: Message):
    channel_title = __try_get_channel_title(msg)
    if channel_title is None:
        return

    channel = get_by_title(channel_title)
    if channel is None:
        bot.send_message(msg.chat.id, "Канал с таким именем не существует.\n/channels - список каналов")
        return
    try_delete(channel.id)
    bot.send_message(msg.chat.id, f"Канал {channel.title}<{channel.id}> успешно удален.")


def process_channel_freezing(msg: Message, status: bool):
    """:param status - one of ChannelStatusAction"""
    channel_title = __try_get_channel_title(msg)
    if channel_title is None:
        return

    channel = get_by_title(channel_title)
    if channel is None:
        bot.send_message(msg.chat.id, "Канал с таким именем не существует.\n/channels - список каналов")
        return
    channel.frozen = status
    channel.save()
    bot.send_message(msg.chat.id, f"Канал {channel.title}<{channel.id}> {ChannelStatusAction.to_text(status)}.")


def add_new(channel_id: int, title: str):
    Channel.create(id=channel_id, title=title)


def get_by_title(title: str) -> Channel or None:
    return Channel.get_or_none(Channel.title == title)


def get_all():
    return Channel.select()


def get_channels_amount() -> int:
    return Channel.select().count()


def get_or_create_post_limit(channel_id: int) -> ChannelPostsLimit:
    posts_limit, created = ChannelPostsLimit.get_or_create(channel_id=channel_id)
    return posts_limit


def try_delete(channel_id: int):
    channel = Channel.get_or_none(Channel.id == channel_id)
    if channel is not None:
        channel.delete_instance()
    channel_posts_limit = ChannelPostsLimit.get_or_none(ChannelPostsLimit.channel_id == channel_id)
    if channel_posts_limit is not None:
        channel_posts_limit.delete_instance()


def __try_get_channel_data(msg: Message) -> (int, str) or None:
    try:
        text_data = msg.text.split(' ')
        channel_id = int(text_data[1])
        title = text_data[2]
        return channel_id, title
    except (ValueError, IndexError):
        bot.send_message(msg.chat.id, "Канал добавляется по шаблону:\n"
                                      "/add_new_channel <id> <title>\n"
                                      "Где <id> - число, которое можно получить командой "
                                      "/get_id (добавив перед этим бота в канал)\n"
                                      "<title> - название канала")
        return None


def __try_get_channel_title(msg: Message) -> str or None:
    try:
        channel_title = msg.text.split(' ')[1]
        return channel_title
    except (ValueError, IndexError):
        bot.send_message(msg.chat.id, "Действия с каналом:\n"
                                      "/<command> <title>\n"
                                      "Где <command> одно из:\n"
                                      "/delete_channel\n"
                                      "/freeze_channel\n"
                                      "/unfreeze_channel\n"
                                      "<title> - название канала\n"
                                      "/channels - список каналов")
        return None
