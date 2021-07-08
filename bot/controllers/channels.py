from models import Channel, ChannelPostsLimit
from telebot.types import Message
from bot import bot


def process_channel_addition(msg: Message):
    try:
        text_data = msg.text.split(' ')
        channel_id = int(text_data[1])
        title = text_data[2]
    except (ValueError, IndexError):
        bot.send_message(msg.chat.id, "Канал добавляется по шаблону:\n"
                                      "/add_new_channel <id> <title>\n"
                                      "Где <id> - число, которое можно получить командой "
                                      "/get_id (добавив перед этим бота в канал)\n"
                                      "<title> - название канала")
    else:
        add_new(channel_id, title)
        bot.send_message(msg.chat.id, f"Канал {title} успешно добавлен.\n"
                                      f"/channels - список каналов.")


def process_channel_deleting(msg: Message):
    try:
        channel_title = msg.text.split(' ')[1]
    except (ValueError, IndexError):
        bot.send_message(msg.chat.id, "Канал можно удалить по шаблону:\n"
                                      "/delete_channel <title>\n"
                                      "Где <title> - название канала\n"
                                      "/channels - список каналов")
    else:
        channel = get_by_title(channel_title)
        if channel is None:
            bot.send_message(msg.chat.id, "Канал с таким именем не существует.\n/channels - список каналов")
            return
        try_delete(channel.id)
        bot.send_message(msg.chat.id, f"Канал {channel.title}<{channel.id}> успешно удален.")


def add_new(channel_id: int, title: str):
    Channel.create(id=channel_id, title=title)


def get_by_title(title: str) -> Channel:
    return Channel.get_or_none(Channel.title == title)


def get_all():
    return Channel.select()


def get_channels_amount() -> int:
    return Channel.select().count()


def get_or_create_post_limit(channel_id: int) -> ChannelPostsLimit:
    return ChannelPostsLimit.get_or_create(
        channel_id=channel_id
    )


def try_delete(channel_id: int):
    channel = Channel.get_or_none(Channel.id == channel_id)
    if channel is not None:
        channel.delete_instance()
    channel_posts_limit = ChannelPostsLimit.get_or_none(ChannelPostsLimit.channel_id == channel_id)
    if channel_posts_limit is not None:
        channel_posts_limit.delete_instance()
