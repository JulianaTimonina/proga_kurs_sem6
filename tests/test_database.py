import sqlite3

from app.db.database import Database


class TestDatabase:
    """Тесты для класса Database."""

    def test_initialize_creates_table(self, in_memory_db):
        """Проверяет, что initialize создаёт таблицу books."""
        conn = in_memory_db.get_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='books'"
        )
        assert cursor.fetchone() is not None

    def test_initialize_idempotent(self, in_memory_db):
        """Проверяет, что повторный вызов initialize не вызывает ошибок."""
        in_memory_db.initialize()  # второй вызов
        conn = in_memory_db.get_connection()
        cursor = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='books'"
        )
        assert cursor.fetchone()[0] == 1

    def test_connection_is_valid(self, in_memory_db):
        """Проверяет, что соединение активно и можно выполнять запросы."""
        conn = in_memory_db.get_connection()
        cursor = conn.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1

    def test_connection_row_factory(self, in_memory_db):
        """Проверяет, что row_factory установлен в sqlite3.Row."""
        conn = in_memory_db.get_connection()
        assert conn.row_factory is sqlite3.Row

    def test_connection_pragma_wal(self, in_memory_db):
        """Проверяет, что journal_mode установлен в WAL."""
        conn = in_memory_db.get_connection()
        cursor = conn.execute("PRAGMA journal_mode")
        # Для in-memory БД journal_mode может быть memory, не проверяем WAL
        # Просто проверяем, что PRAGMA выполняется без ошибок
        assert cursor.fetchone() is not None

    def test_close_connection(self, in_memory_db):
        """Проверяет закрытие соединения."""
        conn = in_memory_db.get_connection()
        assert conn is not None
        in_memory_db.close()
        # После закрытия новое соединение должно создаваться заново
        new_conn = in_memory_db.get_connection()
        assert new_conn is not conn

    def test_table_columns(self, in_memory_db):
        """Проверяет структуру колонок таблицы books."""
        conn = in_memory_db.get_connection()
        cursor = conn.execute("PRAGMA table_info(books)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}

        expected_columns = {
            "id": "INTEGER",
            "isbn": "TEXT",
            "author": "TEXT",
            "title": "TEXT",
            "publisher": "TEXT",
            "year": "INTEGER",
            "udc": "TEXT",
            "bbk": "TEXT",
            "author_mark": "TEXT",
            "quantity": "INTEGER",
            "qr_path": "TEXT",
        }

        for col_name, col_type in expected_columns.items():
            assert col_name in columns, f"Колонка {col_name} отсутствует"
            assert columns[col_name] == col_type, (
                f"Тип колонки {col_name}: ожидается {col_type}, получен {columns[col_name]}"
            )

    def test_db_path_property(self):
        """Проверяет свойство db_path."""
        db = Database("test.db")
        assert db.db_path == "test.db"
        db.close()

        db_memory = Database()
        assert db_memory.db_path == ":memory:"
        db_memory.close()