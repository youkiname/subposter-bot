from telebot.types import Message
from bot.services import users as user_services
from bot.services import posts as post_services
from bot import bot
from bot.controllers import keyboards


def process_cancel(msg: Message):
    user_services.clear_state_by_id(msg.from_user.id)
    post_services.delete_temp_post_data(msg.from_user.id)
    bot.send_message(msg.chat.id, "Отменил всё, что можно", reply_markup=keyboards.get_main_keyboard())
