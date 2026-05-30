from typing import List, Optional

from app.db.book_repository import BookRepository
from app.models.book import Book
from app.services.api_service import ApiService
from app.services.isbn_service import IsbnService
from app.services.ocr_service import OcrService
from app.services.qr_service import QrService


class BookService:
    """Оркестратор бизнес-логики.

    Координирует работу сервисов OCR, ISBN, API, QR и репозитория.
    """

    def __init__(
        self,
        repo: BookRepository,
        api: ApiService,
        qr: QrService,
        ocr: Optional[OcrService] = None,
        isbn: Optional[IsbnService] = None,
    ):
        """Инициализация сервиса-оркестратора.

        Args:
            repo: Репозиторий книг.
            api: Сервис Open Library API.
            qr: Сервис генерации QR-кодов.
            ocr: OCR-сервис (создаётся по умолчанию).
            isbn: Сервис извлечения ISBN (создаётся по умолчанию).
        """
        self._repo = repo
        self._api = api
        self._qr = qr
        self._ocr = ocr or OcrService()
        self._isbn = isbn or IsbnService()

    def create_book(self, book: Book) -> int:
        """Создаёт новую книгу.

        Выполняет валидацию обязательных полей и сохраняет книгу.

        Args:
            book: Объект книги для создания.

        Returns:
            ID созданной книги.

        Raises:
            ValueError: Если не заполнены автор или название.
        """
        if not book.author.strip():
            raise ValueError("Автор не может быть пустым")
        if not book.title.strip():
            raise ValueError("Название не может быть пустым")

        return self._repo.add(book)

    def update_book(self, book: Book) -> None:
        """Обновляет существующую книгу.

        Если у книги был QR-код, пересоздаёт его с новыми данными.

        Args:
            book: Объект книги с обновлёнными полями.

        Raises:
            ValueError: Если не заполнены автор или название.
        """
        if not book.author.strip():
            raise ValueError("Автор не может быть пустым")
        if not book.title.strip():
            raise ValueError("Название не может быть пустым")

        # Если у книги был QR-код, пересоздаём его
        if book.qr_path:
            self._qr.delete_qr(book.qr_path)
            new_qr_path = self._qr.generate_qr(book.id, book.isbn)
            if new_qr_path:
                book.qr_path = new_qr_path

        self._repo.update(book)

    def delete_book(self, book_id: int) -> None:
        """Удаляет книгу и связанный с ней QR-файл.

        Args:
            book_id: ID книги для удаления.
        """
        book = self._repo.get_by_id(book_id)
        if book is None:
            return

        # Удаляем QR-файл, если он есть
        if book.qr_path:
            self._qr.delete_qr(book.qr_path)

        self._repo.delete(book_id)

    def search_books(self, query: str) -> List[Book]:
        """Поиск книг по запросу.

        Args:
            query: Поисковый запрос.

        Returns:
            Список найденных книг.
        """
        return self._repo.search(query)

    def filter_books(
        self,
        year: Optional[int] = None,
        udc: Optional[str] = None,
        bbk: Optional[str] = None,
    ) -> List[Book]:
        """Фильтрация книг по году, УДК и/или ББК.

        Args:
            year: Год публикации.
            udc: УДК.
            bbk: ББК.

        Returns:
            Список отфильтрованных книг.
        """
        return self._repo.filter(year=year, udc=udc, bbk=bbk)

    def process_ocr_and_fetch(self, image_path: str) -> Optional[dict]:
        """Полный пайплайн OCR: распознавание → ISBN → API.

        1. Распознать текст через OcrService.
        2. Извлечь ISBN через IsbnService.
        3. Если ISBN найден — запрос к ApiService.
        4. Вернуть метаданные или None.

        Args:
            image_path: Путь к файлу изображения.

        Returns:
            Словарь с метаданными книги или None.
            Если ISBN найден, но API недоступен, возвращает {"isbn": найденный_isbn}.
        """
        # Шаг 1: OCR-распознавание
        text = self._ocr.recognize_text(image_path)
        if not text:
            return None

        # Шаг 2: Извлечение ISBN
        isbn = self._isbn.extract_isbn(text)

        if not isbn:
            return None

        # Шаг 3: Запрос к API
        metadata = self._api.fetch_book_by_isbn(isbn)
        if metadata:
            metadata["isbn"] = isbn
            return metadata

        # API недоступен, но ISBN найден
        return {"isbn": isbn}

    def get_book(self, book_id: int) -> Optional[Book]:
        """Получает книгу по ID.

        Args:
            book_id: ID книги.

        Returns:
            Объект книги или None.
        """
        return self._repo.get_by_id(book_id)

    def get_all_books(self) -> List[Book]:
        """Возвращает список всех книг.

        Returns:
            Список всех книг.
        """
        return self._repo.get_all()