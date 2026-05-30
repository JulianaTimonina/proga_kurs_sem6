"""Диалог добавления новой книги.

Позволяет ввести данные книги вручную или загрузить фото для OCR-распознавания.
"""

from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QLabel,
    QMessageBox,
    QFileDialog,
    QGroupBox,
    QScrollArea,
    QWidget,
)

from app.models.book import Book
from app.services.book_service import BookService


class AddBookDialog(QDialog):
    """Диалог добавления новой книги."""

    def __init__(self, book_service: BookService, parent=None):
        """Инициализация диалога.

        Args:
            book_service: Сервис для работы с книгами.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._book_service = book_service
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса."""
        self.setWindowTitle("Добавление новой книги")
        self.setMinimumWidth(550)
        self.setModal(True)

        # Основной layout с прокруткой
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Заголовок
        title = QLabel("📖 Добавление новой книги")
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        # Группа: OCR
        ocr_group = QGroupBox("OCR-распознавание")
        ocr_layout = QVBoxLayout(ocr_group)

        ocr_desc = QLabel("Загрузите фото страницы с ISBN для автоматического заполнения полей:")
        ocr_desc.setWordWrap(True)
        ocr_layout.addWidget(ocr_desc)

        ocr_btn_layout = QHBoxLayout()
        self._ocr_button = QPushButton("📷 Загрузить фото")
        self._ocr_button.setObjectName("ocrButton")
        self._ocr_button.setMinimumHeight(36)
        ocr_btn_layout.addWidget(self._ocr_button)
        ocr_btn_layout.addStretch()
        ocr_layout.addLayout(ocr_btn_layout)

        self._ocr_status = QLabel()
        self._ocr_status.setWordWrap(True)
        ocr_layout.addWidget(self._ocr_status)

        layout.addWidget(ocr_group)

        # Группа: поля книги
        fields_group = QGroupBox("Данные книги")
        form_layout = QFormLayout(fields_group)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self._isbn_input = QLineEdit()
        self._isbn_input.setPlaceholderText("978-5-1234-5678-9")
        form_layout.addRow("ISBN:", self._isbn_input)

        self._author_input = QLineEdit()
        self._author_input.setPlaceholderText("Обязательное поле")
        form_layout.addRow("Автор:*", self._author_input)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Обязательное поле")
        form_layout.addRow("Название:*", self._title_input)

        self._publisher_input = QLineEdit()
        self._publisher_input.setPlaceholderText("Издательство")
        form_layout.addRow("Издательство:", self._publisher_input)

        self._year_input = QSpinBox()
        self._year_input.setMinimum(0)
        self._year_input.setMaximum(9999)
        self._year_input.setSpecialValueText("Не указан")
        self._year_input.setValue(0)
        form_layout.addRow("Год:", self._year_input)

        self._udc_input = QLineEdit()
        self._udc_input.setPlaceholderText("УДК")
        form_layout.addRow("УДК:", self._udc_input)

        self._bbk_input = QLineEdit()
        self._bbk_input.setPlaceholderText("ББК")
        form_layout.addRow("ББК:", self._bbk_input)

        self._author_mark_input = QLineEdit()
        self._author_mark_input.setPlaceholderText("Авторский знак")
        form_layout.addRow("Авторский знак:", self._author_mark_input)

        self._quantity_input = QSpinBox()
        self._quantity_input.setMinimum(1)
        self._quantity_input.setMaximum(9999)
        self._quantity_input.setValue(1)
        form_layout.addRow("Количество:", self._quantity_input)

        layout.addWidget(fields_group)

        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self._save_button = QPushButton("💾 Сохранить")
        self._save_button.setObjectName("successButton")
        self._save_button.setMinimumHeight(36)
        buttons_layout.addWidget(self._save_button)

        self._cancel_button = QPushButton("Отмена")
        self._cancel_button.setObjectName("secondaryButton")
        self._cancel_button.setMinimumHeight(36)
        buttons_layout.addWidget(self._cancel_button)

        layout.addLayout(buttons_layout)

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _connect_signals(self) -> None:
        """Подключение сигналов."""
        self._ocr_button.clicked.connect(self._on_ocr)
        self._save_button.clicked.connect(self._on_save)
        self._cancel_button.clicked.connect(self.reject)

    def _on_ocr(self) -> None:
        """Обработка загрузки фото и OCR-распознавания."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg *.bmp *.tiff *.tif)",
        )
        if not file_path:
            return

        self._ocr_button.setEnabled(False)
        self._ocr_status.setText("⏳ Распознавание текста...")
        QApplication.processEvents()

        try:
            metadata = self._book_service.process_ocr_and_fetch(file_path)

            if metadata is None:
                self._ocr_status.setText("❌ Не удалось распознать ISBN на изображении.")
                return

            if "isbn" in metadata:
                self._isbn_input.setText(metadata["isbn"])

            if "author" in metadata:
                self._author_input.setText(metadata["author"])

            if "title" in metadata:
                self._title_input.setText(metadata["title"])

            if "publisher" in metadata:
                self._publisher_input.setText(metadata["publisher"])

            if "year" in metadata and metadata["year"]:
                self._year_input.setValue(metadata["year"])

            if len(metadata) > 1:
                self._ocr_status.setText("✅ Поля успешно заполнены из OCR и Open Library.")
            else:
                self._ocr_status.setText("✅ ISBN найден. Остальные поля заполните вручную.")

        except Exception as e:
            self._ocr_status.setText(f"❌ Ошибка OCR: {e}")
        finally:
            self._ocr_button.setEnabled(True)

    def _on_save(self) -> None:
        """Сохранение книги."""
        author = self._author_input.text().strip()
        title = self._title_input.text().strip()

        if not author:
            QMessageBox.warning(self, "Предупреждение", "Поле 'Автор' обязательно для заполнения.")
            self._author_input.setFocus()
            return

        if not title:
            QMessageBox.warning(self, "Предупреждение", "Поле 'Название' обязательно для заполнения.")
            self._title_input.setFocus()
            return

        book = Book(
            isbn=self._isbn_input.text().strip() or None,
            author=author,
            title=title,
            publisher=self._publisher_input.text().strip() or None,
            year=self._year_input.value() if self._year_input.value() > 0 else None,
            udc=self._udc_input.text().strip() or None,
            bbk=self._bbk_input.text().strip() or None,
            author_mark=self._author_mark_input.text().strip() or None,
            quantity=self._quantity_input.value(),
        )

        try:
            self._book_service.create_book(book)
            QMessageBox.information(self, "Успех", "Книга успешно добавлена в каталог.")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка валидации", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить книгу: {e}")