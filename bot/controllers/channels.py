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


def add_new(channel_id: int, title: str):
    Channel.create(id=channel_id, title=title)


def get_all():
    return Channel.select()


def get_channels_amount() -> int:
    return Channel.select().count()


def get_or_create_post_limit(channel_id: int) -> ChannelPostsLimit:
    return ChannelPostsLimit.get_or_create(
        channel_id=channel_id
    )
