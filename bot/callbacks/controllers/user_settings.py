from telebot.types import CallbackQuery
from bot import bot
from bot.controllers import users
from bot.callbacks import CallbackCommands
from bot.controllers import keyboards


def process_sign_change(call: CallbackQuery):
    command = call.data
    user_settings = users.get_or_create_settings(call.from_user.id)

    if command == CallbackCommands.SET_SHOW_USERNAME:
        user_settings.attaching_username = not user_settings.attaching_username
    elif command == CallbackCommands.SET_SHOW_NAME:
        user_settings.attaching_fullname = not user_settings.attaching_fullname
    user_settings.save()

    keyboard = keyboards.get_user_settings_keyboard(user_settings)
    signature = users.get_user_sign(call.from_user.id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Подпись: {}\nНажми, чтобы изменить".format(signature or "пусто"),
                          reply_markup=keyboard)
