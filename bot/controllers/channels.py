from telebot.types import Message
from bot import bot
from bot.services import channels as channel_services


class ChannelStatusAction:
    freeze = True
    unfreeze = False

    @staticmethod
    def to_text(status: bool):
        if status == ChannelStatusAction.freeze:
            return "заморожен"
        return "разморожен"


def send_channels_list(msg: Message):
    result_text = ""
    for channel in channel_services.get_all():
        result_text += f"{channel.title} <{channel.id}>\n"
    if result_text:
        bot.send_message(msg.chat.id, result_text)
    else:
        bot.send_message(msg.chat.id, "Пока что нет добавленных каналов.\n"
                                      "/add_channel <id> <title> - добавить новый.")


def process_channel_addition(msg: Message):
    channel_data = __try_get_channel_data(msg)
    if channel_data is None:
        return
    channel_id, title = channel_data
    channel_services.add_new(channel_id, title)
    bot.send_message(msg.chat.id, f"Канал {title} успешно добавлен.\n"
                                  f"/channels - список каналов.")


def process_channel_deleting(msg: Message):
    channel_title = __try_get_channel_title(msg)
    if channel_title is None:
        return

    channel = channel_services.get_by_title(channel_title)
    if channel is None:
        bot.send_message(msg.chat.id, "Канал с таким именем не существует.\n/channels - список каналов")
        return
    channel_services.delete_if_exist(channel.id)
    bot.send_message(msg.chat.id, f"Канал {channel.title}<{channel.id}> успешно удален.")


def process_channel_freezing(msg: Message, status: bool):
    channel_title = __try_get_channel_title(msg)
    if channel_title is None:
        return

    channel = channel_services.get_by_title(channel_title)
    if channel is None:
        bot.send_message(msg.chat.id, "Канал с таким именем не существует.\n/channels - список каналов")
        return
    channel.frozen = status
    channel.save()
    bot.send_message(msg.chat.id, f"Канал {channel.title}<{channel.id}> {ChannelStatusAction.to_text(status)}.")


def __try_get_channel_data(msg: Message) -> (int, str) or None:
    try:
        text_data = msg.text.split(' ')
        channel_id = int(text_data[1])
        title = text_data[2]
        return channel_id, title
    except (ValueError, IndexError):
        bot.send_message(msg.chat.id, "Канал добавляется по шаблону:\n"
                                      "/add_channel <id> <title>\n"
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
                                      "/delete_channel <title>\n"
                                      "/freeze_channel <title>\n"
                                      "/unfreeze_channel <title>\n"
                                      "<title> - название канала\n"
                                      "/channels - список каналов")
        return None
