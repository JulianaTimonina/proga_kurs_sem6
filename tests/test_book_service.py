from unittest.mock import MagicMock, patch

import pytest

from app.models.book import Book
from app.services.book_service import BookService


class TestBookService:
    """Тесты для BookService — оркестратора бизнес-логики."""

    @pytest.fixture
    def mock_repo(self):
        return MagicMock()

    @pytest.fixture
    def mock_api(self):
        return MagicMock()

    @pytest.fixture
    def mock_qr(self):
        return MagicMock()

    @pytest.fixture
    def mock_ocr(self):
        return MagicMock()

    @pytest.fixture
    def mock_isbn(self):
        return MagicMock()

    @pytest.fixture
    def service(self, mock_repo, mock_api, mock_qr, mock_ocr, mock_isbn):
        return BookService(
            repo=mock_repo,
            api=mock_api,
            qr=mock_qr,
            ocr=mock_ocr,
            isbn=mock_isbn,
        )

    @pytest.fixture
    def sample_book(self):
        return Book(
            author="Лев Толстой",
            title="Война и мир",
            isbn="9785171234567",
            publisher="АСТ",
            year=2023,
        )

    # --- create_book ---

    def test_create_book_success(self, service, mock_repo, sample_book):
        """Проверяет успешное создание книги."""
        mock_repo.add.return_value = 1
        book_id = service.create_book(sample_book)
        assert book_id == 1
        mock_repo.add.assert_called_once_with(sample_book)

    def test_create_book_empty_author(self, service, sample_book):
        """Проверяет ошибку при пустом авторе."""
        sample_book.author = ""
        with pytest.raises(ValueError, match="Автор не может быть пустым"):
            service.create_book(sample_book)

    def test_create_book_empty_title(self, service, sample_book):
        """Проверяет ошибку при пустом названии."""
        sample_book.title = ""
        with pytest.raises(ValueError, match="Название не может быть пустым"):
            service.create_book(sample_book)

    def test_create_book_whitespace_author(self, service, sample_book):
        """Проверяет ошибку при авторе из пробелов."""
        sample_book.author = "   "
        with pytest.raises(ValueError, match="Автор не может быть пустым"):
            service.create_book(sample_book)

    # --- update_book ---

    def test_update_book_success(self, service, mock_repo, sample_book):
        """Проверяет успешное обновление книги."""
        sample_book.id = 1
        service.update_book(sample_book)
        mock_repo.update.assert_called_once_with(sample_book)

    def test_update_book_empty_author(self, service, sample_book):
        """Проверяет ошибку при пустом авторе при обновлении."""
        sample_book.author = ""
        with pytest.raises(ValueError, match="Автор не может быть пустым"):
            service.update_book(sample_book)

    def test_update_book_empty_title(self, service, sample_book):
        """Проверяет ошибку при пустом названии при обновлении."""
        sample_book.title = ""
        with pytest.raises(ValueError, match="Название не может быть пустым"):
            service.update_book(sample_book)

    def test_update_book_with_qr(self, service, mock_repo, mock_qr, sample_book):
        """Проверяет обновление с удалением QR (данные изменились)."""
        sample_book.id = 1
        sample_book.qr_path = "/old/path/qr.png"

        service.update_book(sample_book)

        mock_qr.delete_qr.assert_called_once_with("/old/path/qr.png")
        mock_qr.generate_qr.assert_not_called()
        assert sample_book.qr_path is None
        mock_repo.update.assert_called_once_with(sample_book)

    def test_update_book_without_qr(self, service, mock_repo, mock_qr, sample_book):
        """Проверяет обновление без QR (не должно вызывать QR-сервис)."""
        sample_book.id = 1
        sample_book.qr_path = None

        service.update_book(sample_book)

        mock_qr.delete_qr.assert_not_called()
        mock_qr.generate_qr.assert_not_called()
        mock_repo.update.assert_called_once_with(sample_book)

    # --- delete_book ---

    def test_delete_book_with_qr(self, service, mock_repo, mock_qr):
        """Проверяет удаление книги с QR-файлом."""
        book = Book(id=1, author="Автор", title="Книга", qr_path="/path/qr.png")
        mock_repo.get_by_id.return_value = book

        service.delete_book(1)

        mock_qr.delete_qr.assert_called_once_with("/path/qr.png")
        mock_repo.delete.assert_called_once_with(1)

    def test_delete_book_without_qr(self, service, mock_repo, mock_qr):
        """Проверяет удаление книги без QR-файла."""
        book = Book(id=1, author="Автор", title="Книга", qr_path=None)
        mock_repo.get_by_id.return_value = book

        service.delete_book(1)

        mock_qr.delete_qr.assert_not_called()
        mock_repo.delete.assert_called_once_with(1)

    def test_delete_book_not_found(self, service, mock_repo, mock_qr):
        """Проверяет удаление несуществующей книги."""
        mock_repo.get_by_id.return_value = None

        service.delete_book(999)

        mock_qr.delete_qr.assert_not_called()
        mock_repo.delete.assert_not_called()

    # --- search_books ---

    def test_search_books(self, service, mock_repo):
        """Проверяет поиск книг."""
        mock_repo.search.return_value = [MagicMock(), MagicMock()]

        results = service.search_books("Толстой")

        mock_repo.search.assert_called_once_with("Толстой")
        assert len(results) == 2

    # --- filter_books ---

    def test_filter_books(self, service, mock_repo):
        """Проверяет фильтрацию книг."""
        mock_repo.filter.return_value = [MagicMock()]

        results = service.filter_books(year=2023, udc="821")

        mock_repo.filter.assert_called_once_with(year=2023, udc="821", bbk=None)
        assert len(results) == 1

    def test_filter_books_no_params(self, service, mock_repo):
        """Проверяет фильтрацию без параметров."""
        mock_repo.filter.return_value = []

        results = service.filter_books()

        mock_repo.filter.assert_called_once_with(year=None, udc=None, bbk=None)
        assert results == []

    # --- process_ocr_and_fetch ---

    def test_process_ocr_and_fetch_success(self, service, mock_ocr, mock_isbn, mock_api):
        """Проверяет полный успешный пайплайн OCR+API."""
        mock_ocr.recognize_text.return_value = "Some text with ISBN 9785171234567"
        mock_isbn.extract_isbn.return_value = "9785171234567"
        mock_api.fetch_book_by_isbn.return_value = {
            "author": "Leo Tolstoy",
            "title": "War and Peace",
            "publisher": "AST",
            "year": 2023,
        }

        result = service.process_ocr_and_fetch("/path/image.jpg")

        mock_ocr.recognize_text.assert_called_once_with("/path/image.jpg")
        mock_isbn.extract_isbn.assert_called_once()
        mock_api.fetch_book_by_isbn.assert_called_once_with("9785171234567")

        assert result is not None
        assert result["isbn"] == "9785171234567"
        assert result["author"] == "Leo Tolstoy"
        assert result["title"] == "War and Peace"

    def test_process_ocr_and_fetch_no_text(self, service, mock_ocr, mock_isbn, mock_api):
        """Проверяет пайплайн, когда OCR не распознал текст."""
        mock_ocr.recognize_text.return_value = None

        result = service.process_ocr_and_fetch("/path/image.jpg")

        assert result is None
        mock_isbn.extract_isbn.assert_not_called()
        mock_api.fetch_book_by_isbn.assert_not_called()

    def test_process_ocr_and_fetch_no_isbn(self, service, mock_ocr, mock_isbn, mock_api):
        """Проверяет пайплайн, когда ISBN не найден."""
        mock_ocr.recognize_text.return_value = "Some text without ISBN"
        mock_isbn.extract_isbn.return_value = None

        result = service.process_ocr_and_fetch("/path/image.jpg")

        assert result is None
        mock_api.fetch_book_by_isbn.assert_not_called()

    def test_process_ocr_and_fetch_api_unavailable(
        self, service, mock_ocr, mock_isbn, mock_api
    ):
        """Проверяет пайплайн, когда API недоступен."""
        mock_ocr.recognize_text.return_value = "ISBN 9785171234567"
        mock_isbn.extract_isbn.return_value = "9785171234567"
        mock_api.fetch_book_by_isbn.return_value = None

        result = service.process_ocr_and_fetch("/path/image.jpg")

        assert result is not None
        assert result["isbn"] == "9785171234567"
        assert "author" not in result

    # --- get_book ---

    def test_get_book(self, service, mock_repo):
        """Проверяет получение книги по ID."""
        expected_book = MagicMock()
        mock_repo.get_by_id.return_value = expected_book

        result = service.get_book(1)

        mock_repo.get_by_id.assert_called_once_with(1)
        assert result == expected_book

    def test_get_book_not_found(self, service, mock_repo):
        """Проверяет получение несуществующей книги."""
        mock_repo.get_by_id.return_value = None

        result = service.get_book(999)

        assert result is None

    # --- get_all_books ---

    def test_get_all_books(self, service, mock_repo):
        """Проверяет получение всех книг."""
        mock_repo.get_all.return_value = [MagicMock(), MagicMock()]

        results = service.get_all_books()

        mock_repo.get_all.assert_called_once()
        assert len(results) == 2