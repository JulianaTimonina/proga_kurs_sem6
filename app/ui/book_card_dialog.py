"""Диалог карточки книги.

Поддерживает два режима:
- Просмотр (read-only): все поля заблокированы, кнопки: Редактировать, Удалить, QR-код, Закрыть.
- Редактирование: поля разблокированы, кнопки: Сохранить, Отмена.
"""

import os
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QLabel,
    QMessageBox,
    QGroupBox,
    QScrollArea,
    QWidget,
)

from app.models.book import Book
from app.services.book_service import BookService


class BookCardDialog(QDialog):
    """Диалог просмотра и редактирования карточки книги."""

    MODE_VIEW = "view"
    MODE_EDIT = "edit"

    def __init__(self, book_service: BookService, book_id: int, parent=None):
        """Инициализация диалога.

        Args:
            book_service: Сервис для работы с книгами.
            book_id: ID книги.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._book_service = book_service
        self._book_id = book_id
        self._book: Optional[Book] = None
        self._mode = self.MODE_VIEW

        self._setup_ui()
        self._connect_signals()
        self._load_book()

    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса."""
        self.setWindowTitle("Карточка книги")
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
        self._title_label = QLabel("📖 Карточка книги")
        self._title_label.setObjectName("titleLabel")
        layout.addWidget(self._title_label)

        # Группа: данные книги
        fields_group = QGroupBox("Данные книги")
        form_layout = QFormLayout(fields_group)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignRight)

        self._isbn_input = QLineEdit()
        self._isbn_input.setPlaceholderText("ISBN")
        form_layout.addRow("ISBN:", self._isbn_input)

        self._author_input = QLineEdit()
        self._author_input.setPlaceholderText("Автор")
        form_layout.addRow("Автор:*", self._author_input)

        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Название")
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

        # Информация о QR
        self._qr_info = QLabel()
        self._qr_info.setWordWrap(True)
        layout.addWidget(self._qr_info)

        # Кнопки действий
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self._edit_button = QPushButton("✏️ Редактировать")
        self._edit_button.setMinimumHeight(36)
        buttons_layout.addWidget(self._edit_button)

        self._qr_button = QPushButton("📱 QR-код")
        self._qr_button.setObjectName("qrButton")
        self._qr_button.setMinimumHeight(36)
        buttons_layout.addWidget(self._qr_button)

        self._delete_button = QPushButton("🗑️ Удалить")
        self._delete_button.setObjectName("dangerButton")
        self._delete_button.setMinimumHeight(36)
        buttons_layout.addWidget(self._delete_button)

        self._save_button = QPushButton("💾 Сохранить")
        self._save_button.setObjectName("successButton")
        self._save_button.setMinimumHeight(36)
        self._save_button.setVisible(False)
        buttons_layout.addWidget(self._save_button)

        self._cancel_button = QPushButton("Отмена")
        self._cancel_button.setObjectName("secondaryButton")
        self._cancel_button.setMinimumHeight(36)
        self._cancel_button.setVisible(False)
        buttons_layout.addWidget(self._cancel_button)

        self._close_button = QPushButton("Закрыть")
        self._close_button.setMinimumHeight(36)
        buttons_layout.addWidget(self._close_button)

        layout.addLayout(buttons_layout)

        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _connect_signals(self) -> None:
        """Подключение сигналов."""
        self._edit_button.clicked.connect(self._on_edit)
        self._save_button.clicked.connect(self._on_save)
        self._cancel_button.clicked.connect(self._on_cancel_edit)
        self._delete_button.clicked.connect(self._on_delete)
        self._qr_button.clicked.connect(self._on_show_qr)
        self._close_button.clicked.connect(self.accept)

    def _load_book(self) -> None:
        """Загрузка данных книги."""
        try:
            self._book = self._book_service.get_book(self._book_id)
            if self._book is None:
                QMessageBox.critical(self, "Ошибка", "Книга не найдена.")
                self.reject()
                return
            self._populate_fields()
            self._set_mode(self.MODE_VIEW)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить книгу: {e}")
            self.reject()

    def _populate_fields(self) -> None:
        """Заполнение полей формы данными книги."""
        if self._book is None:
            return

        self._isbn_input.setText(self._book.isbn or "")
        self._author_input.setText(self._book.author)
        self._title_input.setText(self._book.title)
        self._publisher_input.setText(self._book.publisher or "")
        self._year_input.setValue(self._book.year if self._book.year else 0)
        self._udc_input.setText(self._book.udc or "")
        self._bbk_input.setText(self._book.bbk or "")
        self._author_mark_input.setText(self._book.author_mark or "")
        self._quantity_input.setValue(self._book.quantity)

        # Информация о QR — проверяем реальное существование файла
        if self._book.qr_path and os.path.exists(self._book.qr_path):
            self._qr_info.setText(f"✅ QR-код: {self._book.qr_path}")
            self._qr_info.setStyleSheet("color: #27ae60;")
        else:
            self._qr_info.setText("❌ QR-код не создан")
            self._qr_info.setStyleSheet("color: #e74c3c;")

    def _set_mode(self, mode: str) -> None:
        """Переключение между режимами просмотра и редактирования.

        Args:
            mode: Режим (MODE_VIEW или MODE_EDIT).
        """
        self._mode = mode
        is_edit = mode == self.MODE_EDIT

        # Поля ввода
        self._isbn_input.setReadOnly(not is_edit)
        self._author_input.setReadOnly(not is_edit)
        self._title_input.setReadOnly(not is_edit)
        self._publisher_input.setReadOnly(not is_edit)
        self._year_input.setReadOnly(not is_edit)
        self._udc_input.setReadOnly(not is_edit)
        self._bbk_input.setReadOnly(not is_edit)
        self._author_mark_input.setReadOnly(not is_edit)
        self._quantity_input.setReadOnly(not is_edit)

        # Кнопки
        self._edit_button.setVisible(not is_edit)
        self._qr_button.setVisible(not is_edit)
        self._delete_button.setVisible(not is_edit)
        self._close_button.setVisible(not is_edit)
        self._save_button.setVisible(is_edit)
        self._cancel_button.setVisible(is_edit)

        if is_edit:
            self.setWindowTitle("Редактирование книги")
            self._title_label.setText("✏️ Редактирование книги")
        else:
            self.setWindowTitle("Карточка книги")
            self._title_label.setText("📖 Карточка книги")

    def _on_edit(self) -> None:
        """Переключение в режим редактирования."""
        self._set_mode(self.MODE_EDIT)

    def _on_cancel_edit(self) -> None:
        """Отмена редактирования."""
        self._populate_fields()
        self._set_mode(self.MODE_VIEW)

    def _on_save(self) -> None:
        """Сохранение изменений."""
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

        if self._book is None:
            return

        # Обновляем поля книги
        self._book.isbn = self._isbn_input.text().strip() or None
        self._book.author = author
        self._book.title = title
        self._book.publisher = self._publisher_input.text().strip() or None
        self._book.year = self._year_input.value() if self._year_input.value() > 0 else None
        self._book.udc = self._udc_input.text().strip() or None
        self._book.bbk = self._bbk_input.text().strip() or None
        self._book.author_mark = self._author_mark_input.text().strip() or None
        self._book.quantity = self._quantity_input.value()

        try:
            self._book_service.update_book(self._book)
            # Перезагружаем книгу из БД, чтобы получить актуальное состояние
            # (например, обнулённый qr_path после удаления QR-кода)
            self._book = self._book_service.get_book(self._book_id)
            self._populate_fields()
            self._set_mode(self.MODE_VIEW)
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка валидации", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изменения: {e}")

    def _on_delete(self) -> None:
        """Удаление книги с подтверждением."""
        if self._book is None:
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить книгу\n"
            f"«{self._book.title}» {self._book.author}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                self._book_service.delete_book(self._book_id)
                QMessageBox.information(self, "Успех", "Книга удалена из каталога.")
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить книгу: {e}")

    def _on_show_qr(self) -> None:
        """Открытие диалога просмотра QR-кода."""
        if self._book is None:
            return

        from app.ui.qr_view_dialog import QRViewDialog

        # Если QR-кода нет, создаём его
        if not self._book.qr_path:
            try:
                qr_path = self._book_service._qr.generate_qr(
                    self._book.id, self._book.isbn
                )
                if qr_path:
                    self._book.qr_path = qr_path
                    self._book_service.set_qr_path(self._book.id, qr_path)
                    self._populate_fields()
                else:
                    QMessageBox.warning(
                        self, "Ошибка",
                        "Не удалось создать QR-код. Убедитесь, что библиотека qrcode установлена."
                    )
                    return
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать QR-код: {e}")
                return

        dialog = QRViewDialog(self._book.qr_path, self)
        dialog.exec_()