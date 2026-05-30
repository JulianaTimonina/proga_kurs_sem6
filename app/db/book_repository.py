from typing import List, Optional

from app.db.database import Database
from app.models.book import Book


class BookRepository:
    """Репозиторий для CRUD-операций с таблицей books.

    Содержит только SQL-запросы. Никакой бизнес-логики.
    """

    def __init__(self, database: Database):
        self._db = database

    def _row_to_book(self, row) -> Book:
        """Преобразует sqlite3.Row в объект Book."""
        return Book(
            id=row['id'],
            isbn=row['isbn'],
            author=row['author'],
            title=row['title'],
            publisher=row['publisher'],
            year=row['year'],
            udc=row['udc'],
            bbk=row['bbk'],
            author_mark=row['author_mark'],
            quantity=row['quantity'],
            qr_path=row['qr_path'],
        )

    def get_all(self) -> List[Book]:
        """Возвращает список всех книг, отсортированных по ID."""
        conn = self._db.get_connection()
        cursor = conn.execute("SELECT * FROM books ORDER BY id")
        return [self._row_to_book(row) for row in cursor.fetchall()]

    def get_by_id(self, book_id: int) -> Optional[Book]:
        """Возвращает книгу по ID или None."""
        conn = self._db.get_connection()
        cursor = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,))
        row = cursor.fetchone()
        return self._row_to_book(row) if row else None

    def get_by_isbn(self, isbn: str) -> Optional[Book]:
        """Возвращает книгу по ISBN или None."""
        conn = self._db.get_connection()
        cursor = conn.execute("SELECT * FROM books WHERE isbn = ?", (isbn,))
        row = cursor.fetchone()
        return self._row_to_book(row) if row else None

    def search(self, query: str) -> List[Book]:
        """Поиск книг по ISBN, автору, названию или издательству.

        Поиск регистронезависимый, ищет вхождение подстроки.
        Для корректной работы с кириллицей используется COLLATE NOCASE
        в сочетании с приведением запроса к нижнему регистру.
        """
        pattern = f"%{query}%"
        conn = self._db.get_connection()
        cursor = conn.execute(
            """SELECT * FROM books
               WHERE isbn LIKE ? COLLATE NOCASE
                  OR author LIKE ? COLLATE NOCASE
                  OR title LIKE ? COLLATE NOCASE
                  OR publisher LIKE ? COLLATE NOCASE
               ORDER BY id""",
            (pattern, pattern, pattern, pattern),
        )
        return [self._row_to_book(row) for row in cursor.fetchall()]

    def filter(
        self,
        year: Optional[int] = None,
        udc: Optional[str] = None,
        bbk: Optional[str] = None,
    ) -> List[Book]:
        """Фильтрация книг по году, УДК и/или ББК.

        Если параметр None — фильтр по нему не применяется.
        Для УДК и ББК используется поиск по вхождению подстроки.
        """
        conditions = []
        params = []

        if year is not None:
            conditions.append("year = ?")
            params.append(year)

        if udc is not None:
            conditions.append("LOWER(udc) LIKE LOWER(?)")
            params.append(f"%{udc}%")

        if bbk is not None:
            conditions.append("LOWER(bbk) LIKE LOWER(?)")
            params.append(f"%{bbk}%")

        if not conditions:
            return self.get_all()

        where_clause = " AND ".join(conditions)
        conn = self._db.get_connection()
        cursor = conn.execute(
            f"SELECT * FROM books WHERE {where_clause} ORDER BY id",  # nosec - имена колонок фиксированы, значения через параметры
            params,
        )
        return [self._row_to_book(row) for row in cursor.fetchall()]

    def add(self, book: Book) -> int:
        """Добавляет новую книгу в БД.

        Args:
            book: Объект Book без ID (id будет присвоен БД).

        Returns:
            ID созданной записи.
        """
        conn = self._db.get_connection()
        cursor = conn.execute(
            """INSERT INTO books
               (isbn, author, title, publisher, year, udc, bbk, author_mark, quantity, qr_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                book.isbn,
                book.author,
                book.title,
                book.publisher,
                book.year,
                book.udc,
                book.bbk,
                book.author_mark,
                book.quantity,
                book.qr_path,
            ),
        )
        conn.commit()
        return cursor.lastrowid

    def update(self, book: Book) -> None:
        """Обновляет существующую книгу.

        Args:
            book: Объект Book с заполненным id.
        """
        conn = self._db.get_connection()
        conn.execute(
            """UPDATE books SET
               isbn = ?, author = ?, title = ?, publisher = ?, year = ?,
               udc = ?, bbk = ?, author_mark = ?, quantity = ?, qr_path = ?
               WHERE id = ?""",
            (
                book.isbn,
                book.author,
                book.title,
                book.publisher,
                book.year,
                book.udc,
                book.bbk,
                book.author_mark,
                book.quantity,
                book.qr_path,
                book.id,
            ),
        )
        conn.commit()

    def delete(self, book_id: int) -> None:
        """Удаляет книгу по ID."""
        conn = self._db.get_connection()
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()

    def count(self) -> int:
        """Возвращает общее количество книг в БД."""
        conn = self._db.get_connection()
        cursor = conn.execute("SELECT COUNT(*) FROM books")
        return cursor.fetchone()[0]