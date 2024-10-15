import os
from datetime import datetime
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from services.ocr_service import ocr_service
from bot.states import UserState


async def show_main_menu(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    current_language = user_data.get('language', 'ru')  # Значение по умолчанию

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Выбрать фото"),
             types.KeyboardButton(text=f"Сменить язык ({current_language})"),
            ]
        ],
        resize_keyboard=True
    )

    await message.reply("Добро пожаловать! Выберите опцию:", reply_markup=keyboard)


async def handle_main_menu(message: types.Message, state: FSMContext):
    if message.text == "Выбрать фото":
        await message.reply("Пожалуйста, отправьте изображение.")
    elif message.text.startswith("Сменить язык"):
        await language_command(message, state)


async def start_command(message: types.Message, state: FSMContext):
    await state.clear()  # Сброс состояния при старте
    await show_main_menu(message, state)


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
            ]
        ],
        resize_keyboard=True
    )
    await message.reply("Выберите язык для распознавания:", reply_markup=keyboard)
    await state.set_state(UserState.waiting_for_language)  # Установка состояния


async def process_language_selection(message: types.Message, state: FSMContext):
    language = message.text.lower()
    lang_map = {"english": "en", "русский": "ru"}

    if language in lang_map:
        await state.clear()
        await state.update_data(language=lang_map[language])
        await message.reply(f"Язык распознавания установлен: {message.text}", reply_markup=types.ReplyKeyboardRemove())
        await show_main_menu(message, state)  # Вернуть главное меню после выбора языка
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

            # Сохранение распознанного текста в файл с именем, соответствующим ID пользователя
            # Перед ним строка с текущей датой и временем и языком распознавания
            insert = f"\n\nДата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nЯзык: {lang}\n"
            path = os.path.join("data", "recognized_texts", f"{message.from_user.id}.txt")
            with open(path, 'a', encoding='utf-8') as f:
                f.write(insert + text)

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
    router.message.register(handle_main_menu, F.text.in_(["Выбрать фото", F.text.startswith("Сменить язык")]))
