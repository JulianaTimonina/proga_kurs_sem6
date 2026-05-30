import pytest

from app.services.isbn_service import IsbnService


class TestIsbnService:
    """Тесты для IsbnService — извлечение ISBN из текста."""

    @pytest.fixture
    def service(self):
        return IsbnService()

    def test_extract_isbn13_with_prefix(self, service):
        """ISBN-13 с префиксом 'ISBN'."""
        text = "ISBN 978-5-17-123456-7"
        result = service.extract_isbn(text)
        assert result == "9785171234567"

    def test_extract_isbn13_without_prefix(self, service):
        """ISBN-13 без префикса."""
        text = "978-5-17-123456-7"
        result = service.extract_isbn(text)
        assert result == "9785171234567"

    def test_extract_isbn13_with_13_prefix(self, service):
        """ISBN-13 с префиксом 'ISBN-13'."""
        text = "ISBN-13: 978-5-17-123456-7"
        result = service.extract_isbn(text)
        assert result == "9785171234567"

    def test_extract_isbn10_with_prefix(self, service):
        """ISBN-10 с префиксом 'ISBN'."""
        text = "ISBN 0-596-52068-9"
        result = service.extract_isbn(text)
        assert result == "0596520689"

    def test_extract_isbn10_without_prefix(self, service):
        """ISBN-10 без префикса."""
        text = "0-596-52068-9"
        result = service.extract_isbn(text)
        assert result == "0596520689"

    def test_extract_isbn10_with_10_prefix(self, service):
        """ISBN-10 с префиксом 'ISBN-10'."""
        text = "ISBN-10: 0-596-52068-9"
        result = service.extract_isbn(text)
        assert result == "0596520689"

    def test_extract_isbn_with_hyphens(self, service):
        """ISBN с дефисами."""
        text = "ISBN 978-5-17-123456-7"
        result = service.extract_isbn(text)
        assert result == "9785171234567"

    def test_extract_isbn_with_spaces(self, service):
        """ISBN с пробелами."""
        text = "ISBN 978 5 17 123456 7"
        result = service.extract_isbn(text)
        assert result == "9785171234567"

    def test_extract_isbn10_with_x(self, service):
        """ISBN-10 с контрольной цифрой X."""
        text = "ISBN 0-306-40615-2"
        result = service.extract_isbn(text)
        assert result == "0306406152"

    def test_extract_no_isbn(self, service):
        """Текст без ISBN."""
        text = "Это обычный текст без номера книги"
        result = service.extract_isbn(text)
        assert result is None

    def test_extract_isbn_from_noisy_text(self, service):
        """ISBN в зашумлённом тексте."""
        text = """
        Книга: Война и мир
        Автор: Лев Толстой
        Издательство: АСТ, 2023
        ISBN: 978-5-17-123456-7
        Тираж: 5000 экз.
        """
        result = service.extract_isbn(text)
        assert result == "9785171234567"

    def test_extract_isbn13_979_prefix(self, service):
        """ISBN-13 с префиксом 979."""
        text = "ISBN 979-5-17-123456-7"
        result = service.extract_isbn(text)
        assert result == "9795171234567"

    def test_extract_isbn_prefers_13_over_10(self, service):
        """При наличии ISBN-13 и ISBN-10 должен вернуться ISBN-13."""
        text = "ISBN-10: 0-596-52068-9, ISBN-13: 978-5-17-123456-7"
        result = service.extract_isbn(text)
        assert result == "9785171234567"

    def test_extract_empty_text(self, service):
        """Пустой текст."""
        result = service.extract_isbn("")
        assert result is None

    def test_extract_none_text(self, service):
        """None как текст."""
        result = service.extract_isbn(None)
        assert result is None

    def test_extract_isbn_with_colon(self, service):
        """ISBN с двоеточием после префикса."""
        text = "ISBN:978-5-17-123456-7"
        result = service.extract_isbn(text)
        assert result == "9785171234567"

    def test_extract_isbn10_without_separators(self, service):
        """ISBN-10 без разделителей."""
        text = "ISBN 0306406152"
        result = service.extract_isbn(text)
        assert result == "0306406152"

    def test_extract_isbn13_without_separators(self, service):
        """ISBN-13 без разделителей."""
        text = "ISBN 9785171234567"
        result = service.extract_isbn(text)
        assert result == "9785171234567"