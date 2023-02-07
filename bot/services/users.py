from datetime import datetime

from bot.services.user_states import UserStates
from bot.services import channels as channel_services
from config import config
from models import (User, UserSettings, Admin, Post,
                    Channel, Vote, VoteTypes, CustomUserPostsLimit,
                    TargetChannel, TargetUser)


def create_or_update_user(from_user) -> User:
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
    info = f"Ваш рейтинг: {user.rating}\n" \
           f"Посты за сегодня:\n"
    for channel_title, posts_amount in get_daily_posts_amount_by_channels(user.id).items():
        info += f"{channel_title}: {posts_amount}\n"
    info += "Посты за всё время:\n"
    for channel_title, posts_amount in get_posts_amount_by_channels(user.id).items():
        info += f"{channel_title}: {posts_amount}\n"
    info += f"Всего:{get_posts_amount(user.id)}\n"

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


def get_daily_posts_amount(user_id: int, channel_id: int) -> int:
    """:returns posts amount was sent by user today"""
    day_start_time = datetime.now().replace(hour=0, minute=0).timestamp()
    return Post.select().where(Post.creator_id == user_id,
                               Post.channel_id == channel_id,
                               Post.created_at > day_start_time).count()


def get_daily_posts_amount_by_channels(user_id: int) -> dict:
    """:returns dict with key = channel title, value = posts amount"""
    result = {}
    channels = Channel.select()
    for channel in channels:
        result[channel.title] = get_daily_posts_amount(user_id, channel.id)
    return result


def get_posts_amount_by_channels(user_id: int) -> dict:
    """:returns dict with key = channel title, value = posts amount"""
    result = {}
    channels = Channel.select()
    for channel in channels:
        result[channel.title] = Post.select().where(Post.creator_id == user_id,
                                                    Post.channel_id == channel.id).count()
    return result


def get_posts_amount(user_id: int) -> int:
    return Post.select().where(Post.creator_id == user_id).count()


def get_likes_amount_in_all_channels(user_id: int) -> dict:
    """:returns dict with key = channel title, value = likes amount"""
    return __get_votes_amount_in_all_channels(user_id, VoteTypes.like)


def get_dislikes_amount_in_all_channels(user_id: int) -> dict:
    """:returns dict with key = channel title, value = dislikes amount"""
    return __get_votes_amount_in_all_channels(user_id, VoteTypes.dislike)


def change_rating_by_id(user_id: int, offset: int):
    user = User.get_or_none(id=user_id)
    user.rating += offset
    user.save()


def clear_state_by_id(user_id: int):
    user = User.get_by_id(user_id)
    clear_state(user)


def clear_state(user: User):
    user.state = UserStates.FREE
    user.save()


def get_by_id(user_id: int) -> User:
    return User.get_by_id(user_id)


def get_daily_posts_limit(user_id: int, channel_id: int) -> int:
    custom_posts_limit = CustomUserPostsLimit.get_or_none(
        CustomUserPostsLimit.user_id == user_id,
        CustomUserPostsLimit.channel_id == channel_id
    )
    if custom_posts_limit is not None:
        return custom_posts_limit.limit
    channel_daily_post_limit = channel_services.get_or_create_post_limit(channel_id)
    return channel_daily_post_limit.limit


def get_or_create_target_user(admin_id: int, target_id: int) -> TargetUser:
    target_user = TargetUser.get_or_none(TargetUser.user_id == admin_id)
    if target_user is not None:
        target_user.target_id = target_id
        target_user.save()
        return target_user
    return TargetUser.create(user_id=admin_id, target_id=target_id)


def get_or_create_target_channel(admin_id: int, channel_id: int) -> TargetChannel:
    target_channel = TargetChannel.get_or_none(TargetChannel.user_id == admin_id)
    if target_channel is not None:
        target_channel.channel_id = channel_id
        target_channel.save()
        return target_channel
    return TargetChannel.create(user_id=admin_id, channel_id=channel_id)


def get_target_user_by_id(user_id: int) -> TargetUser:
    return TargetUser.get_or_none(TargetUser.user_id == user_id)


def create_or_set_custom_posts_limit(user_id: int, channel_id: int, posts_limit: int) -> CustomUserPostsLimit:
    limit = CustomUserPostsLimit.get_or_none(CustomUserPostsLimit.user_id == user_id,
                                             CustomUserPostsLimit.channel_id == channel_id)
    if limit is not None:
        limit.limit = posts_limit
        limit.save()
        return limit
    return CustomUserPostsLimit.create(user_id=user_id, channel_id=channel_id, limit=posts_limit)


def __get_votes_amount_in_all_channels(user_id: int, vote_type: int) -> dict:
    """:returns dict with key = channel title, value = votes amount"""
    result = {}
    channels = Channel.select()
    for channel in channels:
        result[channel.title] = Vote.select().where(Vote.user_id == user_id,
                                                    Vote.channel_id == channel.id,
                                                    Vote.type == vote_type).count()
    return result
