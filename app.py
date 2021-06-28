# -*- coding: utf-8 -*-

from aiohttp import web
from telebot.types import Update

from bot import bot
from config import config

app = web.Application()


# Process webhook calls
async def bot_handle(request):
    request_body_dict = await request.json()
    update = Update.de_json(request_body_dict)
    bot.process_new_updates([update])
    return web.Response()

app.router.add_post(config.WEBHOOK_URL, bot_handle)
