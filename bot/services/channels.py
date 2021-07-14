from models import Channel, ChannelPostsLimit


def add_new(channel_id: int, title: str):
    Channel.create(id=channel_id, title=title)


def get_by_title(title: str) -> Channel or None:
    return Channel.get_or_none(Channel.title == title)


def get_all():
    return Channel.select()


def get_channels_amount() -> int:
    return Channel.select().count()


def get_or_create_post_limit(channel_id: int) -> ChannelPostsLimit:
    posts_limit, created = ChannelPostsLimit.get_or_create(channel_id=channel_id)
    return posts_limit


def delete_if_exist(channel_id: int):
    channel = Channel.get_or_none(Channel.id == channel_id)
    if channel is not None:
        channel.delete_instance()
    channel_posts_limit = ChannelPostsLimit.get_or_none(ChannelPostsLimit.channel_id == channel_id)
    if channel_posts_limit is not None:
        channel_posts_limit.delete_instance()
