from telebot.types import Message

from bot import bot
from bot.services import admins as admin_services
from bot.utils import MessageTextSplitter


def try_add_new_admin(msg: Message):
    future_admin = MessageTextSplitter.try_get_user_from_message_text(msg)
    if future_admin is None:
        return
    admin = admin_services.get_or_create(future_admin.id, future_admin.username)
    bot.send_message(msg.chat.id, f"Новый администратор добавлен:\n"
                                  f"{admin.id}: {admin.username}")


def send_admins_list(chat_id: int):
    str_admins_list = ""
    for admin in admin_services.get_all():
        str_admins_list += f"{admin.id}: {admin.username}\n"
    bot.send_message(chat_id, str_admins_list)


def try_delete_admin(msg: Message):
    admin = MessageTextSplitter.try_get_admin_from_message_text(msg)
    if admin is None:
        bot.send_message(msg.chat.id, "Администратор с таким именем не существует.\n"
                                      "/admins - список администраторов")
        return

    bot.send_message(msg.chat.id, f"Администратор с именем {admin.username} успешно удалён.")
    admin.delete_instance()
