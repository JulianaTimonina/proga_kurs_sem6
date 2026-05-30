import json
import os
import tempfile

import pytest

from app.services.qr_service import QrService


class TestQrService:
    """Тесты для QrService — генерация и удаление QR-кодов."""

    @pytest.fixture
    def temp_dir(self):
        """Создаёт временную директорию для тестов."""
        dir_path = tempfile.mkdtemp()
        yield dir_path
        # Очистка после тестов
        for file in os.listdir(dir_path):
            os.remove(os.path.join(dir_path, file))
        os.rmdir(dir_path)

    @pytest.fixture
    def service(self, temp_dir):
        return QrService(output_dir=temp_dir)

    def test_generate_qr_creates_file(self, service, temp_dir):
        """Проверяет, что создаётся PNG-файл."""
        filepath = service.generate_qr(book_id=1, isbn="9785171234567")
        assert filepath is not None
        assert os.path.exists(filepath)
        assert filepath.endswith(".png")

    def test_generate_qr_with_isbn(self, service, temp_dir):
        """Проверяет генерацию QR с ISBN."""
        filepath = service.generate_qr(book_id=1, isbn="9785171234567")
        assert filepath is not None
        assert os.path.exists(filepath)

    def test_generate_qr_without_isbn(self, service, temp_dir):
        """Проверяет генерацию QR с null ISBN."""
        filepath = service.generate_qr(book_id=1, isbn=None)
        assert filepath is not None
        assert os.path.exists(filepath)

    def test_generate_qr_content(self, service, temp_dir):
        """Проверяет содержимое QR-кода (декодировать и проверить JSON)."""
        filepath = service.generate_qr(book_id=42, isbn="978-5-17-123456-7")
        assert filepath is not None

        # Декодируем QR-код
        try:
            from pyzbar.pyzbar import decode
            from PIL import Image

            img = Image.open(filepath)
            decoded = decode(img)
            assert len(decoded) > 0

            data = json.loads(decoded[0].data.decode("utf-8"))
            assert data["id"] == 42
            assert data["isbn"] == "978-5-17-123456-7"
        except ImportError:
            # Если pyzbar не установлен, пропускаем проверку содержимого
            # Проверяем хотя бы, что файл создан и не пустой
            assert os.path.getsize(filepath) > 0

    def test_generate_qr_content_without_isbn(self, service, temp_dir):
        """Проверяет содержимое QR с null ISBN."""
        filepath = service.generate_qr(book_id=5, isbn=None)
        assert filepath is not None

        try:
            from pyzbar.pyzbar import decode
            from PIL import Image

            img = Image.open(filepath)
            decoded = decode(img)
            assert len(decoded) > 0

            data = json.loads(decoded[0].data.decode("utf-8"))
            assert data["id"] == 5
            assert data["isbn"] is None
        except ImportError:
            assert os.path.getsize(filepath) > 0

    def test_generate_qr_filename_format(self, service, temp_dir):
        """Проверяет формат имени файла."""
        filepath = service.generate_qr(book_id=123, isbn="9785171234567")
        assert filepath is not None
        filename = os.path.basename(filepath)
        assert filename == "qr_book_123.png"

    def test_generate_qr_custom_output_dir(self, service):
        """Проверяет генерацию QR с переопределением директории."""
        with tempfile.TemporaryDirectory() as custom_dir:
            filepath = service.generate_qr(
                book_id=1, isbn="9785171234567", output_dir=custom_dir
            )
            assert filepath is not None
            assert os.path.exists(filepath)
            assert custom_dir in filepath

    def test_delete_qr_removes_file(self, service, temp_dir):
        """Проверяет удаление файла QR-кода."""
        filepath = service.generate_qr(book_id=1, isbn="9785171234567")
        assert os.path.exists(filepath)

        service.delete_qr(filepath)
        assert not os.path.exists(filepath)

    def test_delete_qr_nonexistent_file(self, service):
        """Проверяет удаление несуществующего файла (не должно вызывать ошибок)."""
        service.delete_qr("/nonexistent/path/qr.png")  # не должно быть исключения

    def test_delete_qr_empty_path(self, service):
        """Проверяет удаление с пустым путём."""
        service.delete_qr("")  # не должно быть исключения

    def test_delete_qr_none_path(self, service):
        """Проверяет удаление с None."""
        service.delete_qr(None)  # не должно быть исключения

    def test_generate_multiple_qrs(self, service, temp_dir):
        """Проверяет генерацию нескольких QR-кодов."""
        path1 = service.generate_qr(book_id=1, isbn="9785171234567")
        path2 = service.generate_qr(book_id=2, isbn="9785046543210")
        path3 = service.generate_qr(book_id=3, isbn=None)

        assert all(p is not None for p in [path1, path2, path3])
        assert all(os.path.exists(p) for p in [path1, path2, path3])

        files = os.listdir(temp_dir)
        assert len(files) == 3