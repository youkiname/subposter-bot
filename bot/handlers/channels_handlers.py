from bot import bot, exception_handler, admin_required
from telebot.types import Message
from bot.controllers import channels


@bot.channel_post_handler(commands=['get_id'])
def send_channel_id(msg: Message):
    bot.send_message(msg.chat.id, "ID этого канала: {}".format(msg.chat.id))


@bot.message_handler(commands=['channels'])
@exception_handler
@admin_required
def send_channels_list(msg: Message):
    result_text = ""
    for channel in channels.get_all():
        result_text += f"{channel.title}: {channel.id}\n"
    if result_text:
        bot.send_message(msg.chat.id, result_text)
    else:
        bot.send_message(msg.chat.id, "Пока что нет добавленных каналов.\n"
                                      "/add_new_channel <id> <title> - добавить новый.")


@bot.message_handler(commands=['add_channel'])
@exception_handler
@admin_required
def add_new_channel(msg: Message):
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
        channels.add_new(channel_id, title)
        bot.send_message(msg.chat.id, f"Канал {title} успешно добавлен.\n"
                                      f"/channels - список каналов.")
