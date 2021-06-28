import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Configuration:
    TOKEN = ""
    WEBHOOK_HOST = '127.0.0.1'
    WEBHOOK_PORT = 5000
    WEBHOOK_URL = "/bot/"
    POLLING_USING = True

    DB_HOST = ""
    DB_PORT = ""
    DB_NAME = ""

    IMAGES_PATH = "./images"
    TEMP_THUMB_PATH = "./thumbs"

    SUPER_ADMIN_ID = None
    EXCEPTION_LOG_CHAT_ID = None
    LOG_CHAT_ID = None

    MODERATED_CHANNEL_ID = None


config = Configuration()
