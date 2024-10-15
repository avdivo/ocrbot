from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from config import Config


async def webhook_handler(request):
    """Обработка запросов. Передача боту.
    """
    bot = request.app['bot']
    dispatcher = request.app['dispatcher']

    update = await request.json()  # Получение данных из запроса
    update = Update(**update)  # Создание объекта Update
    await dispatcher.feed_update(bot, update)  # Передача обновления диспетчеру
    return web.Response()  # Возвращаем пустой ответ


def setup_routes(app: web.Application, bot: Bot, dp: Dispatcher):
    """Установка маршрутов для веб-приложения.
    """
    app['bot'] = bot
    app['dispatcher'] = dp
    app.router.add_post(Config.WEBHOOK_PATH, webhook_handler)  # Установка обработчика POST запросов
