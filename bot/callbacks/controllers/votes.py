import time

from telebot.apihelper import ApiTelegramException
from telebot.types import CallbackQuery, Message

from bot import bot
from bot.controllers import keyboards
from bot.services import users as user_services
from models import Vote, VoteTypes, Post, Channel
from config import config


def process_vote(call: CallbackQuery):
    __save_post_if_not_exists(call.message)
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
    __update_post_creator_rating(previous_vote, new_vote, post_id)

    if previous_vote is None:
        new_vote.save()
    else:
        previous_vote.type = new_vote.type
        previous_vote.save()

    __update_post_keyboard(channel_id, post_id)

    bot.answer_callback_query(call.id, "Success", cache_time=5)


def __save_post_if_not_exists(msg: Message) -> Post:
    """This will be useful if posts database was dropped
    or if you use another service for creating post."""
    post = Post.get_or_none(Post.id == msg.message_id, Post.channel_id == msg.chat.id)
    if post is not None:
        return post
    # idk Post.get_or_create() raises 'duplicate key value violates unique constraint' exception ¯\_(ツ)_/¯
    post = Post.create(
        id=msg.message_id,
        channel_id=msg.chat.id,
        creator_id=config.SUPER_ADMIN_ID,
        type=msg.content_type,
        text=msg.caption or msg.text
    )
    return post


def __get_votes_count(channel_id: int, post_id: int, vote_type: int) -> int:
    return Vote.select().where(Vote.post_id == post_id, Vote.channel_id == channel_id, Vote.type == vote_type).count()


def __get_likes_count(channel_id: int, post_id: int) -> int:
    return __get_votes_count(channel_id, post_id, VoteTypes.like)


def __get_dislikes_count(channel_id: int, post_id: int) -> int:
    return __get_votes_count(channel_id, post_id, VoteTypes.dislike)


def __update_post_creator_rating(previous_vote: Vote or None, new_vote: Vote, post_id: int):
    post = Post.get(Post.id == post_id)
    user_id = post.creator_id
    if previous_vote is None:
        if new_vote.type == VoteTypes.like:
            user_services.change_rating_by_id(user_id, offset=1)
        else:
            user_services.change_rating_by_id(user_id, offset=-1)
        return

    if previous_vote.type == VoteTypes.like and new_vote.type == VoteTypes.dislike:
        user_services.change_rating_by_id(user_id, offset=-2)
        return
    if previous_vote.type == VoteTypes.dislike and new_vote.type == VoteTypes.like:
        user_services.change_rating_by_id(user_id, offset=2)


def __update_post_keyboard(channel_id: int, post_id: int):
    channel = Channel.get_by_id(channel_id)
    if channel.markup_updating_limit > time.time():
        # can't update keyboard. Telegram api prevents flood.
        return
    likes_count = __get_likes_count(channel_id, post_id)
    dislikes_count = __get_dislikes_count(channel_id, post_id)
    keyboard = keyboards.get_post_keyboard(likes_count, dislikes_count)
    try:
        bot.edit_message_reply_markup(channel_id, post_id, reply_markup=keyboard)
    except ApiTelegramException as e:
        if e.error_code != 429:
            raise e
        delay = 7
        channel.markup_updating_limit = int(time.time()) + delay
        channel.save()
