import sqlite3
import os
from typing import Optional


class Database:
    """Управление подключением к SQLite.

    Предоставляет единную точку доступа к базе данных.
    При инициализации создаёт таблицу books, если она не существует.
    """

    def __init__(self, db_path: Optional[str] = None):
        """Инициализация подключения к БД.

        Args:
            db_path: Путь к файлу БД. Если None, используется ':memory:'.
        """
        self._db_path = db_path or ':memory:'
        self._connection: Optional[sqlite3.Connection] = None

    def get_connection(self) -> sqlite3.Connection:
        """Возвращает активное соединение с БД.

        Создаёт новое соединение при первом вызове или после закрытия.
        Устанавливает row_factory для доступа к колонкам по имени.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self._db_path)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
        return self._connection

    def initialize(self) -> None:
        """Создаёт таблицу books, если она не существует.

        Должна вызываться при запуске приложения.
        """
        conn = self.get_connection()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                isbn TEXT UNIQUE,
                author TEXT NOT NULL,
                title TEXT NOT NULL,
                publisher TEXT,
                year INTEGER,
                udc TEXT,
                bbk TEXT,
                author_mark TEXT,
                quantity INTEGER NOT NULL DEFAULT 1,
                qr_path TEXT
            );
        """)
        conn.commit()

    def close(self) -> None:
        """Закрывает соединение с БД."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    @property
    def db_path(self) -> str:
        return self._db_path