from models import Admin, User, PostData, UserSettings, UsersPostsLimit, Post, Channel, Vote, VoteTypes
from telebot import types
from datetime import datetime
from config import config


class States:
    FREE = 0
    CHANNEL_CHOOSING = 1
    POST_CREATING = 2


def get_or_create_user(from_user: types.User) -> User:
    db_user = User.get_or_none(id=from_user.id)
    if db_user is None:
        db_user = User.create(id=from_user.id, username=from_user.username,
                              first_name=from_user.first_name, last_name=from_user.last_name)
        db_user.save()
        return db_user
    is_user_changed = False
    if db_user.username != from_user.username:
        db_user.username = from_user.username
        is_user_changed = True
    if db_user.first_name != from_user.first_name:
        db_user.username = from_user.username
        is_user_changed = True
    if db_user.last_name != from_user.last_name:
        db_user.last_name = from_user.last_name
        is_user_changed = True

    if is_user_changed:
        db_user.save()
    return db_user


def get_or_create_settings(user_id: int) -> UserSettings:
    settings, created = UserSettings.get_or_create(id=user_id)
    return settings


def get_profile_info(user: User) -> str:
    info = f"Ваш рейтинг: {user.rating}\nПосты за сегодня:\n"
    for channel_title, posts_amount in get_daily_posts_amount_in_all_channels(user.id).items():
        info += f"{channel_title}: {posts_amount}\n"
    info += "Посты за всё время:\n"
    for channel_title, posts_amount in get_posts_amount_in_all_channels(user.id).items():
        info += f"{channel_title}: {posts_amount}\n"

    info += "Вы поставили лайков:\n"
    for channel_title, likes_amount in get_likes_amount_in_all_channels(user.id).items():
        info += f"{channel_title}: {likes_amount}\n"
    info += "Вы поставили дизлайков:\n"
    for channel_title, dislikes_amount in get_dislikes_amount_in_all_channels(user.id).items():
        info += f"{channel_title}: {dislikes_amount}\n"
    return info


def get_user_sign(user_id: int) -> str:
    """:returns string 'by first_name last_name' if user has activated this in the settings.
                Empty string if user want to sent posts anonymously"""
    settings = get_or_create_settings(user_id)
    user = User.get_by_id(user_id)
    if settings.attaching_fullname and settings.attaching_username and user.username:
        if user.last_name:
            return f"by {user.first_name} {user.last_name} (@{user.username})"
        return f"by {user.first_name} (@{user.username})"
    elif settings.attaching_username and user.username:
        return f"by @{user.username}"
    elif settings.attaching_fullname:
        if user.last_name:
            return f"by {user.first_name} {user.last_name}"
        return f"by {user.first_name}"
    return ""


def is_admin(user_id: int) -> bool:
    return Admin.get_or_none(id=user_id) is not None


def is_superuser(user_id: int) -> bool:
    return user_id == config.SUPER_ADMIN_ID


def is_user_creating_post(msg: types.Message) -> bool:
    user = get_or_create_user(msg.from_user)
    return user.state in [States.POST_CREATING, States.CHANNEL_CHOOSING]


def get_or_create_user_post_limit(user_id: int, channel_id: int) -> UsersPostsLimit:
    posts_limit, created = UsersPostsLimit.get_or_create(user_id=user_id,
                                                channel_id=channel_id)
    return posts_limit


def get_daily_posts_amount(user_id: int, channel_id: int) -> int:
    """:returns posts amount was sent by user today"""
    day_start_time = datetime.now().replace(hour=0, minute=0).timestamp()
    return Post.select().where(Post.creator_id == user_id,
                               Post.channel_id == channel_id,
                               Post.created_at > day_start_time).count()


def get_daily_posts_amount_in_all_channels(user_id: int) -> dict:
    """:returns dict with key = channel title, value = posts amount"""
    result = {}
    channels = Channel.select()
    for channel in channels:
        result[channel.title] = get_daily_posts_amount(user_id, channel.id)
    return result


def get_posts_amount_in_all_channels(user_id: int) -> dict:
    """:returns dict with key = channel title, value = posts amount"""
    result = {}
    channels = Channel.select()
    for channel in channels:
        result[channel.title] = Post.select().where(Post.creator_id == user_id,
                                                    Post.channel_id == channel.id).count()
    return result


def __get_votes_amount_in_all_channels(user_id: int, vote_type: int) -> dict:
    """:returns dict with key = channel title, value = votes amount"""
    result = {}
    channels = Channel.select()
    for channel in channels:
        result[channel.title] = Vote.select().where(Vote.user_id == user_id,
                                                    Vote.channel_id == channel.id,
                                                    Vote.type == vote_type).count()
    return result


def get_likes_amount_in_all_channels(user_id: int) -> dict:
    """:returns dict with key = channel title, value = likes amount"""
    return __get_votes_amount_in_all_channels(user_id, VoteTypes.like)


def get_dislikes_amount_in_all_channels(user_id: int) -> dict:
    """:returns dict with key = channel title, value = dislikes amount"""
    return __get_votes_amount_in_all_channels(user_id, VoteTypes.like)


def clear_state(user_id: int):
    user = User.get_by_id(user_id)
    user.state = States.FREE
    PostData.delete().where(PostData.creator_id == user.id).execute()
    user.save()
