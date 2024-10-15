import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from config import Config
from bot.handlers import register_handlers
from web.routes import setup_routes

logging.basicConfig(level=logging.INFO)

bot = Bot(token=Config.BOT_TOKEN)
router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)

app = web.Application()

async def on_startup(app):
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != Config.WEBHOOK_URL:
        await bot.set_webhook(Config.WEBHOOK_URL)
    logging.info(f"Webhook set to URL: {Config.WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    await dp.storage.close()

if __name__ == '__main__':
    register_handlers(router)
    setup_routes(app, bot, dp)
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app, host=Config.WEBAPP_HOST, port=Config.WEBAPP_PORT)