import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Configuration:
    TOKEN = ""
    WEBHOOK_HOST = '127.0.0.1'
    WEBHOOK_PORT = 5000
    WEBHOOK_URL = "/bot/"
    POLLING_USING = True

    # DB_DRIVER = 'sqlite' or 'postgres'.
    # Sqlite requires only DB_NAME. Postgres requires all fields below.
    # You also can use MySQL and CockroachDB with customizing models/__init__.py
    DB_DRIVER = "sqlite"
    DB_HOST = ""
    DB_PORT = ""
    DB_NAME = ""
    DB_USER = ""
    DB_PASSWORD = ""

    SUPER_ADMIN_ID = None
    EXCEPTION_LOG_CHAT_ID = None

    MODERATED_CHANNEL_ID = None


config = Configuration()
