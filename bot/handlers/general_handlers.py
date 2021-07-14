from telebot.types import Message

from bot import bot
from bot.controllers import general, keyboards
from bot.middleware import exception_handler


@bot.message_handler(commands=['start'])
def send_welcome(msg: Message):
    bot.send_message(msg.chat.id, "Я бот для создания пользовательских постов.\n"
                                  "/info - дополнительная информация и команды",
                     reply_markup=keyboards.get_main_keyboard())


@bot.message_handler(commands=['get_id'])
def send_chat_id(msg: Message):
    bot.send_message(msg.chat.id, "ID этого чата: {}".format(msg.chat.id))


@bot.message_handler(regexp="\/cancel|Отмена")
@exception_handler
def cancel(msg: Message):
    general.process_cancel(msg)


@bot.message_handler(regexp="\/info|Инфо")
@exception_handler
def send_profile_info(msg: Message):
    info = "Инфо"
    bot.send_message(msg.chat.id, info)
