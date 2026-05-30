from typing import Optional

import requests


class ApiService:
    """Сервис для запросов к Open Library API.

    Позволяет получать метаданные книги по ISBN.
    """

    OPEN_LIBRARY_URL = "https://openlibrary.org/isbn/{isbn}.json"
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

            return self._map_response(data)

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

    def _map_response(self, data: dict) -> dict:
        """Преобразует ответ API в единый формат метаданных.

        Args:
            data: Сырой ответ от Open Library API.

        Returns:
            Словарь с полями: author, title, publisher, year.
        """
        result: dict = {}

        # Извлечение названия
        result["title"] = data.get("title", "")

        # Извлечение авторов
        authors = data.get("authors", [])
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

        # Извлечение издательства
        publishers = data.get("publishers", [])
        if publishers:
            result["publisher"] = publishers[0] if isinstance(publishers[0], str) else ""
        else:
            result["publisher"] = None

        # Извлечение года публикации
        publish_date = data.get("publish_date", "")
        if publish_date:
            # Пытаемся извлечь год из строки даты
            import re
            year_match = re.search(r"(\d{4})", publish_date)
            if year_match:
                result["year"] = int(year_match.group(1))
            else:
                result["year"] = None
        else:
            result["year"] = None

        return result