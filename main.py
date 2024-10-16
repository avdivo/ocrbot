import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI, Request
from config import Config
from bot.handlers import register_handlers

logging.basicConfig(level=logging.INFO)  # Лог файл не создается, логи выводятся в консоль

bot = Bot(token=Config.BOT_TOKEN)
router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)

app = FastAPI()


@app.on_event("startup")
async def on_startup(app):
    """Установка вебхука при запуске приложения"""
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != Config.WEBHOOK_URL:
        await bot.set_webhook(Config.WEBHOOK_URL)
    app.state.bot = bot  # Сохранение объекта бота в состоянии приложения
    app.state.dp = dp  # Сохранение объекта диспетчера в состоянии приложения
    logging.info(f"Webhook set to URL: {Config.WEBHOOK_URL}")


@app.on_event("shutdown")
async def on_shutdown():
    """Удаление вебхука и закрытие хранилища при завершении работы приложения"""
    await bot.delete_webhook()
    await dp.storage.close()


register_handlers(router)
