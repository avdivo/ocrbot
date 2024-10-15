from paddleocr import PaddleOCR


class OCRService:
    """Сервис для распознавания текста на изображениях
    """
    def __init__(self):
        self.lang = 'ru'  # Язык по умолчанию
        self.ocr = None  # Объект OCR

    async def recognize_text(self, image_path, lang='ru'):
        """Распознавание текста на изображении
        :param image_path: Путь к изображению
        :param lang: Язык распознавания

        :return: Распознанный текст
        """
        try:
            if not self.ocr or self.lang != lang:
                # Если объект OCR не создан или язык изменился
                self.lang = lang
                self.ocr = PaddleOCR(use_angle_cls=True, lang=self.lang)
            result = self.ocr.ocr(image_path, cls=True)

            # Преобразуем результат в текст
            text_lines = []
            for line in result:
                line_text = " ".join([word_info[1][0] for word_info in line])  # Объединяем слова в строку
                text_lines.append(line_text)  # Добавляем строку в список

            return "\n".join(text_lines)  # Объединяем строки с переносом

        except Exception as e:
            print(f"Error in OCR processing: {e}")
            return None


ocr_service = OCRService()  # Создаем экземпляр сервиса
