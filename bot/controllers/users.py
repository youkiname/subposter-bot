from telebot import types

from bot import bot
from bot.services import channels as channel_services
from bot.services import users as user_services
from bot.services.user_states import UserStates
from bot.utils import MessageTextSplitter


def superuser_required(handler):
    def wrapper_accepting_arguments(msg):
        if user_services.is_superuser(msg.from_user.id):
            handler(msg)
        else:
            bot.send_message(msg.chat.id, "Недостаточно полномочий")

    return wrapper_accepting_arguments


def admin_required(handler):
    def wrapper_accepting_arguments(msg):
        if user_services.is_admin(msg.from_user.id):
            handler(msg)
        else:
            bot.send_message(msg.chat.id, "Недостаточно полномочий")

    return wrapper_accepting_arguments


def send_profile_info(msg: types.Message):
    user = user_services.create_or_update_user(msg.from_user)
    info = user_services.get_profile_info(user)
    bot.send_message(msg.chat.id, info)


def start_rating_change(msg: types.Message):
    admin = user_services.create_or_update_user(msg.from_user)
    user = MessageTextSplitter.try_get_user_from_message_text(msg)
    if not user:
        return
    admin.state = UserStates.RATING_CHANGE
    admin.save()
    user_services.get_or_create_target_user(admin.id, user.id)
    bot.send_message(msg.chat.id, f"Вы выбрали пользователя:\n"
                                  f"@{user.username} <{user.id}>\n"
                                  f"Рейтинг: {user.rating}\n"
                                  f"Отправьте число, на которое будет изменен рейтинг.\n"
                                  f"Пример: '20' - увеличить на 20\n"
                                  f"'-20' - уменьшить на 20")


def continue_rating_change(msg: types.Message):
    admin = user_services.create_or_update_user(msg.from_user)
    temp_target_user_data = user_services.get_target_user_by_id(admin.id)
    if temp_target_user_data is None:
        bot.send_message(msg.chat.id, "Пользователь не выбран. Попробуйте ещё раз.\n"
                                      "/change_rating")
        user_services.clear_state(admin)
        return
    if not msg.text.isnumeric():
        bot.send_message(msg.chat.id, "Отправь сдвиг рейтинга числом.")
        return
    rating_offset = int(msg.text)

    target_user = user_services.get_by_id(temp_target_user_data.target_id)
    target_user.rating += rating_offset

    user_services.clear_state(admin)
    temp_target_user_data.delete_instance()
    bot.send_message(msg.chat.id, f"Рейтинг пользователя успешно изменён.\n"
                                  f"@{target_user.username} <{target_user.id}>\n"
                                  f"Рейтинг: {target_user.rating}\n")
    target_user.save()


def start_daily_post_limit_change(msg: types.Message):
    admin = user_services.create_or_update_user(msg.from_user)
    user = MessageTextSplitter.try_get_user_from_message_text(msg)
    channel = MessageTextSplitter.try_get_channel_from_message_text(msg)
    if not user or not channel:
        return

    admin.state = UserStates.DAILY_POST_LIMIT_CHANGE
    admin.save()

    user_services.get_or_create_target_user(admin.id, user.id)
    user_services.get_or_create_target_channel(admin.id, channel.id)

    user_daily_posts_limit = user_services.get_daily_posts_limit(user.id, channel.id)
    bot.send_message(msg.chat.id, f"Вы выбрали пользователя:\n"
                                  f"@{user.username} <{user.id}>\n"
                                  f"Канал:\n"
                                  f"{channel.title} <{channel.id}>\n"
                                  f"Текущий суточный лимит: {user_daily_posts_limit}\n"
                                  f"Отправьте новый суточный лимит числом в следующем сообщении.")


def continue_daily_post_limit_change(msg: types.Message):
    admin = user_services.create_or_update_user(msg.from_user)
    temp_target_user_data = user_services.get_target_user_by_id(admin.id)
    temp_target_channel_data = channel_services.get_target_channel_by_user_id(admin.id)
    if temp_target_user_data is None or temp_target_channel_data is None:
        bot.send_message(msg.chat.id, "Пользователь или канал не выбран. Попробуйте ещё раз.\n"
                                      "/change_post_limit")
        user_services.clear_state(admin)
        return
    if not msg.text.isnumeric() or int(msg.text) < 0:
        bot.send_message(msg.chat.id, "Отправь новый лимит положительным числом.")
        return
    new_daily_limit = int(msg.text)
    user_services.create_or_set_custom_posts_limit(user_id=temp_target_user_data.target_id,
                                                   channel_id=temp_target_channel_data.channel_id,
                                                   posts_limit=new_daily_limit)

    user_services.clear_state(admin)
    temp_target_user_data.delete_instance()
    temp_target_channel_data.delete_instance()

    bot.send_message(msg.chat.id, f"Новый суточный лимит постов установлен.")


def is_user_creating_post(msg: types.Message) -> bool:
    user = user_services.create_or_update_user(msg.from_user)
    return user.state in [UserStates.POST_CREATING, UserStates.CHANNEL_CHOOSING]


def is_admin_on_rating_change_state(msg: types.Message) -> bool:
    admin = user_services.create_or_update_user(msg.from_user)
    return admin.state == UserStates.RATING_CHANGE


def is_admin_on_daily_posts_limit_change_state(msg: types.Message) -> bool:
    admin = user_services.create_or_update_user(msg.from_user)
    return admin.state == UserStates.DAILY_POST_LIMIT_CHANGE
