from telebot.types import Message
from bot.controllers import users, keyboards
from bot import bot


def send_user_settings_panel(msg: Message):
    signature = users.get_user_sign(msg.from_user.id)
    current_settings = users.get_or_create_settings(msg.from_user.id)
    keyboard = keyboards.get_user_settings_keyboard(current_settings)
    bot.send_message(msg.chat.id, "Подпись: {}\nНажми, чтобы изменить".format(signature or "пусто"),
                     reply_markup=keyboard)
