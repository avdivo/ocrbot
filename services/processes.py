# Воркеры для процессов распознавания текста

import os
from paddleocr import PaddleOCR

OCR_OBJECTS = None


def _worker_load_models(lang_map):
    """Загрузка моделей OCR в каждом процессе и сохранение их в глобальной переменной
    :param lang_map: Словарь языков для загрузки моделей
    """
    try:
        print(f"Загрузка {len(lang_map)} моделей OCR в PID {os.getpid()}")
        print(f"Языки для загрузки: {' ,'.join(lang_map.keys())}")
        global OCR_OBJECTS
        OCR_OBJECTS = {}
        for lang, lang_code in lang_map.items():
            OCR_OBJECTS[lang] = PaddleOCR(use_angle_cls=True, lang=lang_code)
        import time
        time.sleep(10)
    except Exception as e:
        print(f"Ошибка при загрузке модели: {e}")
        raise

def _worker_process_recognition(image_path, lang) -> str:
    """Выполнение распознавания в отдельном процессе
    :param image_path: Путь к изображению
    :param lang: Язык для распознавания

    :return: Результат OCR в виде текста
    """
    if lang not in OCR_OBJECTS:
        raise ValueError("Модель OCR не загружена для указанного языка")

    try:
        ocr = OCR_OBJECTS[lang]
        result = ocr.ocr(image_path, True)

        # Преобразуем результат в текст
        text_lines = []
        for line in result:
            line_text = " ".join([word_info[1][0] for word_info in line])  # Объединяем слова в строку
            text_lines.append(line_text)  # Добавляем строку в список
    except Exception as e:
        print(f"Ошибка распознавания: {e}")
        raise

    return "\n".join(text_lines)  # Объединяем строки с переносом
