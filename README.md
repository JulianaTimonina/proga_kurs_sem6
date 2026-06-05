# Картотека книжной библиотеки с OCR-распознаванием

Десктопное приложение для ведения картотеки библиотечного фонда с возможностью OCR-распознавания ISBN и автоматического получения метаданных книг через Open Library API.

## Возможности

- **Ведение каталога книг** — добавление, редактирование, удаление записей
- **Поиск и фильтрация** — поиск по ISBN, автору, названию, издательству; фильтрация по году, УДК, ББК
- **OCR-распознавание** — загрузка фотографии книги, автоматическое извлечение ISBN через Tesseract OCR
- **Автозаполнение** — получение метаданных книги (автор, название, издательство, год) по ISBN через Open Library API
- **QR-коды** — генерация QR-кодов для книг с возможностью сохранения
- **Современный UI** — стилизованный интерфейс на PyQt5

## Технологии

| Компонент | Технология |
|-----------|-----------|
| Язык | Python 3.11+ |
| GUI | PyQt5 |
| База данных | SQLite |
| OCR | Tesseract (pytesseract) |
| API | Open Library API (ISBN → метаданные) |
| QR | qrcode[pil] |
| Тестирование | pytest, pytest-cov |
| SAST | Bandit, pip-audit |
| Контейнеризация | Docker |

## Архитектура

Проект построен по многослойной архитектуре:

```
UI (PyQt5) → Controllers → Services → Repository → SQLite
                                ↕
                    Tesseract OCR / Open Library API
```

Подробное описание архитектуры см. в [plans/architecture.md](plans/architecture.md).

## Установка и запуск

### Локальный запуск

#### 1. Установка Tesseract OCR

**Windows:**
1. Скачайте установщик с [GitHub UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Установите, выбрав языки **English** и **Russian**
3. Добавьте путь к `tesseract.exe` в `PATH` или укажите в коде:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract tesseract-lang
```

#### 2. Установка зависимостей Python

```bash
# Создание виртуального окружения (рекомендуется)
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt
```

#### 3. Запуск приложения

```bash
python -m app.main
```

### Запуск через Docker

```bash
# Сборка образа
docker-compose build

# Запуск (требуется X-сервер для GUI)
docker-compose up
```

> **Примечание:** Для работы GUI в Docker на Windows используйте VcXsrv или WSLg. На Linux — X-сервер должен быть запущен.

## Переменные окружения

| Переменная | Описание | По умолчанию |
|-----------|----------|-------------|
| `LIBRARY_DB_PATH` | Путь к файлу базы данных | `data/library.db` |
| `LIBRARY_QR_DIR` | Директория для QR-кодов | `data/qr_codes/` |

## Тестирование

```bash
# Запуск всех тестов
pytest tests/ -v

# Запуск с покрытием
pytest tests/ -v --cov=app

# Запуск конкретного тестового файла
pytest tests/test_book_repository.py -v
```

### Текущее покрытие

Всего тестов: **164** (все проходят)

| Модуль | Тесты |
|--------|-------|
| database | 8 |
| book_repository | 34 |
| isbn_service | 18 |
| qr_service | 15 |
| book_service | 24 |
| api_service | 20 |
| ocr_service | 11 |
| controllers | 24 |
| main | 10 |

## SAST-проверки

```bash
# Установка инструментов
pip install bandit pip-audit

# Статический анализ кода
bandit -r app/ -c .bandit.yml

# Проверка зависимостей на уязвимости
pip-audit -r requirements.txt
```

## Структура проекта

```
library_catalog/
├── app/                          # Основной пакет приложения
│   ├── main.py                   # Точка входа
│   ├── models/                   # Модели данных (Book dataclass)
│   ├── db/                       # Data Access Layer (SQLite)
│   ├── services/                 # Бизнес-логика (OCR, ISBN, API, QR)
│   ├── controllers/              # Связующее звено UI ↔ Services
│   └── ui/                       # PyQt5 интерфейс
├── tests/                        # Модульные тесты (pytest)
├── data/                         # Данные (БД, QR-коды)
├── plans/                        # Документация архитектуры
├── requirements.txt              # Зависимости Python
├── Dockerfile                    # Docker-образ
├── docker-compose.yml            # Docker Compose
└── .bandit.yml                   # Конфигурация Bandit
```

## Лицензия

Проект выполнен в рамках учебного задания.
