from telebot.types import CallbackQuery
from bot import bot
from bot.controllers import keyboards
from models import Vote, VoteTypes


def __get_votes_count(channel_id: int, post_id: int, vote_type: int) -> int:
    return Vote.select().where(Vote.post_id == post_id, Vote.channel_id == channel_id, Vote.type == vote_type).count()


def __get_likes_count(channel_id: int, post_id: int) -> int:
    return __get_votes_count(channel_id, post_id, VoteTypes.like)


def __get_dislikes_count(channel_id: int, post_id: int) -> int:
    return __get_votes_count(channel_id, post_id, VoteTypes.dislike)


def __update_vote(channel_id: int, post_id: int, user_id: int, new_vote_type: int) -> bool:
    """ Saves new vote to DB or update existed.
        :returns True if vote update is successful
                False if vote_type matches with existed"""
    current_vote = Vote.get_or_none(Vote.user_id == user_id,
                                    Vote.channel_id == channel_id,
                                    Vote.post_id == post_id)
    if current_vote is None:
        Vote(user_id=user_id, channel_id=channel_id, post_id=post_id, type=new_vote_type).save()
        return True
    elif new_vote_type == current_vote.type:
        return False
    current_vote.type = new_vote_type
    current_vote.save()
    return True


def process_vote(call: CallbackQuery):
    new_vote = int(call.data)
    channel_id = call.message.chat.id
    post_id = call.message.message_id
    user_id = call.from_user.id

    if not __update_vote(channel_id, post_id, user_id, new_vote):
        bot.answer_callback_query(call.id, f"Already {VoteTypes.to_text(new_vote)}",
                                  cache_time=2)
        return
    bot.answer_callback_query(call.id, "Success", cache_time=5)

    likes_count = __get_likes_count(channel_id, post_id)
    dislikes_count = __get_dislikes_count(channel_id, post_id)
    keyboard = keyboards.get_post_keyboard(likes_count, dislikes_count)
    bot.edit_message_reply_markup(channel_id, post_id, reply_markup=keyboard)
