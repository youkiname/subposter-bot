from bot import bot
from bot.middleware import exception_handler
from telebot.types import Message
from bot.controllers import channels, users


@bot.channel_post_handler(commands=['get_id'])
def send_channel_id(msg: Message):
    bot.send_message(msg.chat.id, "ID этого канала: {}".format(msg.chat.id))


@bot.message_handler(commands=['channels'])
@exception_handler
@users.admin_required
def send_channels_list(msg: Message):
    channels.send_channels_list(msg)


@bot.message_handler(commands=['add_channel'])
@exception_handler
@users.superuser_required
def add_new_channel(msg: Message):
    channels.process_channel_addition(msg)


@bot.message_handler(commands=['delete_channel'])
@exception_handler
@users.superuser_required
def delete_channel(msg: Message):
    channels.process_channel_deleting(msg)


@bot.message_handler(commands=['freeze_channel'])
@exception_handler
@users.admin_required
def freeze_channel(msg: Message):
    channels.process_channel_freezing(msg, channels.ChannelStatusAction.freeze)


@bot.message_handler(commands=['unfreeze_channel'])
@exception_handler
@users.admin_required
def unfreeze_channel(msg: Message):
    channels.process_channel_freezing(msg, channels.ChannelStatusAction.unfreeze)


@bot.message_handler(commands=['change_channel_post_limit'])
@exception_handler
@users.superuser_required
def change_channel_post_limit(msg: Message):
    channels.process_post_limit_changing(msg)
