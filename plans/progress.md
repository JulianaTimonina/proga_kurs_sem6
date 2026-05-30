# Журнал выполнения проекта

## Этап 1: База и БД ✅

**Коммит:** `b939d82` — `feat: implement database layer with Book model, SQLite repository, and tests`

**Что сделано:**
- Создана структура директорий проекта
- Реализован [`app/models/book.py`](../app/models/book.py) — dataclass `Book` со всеми полями согласно ТЗ
- Реализован [`app/db/database.py`](../app/db/database.py) — класс `Database` для управления SQLite-соединением, автосоздание таблицы `books`
- Реализован [`app/db/book_repository.py`](../app/db/book_repository.py) — `BookRepository` с полным CRUD, поиском по 4 полям (ISBN, автор, название, издательство), фильтрацией по году/УДК/ББК
- Написаны тесты: [`tests/test_database.py`](../tests/test_database.py) (8 тестов), [`tests/test_book_repository.py`](../tests/test_book_repository.py) (34 теста)
- Все 42 теста проходят

---

## Этап 2: Сервисы ✅

**Коммит:** (текущий) — `feat: implement service layer with OCR, ISBN, API, QR services and orchestrator`

**Что сделано:**
- Реализован [`app/services/isbn_service.py`](../app/services/isbn_service.py) — извлечение ISBN-10/ISBN-13 из текста с помощью регулярных выражений, очистка от разделителей
- Реализован [`app/services/ocr_service.py`](../app/services/ocr_service.py) — Tesseract OCR с предобработкой изображения (grayscale, контраст, резкость, бинаризация Otsu, медианный фильтр), поддержка `rus+eng`
- Реализован [`app/services/api_service.py`](../app/services/api_service.py) — запросы к Open Library API по ISBN, маппинг ответа (author, title, publisher, year), обработка таймаутов и ошибок
- Реализован [`app/services/qr_service.py`](../app/services/qr_service.py) — генерация QR-кодов с JSON-данными `{"id", "isbn"}`, сохранение в PNG, удаление файлов
- Реализован [`app/services/book_service.py`](../app/services/book_service.py) — оркестратор: create/update/delete/search/filter книг, полный пайплайн OCR+ISBN+API, валидация полей, управление QR
- Написаны тесты: [`tests/test_isbn_service.py`](../tests/test_isbn_service.py) (18 тестов), [`tests/test_qr_service.py`](../tests/test_qr_service.py) (12 тестов), [`tests/test_book_service.py`](../tests/test_book_service.py) (22 теста)
- **Все 94 теста проходят**

---

## Этап 3: UI (PyQt5) ⏳

**Статус:** Ожидает реализации

**План:**
- [ ] `app/ui/styles/theme.py` — стилизация
- [ ] `app/ui/main_window.py` — главное окно
- [ ] `app/ui/add_book_dialog.py` — добавление книги
- [ ] `app/ui/book_card_dialog.py` — карточка книги
- [ ] `app/ui/qr_view_dialog.py` — просмотр QR

---

## Этап 4: Контроллеры и интеграция ⏳

**Статус:** Ожидает реализации

**План:**
- [ ] `app/controllers/catalog_controller.py`
- [ ] `app/controllers/book_controller.py`
- [ ] `app/main.py` — точка входа
- [ ] Интеграционное тестирование

---

## Этап 5: Инфраструктура ⏳

**Статус:** Ожидает реализации

**План:**
- [ ] `requirements.txt`
- [ ] `Dockerfile` и `docker-compose.yml`
- [ ] `.bandit.yml`
- [ ] `README.md`
- [ ] Финальное тестирование и SAST