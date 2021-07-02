from bot import bot
from telebot.types import CallbackQuery
from bot.callbacks import CallbackCommands, callback_exception_handler
from bot.callbacks.controllers import votes


def __is_votes_command(call: CallbackQuery):
    return call.data in (CallbackCommands.POST_LIKE, CallbackCommands.POST_DISLIKE)


@bot.callback_query_handler(func=__is_votes_command)
@callback_exception_handler
def sign_change_handler(call: CallbackQuery):
    votes.process_vote(call)
