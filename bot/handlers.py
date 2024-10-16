import os
from datetime import datetime
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from services.ocr_service import ocr_service
from bot.states import UserState


async def show_main_menu(message: types.Message, state: FSMContext):
    """Отображение главного меню
    :param message:
    :param state:
    :return:
    """
    user_data = await state.get_data()  # Получение данных пользователя из состояния
    current_language = user_data.get('language', 'ru')  # Значение по умолчанию

    # Создание клавиатуры
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(text=f"Сменить язык ({current_language})"),
                types.KeyboardButton(text="Посмотреть историю"),
            ]
        ],
        resize_keyboard=True
    )

    await message.reply("Отправьте изображение или выберите опцию:", reply_markup=keyboard)


async def handle_main_menu(message: types.Message, state: FSMContext):
    """Обработка нажатий на кнопки главного меню
    :param message:
    :param state:
    :return
    """
    if message.text == "Посмотреть историю":
        # Читаем файл с именем по id пользователя и отправляем содержимое пользователю
        bot = message.bot  # Получение объекта бота из сообщения
        user_id = message.from_user.id  # Получение ID пользователя
        path = os.path.join("data", "recognized_texts", f"{user_id}.txt")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
                await message.reply(f"История распознанных текстов:\n")

                # Отправка текста частями, если он слишком длинный
                max_length = 4096
                for i in range(0, len(text), max_length):
                    message_chunk = text[i:i + max_length]
                    await bot.send_message(message.chat.id, message_chunk)  # Отправка без вопроса
        except FileNotFoundError:
            await message.reply("История пуста.")

    elif message.text.startswith("Сменить язык"):
        await language_command(message, state)  # Переход к выбору языка


async def start_command(message: types.Message, state: FSMContext):
    """Обработка команды /start"""
    await state.clear()  # Сброс состояния при старте
    await message.reply("Добро пожаловать!")
    await show_main_menu(message, state)  # Отображение главного меню


async def help_command(message: types.Message):
    """Обработка команды /help"""
    help_text = """
    Доступные команды:
    /start - Начать работу с ботом
    /help - Показать это сообщение
    /language - Выбрать язык распознавания

    Просто отправьте мне изображение, и я попробую распознать на нем текст.
    """
    await message.reply(help_text)


async def language_command(message: types.Message, state: FSMContext):
    """Обработка команды /language. Вывод клавиатуры для выбора языка
        и установка состояния ожидания выбора языка
    :param message:
    :param state:
    :return:
    """
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
    """Обработка выбора языка и установка его в данных пользователя
    :param message:
    :param state:
    :return
    """
    if not message.text:
        return

    language = message.text.lower()
    lang_map = {"english": "en", "русский": "ru"}

    if language in lang_map:
        # Сохранение выбранного языка в данных пользователя
        await state.clear()
        await state.update_data(language=lang_map[language])
        await message.reply(f"Язык распознавания установлен: {message.text}", reply_markup=types.ReplyKeyboardRemove())
        await show_main_menu(message, state)  # Вернуть главное меню после выбора языка
    else:
        await message.reply("Пожалуйста, выберите язык из предложенных вариантов.")


async def process_image(message: types.Message, state: FSMContext):
    """Обработка отправленного изображения и попытка распознавания текста
    :param message:
    :param state:
    :return:
    """
    if message.photo:
        # Получение данных пользователя из состояния
        user_data = await state.get_data()
        lang = user_data.get('language', 'ru')

        # Получение пути к файлу изображения и его загрузка
        file_id = message.photo[-1].file_id
        file = await message.bot.get_file(file_id)
        file_path = file.file_path

        download_path = f"temp_{message.from_user.id}.jpg"
        await message.bot.download_file(file_path, destination=download_path)

        # Распознавание текста на изображении
        text = await ocr_service.recognize_text(download_path, lang)

        if text:
            # Отправка распознанного текста пользователю
            await message.reply(f"Язык распознавания {lang}\nРаспознанный текст:\n\n{text}")

            # Сохранение распознанного текста в файл с именем, соответствующим ID пользователя
            # Перед ним строка с текущей датой, временем и языком распознавания
            insert = f"\n\nДата и время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nЯзык: {lang}\n"
            path = os.path.join("data", "recognized_texts", f"{message.from_user.id}.txt")
            with open(path, 'a', encoding='utf-8') as f:
                f.write(insert + text)

        else:
            await message.reply("Не удалось распознать текст на изображении.")

        os.remove(download_path)  # Удаление временного файла
    else:
        await message.reply("Пожалуйста, отправьте изображение.")


def register_handlers(router):
    """Регистрация обработчиков сообщений
    :param router:
    :return:
    """
    router.message.register(start_command, Command(commands=['start']))
    router.message.register(help_command, Command(commands=['help']))
    router.message.register(language_command, Command(commands=['language']))
    router.message.register(process_language_selection, StateFilter(UserState.waiting_for_language))  # Фильтр по состоянию
    router.message.register(process_image, F.content_type == 'photo')
    router.message.register(handle_main_menu, F.text.in_(["Выбрать фото", F.text.startswith("Сменить язык")]))
