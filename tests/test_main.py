"""Тесты для точки входа приложения.

Проверяют инициализацию компонентов в main.py.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest


class TestMain:
    """Тесты для функций инициализации в main.py."""

    # --- get_db_path ---

    def test_get_db_path_default(self):
        """Проверяет путь к БД по умолчанию."""
        from app.main import get_db_path

        # Убираем переменную окружения, если она есть
        if "LIBRARY_DB_PATH" in os.environ:
            del os.environ["LIBRARY_DB_PATH"]

        path = get_db_path()

        # Проверяем, что путь заканчивается на data/library.db (с любым разделителем)
        assert path.replace("\\", "/").endswith("data/library.db")
        # Проверяем, что директория data создаётся
        assert os.path.exists(os.path.dirname(path))

    def test_get_db_path_from_env(self):
        """Проверяет путь к БД из переменной окружения."""
        from app.main import get_db_path

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            try:
                os.environ["LIBRARY_DB_PATH"] = tmp.name
                path = get_db_path()
                assert path == tmp.name
            finally:
                del os.environ["LIBRARY_DB_PATH"]
                try:
                    os.unlink(tmp.name)
                except OSError:
                    pass

    # --- get_qr_output_dir ---

    def test_get_qr_output_dir_default(self):
        """Проверяет директорию QR по умолчанию."""
        from app.main import get_qr_output_dir

        if "LIBRARY_QR_DIR" in os.environ:
            del os.environ["LIBRARY_QR_DIR"]

        path = get_qr_output_dir()

        assert path.replace("\\", "/").endswith("data/qr_codes")
        assert os.path.exists(path)

    def test_get_qr_output_dir_from_env(self):
        """Проверяет директорию QR из переменной окружения."""
        from app.main import get_qr_output_dir

        with tempfile.TemporaryDirectory() as tmp_dir:
            try:
                os.environ["LIBRARY_QR_DIR"] = tmp_dir
                path = get_qr_output_dir()
                assert path == tmp_dir
            finally:
                del os.environ["LIBRARY_QR_DIR"]

    # --- create_services ---

    def test_create_services(self):
        """Проверяет создание сервисов."""
        from app.main import create_services

        with tempfile.TemporaryDirectory() as tmp_dir:
            db_path = os.path.join(tmp_dir, "test.db")
            qr_dir = os.path.join(tmp_dir, "qr_codes")

            book_service = create_services(db_path, qr_dir)

            assert book_service is not None
            # Проверяем, что сервис имеет все необходимые методы
            assert hasattr(book_service, "create_book")
            assert hasattr(book_service, "update_book")
            assert hasattr(book_service, "delete_book")
            assert hasattr(book_service, "search_books")
            assert hasattr(book_service, "filter_books")
            assert hasattr(book_service, "process_ocr_and_fetch")
            assert hasattr(book_service, "get_book")
            assert hasattr(book_service, "get_all_books")

            # Проверяем, что БД создана
            assert os.path.exists(db_path)

            # Закрываем соединение с БД, чтобы tempfile мог удалить директорию
            book_service._repo._db.close()

    def test_create_services_in_memory(self):
        """Проверяет создание сервисов с in-memory БД."""
        from app.main import create_services

        with tempfile.TemporaryDirectory() as tmp_dir:
            qr_dir = os.path.join(tmp_dir, "qr_codes")
            book_service = create_services(":memory:", qr_dir)

            assert book_service is not None
            # Проверяем, что можно создать книгу
            from app.models.book import Book

            book = Book(author="Тест", title="Тестовая книга")
            book_id = book_service.create_book(book)
            assert book_id is not None
            assert book_id > 0

            # Закрываем соединение с БД
            book_service._repo._db.close()

    # --- create_controllers ---

    def test_create_controllers(self):
        """Проверяет создание контроллеров."""
        from app.main import create_controllers

        mock_service = MagicMock()
        catalog_ctrl, book_ctrl = create_controllers(mock_service)

        from app.controllers.catalog_controller import CatalogController
        from app.controllers.book_controller import BookController

        assert isinstance(catalog_ctrl, CatalogController)
        assert isinstance(book_ctrl, BookController)

    # --- run_app (без GUI) ---

    def test_run_app_initialization_error(self):
        """Проверяет обработку ошибки при инициализации."""
        from app.main import run_app

        with patch('app.main.QApplication') as mock_qapp:
            with patch('app.main.create_services', side_effect=Exception("Init error")):
                with patch('app.main.QMessageBox.critical') as mock_critical:
                    with patch('sys.exit') as mock_exit:
                        run_app()

                        mock_critical.assert_called_once()
                        mock_exit.assert_called_once_with(1)

    def test_main_function(self):
        """Проверяет, что функция main вызывает run_app."""
        from app.main import main

        with patch('app.main.run_app') as mock_run:
            main()
            mock_run.assert_called_once()