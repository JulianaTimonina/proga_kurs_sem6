import pytest

from app.db.database import Database
from app.db.book_repository import BookRepository
from app.models.book import Book


@pytest.fixture
def in_memory_db():
    """Создаёт in-memory БД для тестов."""
    db = Database(":memory:")
    db.initialize()
    yield db
    db.close()


@pytest.fixture
def book_repo(in_memory_db):
    """Создаёт репозиторий на in-memory БД."""
    return BookRepository(in_memory_db)


@pytest.fixture
def sample_book():
    """Тестовый объект книги."""
    return Book(
        isbn="978-5-17-123456-7",
        author="Лев Толстой",
        title="Война и мир",
        publisher="АСТ",
        year=2023,
        udc="821.161.1",
        bbk="84(2Рос=Рус)6",
        author_mark="Т53",
        quantity=5,
    )


@pytest.fixture
def another_book():
    """Ещё один тестовый объект книги."""
    return Book(
        isbn="978-5-04-654321-0",
        author="Фёдор Достоевский",
        title="Преступление и наказание",
        publisher="Эксмо",
        year=2022,
        udc="821.161.1",
        bbk="84(2Рос=Рус)6",
        author_mark="Д70",
        quantity=3,
    )


@pytest.fixture
def book_without_isbn():
    """Книга без ISBN."""
    return Book(
        author="Иван Тургенев",
        title="Отцы и дети",
        publisher="Дрофа",
        year=2021,
        quantity=2,
    )