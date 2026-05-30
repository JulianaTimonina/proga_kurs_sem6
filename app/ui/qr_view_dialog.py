"""Диалог просмотра QR-кода книги.

Отображает QR-код и позволяет сохранить его как PNG-файл.
"""

import os
import shutil

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
)


class QRViewDialog(QDialog):
    """Диалог просмотра QR-кода."""

    def __init__(self, qr_path: str, parent=None):
        """Инициализация диалога.

        Args:
            qr_path: Путь к файлу QR-кода.
            parent: Родительский виджет.
        """
        super().__init__(parent)
        self._qr_path = qr_path

        self._setup_ui()
        self._connect_signals()
        self._load_qr()

    def _setup_ui(self) -> None:
        """Настройка пользовательского интерфейса."""
        self.setWindowTitle("QR-код книги")
        self.setMinimumWidth(400)
        self.setMinimumHeight(480)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignCenter)

        # Заголовок
        title = QLabel("📱 QR-код книги")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Изображение QR-кода
        self._qr_label = QLabel()
        self._qr_label.setAlignment(Qt.AlignCenter)
        self._qr_label.setMinimumSize(300, 300)
        self._qr_label.setStyleSheet(
            "background-color: white; border: 2px solid #dcdde1; border-radius: 8px; padding: 10px;"
        )
        layout.addWidget(self._qr_label, 1)

        # Информация о файле
        self._info_label = QLabel()
        self._info_label.setAlignment(Qt.AlignCenter)
        self._info_label.setStyleSheet("color: #636e72; font-size: 12px;")
        layout.addWidget(self._info_label)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self._save_button = QPushButton("💾 Сохранить PNG")
        self._save_button.setObjectName("successButton")
        self._save_button.setMinimumHeight(36)
        buttons_layout.addWidget(self._save_button)

        self._close_button = QPushButton("Закрыть")
        self._close_button.setMinimumHeight(36)
        buttons_layout.addWidget(self._close_button)

        layout.addLayout(buttons_layout)

    def _connect_signals(self) -> None:
        """Подключение сигналов."""
        self._save_button.clicked.connect(self._on_save)
        self._close_button.clicked.connect(self.accept)

    def _load_qr(self) -> None:
        """Загрузка и отображение QR-кода."""
        if not self._qr_path or not os.path.exists(self._qr_path):
            self._qr_label.setText("❌ Файл QR-кода не найден")
            self._qr_label.setStyleSheet(
                "color: #e74c3c; font-size: 16px; "
                "background-color: white; border: 2px solid #dcdde1; "
                "border-radius: 8px; padding: 10px;"
            )
            self._save_button.setEnabled(False)
            return

        pixmap = QPixmap(self._qr_path)
        if pixmap.isNull():
            self._qr_label.setText("❌ Не удалось загрузить изображение")
            self._save_button.setEnabled(False)
            return

        # Масштабируем изображение с сохранением пропорций
        scaled = pixmap.scaled(
            300, 300,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._qr_label.setPixmap(scaled)

        # Информация о файле
        file_size = os.path.getsize(self._qr_path)
        filename = os.path.basename(self._qr_path)
        self._info_label.setText(f"Файл: {filename}  |  Размер: {file_size} байт")

    def _on_save(self) -> None:
        """Сохранение QR-кода в выбранную директорию."""
        if not self._qr_path or not os.path.exists(self._qr_path):
            return

        default_name = os.path.basename(self._qr_path)
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить QR-код",
            default_name,
            "PNG-изображение (*.png)",
        )

        if not save_path:
            return

        try:
            shutil.copy2(self._qr_path, save_path)
            QMessageBox.information(
                self, "Успех",
                f"QR-код сохранён:\n{save_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка",
                f"Не удалось сохранить файл: {e}",
            )