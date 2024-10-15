from paddleocr import PaddleOCR

class OCRService:
    def __init__(self):
        self.lang = 'ru'
        self.ocr = None

    async def recognize_text(self, image_path, lang='en'):
        try:
            if not self.ocr or self.lang != lang:
                self.lang = lang
                self.ocr = PaddleOCR(use_angle_cls=True, lang=self.lang)
            print(self.lang, '------------------------------------------')
            result = self.ocr.ocr(image_path, cls=True)

            text_lines = []
            for line in result:
                line_text = " ".join([word_info[1][0] for word_info in line])  # Объединяем слова в строку
                text_lines.append(line_text)  # Добавляем строку в список

            return "\n".join(text_lines)  # Объединяем строки с переносом

        except Exception as e:
            print(f"Error in OCR processing: {e}")
            return None

ocr_service = OCRService()