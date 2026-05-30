import re
from typing import Optional


class IsbnService:
    """Сервис для извлечения ISBN из текста с помощью регулярных выражений."""

    # ISBN-13: 978 или 979, затем 10 цифр (с возможными разделителями)
    ISBN13_PATTERN = (
        r"(?:ISBN[-]?(?:13)?[:]?\s*)?"
        r"(97[89][-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,6}[-\s]?\d)"
    )

    # ISBN-10: 10 цифр (последняя может быть X), с возможными разделителями
    ISBN10_PATTERN = (
        r"(?:ISBN[-]?(?:10)?[:]?\s*)?"
        r"(\d[-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,6}[-\s]?[\dX])"
    )

    def extract_isbn(self, text: str) -> Optional[str]:
        """Извлекает ISBN-10 или ISBN-13 из текста.

        Args:
            text: Исходный текст для поиска ISBN.

        Returns:
            Первый найденный ISBN (очищенный от разделителей) или None.
        """
        if not text:
            return None

        # Сначала ищем ISBN-13 (более приоритетный)
        match = re.search(self.ISBN13_PATTERN, text, re.IGNORECASE)
        if match:
            return self._clean_isbn(match.group(1))

        # Затем ISBN-10
        match = re.search(self.ISBN10_PATTERN, text, re.IGNORECASE)
        if match:
            return self._clean_isbn(match.group(1))

        return None

    def _clean_isbn(self, isbn: str) -> str:
        """Удаляет разделители (дефисы, пробелы) из ISBN.

        Args:
            isbn: ISBN с возможными разделителями.

        Returns:
            ISBN только из цифр (и X для ISBN-10).
        """
        return re.sub(r"[\s-]", "", isbn)