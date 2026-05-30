"""Интеграционные тесты для контроллеров.

Проверяют взаимодействие контроллеров с сервисами через моки.
"""

from unittest.mock import MagicMock, patch

import pytest
from PyQt5.QtWidgets import QMessageBox

from app.controllers.book_controller import BookController
from app.controllers.catalog_controller import CatalogController
from app.models.book import Book


class TestCatalogController:
    """Тесты для CatalogController."""

    @pytest.fixture
    def mock_book_service(self):
        return MagicMock()

    @pytest.fixture
    def controller(self, mock_book_service):
        return CatalogController(mock_book_service)

    # --- load_catalog ---

    def test_load_catalog(self, controller, mock_book_service):
        """Проверяет загрузку всех книг."""
        expected_books = [MagicMock(spec=Book), MagicMock(spec=Book)]
        mock_book_service.get_all_books.return_value = expected_books

        result = controller.load_catalog()

        mock_book_service.get_all_books.assert_called_once()
        assert result == expected_books

    def test_load_catalog_empty(self, controller, mock_book_service):
        """Проверяет загрузку пустого каталога."""
        mock_book_service.get_all_books.return_value = []

        result = controller.load_catalog()

        assert result == []

    # --- search ---

    def test_search_with_query(self, controller, mock_book_service):
        """Проверяет поиск с непустым запросом."""
        expected_books = [MagicMock(spec=Book)]
        mock_book_service.search_books.return_value = expected_books

        result = controller.search("Толстой")

        mock_book_service.search_books.assert_called_once_with("Толстой")
        assert result == expected_books

    def test_search_empty_query(self, controller, mock_book_service):
        """Проверяет поиск с пустым запросом — возвращает все книги."""
        expected_books = [MagicMock(spec=Book)]
        mock_book_service.get_all_books.return_value = expected_books

        result = controller.search("")

        mock_book_service.get_all_books.assert_called_once()
        mock_book_service.search_books.assert_not_called()
        assert result == expected_books

    def test_search_whitespace_query(self, controller, mock_book_service):
        """Проверяет поиск с запросом из пробелов."""
        expected_books = [MagicMock(spec=Book)]
        mock_book_service.get_all_books.return_value = expected_books

        result = controller.search("   ")

        mock_book_service.get_all_books.assert_called_once()
        mock_book_service.search_books.assert_not_called()

    # --- apply_filters ---

    def test_apply_filters_all_params(self, controller, mock_book_service):
        """Проверяет фильтрацию со всеми параметрами."""
        expected_books = [MagicMock(spec=Book)]
        mock_book_service.filter_books.return_value = expected_books

        result = controller.apply_filters(year=2023, udc="821", bbk="84")

        mock_book_service.filter_books.assert_called_once_with(
            year=2023, udc="821", bbk="84"
        )
        assert result == expected_books

    def test_apply_filters_no_params(self, controller, mock_book_service):
        """Проверяет фильтрацию без параметров."""
        expected_books = [MagicMock(spec=Book)]
        mock_book_service.filter_books.return_value = expected_books

        result = controller.apply_filters()

        mock_book_service.filter_books.assert_called_once_with(
            year=None, udc=None, bbk=None
        )

    def test_apply_filters_empty_strings(self, controller, mock_book_service):
        """Проверяет фильтрацию с пустыми строками — преобразует в None."""
        expected_books = [MagicMock(spec=Book)]
        mock_book_service.filter_books.return_value = expected_books

        result = controller.apply_filters(year=2023, udc="", bbk="")

        mock_book_service.filter_books.assert_called_once_with(
            year=2023, udc=None, bbk=None
        )

    # --- delete_book ---

    def test_delete_book_success(self, controller, mock_book_service):
        """Проверяет успешное удаление книги (с подтверждением)."""
        book = Book(id=1, author="Автор", title="Книга")
        mock_book_service.get_book.return_value = book

        with patch(
            'app.controllers.catalog_controller.QMessageBox.question',
            return_value=QMessageBox.Yes,
        ):
            result = controller.delete_book(1)

            assert result is True
            mock_book_service.delete_book.assert_called_once_with(1)

    def test_delete_book_not_found(self, controller, mock_book_service):
        """Проверяет удаление несуществующей книги."""
        mock_book_service.get_book.return_value = None

        result = controller.delete_book(999)

        assert result is False
        mock_book_service.delete_book.assert_not_called()

    def test_delete_book_cancelled(self, controller, mock_book_service):
        """Проверяет отмену удаления пользователем."""
        book = Book(id=1, author="Автор", title="Книга")
        mock_book_service.get_book.return_value = book

        with patch(
            'app.controllers.catalog_controller.QMessageBox.question',
            return_value=QMessageBox.No,
        ):
            result = controller.delete_book(1)

            assert result is False
            mock_book_service.delete_book.assert_not_called()

    def test_delete_book_error(self, controller, mock_book_service):
        """Проверяет ошибку при удалении."""
        book = Book(id=1, author="Автор", title="Книга")
        mock_book_service.get_book.return_value = book
        mock_book_service.delete_book.side_effect = Exception("DB error")

        with patch(
            'app.controllers.catalog_controller.QMessageBox.question',
            return_value=QMessageBox.Yes,
        ):
            with patch('app.controllers.catalog_controller.QMessageBox.critical'):
                result = controller.delete_book(1)

                assert result is False
                mock_book_service.delete_book.assert_called_once_with(1)


