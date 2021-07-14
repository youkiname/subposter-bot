from models import Admin


class AdminAlreadyExist(Exception):
    pass


def get_or_create(id: int, username: str) -> Admin:
    admin, created = Admin.get_or_create(id=id)
    if not created:
        raise AdminAlreadyExist
    admin.username = username
    admin.save()
    return admin


def get_all():
    return Admin.select()
