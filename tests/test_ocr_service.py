"""Тесты для OcrService — OCR-распознавание текста.

Используют моки для pytesseract и PIL.Image, чтобы не требовать
реального Tesseract OCR и файлов изображений.
"""

import sys
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from app.services.ocr_service import OcrService


class TestOcrService:
    """Тесты для OcrService."""

    @pytest.fixture
    def mock_image(self):
        """Создаёт реальное PIL Image для тестов предобработки."""
        return Image.new("RGB", (100, 50), color="white")

    @pytest.fixture
    def service(self):
        """Создаёт OcrService с принудительно доступным Tesseract."""
        svc = OcrService()
        svc._tesseract_available = True
        return svc

    @pytest.fixture
    def service_unavailable(self):
        """Создаёт OcrService с недоступным Tesseract."""
        svc = OcrService()
        svc._tesseract_available = False
        return svc

    # --- recognize_text ---

    def _patch_pytesseract(self):
        """Подменяет модуль pytesseract в sys.modules для тестов recognize_text.

        pytesseract импортируется внутри метода recognize_text() через
        'import pytesseract', поэтому стандартный patch не работает.
        Используем patch.dict для подмены в sys.modules.
        """
        mock_module = MagicMock()
        return patch.dict("sys.modules", {"pytesseract": mock_module})

    @patch("app.services.ocr_service.Image.open")
    def test_recognize_text_success(self, mock_image_open, service):
        """Успешное распознавание текста."""
        mock_image_open.return_value = Image.new("RGB", (10, 10))
        with self._patch_pytesseract() as sys_modules:
            mock_pytesseract = sys_modules["pytesseract"]
            mock_pytesseract.image_to_string.return_value = "ISBN 978-5-17-123456-7"

            result = service.recognize_text("/path/image.jpg")

        mock_image_open.assert_called_once_with("/path/image.jpg")
        assert result == "ISBN 978-5-17-123456-7"

    @patch("app.services.ocr_service.Image.open")
    def test_recognize_text_empty_result(self, mock_image_open, service):
        """Tesseract вернул пустую строку — должен вернуть None."""
        mock_image_open.return_value = Image.new("RGB", (10, 10))
        with self._patch_pytesseract() as sys_modules:
            mock_pytesseract = sys_modules["pytesseract"]
            mock_pytesseract.image_to_string.return_value = ""

            result = service.recognize_text("/path/image.jpg")

        assert result is None

    @patch("app.services.ocr_service.Image.open")
    def test_recognize_text_whitespace_result(self, mock_image_open, service):
        """Tesseract вернул только пробелы — должен вернуть None."""
        mock_image_open.return_value = Image.new("RGB", (10, 10))
        with self._patch_pytesseract() as sys_modules:
            mock_pytesseract = sys_modules["pytesseract"]
            mock_pytesseract.image_to_string.return_value = "   \n  \t  "

            result = service.recognize_text("/path/image.jpg")

        assert result is None

    def test_recognize_text_tesseract_unavailable(self, service_unavailable):
        """Tesseract недоступен — должен вернуть None."""
        result = service_unavailable.recognize_text("/path/image.jpg")
        assert result is None

    @patch("app.services.ocr_service.Image.open")
    def test_recognize_text_image_error(self, mock_image_open, service):
        """Ошибка загрузки изображения — должен вернуть None."""
        mock_image_open.side_effect = FileNotFoundError("File not found")

        result = service.recognize_text("/nonexistent/image.jpg")

        assert result is None

    @patch("app.services.ocr_service.Image.open")
    def test_recognize_text_tesseract_error(self, mock_image_open, service):
        """Ошибка Tesseract — должен вернуть None."""
        mock_image_open.return_value = Image.new("RGB", (10, 10))
        with self._patch_pytesseract() as sys_modules:
            mock_pytesseract = sys_modules["pytesseract"]
            mock_pytesseract.image_to_string.side_effect = RuntimeError("Tesseract crashed")

            result = service.recognize_text("/path/image.jpg")

        assert result is None

    # --- _preprocess_image ---

    def test_preprocess_image_returns_image(self, service, mock_image):
        """Проверяет, что _preprocess_image возвращает объект Image."""
        result = service._preprocess_image(mock_image)
        assert isinstance(result, Image.Image)

    def test_preprocess_image_grayscale(self, service, mock_image):
        """Проверяет, что изображение переводится в оттенки серого."""
        result = service._preprocess_image(mock_image)
        # Режим 'L' (Luminance) или '1' (binary) после обработки
        assert result.mode in ("L", "1")

    def test_preprocess_image_binarized(self, service, mock_image):
        """Проверяет, что изображение после бинаризации имеет только 2 цвета."""
        result = service._preprocess_image(mock_image)
        # После point(lambda x: 255 if x > 128 else 0, mode='1') режим будет '1'
        assert result.mode == "1"

    # --- is_available ---

    def test_is_available_true(self, service):
        """Проверяет is_available когда Tesseract доступен."""
        assert service.is_available is True

    def test_is_available_false(self, service_unavailable):
        """Проверяет is_available когда Tesseract недоступен."""
        assert service_unavailable.is_available is False