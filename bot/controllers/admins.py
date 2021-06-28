from bot import bot
from telebot.types import Message
from models import Admin, User


def try_add_new_admin(msg: Message):
    new_admin_username = msg.text.split(' ', 1)[1]
    existed_user = User.get_or_none(User.username == new_admin_username)
    if existed_user is None:
        bot.send_message(msg.chat.id, "Пользователя с таким именем не существует")
        return

    admin, created = Admin.get_or_create(id=existed_user.id)
    if created:
        admin.username = new_admin_username
        admin.save()
        bot.send_message(msg.chat.id, f"Новый администратор добавлен:\n"
                                      f"{admin.id}: {admin.username}")
        return
    bot.send_message(msg.chat.id, f"Администратор с этим ID уже существует:\n"
                                  f"{admin.id}: {admin.username}")


def send_admins_list(chat_id: int):
    str_admins_list = ""
    for admin in Admin.select():
        str_admins_list += f"{admin.id}: {admin.username}\n"
    bot.send_message(chat_id, str_admins_list)


def try_remove_admin(msg: Message):
    admin_username = msg.text.split(' ', 1)[1]
    existed_admin = Admin.get_or_none(Admin.username == admin_username)
    if existed_admin is None:
        bot.send_message(msg.chat.id, "Администратор с таким именем не существует.\n"
                                      "/admins - список администраторов")
        return
    existed_admin.delete_instance()
    bot.send_message(msg.chat.id, f"Администратор с именем {admin_username} успешно удалён.")
