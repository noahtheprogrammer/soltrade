import asyncio
import telegram
from soltrade.config import config
from telegram.ext import ApplicationBuilder

# bot_token = config().tg_bot_token
# chat = config().tg_bot_uid

async def send_info(msg):
    bot_token = config().tg_bot_token
    chat = config().tg_bot_uid
    application = ApplicationBuilder().token(bot_token).build()
    await application.bot.sendMessage(chat_id=chat, text=msg, parse_mode="HTML")
