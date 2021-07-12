from telebot import types
from models import Channel, UserSettings
from bot.callbacks import CallbackCommands
from models import VoteTypes


def get_main_keyboard() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('Создать пост'),
        types.KeyboardButton('Инфо'),
        types.KeyboardButton('Профиль'),
        types.KeyboardButton('Отмена'),
    )
    return markup


def get_cancel() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton('Отмена')
    )
    return markup


def get_channels() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    for channel in Channel.select():
        if not channel.frozen:
            markup.add(
                types.KeyboardButton(channel.title)
            )
    markup.add(types.KeyboardButton('Отмена'))
    return markup


def get_for_post_creating() -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton('Превью'),
        types.KeyboardButton('Отправить'),
        types.KeyboardButton('Отмена')
    )
    return markup


def get_user_settings_keyboard(current_settings: UserSettings) -> types.InlineKeyboardMarkup:
    display_name_text = "Отображать имя: {}".format("ДА" if current_settings.attaching_fullname else "НЕТ")
    display_username_text = "Отображать юзернейм: {}".format("ДА" if current_settings.attaching_username else "НЕТ")
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(display_name_text, callback_data=str(CallbackCommands.SET_SHOW_NAME)),
        types.InlineKeyboardButton(display_username_text, callback_data=str(CallbackCommands.SET_SHOW_USERNAME))
    )
    return keyboard


def get_post_keyboard(likes_count=0, dislikes_count=0):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(f"{VoteTypes.like_text} {likes_count}", callback_data=str(CallbackCommands.POST_LIKE)),
        types.InlineKeyboardButton(f"{VoteTypes.dislike_text} {dislikes_count}", callback_data=str(CallbackCommands.POST_DISLIKE))
    )
    return keyboard
