from peewee import *
from config import config
import time


def __get_inheritors(parent):
    """:return list of child classes"""
    subclasses = set()
    for child in parent.__subclasses__():
        subclasses.add(child)
    return subclasses


# Peewee database connection documentation
# http://docs.peewee-orm.com/en/latest/peewee/database.html
db = PostgresqlDatabase(config.DB_NAME, user=config.DB_USER, password=config.DB_PASSWORD,
                        host=config.DB_HOST, port=config.DB_PORT)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    """This data will be automatically created for every user.
    If user changed his data in the Telegram, it will be updated after sending post.
    See: handlers -> posts_handlers -> start_post_creating()"""
    id = BigIntegerField(unique=True, primary_key=True, index=True)
    username = CharField(null=True, unique=True, index=True)
    first_name = CharField()
    last_name = CharField(null=True)
    rating = IntegerField(default=0)
    state = IntegerField(default=0)

    class Meta:
        database = db
        table_name = 'users'


class TargetUser(BaseModel):
    """This model is used to save temp user_id while
    rating change or forwarding message from bot by admin"""
    id = AutoField()
    user_id = BigIntegerField(index=True, unique=True)
    target_id = BigIntegerField()


class Admin(BaseModel):
    id = BigIntegerField(unique=True, primary_key=True, index=True)
    username = CharField(unique=True, null=True)


class ChannelPostsLimit(BaseModel):
    id = AutoField()
    channel_id = BigIntegerField(index=True, unique=True)
    limit = IntegerField(default=2)
    moderating_limit = IntegerField(default=2, verbose_name="posts limit in the moderated channel")


class CustomUserPostsLimit(BaseModel):
    """Defines users posts limit per day in the specific channel.
    You can set unique limit for every user and every channel."""
    id = AutoField()
    user_id = BigIntegerField(index=True)
    channel_id = BigIntegerField()
    posts_limit = IntegerField(default=2)
    moderating_limit = IntegerField(default=2, verbose_name="posts limit in the moderated channel")


class UserSettings(BaseModel):
    """Bot can automatically attach creator name to the post caption.
       Example:
       Very creative post title =)
       by Youta Haruki
    """
    id = BigIntegerField(unique=True, primary_key=True, index=True)
    attaching_username = BooleanField(default=False)
    attaching_fullname = BooleanField(default=False)


class Channel(BaseModel):
    id = BigIntegerField(unique=True, primary_key=True, index=True)
    title = CharField(unique=True)
    link = CharField(default="")
    frozen = BooleanField(default=False)


class MediaTypes:
    photo = "photo"
    album = "album"
    video = "video"
    animation = "animation"


class PostData(BaseModel):
    """Data is received while post creating"""
    id = AutoField()
    creator_id = BigIntegerField(unique=True, index=True)
    channel_id = BigIntegerField()
    type = CharField(null=True)  # one of the MediaTypes
    text = CharField(max_length=4096, default="")
    media_group_id = CharField(null=True)  # only for albums
    forced_moderating = BooleanField(default=False)
    forward_from = CharField(null=True)  # channel title
    forward_caption = CharField(null=True)  # caption of the original post


class PostDataMedia(BaseModel):
    """Photo, video, animation or few photos for album."""
    id = AutoField()
    type = CharField()  # one of the MediaTypes except of album
    post_data_id = ForeignKeyField(PostData, on_delete="CASCADE", backref="media")
    media_id = CharField()


class Post(BaseModel):
    """Post was sent to a channel."""
    id = AutoField()
    creator_id = BigIntegerField(index=True)
    channel_id = BigIntegerField()
    type = CharField()  # one of the MediaTypes
    text = CharField(max_length=4096, default="")
    created_at = TimestampField(default=time.time)


class VoteTypes:
    like = 0
    dislike = 1
    like_text = '👍'
    dislike_text = '👎'

    @staticmethod
    def to_text(vote_type: int):
        type_to_text = {
            VoteTypes.like: VoteTypes.like_text,
            VoteTypes.dislike: VoteTypes.dislike_text
        }
        return type_to_text[vote_type]


class Vote(BaseModel):
    """Users can upvote or downvote posts."""
    id = AutoField()
    user_id = BigIntegerField(index=True)
    channel_id = BigIntegerField()
    post_id = IntegerField(index=True)
    type = IntegerField()  # one of VoteTypes


def init_db():
    db.connect()
    db.create_tables(__get_inheritors(BaseModel))
    Admin.get_or_create(id=config.SUPER_ADMIN_ID, username="superuser")
