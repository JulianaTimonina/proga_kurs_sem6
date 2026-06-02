import re
from typing import Optional

import requests


class ApiService:
    """Сервис для запросов к Open Library API.

    Позволяет получать метаданные книги по ISBN.
    Использует Books API (/api/books) с параметром jscmd=data,
    который возвращает полные метаданные, включая имена авторов.
    """

    OPEN_LIBRARY_URL = (
        "https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    )
    REQUEST_TIMEOUT = 5  # секунд

    def fetch_book_by_isbn(self, isbn: str) -> Optional[dict]:
        """Запрашивает метаданные книги через Open Library API.

        Args:
            isbn: ISBN книги (10 или 13 символов, без разделителей).

        Returns:
            Словарь с полями author, title, publisher, year
            или None при ошибке/недоступности.
        """
        if not isbn:
            return None

        url = self.OPEN_LIBRARY_URL.format(isbn=isbn)

        try:
            response = requests.get(url, timeout=self.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            return self._map_response(data, isbn)

        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.HTTPError:
            return None
        except requests.exceptions.ConnectionError:
            return None
        except requests.exceptions.RequestException:
            return None
        except ValueError:  # Ошибка парсинга JSON
            return None

    def _map_response(self, data: dict, isbn: str) -> dict:
        """Преобразует ответ Books API в единый формат метаданных.

        Ответ от /api/books приходит в виде:
            {"ISBN:{isbn}": { ... book data ... }}

        Внутри book data поля:
            - title: str
            - authors: [{"name": "...", "key": "..."}]
            - publishers: [{"name": "..."}]
            - publish_date: str

        Args:
            data: Сырой ответ от Open Library API.
            isbn: ISBN, использованный в запросе (ключ для извлечения из обёртки).

        Returns:
            Словарь с полями: author, title, publisher, year.
        """
        result: dict = {}

        # Ответ обёрнут в ключ "ISBN:{isbn}"
        book_key = f"ISBN:{isbn}"
        book_data = data.get(book_key, {})
        if not book_data:
            return result

        # Извлечение названия
        result["title"] = book_data.get("title", "")

        # Извлечение авторов
        authors = book_data.get("authors", [])
        if authors:
            author_names = []
            for author in authors:
                if isinstance(author, dict):
                    name = author.get("name", "")
                    if name:
                        author_names.append(name)
                elif isinstance(author, str):
                    author_names.append(author)
            result["author"] = ", ".join(author_names)
        else:
            result["author"] = ""

        # Извлечение издательства (теперь массив объектов {name: ...})
        publishers = book_data.get("publishers", [])
        if publishers:
            first = publishers[0]
            if isinstance(first, dict):
                result["publisher"] = first.get("name", "")
            else:
                result["publisher"] = str(first)
        else:
            result["publisher"] = None

        # Извлечение года публикации
        publish_date = book_data.get("publish_date", "")
        if publish_date:
            year_match = re.search(r"(\d{4})", publish_date)
            if year_match:
                result["year"] = int(year_match.group(1))
            else:
                result["year"] = None
        else:
            result["year"] = None

        return result