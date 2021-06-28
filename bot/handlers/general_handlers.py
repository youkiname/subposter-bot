from bot import bot, exception_handler
from telebot.types import Message
from bot.controllers import keyboards, users, user_settings


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
    users.clear_state(msg.from_user.id)
    bot.send_message(msg.chat.id, "Отменил всё, что можно", reply_markup=keyboards.get_main_keyboard())


@bot.message_handler(regexp="\/profile|Профиль")
@exception_handler
def send_profile_info(msg: Message):
    user = users.get_or_create_user(msg.from_user)
    bot.send_message(msg.chat.id, users.get_profile_info(user))


@bot.message_handler(regexp="\/info|Инфо")
@exception_handler
def send_profile_info(msg: Message):
    info = "Инфо"
    bot.send_message(msg.chat.id, info)


@bot.message_handler(commands=['settings'])
@exception_handler
def send_profile_info(msg: Message):
    user_settings.send_user_settings_panel(msg)
