"""Тесты для ApiService — запросы к Open Library API.

Проверяют как успешные сценарии, так и обработку ошибок
(таймауты, HTTP-ошибки, ошибки соединения, невалидный JSON).
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from app.services.api_service import ApiService


class TestApiService:
    """Тесты для ApiService."""

    @pytest.fixture
    def service(self):
        return ApiService()

    # --- fetch_book_by_isbn ---

    @patch("app.services.api_service.requests.get")
    def test_fetch_success(self, mock_get, service):
        """Успешный ответ API с полными данными."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ISBN:9785171234567": {
                "title": "War and Peace",
                "authors": [{"name": "Leo Tolstoy"}],
                "publishers": [{"name": "AST"}],
                "publish_date": "2023",
            }
        }
        mock_get.return_value = mock_response

        result = service.fetch_book_by_isbn("9785171234567")

        mock_get.assert_called_once_with(
            "https://openlibrary.org/api/books?bibkeys=ISBN:9785171234567&format=json&jscmd=data",
            timeout=5,
        )
        assert result is not None
        assert result["title"] == "War and Peace"
        assert result["author"] == "Leo Tolstoy"
        assert result["publisher"] == "AST"
        assert result["year"] == 2023

    @patch("app.services.api_service.requests.get")
    def test_fetch_no_authors(self, mock_get, service):
        """Ответ API без поля authors."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ISBN:9785171234567": {
                "title": "Book Without Authors",
                "publishers": [{"name": "Publisher"}],
                "publish_date": "2022",
            }
        }
        mock_get.return_value = mock_response

        result = service.fetch_book_by_isbn("9785171234567")

        assert result is not None
        assert result["author"] == ""

    @patch("app.services.api_service.requests.get")
    def test_fetch_no_publishers(self, mock_get, service):
        """Ответ API без поля publishers."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ISBN:9785171234567": {
                "title": "Book Without Publishers",
                "authors": [{"name": "Author"}],
                "publish_date": "2022",
            }
        }
        mock_get.return_value = mock_response

        result = service.fetch_book_by_isbn("9785171234567")

        assert result is not None
        assert result["publisher"] is None

    @patch("app.services.api_service.requests.get")
    def test_fetch_no_publish_date(self, mock_get, service):
        """Ответ API без поля publish_date."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "ISBN:9785171234567": {
                "title": "Book Without Date",
                "authors": [{"name": "Author"}],
                "publishers": [{"name": "Publisher"}],
            }
        }
        mock_get.return_value = mock_response

        result = service.fetch_book_by_isbn("9785171234567")

        assert result is not None
        assert result["year"] is None

    def test_fetch_empty_isbn(self, service):
        """Пустой ISBN — должен вернуть None."""
        result = service.fetch_book_by_isbn("")
        assert result is None

    def test_fetch_none_isbn(self, service):
        """None как ISBN — должен вернуть None."""
        result = service.fetch_book_by_isbn(None)
        assert result is None

    @patch("app.services.api_service.requests.get")
    def test_fetch_timeout(self, mock_get, service):
        """Таймаут запроса — должен вернуть None."""
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")

        result = service.fetch_book_by_isbn("9785171234567")
        assert result is None

    @patch("app.services.api_service.requests.get")
    def test_fetch_http_error(self, mock_get, service):
        """HTTP-ошибка (404) — должен вернуть None."""
        mock_get.side_effect = requests.exceptions.HTTPError("404 Not Found")

        result = service.fetch_book_by_isbn("9785171234567")
        assert result is None

    @patch("app.services.api_service.requests.get")
    def test_fetch_connection_error(self, mock_get, service):
        """Ошибка соединения — должен вернуть None."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        result = service.fetch_book_by_isbn("9785171234567")
        assert result is None

    @patch("app.services.api_service.requests.get")
    def test_fetch_request_exception(self, mock_get, service):
        """Общая ошибка запроса — должен вернуть None."""
        mock_get.side_effect = requests.exceptions.RequestException("Generic error")

        result = service.fetch_book_by_isbn("9785171234567")
        assert result is None

    @patch("app.services.api_service.requests.get")
    def test_fetch_invalid_json(self, mock_get, service):
        """Невалидный JSON в ответе — должен вернуть None."""
        mock_response = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        result = service.fetch_book_by_isbn("9785171234567")
        assert result is None

    # --- _map_response ---

    def test_map_response_full(self, service):
        """Полный ответ со всеми полями."""
        data = {
            "ISBN:9785171234567": {
                "title": "War and Peace",
                "authors": [{"name": "Leo Tolstoy"}],
                "publishers": [{"name": "AST"}],
                "publish_date": "2023-05-15",
            }
        }
        result = service._map_response(data, "9785171234567")

        assert result["title"] == "War and Peace"
        assert result["author"] == "Leo Tolstoy"
        assert result["publisher"] == "AST"
        assert result["year"] == 2023

    def test_map_response_authors_as_strings(self, service):
        """Авторы в виде списка строк."""
        data = {
            "ISBN:9785171234567": {
                "title": "Book",
                "authors": ["Author One", "Author Two"],
                "publishers": [{"name": "Publisher"}],
                "publish_date": "2023",
            }
        }
        result = service._map_response(data, "9785171234567")

        assert result["author"] == "Author One, Author Two"

    def test_map_response_multiple_authors(self, service):
        """Несколько авторов через запятую."""
        data = {
            "ISBN:9785171234567": {
                "title": "Book",
                "authors": [{"name": "Author A"}, {"name": "Author B"}],
                "publishers": [{"name": "Publisher"}],
                "publish_date": "2023",
            }
        }
        result = service._map_response(data, "9785171234567")

        assert result["author"] == "Author A, Author B"

    def test_map_response_year_extraction(self, service):
        """Извлечение года из строки даты."""
        data = {
            "ISBN:9785171234567": {
                "title": "Book",
                "authors": [{"name": "Author"}],
                "publishers": [{"name": "Publisher"}],
                "publish_date": "2023-05-15",
            }
        }
        result = service._map_response(data, "9785171234567")

        assert result["year"] == 2023

    def test_map_response_year_missing(self, service):
        """Отсутствие года — должен быть None."""
        data = {
            "ISBN:9785171234567": {
                "title": "Book",
                "authors": [{"name": "Author"}],
                "publishers": [{"name": "Publisher"}],
            }
        }
        result = service._map_response(data, "9785171234567")

        assert result["year"] is None

    def test_map_response_year_no_digits(self, service):
        """Дата без цифр года — должен быть None."""
        data = {
            "ISBN:9785171234567": {
                "title": "Book",
                "authors": [{"name": "Author"}],
                "publishers": [{"name": "Publisher"}],
                "publish_date": "unknown",
            }
        }
        result = service._map_response(data, "9785171234567")

        assert result["year"] is None

    def test_map_response_publisher_string(self, service):
        """Издательство как строка."""
        data = {
            "ISBN:9785171234567": {
                "title": "Book",
                "authors": [{"name": "Author"}],
                "publishers": ["Some Publisher"],
                "publish_date": "2023",
            }
        }
        result = service._map_response(data, "9785171234567")

        assert result["publisher"] == "Some Publisher"

    def test_map_response_no_title(self, service):
        """Отсутствие названия — пустая строка."""
        data = {
            "ISBN:9785171234567": {
                "authors": [{"name": "Author"}],
                "publishers": [{"name": "Publisher"}],
                "publish_date": "2023",
            }
        }
        result = service._map_response(data, "9785171234567")

        assert result["title"] == ""

    def test_map_response_empty_book_data(self, service):
        """Пустой ответ API (нет ключа ISBN) — пустой словарь."""
        data = {}
        result = service._map_response(data, "9785171234567")
        assert result == {}