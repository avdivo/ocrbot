import asyncio
from functools import partial
from .processes import _worker_load_models, _worker_process_recognition
from concurrent.futures import ProcessPoolExecutor


class OcrService:
    """Сервис для распознавания текста на изображениях
    """
    # Словарь с соответствием языков и кодов для PaddleOCR, а также объектов OCR
    LANG_MAP = {"English": "en", "Русский": "ru"}

    def __init__(self):
        self.lang = 'Русский'  # Язык по умолчанию
        cpu_count = 2  # os.cpu_count() or 2  # Определение количества ядер CPU
        self.executor = ProcessPoolExecutor(max_workers=cpu_count)

        print(f'------------------ Загрузка моделей распознавания для {cpu_count} процессов --------------------')
        # Загрузка занимает много времени, поэтому чтобы не загружать при распознавании
        # делаем это заранее, до начала работы сервиса
        # Инициализация загрузки моделей в каждом процессе
        # futures = [self.executor.submit(_worker_load_models, self.LANG_MAP) for _ in range(cpu_count)]
        self.executor = ProcessPoolExecutor(max_workers=cpu_count, initializer=_worker_load_models,
                                            initargs=(self.LANG_MAP,))

        # for future in futures:
        #     future.result()  # Ожидание завершения загрузки моделей
        print('------------------ Модели загружены --------------------')

    async def recognize_text(self, image_path, lang):
        """Распознавание текста на изображении
        :param image_path: Путь к изображению
        :param lang: Язык распознавания

        :return: Распознанный текст
        """
        try:
            # Распознавание текста на изображении в пуле потоков
            loop = asyncio.get_running_loop()
            text = await loop.run_in_executor(
                self.executor,
                partial(_worker_process_recognition, image_path, lang)
            )
            return text

        except Exception as e:
            print(f"Ошибка при распознавании: {e}")
            return None

    def shutdown_executor(self):
        """Завершение пула процессов"""
        print('------------------ Завершение работы пула процессов --------------------')
        self.executor.shutdown(wait=True)


ocr_service = OcrService()
