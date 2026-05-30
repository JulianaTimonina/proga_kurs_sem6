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
            return None

        try:
            import pytesseract

            # Загрузка изображения
            image = Image.open(image_path)

            # Предобработка
            processed = self._preprocess_image(image)

            # Распознавание текста
            text = pytesseract.image_to_string(processed, lang=self._lang)
            return text.strip() if text.strip() else None

        except Exception:
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