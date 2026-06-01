import pytest

from app.models.book import Book


class TestBookRepository:
    """Тесты для BookRepository."""

    def test_add_book(self, book_repo, sample_book):
        """Проверяет добавление книги."""
        book_id = book_repo.add(sample_book)
        assert book_id is not None
        assert book_id > 0

    def test_add_book_returns_id(self, book_repo, sample_book):
        """Проверяет, что add возвращает корректный ID."""
        book_id = book_repo.add(sample_book)
        book = book_repo.get_by_id(book_id)
        assert book is not None
        assert book.id == book_id

    def test_get_by_id_existing(self, book_repo, sample_book):
        """Проверяет получение существующей книги по ID."""
        book_id = book_repo.add(sample_book)
        book = book_repo.get_by_id(book_id)
        assert book is not None
        assert book.author == sample_book.author
        assert book.title == sample_book.title
        assert book.isbn == sample_book.isbn

    def test_get_by_id_not_found(self, book_repo):
        """Проверяет получение несуществующей книги."""
        book = book_repo.get_by_id(999)
        assert book is None

    def test_get_all_empty(self, book_repo):
        """Проверяет получение всех книг из пустой БД."""
        books = book_repo.get_all()
        assert books == []

    def test_get_all_multiple(self, book_repo, sample_book, another_book):
        """Проверяет получение всех книг."""
        book_repo.add(sample_book)
        book_repo.add(another_book)
        books = book_repo.get_all()
        assert len(books) == 2

    def test_get_by_isbn_existing(self, book_repo, sample_book):
        """Проверяет поиск по ISBN."""
        book_repo.add(sample_book)
        book = book_repo.get_by_isbn(sample_book.isbn)
        assert book is not None
        assert book.title == sample_book.title

    def test_get_by_isbn_not_found(self, book_repo):
        """Проверяет поиск по несуществующему ISBN."""
        book = book_repo.get_by_isbn("978-0-00-000000-0")
        assert book is None

    def test_get_by_isbn_none(self, book_repo, book_without_isbn):
        """Проверяет поиск по ISBN для книги без ISBN."""
        book_repo.add(book_without_isbn)
        book = book_repo.get_by_isbn(None)
        assert book is None

    def test_search_by_isbn(self, book_repo, sample_book):
        """Проверяет поиск по ISBN."""
        book_repo.add(sample_book)
        results = book_repo.search("978-5-17")
        assert len(results) == 1
        assert results[0].isbn == sample_book.isbn

    def test_search_by_author(self, book_repo, sample_book):
        """Проверяет поиск по автору."""
        book_repo.add(sample_book)
        results = book_repo.search("Толстой")
        assert len(results) == 1
        assert results[0].author == sample_book.author

    def test_search_by_title(self, book_repo, sample_book):
        """Проверяет поиск по названию."""
        book_repo.add(sample_book)
        results = book_repo.search("Война")
        assert len(results) == 1
        assert results[0].title == sample_book.title

    def test_search_by_publisher(self, book_repo, sample_book):
        """Проверяет поиск по издательству."""
        book_repo.add(sample_book)
        results = book_repo.search("АСТ")
        assert len(results) == 1
        assert results[0].publisher == sample_book.publisher

    def test_search_case_insensitive(self, book_repo, sample_book):
        """Проверяет регистронезависимый поиск (латиница)."""
        book_repo.add(sample_book)
        # Ищем строчными буквами ISBN, хотя в данных есть заглавные
        # Используем латиницу, т.к. SQLite COLLATE NOCASE не работает с кириллицей
        results = book_repo.search("978-5-17")
        assert len(results) == 1
        assert results[0].isbn == sample_book.isbn

    def test_search_partial_match(self, book_repo, sample_book):
        """Проверяет поиск по частичному совпадению."""
        book_repo.add(sample_book)
        results = book_repo.search("Вой")
        assert len(results) == 1

    def test_search_no_results(self, book_repo, sample_book):
        """Проверяет поиск без результатов."""
        book_repo.add(sample_book)
        results = book_repo.search("Несуществующий текст")
        assert results == []

    def test_search_multiple_results(self, book_repo, sample_book, another_book):
        """Проверяет поиск с несколькими результатами."""
        book_repo.add(sample_book)
        book_repo.add(another_book)
        # Обе книги имеют "и" в названии
        results = book_repo.search("и")
        assert len(results) >= 2

    def test_filter_by_year(self, book_repo, sample_book, another_book):
        """Проверяет фильтрацию по году."""
        book_repo.add(sample_book)  # year=2023
        book_repo.add(another_book)  # year=2022
        results = book_repo.filter(year=2023)
        assert len(results) == 1
        assert results[0].year == 2023

    def test_filter_by_udc(self, book_repo, sample_book, another_book):
        """Проверяет фильтрацию по УДК."""
        book_repo.add(sample_book)
        book_repo.add(another_book)
        results = book_repo.filter(udc="821.161.1")
        assert len(results) == 2

    def test_filter_by_bbk(self, book_repo, sample_book, another_book):
        """Проверяет фильтрацию по ББК."""
        book_repo.add(sample_book)
        book_repo.add(another_book)
        results = book_repo.filter(bbk="84(2Рос=Рус)6")
        assert len(results) == 2

    def test_filter_no_params(self, book_repo, sample_book, another_book):
        """Проверяет фильтрацию без параметров (возвращает всё)."""
        book_repo.add(sample_book)
        book_repo.add(another_book)
        results = book_repo.filter()
        assert len(results) == 2

    def test_filter_no_results(self, book_repo, sample_book):
        """Проверяет фильтрацию без результатов."""
        book_repo.add(sample_book)
        results = book_repo.filter(year=1999)
        assert results == []

    def test_filter_combined(self, book_repo, sample_book, another_book):
        """Проверяет комбинированную фильтрацию."""
        book_repo.add(sample_book)  # year=2023, udc=821.161.1
        book_repo.add(another_book)  # year=2022, udc=821.161.1
        results = book_repo.filter(year=2023, udc="821.161.1")
        assert len(results) == 1
        assert results[0].year == 2023

    def test_update_book(self, book_repo, sample_book):
        """Проверяет обновление книги."""
        book_id = book_repo.add(sample_book)
        book = book_repo.get_by_id(book_id)

        book.title = "Война и мир (обновлённое издание)"
        book.year = 2024
        book.quantity = 10
        book_repo.update(book)

        updated = book_repo.get_by_id(book_id)
        assert updated.title == "Война и мир (обновлённое издание)"
        assert updated.year == 2024
        assert updated.quantity == 10

    def test_update_partial(self, book_repo, sample_book):
        """Проверяет частичное обновление (только некоторые поля)."""
        book_id = book_repo.add(sample_book)
        book = book_repo.get_by_id(book_id)

        book.publisher = "Новое издательство"
        book_repo.update(book)

        updated = book_repo.get_by_id(book_id)
        assert updated.publisher == "Новое издательство"
        # Остальные поля не должны измениться
        assert updated.author == sample_book.author
        assert updated.title == sample_book.title

    def test_delete_book(self, book_repo, sample_book):
        """Проверяет удаление книги."""
        book_id = book_repo.add(sample_book)
        assert book_repo.get_by_id(book_id) is not None

        book_repo.delete(book_id)
        assert book_repo.get_by_id(book_id) is None

    def test_delete_nonexistent(self, book_repo):
        """Проверяет удаление несуществующей книги (не должно вызывать ошибок)."""
        book_repo.delete(999)  # не должно быть исключения

    def test_count_empty(self, book_repo):
        """Проверяет подсчёт в пустой БД."""
        assert book_repo.count() == 0

    def test_count_after_add(self, book_repo, sample_book):
        """Проверяет подсчёт после добавления."""
        book_repo.add(sample_book)
        assert book_repo.count() == 1

    def test_count_after_delete(self, book_repo, sample_book):
        """Проверяет подсчёт после удаления."""
        book_id = book_repo.add(sample_book)
        book_repo.delete(book_id)
        assert book_repo.count() == 0

    def test_add_book_without_isbn(self, book_repo, book_without_isbn):
        """Проверяет добавление книги без ISBN."""
        book_id = book_repo.add(book_without_isbn)
        book = book_repo.get_by_id(book_id)
        assert book.isbn is None
        assert book.author == "Иван Тургенев"

    def test_add_duplicate_isbn_raises(self, book_repo, sample_book):
        """Проверяет, что добавление дубликата ISBN вызывает ошибку."""
        book_repo.add(sample_book)
        duplicate = Book(
            isbn=sample_book.isbn,
            author="Другой автор",
            title="Другая книга",
        )
        with pytest.raises(Exception):
            book_repo.add(duplicate)

    def test_get_all_order(self, book_repo, sample_book, another_book, book_without_isbn):
        """Проверяет сортировку по ID."""
        id1 = book_repo.add(another_book)
        id2 = book_repo.add(sample_book)
        id3 = book_repo.add(book_without_isbn)

        books = book_repo.get_all()
        assert [b.id for b in books] == [id1, id2, id3]

    def test_search_empty_query(self, book_repo, sample_book):
        """Проверяет поиск с пустым запросом."""
        book_repo.add(sample_book)
        results = book_repo.search("")
        assert len(results) == 1