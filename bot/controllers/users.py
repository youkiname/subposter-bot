from models import Admin, User, PostData, UserSettings, Post, Channel, Vote, VoteTypes, TargetUser
from telebot import types
from datetime import datetime
from config import config
from bot import bot


class States:
    FREE = 0
    CHANNEL_CHOOSING = 1
    POST_CREATING = 2
    RATING_CHANGE = 3
    MESSAGE_FORWARDING = 4


def superuser_required(handler):
    def wrapper_accepting_arguments(msg):
        if is_superuser(msg.from_user.id):
            handler(msg)
        else:
            bot.send_message(msg.chat.id, "Недостаточно полномочий")
    return wrapper_accepting_arguments


def admin_required(handler):
    def wrapper_accepting_arguments(msg):
        if is_admin(msg.from_user.id):
            handler(msg)
        else:
            bot.send_message(msg.chat.id, "Недостаточно полномочий")
    return wrapper_accepting_arguments


def start_rating_change(msg: types.Message):
    admin = get_or_create_user(msg.from_user)
    target_user = __try_get_user_from_message_text(msg)
    if not target_user:
        return
    admin.state = States.RATING_CHANGE
    admin.save()
    __get_or_create_target_user(admin.id, target_user.id)
    bot.send_message(msg.chat.id, f"Вы выбрали пользователя:\n"
                                  f"@{target_user.username} <{target_user.id}>\n"
                                  f"Рейтинг: {target_user.rating}\n"
                                  f"Отправьте число, на которое будет изменен рейтинг.\n"
                                  f"Пример: '20' - увеличить на 20\n"
                                  f"'-20' - уменьшить на 20")


def continue_rating_change(msg: types.Message):
    admin = get_or_create_user(msg.from_user)
    temp_target_user_data = TargetUser.get_or_none(TargetUser.user_id == admin.id)
    if temp_target_user_data is None:
        bot.send_message(msg.chat.id, "Пользователь не выбран. Попробуйте ещё раз.\n"
                                      "/change_user_rating")
        clear_state(admin)
        return
    if not msg.text.isnumeric():
        bot.send_message(msg.chat.id, "Отправь сдвиг рейтинга числом.")
        return
    rating_offset = int(msg.text)

    target_user = User.get_by_id(temp_target_user_data.target_id)
    target_user.rating += rating_offset


    clear_state(admin)
    temp_target_user_data.delete_instance()
    bot.send_message(msg.chat.id, f"Рейтинг пользователя успешно изменён.\n"
                                  f"@{target_user.username} <{target_user.id}>\n"
                                  f"Рейтинг: {target_user.rating}\n")
    target_user.save()


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


def is_user_creating_post(msg: types.Message) -> bool:
    user = get_or_create_user(msg.from_user)
    return user.state in [States.POST_CREATING, States.CHANNEL_CHOOSING]


def is_admin_on_rating_change_state(msg: types.Message) -> bool:
    admin = get_or_create_user(msg.from_user)
    return admin.state == States.RATING_CHANGE


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


def try_change_rating_by_id(user_id: int, offset: int):
    user = User.get_or_none(id=user_id)
    if user:
        user.rating += offset
        user.save()


def clear_state_by_id(user_id: int):
    user = User.get_by_id(user_id)
    user.state = States.FREE
    PostData.delete().where(PostData.creator_id == user.id).execute()
    user.save()


def clear_state(user: User):
    user.state = States.FREE
    user.save()


def __try_get_user_from_message_text(msg: types.Message) -> User or None:
    """example: /command <username or id>"""
    try:
        username = msg.text.split(' ')[1]
    except (ValueError, IndexError):
        bot.send_message(msg.chat.id, "Действия с пользователем:\n"
                                      "/change_rating <username>\n"
                                      "<username or id> - имя пользователя или id")
        return None
    else:
        if username.isnumeric():
            user_id = int(username)
            return User.get_or_none(User.id == user_id)
        return User.get_or_none(User.username == username)


def __get_or_create_target_user(admin_id: int, target_id: int):
    target_user = TargetUser.get_or_none(TargetUser.user_id == admin_id)
    if target_user is not None:
        target_user.target_id = target_id
        target_user.save()
        return target_user
    return TargetUser.create(user_id=admin_id, target_id=target_id)
