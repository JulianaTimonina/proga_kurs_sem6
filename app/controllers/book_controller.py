"""Контроллер карточки книги.

Связывает диалоги карточки книги (BookCardDialog, AddBookDialog) с сервисами.
Обрабатывает: получение данных книги, сохранение, обновление, OCR, генерацию QR.
"""

from typing import Optional

from app.models.book import Book
from app.services.book_service import BookService


class BookController:
    """Контроллер для операций с отдельной книгой.

    Предоставляет методы для получения, сохранения, обновления книги,
    запуска OCR-пайплайна и генерации QR-кода.
    """

    def __init__(self, book_service: BookService):
        """Инициализация контроллера книги.

        Args:
            book_service: Сервис для работы с книгами.
        """
        self._book_service = book_service

    def get_book(self, book_id: int) -> Optional[Book]:
        """Получает данные книги по ID.

        Args:
            book_id: ID книги.

        Returns:
            Объект книги или None, если книга не найдена.
        """
        return self._book_service.get_book(book_id)

    def save_book(self, book: Book) -> int:
        """Сохраняет новую книгу.

        Args:
            book: Объект книги для создания.

        Returns:
            ID созданной книги.

        Raises:
            ValueError: Если не заполнены обязательные поля.
        """
        return self._book_service.create_book(book)

    def update_book(self, book: Book) -> None:
        """Обновляет существующую книгу.

        Args:
            book: Объект книги с обновлёнными полями.

        Raises:
            ValueError: Если не заполнены обязательные поля.
        """
        self._book_service.update_book(book)

    def process_ocr(self, image_path: str) -> Optional[dict]:
        """Запускает полный пайплайн OCR.

        Последовательно выполняет:
        1. OCR-распознавание текста с изображения.
        2. Извлечение ISBN из распознанного текста.
        3. Запрос метаданных книги через Open Library API.

        Args:
            image_path: Путь к файлу изображения.

        Returns:
            Словарь с метаданными книги (isbn, author, title, publisher, year)
            или None, если ISBN не найден.
            Если ISBN найден, но API недоступен, возвращает {"isbn": найденный_isbn}.
        """
        return self._book_service.process_ocr_and_fetch(image_path)

    def generate_qr(self, book_id: int, isbn: Optional[str]) -> Optional[str]:
        """Генерирует QR-код для книги.

        Args:
            book_id: ID книги.
            isbn: ISBN книги (может быть None).

        Returns:
            Путь к сгенерированному файлу QR-кода или None в случае ошибки.
        """
        try:
            return self._book_service._qr.generate_qr(book_id, isbn)
        except Exception:
            return None