class TestBookController:
    """Тесты для BookController."""

    @pytest.fixture
    def mock_book_service(self):
        return MagicMock()

    @pytest.fixture
    def controller(self, mock_book_service):
        return BookController(mock_book_service)

    @pytest.fixture
    def sample_book(self):
        return Book(
            author="Лев Толстой",
            title="Война и мир",
            isbn="9785171234567",
            publisher="АСТ",
            year=2023,
        )

    # --- get_book ---

    def test_get_book(self, controller, mock_book_service):
        """Проверяет получение книги по ID."""
        expected_book = MagicMock(spec=Book)
        mock_book_service.get_book.return_value = expected_book

        result = controller.get_book(1)

        mock_book_service.get_book.assert_called_once_with(1)
        assert result == expected_book

    def test_get_book_not_found(self, controller, mock_book_service):
        """Проверяет получение несуществующей книги."""
        mock_book_service.get_book.return_value = None

        result = controller.get_book(999)

        assert result is None

    # --- save_book ---

    def test_save_book(self, controller, mock_book_service, sample_book):
        """Проверяет сохранение новой книги."""
        mock_book_service.create_book.return_value = 1

        book_id = controller.save_book(sample_book)

        mock_book_service.create_book.assert_called_once_with(sample_book)
        assert book_id == 1

    def test_save_book_validation_error(self, controller, mock_book_service, sample_book):
        """Проверяет ошибку валидации при сохранении."""
        mock_book_service.create_book.side_effect = ValueError("Автор не может быть пустым")

        with pytest.raises(ValueError, match="Автор не может быть пустым"):
            controller.save_book(sample_book)

    # --- update_book ---

    def test_update_book(self, controller, mock_book_service, sample_book):
        """Проверяет обновление книги."""
        sample_book.id = 1
        controller.update_book(sample_book)

        mock_book_service.update_book.assert_called_once_with(sample_book)

    def test_update_book_validation_error(self, controller, mock_book_service, sample_book):
        """Проверяет ошибку валидации при обновлении."""
        mock_book_service.update_book.side_effect = ValueError("Название не может быть пустым")

        with pytest.raises(ValueError, match="Название не может быть пустым"):
            controller.update_book(sample_book)

    # --- process_ocr ---

    def test_process_ocr_success(self, controller, mock_book_service):
        """Проверяет успешный OCR-пайплайн."""
        expected_metadata = {
            "isbn": "9785171234567",
            "author": "Leo Tolstoy",
            "title": "War and Peace",
        }
        mock_book_service.process_ocr_and_fetch.return_value = expected_metadata

        result = controller.process_ocr("/path/image.jpg")

        mock_book_service.process_ocr_and_fetch.assert_called_once_with("/path/image.jpg")
        assert result == expected_metadata

    def test_process_ocr_no_isbn(self, controller, mock_book_service):
        """Проверяет OCR-пайплайн, когда ISBN не найден."""
        mock_book_service.process_ocr_and_fetch.return_value = None

        result = controller.process_ocr("/path/image.jpg")

        assert result is None

    def test_process_ocr_api_unavailable(self, controller, mock_book_service):
        """Проверяет OCR-пайплайн, когда API недоступен."""
        mock_book_service.process_ocr_and_fetch.return_value = {"isbn": "9785171234567"}

        result = controller.process_ocr("/path/image.jpg")

        assert result == {"isbn": "9785171234567"}

    # --- generate_qr ---

    def test_generate_qr_success(self, controller, mock_book_service):
        """Проверяет успешную генерацию QR-кода."""
        mock_book_service._qr.generate_qr.return_value = "/path/qr_book_1.png"

        result = controller.generate_qr(1, "9785171234567")

        mock_book_service._qr.generate_qr.assert_called_once_with(1, "9785171234567")
        assert result == "/path/qr_book_1.png"

    def test_generate_qr_error(self, controller, mock_book_service):
        """Проверяет ошибку при генерации QR-кода."""
        mock_book_service._qr.generate_qr.side_effect = Exception("QR error")

        result = controller.generate_qr(1, "9785171234567")

        assert result is None

    def test_generate_qr_without_isbn(self, controller, mock_book_service):
        """Проверяет генерацию QR-кода без ISBN."""
        mock_book_service._qr.generate_qr.return_value = "/path/qr_book_2.png"

        result = controller.generate_qr(2, None)

        mock_book_service._qr.generate_qr.assert_called_once_with(2, None)
        assert result == "/path/qr_book_2.png"