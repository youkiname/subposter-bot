from telebot.types import Message

from bot import bot
from bot.controllers import keyboards
from bot.services import users as user_services


def send_user_settings_panel(msg: Message):
    signature = user_services.get_user_sign(msg.from_user.id)
    current_settings = user_services.get_or_create_settings(msg.from_user.id)
    keyboard = keyboards.get_user_settings_keyboard(current_settings)
    bot.send_message(msg.chat.id, "Подпись: {}\nНажми, чтобы изменить".format(signature or "пусто"),
                     reply_markup=keyboard)
