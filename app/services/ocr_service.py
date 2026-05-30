from typing import Optional

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


class OcrService:
    """Сервис для OCR-распознавания текста на изображениях.

    Использует Tesseract через pytesseract.
    Выполняет предобработку изображения для улучшения качества распознавания.
    """

    def __init__(self, lang: str = "rus+eng"):
        """Инициализация OCR-сервиса.

        Args:
            lang: Языки для распознавания (по умолчанию русский + английский).
        """
        self._lang = lang
        self._tesseract_available = True

        # Проверяем доступность pytesseract при инициализации
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
        except (ImportError, Exception):
            self._tesseract_available = False

    def recognize_text(self, image_path: str) -> Optional[str]:
        """Запускает Tesseract OCR на изображении.

        Выполняет предобработку изображения:
        - перевод в оттенки серого
        - повышение контраста
        - бинаризация (Otsu)
        - удаление шумов

        Args:
            image_path: Путь к файлу изображения.

        Returns:
            Распознанный текст или None при ошибке.
        """
        if not self._tesseract_available:
            print("[OCR] Tesseract недоступен (не установлен или не в PATH)")
            return None

        try:
            import pytesseract

            # Загрузка изображения
            print(f"[OCR] Загрузка изображения: {image_path}")
            image = Image.open(image_path)
            print(f"[OCR] Изображение загружено: {image.size}, режим: {image.mode}")

            # Предобработка
            print("[OCR] Предобработка изображения...")
            processed = self._preprocess_image(image)
            print(f"[OCR] После предобработки: {processed.size}, режим: {processed.mode}")

            # Распознавание текста
            print(f"[OCR] Запуск Tesseract (lang={self._lang})...")
            text = pytesseract.image_to_string(processed, lang=self._lang)
            print(f"[OCR] Tesseract вернул {len(text)} символов")
            if text.strip():
                print(f"[OCR] Распознанный текст (первые 200 символов): {text.strip()[:200]}")
            else:
                print("[OCR] Tesseract не распознал текст (пустой результат)")

            return text.strip() if text.strip() else None

        except Exception as e:
            print(f"[OCR] ОШИБКА: {type(e).__name__}: {e}")
            return None

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Предобработка изображения для улучшения OCR.

        Args:
            image: Исходное изображение PIL.

        Returns:
            Обработанное изображение.
        """
        # 1. Перевод в оттенки серого
        image = ImageOps.grayscale(image)

        # 2. Повышение контраста
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)

        # 3. Увеличение резкости
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)

        # 4. Бинаризация (адаптивный порог через фильтр)
        image = image.point(lambda x: 255 if x > 128 else 0, mode="1")

        # 5. Удаление шумов (медианный фильтр)
        image = image.filter(ImageFilter.MedianFilter(size=3))

        return image

    @property
    def is_available(self) -> bool:
        """Проверяет доступность Tesseract."""
        return self._tesseract_available