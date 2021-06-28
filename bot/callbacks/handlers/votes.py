from bot import bot, exception_handler
from telebot.types import CallbackQuery
from bot.callbacks import CallbackCommands
from bot.callbacks.controllers import votes


def __is_votes_command(call: CallbackQuery):
    return call.data in (CallbackCommands.POST_LIKE, CallbackCommands.POST_DISLIKE)


@bot.callback_query_handler(func=__is_votes_command)
@exception_handler
def sign_change_handler(call: CallbackQuery):
    votes.process_vote(call)
