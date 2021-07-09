from telebot.types import CallbackQuery
from bot import bot
from bot.controllers import keyboards, users
from models import Vote, VoteTypes


def __get_votes_count(channel_id: int, post_id: int, vote_type: int) -> int:
    return Vote.select().where(Vote.post_id == post_id, Vote.channel_id == channel_id, Vote.type == vote_type).count()


def __get_likes_count(channel_id: int, post_id: int) -> int:
    return __get_votes_count(channel_id, post_id, VoteTypes.like)


def __get_dislikes_count(channel_id: int, post_id: int) -> int:
    return __get_votes_count(channel_id, post_id, VoteTypes.dislike)


def __update_post_creator_rating(previous_vote: Vote, new_vote: Vote, user_id: int):
    if previous_vote is None:
        if new_vote.type == VoteTypes.like:
            users.try_change_rating_by_id(user_id, offset=1)
        else:
            users.try_change_rating_by_id(user_id, offset=-1)
        return

    if previous_vote.type == VoteTypes.like and new_vote.type == VoteTypes.dislike:
        users.try_change_rating_by_id(user_id, offset=-2)
        return
    if previous_vote.type == VoteTypes.dislike and new_vote.type == VoteTypes.like:
        users.try_change_rating_by_id(user_id, offset=2)


def __update_post_keyboard(channel_id: int, post_id: int):
    likes_count = __get_likes_count(channel_id, post_id)
    dislikes_count = __get_dislikes_count(channel_id, post_id)
    keyboard = keyboards.get_post_keyboard(likes_count, dislikes_count)
    bot.edit_message_reply_markup(channel_id, post_id, reply_markup=keyboard)


def process_vote(call: CallbackQuery):
    user_id = call.from_user.id
    channel_id = call.message.chat.id
    post_id = call.message.message_id
    new_vote_type = int(call.data)

    new_vote = Vote(user_id=user_id,
                    channel_id=channel_id,
                    post_id=post_id,
                    type=new_vote_type)

    previous_vote = Vote.get_or_none(user_id=user_id,
                                     channel_id=channel_id,
                                     post_id=post_id)

    if previous_vote is not None and previous_vote.type == new_vote.type:
        bot.answer_callback_query(call.id, f"Already {VoteTypes.to_text(new_vote.type)}",
                                  cache_time=2)
        return

    __update_post_creator_rating(previous_vote, new_vote, user_id)

    if previous_vote is None:
        new_vote.save()
    else:
        previous_vote.type = new_vote.type
        previous_vote.save()

    __update_post_keyboard(channel_id, post_id)

    bot.answer_callback_query(call.id, "Success", cache_time=5)
