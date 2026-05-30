"""Точка входа в приложение «Картотека книжной библиотеки с OCR-распознаванием».

Инициализирует все компоненты приложения:
- Базу данных (SQLite)
- Репозиторий
- Сервисы (OCR, ISBN, API, QR, BookService)
- Контроллеры
- Пользовательский интерфейс (PyQt5)

Запускает главное окно приложения.
"""

import os
import sys
from typing import Optional

from PyQt5.QtWidgets import QApplication, QMessageBox

from app.controllers.book_controller import BookController
from app.controllers.catalog_controller import CatalogController
from app.db.book_repository import BookRepository
from app.db.database import Database
from app.services.api_service import ApiService
from app.services.book_service import BookService
from app.services.isbn_service import IsbnService
from app.services.ocr_service import OcrService
from app.services.qr_service import QrService
from app.ui.main_window import MainWindow
from app.ui.styles.theme import apply_theme


def get_db_path() -> str:
    """Определяет путь к файлу базы данных.

    Приоритет:
    1. Переменная окружения LIBRARY_DB_PATH.
    2. Путь по умолчанию: data/library.db (в директории проекта).

    Returns:
        Абсолютный путь к файлу БД.
    """
    env_path = os.environ.get("LIBRARY_DB_PATH")
    if env_path:
        return env_path

    # Создаём директорию data, если её нет
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    return os.path.join(data_dir, "library.db")


def get_qr_output_dir() -> str:
    """Определяет директорию для сохранения QR-кодов.

    Приоритет:
    1. Переменная окружения LIBRARY_QR_DIR.
    2. Путь по умолчанию: data/qr_codes (в директории проекта).

    Returns:
        Абсолютный путь к директории QR-кодов.
    """
    env_path = os.environ.get("LIBRARY_QR_DIR")
    if env_path:
        os.makedirs(env_path, exist_ok=True)
        return env_path

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    qr_dir = os.path.join(base_dir, "data", "qr_codes")
    os.makedirs(qr_dir, exist_ok=True)

    return qr_dir


def create_services(db_path: str, qr_output_dir: str) -> BookService:
    """Создаёт и инициализирует все сервисы приложения.

    Args:
        db_path: Путь к файлу базы данных.
        qr_output_dir: Директория для сохранения QR-кодов.

    Returns:
        Сконфигурированный BookService (оркестратор).
    """
    # База данных
    database = Database(db_path)
    database.initialize()

    # Репозиторий
    repo = BookRepository(database)

    # Сервисы
    ocr_service = OcrService()
    isbn_service = IsbnService()
    api_service = ApiService()
    qr_service = QrService(output_dir=qr_output_dir)

    # Оркестратор
    book_service = BookService(
        repo=repo,
        api=api_service,
        qr=qr_service,
        ocr=ocr_service,
        isbn=isbn_service,
    )

    return book_service


def create_controllers(book_service: BookService) -> tuple:
    """Создаёт контроллеры приложения.

    Args:
        book_service: Сервис для работы с книгами.

    Returns:
        Кортеж (catalog_controller, book_controller).
    """
    catalog_controller = CatalogController(book_service)
    book_controller = BookController(book_service)
    return catalog_controller, book_controller


def run_app() -> None:
    """Инициализирует и запускает приложение."""
    app = QApplication(sys.argv)

    # Применяем стилизацию
    apply_theme(app)

    try:
        # Инициализация сервисов
        db_path = get_db_path()
        qr_output_dir = get_qr_output_dir()
        book_service = create_services(db_path, qr_output_dir)

        # Создание контроллеров
        catalog_controller, book_controller = create_controllers(book_service)

        # Запуск главного окна
        window = MainWindow(book_service)
        window.show()

        sys.exit(app.exec_())

    except Exception as e:
        QMessageBox.critical(
            None,
            "Критическая ошибка",
            f"Не удалось запустить приложение:\n{e}",
        )
        sys.exit(1)


def main() -> None:
    """Точка входа для запуска через python -m app.main."""
    run_app()


if __name__ == "__main__":
    main()