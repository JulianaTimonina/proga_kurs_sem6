from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Book:
    """Модель данных книги.

    Соответствует структуре таблицы books в SQLite.
    Используется для передачи данных между слоями приложения.
    """
    id: Optional[int] = None
    isbn: Optional[str] = None
    author: str = ""
    title: str = ""
    publisher: Optional[str] = None
    year: Optional[int] = None
    udc: Optional[str] = None
    bbk: Optional[str] = None
    author_mark: Optional[str] = None
    quantity: int = 1
    qr_path: Optional[str] = None