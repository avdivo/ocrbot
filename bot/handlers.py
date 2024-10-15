import os
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from services.ocr_service import ocr_service
from bot.states import UserState


async def start_command(message: types.Message):
    await message.reply(
        "Привет! Я бот для распознавания текста на изображениях. Отправь мне изображение, и я попробую распознать текст.")


async def help_command(message: types.Message):
    help_text = """
    Доступные команды:
    /start - Начать работу с ботом
    /help - Показать это сообщение
    /language - Выбрать язык распознавания

    Просто отправьте мне изображение, и я попробую распознать на нем текст.
    """
    await message.reply(help_text)


async def language_command(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="English"),
             types.KeyboardButton(text="Русский"),
             types.KeyboardButton(text="中文")]
        ],
        resize_keyboard=True
    )
    await message.reply("Выберите язык для распознавания:", reply_markup=keyboard)
    await state.set_state(UserState.waiting_for_language)  # Установка состояния


async def process_language_selection(message: types.Message, state: FSMContext):
    language = message.text.lower()
    lang_map = {"english": "en", "русский": "ru", "中文": "ch"}

    if language in lang_map:
        await state.clear()
        await state.update_data(language=lang_map[language])
        await message.reply(f"Язык распознавания установлен: {message.text}", reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.reply("Пожалуйста, выберите язык из предложенных вариантов.")


async def process_image(message: types.Message, state: FSMContext):
    if message.photo:
        user_data = await state.get_data()
        lang = user_data.get('language', 'ru')

        file_id = message.photo[-1].file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path

        download_path = f"temp_{message.from_user.id}.jpg"
        await message.bot.download_file(file_path, destination=download_path)

        text = await ocr_service.recognize_text(download_path, lang)

        if text:
            await message.reply(f"Язык распознавания {lang}\nРаспознанный текст:\n\n{text}")
        else:
            await message.reply("Не удалось распознать текст на изображении.")

        os.remove(download_path)
    else:
        await message.reply("Пожалуйста, отправьте изображение.")


def register_handlers(router):
    router.message.register(start_command, Command(commands=['start']))
    router.message.register(help_command, Command(commands=['help']))
    router.message.register(language_command, Command(commands=['language']))
    router.message.register(process_language_selection, StateFilter(UserState.waiting_for_language))
    router.message.register(process_image, F.content_type == 'photo')
