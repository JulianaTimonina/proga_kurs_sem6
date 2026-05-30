"""Контроллер каталога книг.

Связывает главное окно (MainWindow) с сервисами.
Обрабатывает события: загрузка каталога, поиск, фильтрация, удаление книг.
"""

from typing import List, Optional

from PyQt5.QtWidgets import QMessageBox, QWidget

from app.models.book import Book
from app.services.book_service import BookService


class CatalogController:
    """Контроллер для главного окна каталога.

    Предоставляет методы для загрузки, поиска, фильтрации и удаления книг.
    Выступает тонким посредником между UI (MainWindow) и BookService.
    """

    def __init__(self, book_service: BookService):
        """Инициализация контроллера каталога.

        Args:
            book_service: Сервис для работы с книгами.
        """
        self._book_service = book_service

    def load_catalog(self) -> List[Book]:
        """Загружает список всех книг.

        Returns:
            Список всех книг из каталога.
        """
        return self._book_service.get_all_books()

    def search(self, query: str) -> List[Book]:
        """Выполняет поиск книг по запросу.

        Args:
            query: Поисковый запрос (ISBN, автор, название, издательство).

        Returns:
            Список найденных книг. Если запрос пуст, возвращает все книги.
        """
        if not query.strip():
            return self._book_service.get_all_books()
        return self._book_service.search_books(query.strip())

    def apply_filters(
        self,
        year: Optional[int] = None,
        udc: Optional[str] = None,
        bbk: Optional[str] = None,
    ) -> List[Book]:
        """Применяет фильтры к каталогу.

        Args:
            year: Год публикации (None — без фильтра).
            udc: УДК (None или пустая строка — без фильтра).
            bbk: ББК (None или пустая строка — без фильтра).

        Returns:
            Отфильтрованный список книг.
        """
        return self._book_service.filter_books(
            year=year,
            udc=udc if udc else None,
            bbk=bbk if bbk else None,
        )

    def delete_book(self, book_id: int, parent: Optional[QWidget] = None) -> bool:
        """Удаляет книгу с подтверждением от пользователя.

        Args:
            book_id: ID книги для удаления.
            parent: Родительский виджет для диалога подтверждения.

        Returns:
            True, если книга удалена, False — если пользователь отменил.
        """
        book = self._book_service.get_book(book_id)
        if book is None:
            return False

        reply = QMessageBox.question(
            parent,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить книгу\n"
            f"«{book.title}» {book.author}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply != QMessageBox.Yes:
            return False

        try:
            self._book_service.delete_book(book_id)
            return True
        except Exception as e:
            QMessageBox.critical(
                parent,
                "Ошибка",
                f"Не удалось удалить книгу: {e}",
            )
            return False