from models import Channel


def add_new(channel_id: int, title: str):
    Channel.create(id=channel_id, title=title)


def get_all():
    return Channel.select()
