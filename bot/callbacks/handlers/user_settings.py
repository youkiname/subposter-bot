from bot import bot
from telebot.types import CallbackQuery
from bot.callbacks.controllers import user_settings
from bot.callbacks import CallbackCommands, callback_exception_handler


def __is_sign_change_command(call: CallbackQuery):
    return call.data in (CallbackCommands.SET_SHOW_NAME, CallbackCommands.SET_SHOW_USERNAME)


@bot.callback_query_handler(func=__is_sign_change_command)
@callback_exception_handler
def sign_change_handler(call: CallbackQuery):
    bot.answer_callback_query(call.id)
    user_settings.process_sign_change(call)
