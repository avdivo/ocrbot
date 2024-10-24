import logging
import asyncio
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request

from config import Config
from bot.handlers import register_handlers
from services.ocr_service import ocr_service

logging.basicConfig(level=logging.INFO)  # Лог файл не создается, логи выводятся в консоль

bot = Bot(token=Config.BOT_TOKEN)
router = Router()
register_handlers(router)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    """Установка вебхука при запуске приложения"""
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != Config.WEBHOOK_URL:
        await bot.set_webhook(Config.WEBHOOK_URL)
    logging.info(f"Webhook set to URL: {Config.WEBHOOK_URL}")


@app.on_event("shutdown")
async def on_shutdown():
    """Удаление вебхука и закрытие хранилища при завершении работы приложения"""
    await bot.delete_webhook()
    await dp.storage.close()
    ocr_service.shutdown_executor()  # Завершение пула процессов


# Обработка вебхуков
@app.post(Config.WEBHOOK_PATH)
async def webhook_handler(request: Request):
    """Обработка запросов. Передача боту.
    """
    update_data = await request.json()  # Получение данных из запроса
    update = Update(**update_data)  # Создание объекта обновления
    asyncio.create_task(dp.feed_update(bot, update))  # Передача обновления боту
    return JSONResponse(content={})  # Возвращение пустого ответа


if __name__ == "__main__":
    app = FastAPI()
