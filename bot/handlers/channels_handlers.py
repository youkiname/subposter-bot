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
    channels.process_channel_addition(msg)


@bot.message_handler(commands=['add_channel'])
@exception_handler
@admin_required
def delete_channel(msg: Message):
    channels.process_channel_deleting(msg)
