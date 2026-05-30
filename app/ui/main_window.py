"""Главное окно библиотечного каталога.

Содержит таблицу книг, строку поиска, панель фильтров и кнопки управления.
"""

from typing import List, Optional

from PyQt5.QtCore import Qt, QSortFilterProxyModel, QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableView,
    QHeaderView,
    QSpinBox,
    QLabel,
    QMessageBox,
    QStatusBar,
    QFrame,
    QApplication,
)

from app.models.book import Book
from app.services.book_service import BookService


class BookTableModel(QStandardItemModel):
    """Модель данных для таблицы книг.

    Колонки: ID, ISBN, Автор, Название, Издательство, Год, УДК, ББК, Кол-во.
    """

    COLUMNS = [
        "ID", "ISBN", "Автор", "Название",
        "Издательство", "Год", "УДК", "ББК", "Кол-во",
    ]

    def __init__(self, parent=None):
        super().__init__(len(self.COLUMNS), 0, parent)
        self.setHorizontalHeaderLabels(self.COLUMNS)

    def set_books(self, books: List[Book]) -> None:
        """Заполняет модель данными книг.

        Args:
            books: Список книг для отображения.
        """
        self.removeRows(0, self.rowCount())
        for book in books:
            row = [
                str(book.id) if book.id is not None else "",
                book.isbn or "",
                book.author,
                book.title,
                book.publisher or "",
                str(book.year) if book.year is not None else "",
                book.udc or "",
                book.bbk or "",
                str(book.quantity),
            ]
            items = [QStandardItem(cell) for cell in row]
            # Храним book_id в UserRole для доступа
            items[0].setData(book.id, Qt.UserRole)
            self.appendRow(items)

    def get_book_id_at(self, row: int) -> Optional[int]:
        """Возвращает ID книги в указанной строке.

        Args:
            row: Индекс строки.

        Returns:
            ID книги или None.
        """
        index = self.index(row, 0)
        if index.isValid():
            return index.data(Qt.UserRole)
        return None


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    def __init__(self, book_service: BookService):
        """Инициализация главного окна.

        Args:
            book_service: Сервис для работы с книгами.
        """
        super().__init__()
        self._book_service = book_service

        self._setup_ui()
        self._connect_signals()
        self._load_catalog()

    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса."""
        self.setWindowTitle("Картотека библиотеки")
        self.setMinimumSize(1100, 600)
        self.resize(1200, 700)

        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Заголовок
        title = QLabel("📚 Картотека библиотеки")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # Панель поиска
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("🔍 Поиск по ISBN, автору, названию, издательству...")
        self._search_input.setMinimumHeight(36)
        search_layout.addWidget(self._search_input, 1)

        self._search_button = QPushButton("Поиск")
        self._search_button.setMinimumHeight(36)
        search_layout.addWidget(self._search_button)

        self._clear_search_button = QPushButton("Сброс")
        self._clear_search_button.setObjectName("secondaryButton")
        self._clear_search_button.setMinimumHeight(36)
        search_layout.addWidget(self._clear_search_button)

        self._add_book_button = QPushButton("➕ Добавить книгу")
        self._add_book_button.setObjectName("successButton")
        self._add_book_button.setMinimumHeight(36)
        search_layout.addWidget(self._add_book_button)

        layout.addLayout(search_layout)

        # Панель фильтров
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        filter_layout.addWidget(QLabel("Год:"))

        self._year_filter = QSpinBox()
        self._year_filter.setMinimum(0)
        self._year_filter.setMaximum(9999)
        self._year_filter.setSpecialValueText("Любой")
        self._year_filter.setValue(0)
        self._year_filter.setMinimumWidth(100)
        self._year_filter.setMinimumHeight(32)
        filter_layout.addWidget(self._year_filter)

        filter_layout.addSpacing(16)
        filter_layout.addWidget(QLabel("УДК:"))

        self._udc_filter = QLineEdit()
        self._udc_filter.setPlaceholderText("Любой")
        self._udc_filter.setMinimumWidth(120)
        self._udc_filter.setMinimumHeight(32)
        filter_layout.addWidget(self._udc_filter)

        filter_layout.addSpacing(16)
        filter_layout.addWidget(QLabel("ББК:"))

        self._bbk_filter = QLineEdit()
        self._bbk_filter.setPlaceholderText("Любой")
        self._bbk_filter.setMinimumWidth(120)
        self._bbk_filter.setMinimumHeight(32)
        filter_layout.addWidget(self._bbk_filter)

        filter_layout.addSpacing(16)

        self._apply_filter_button = QPushButton("Применить")
        self._apply_filter_button.setMinimumHeight(32)
        filter_layout.addWidget(self._apply_filter_button)

        self._clear_filter_button = QPushButton("Сброс")
        self._clear_filter_button.setObjectName("secondaryButton")
        self._clear_filter_button.setMinimumHeight(32)
        filter_layout.addWidget(self._clear_filter_button)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        # Таблица книг
        self._model = BookTableModel(self)
        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSourceModel(self._model)

        self._table = QTableView()
        self._table.setModel(self._proxy_model)
        self._table.setSortingEnabled(True)
        self._table.setSelectionBehavior(QTableView.SelectRows)
        self._table.setSelectionMode(QTableView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(True)
        self._table.verticalHeader().hide()
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self._table.setMinimumHeight(300)

        # Настройка ширины колонок
        header = self._table.horizontalHeader()
        header.resizeSection(0, 50)    # ID
        header.resizeSection(1, 140)   # ISBN
        header.resizeSection(2, 180)   # Автор
        header.resizeSection(3, 250)   # Название
        header.resizeSection(4, 150)   # Издательство
        header.resizeSection(5, 60)    # Год
        header.resizeSection(6, 100)   # УДК
        header.resizeSection(7, 100)   # ББК
        header.resizeSection(8, 70)    # Кол-во

        layout.addWidget(self._table, 1)

        # Статусбар
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_label = QLabel()
        self._status_bar.addWidget(self._status_label)

    def _connect_signals(self) -> None:
        """Подключение сигналов к слотам."""
        self._search_button.clicked.connect(self._on_search)
        self._clear_search_button.clicked.connect(self._on_clear_search)
        self._search_input.returnPressed.connect(self._on_search)
        self._add_book_button.clicked.connect(self._on_add_book)
        self._apply_filter_button.clicked.connect(self._on_apply_filters)
        self._clear_filter_button.clicked.connect(self._on_clear_filters)
        self._table.doubleClicked.connect(self._on_book_double_clicked)

    def _load_catalog(self) -> None:
        """Загрузка каталога книг."""
        try:
            books = self._book_service.get_all_books()
            self._model.set_books(books)
            self._update_status()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить каталог: {e}")

    def _update_status(self) -> None:
        """Обновление строки состояния."""
        count = self._model.rowCount()
        self._status_label.setText(f"Всего книг: {count}")

    def _on_search(self) -> None:
        """Обработка поиска."""
        query = self._search_input.text().strip()
        try:
            if query:
                books = self._book_service.search_books(query)
            else:
                books = self._book_service.get_all_books()
            self._model.set_books(books)
            self._update_status()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка поиска: {e}")

    def _on_clear_search(self) -> None:
        """Сброс поиска."""
        self._search_input.clear()
        self._load_catalog()

    def _on_apply_filters(self) -> None:
        """Применение фильтров."""
        year = self._year_filter.value() if self._year_filter.value() > 0 else None
        udc = self._udc_filter.text().strip() or None
        bbk = self._bbk_filter.text().strip() or None

        try:
            books = self._book_service.filter_books(year=year, udc=udc, bbk=bbk)
            self._model.set_books(books)
            self._update_status()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка фильтрации: {e}")

    def _on_clear_filters(self) -> None:
        """Сброс фильтров."""
        self._year_filter.setValue(0)
        self._udc_filter.clear()
        self._bbk_filter.clear()
        self._load_catalog()

    def _on_add_book(self) -> None:
        """Открытие диалога добавления книги."""
        from app.ui.add_book_dialog import AddBookDialog

        dialog = AddBookDialog(self._book_service, self)
        if dialog.exec_():
            self._load_catalog()

    def _on_book_double_clicked(self) -> None:
        """Открытие карточки книги по двойному клику."""
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return

        proxy_index = indexes[0]
        source_index = self._proxy_model.mapToSource(proxy_index)
        book_id = self._model.get_book_id_at(source_index.row())

        if book_id is not None:
            from app.ui.book_card_dialog import BookCardDialog

            dialog = BookCardDialog(self._book_service, book_id, self)
            if dialog.exec_():
                self._load_catalog()

    def refresh_catalog(self) -> None:
        """Обновление каталога (вызывается из дочерних диалогов)."""
        self._load_catalog()