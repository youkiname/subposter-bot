from web_app import web, app
from bot import bot
from config import config
import logging
from models import init_db


logging.basicConfig(level=logging.INFO)


if __name__ == '__main__':
    init_db()
    if config.POLLING_USING:
        bot.polling()
    else:
        web.run_app(
            app,
            host=config.WEBHOOK_HOST,
            port=config.WEBHOOK_PORT,
        )
