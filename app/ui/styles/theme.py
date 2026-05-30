"""Стилизация UI (QSS).

Современная светлая цветовая схема для библиотечного каталога.
"""

MAIN_STYLE = """
/* === Глобальные стили === */
QMainWindow, QDialog {
    background-color: #f5f6fa;
    font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
}

/* === Заголовки === */
QLabel#titleLabel {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
    padding: 8px 0;
}

QLabel#sectionLabel {
    font-size: 14px;
    font-weight: 600;
    color: #34495e;
    padding: 4px 0;
}

/* === Кнопки === */
QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #2471a3;
}

QPushButton:disabled {
    background-color: #bdc3c7;
    color: #95a5a6;
}

QPushButton#dangerButton {
    background-color: #e74c3c;
}

QPushButton#dangerButton:hover {
    background-color: #c0392b;
}

QPushButton#successButton {
    background-color: #27ae60;
}

QPushButton#successButton:hover {
    background-color: #219a52;
}

QPushButton#secondaryButton {
    background-color: #95a5a6;
}

QPushButton#secondaryButton:hover {
    background-color: #7f8c8d;
}

QPushButton#ocrButton {
    background-color: #8e44ad;
}

QPushButton#ocrButton:hover {
    background-color: #7d3c98;
}

QPushButton#qrButton {
    background-color: #f39c12;
}

QPushButton#qrButton:hover {
    background-color: #d68910;
}

/* === Поля ввода === */
QLineEdit, QSpinBox {
    background-color: white;
    border: 2px solid #dcdde1;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    color: #2c3e50;
    min-height: 20px;
}

QLineEdit:focus, QSpinBox:focus {
    border-color: #3498db;
}

QLineEdit:read-only {
    background-color: #f1f2f6;
    color: #636e72;
}

/* === Выпадающие списки === */
QComboBox {
    background-color: white;
    border: 2px solid #dcdde1;
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
    color: #2c3e50;
    min-height: 20px;
}

QComboBox:focus {
    border-color: #3498db;
}

QComboBox::drop-down {
    border: 2px solid #dcdde1;
    border-radius: 6px;
}

/* === Таблица === */
QTableView {
    background-color: white;
    border: 1px solid #dcdde1;
    border-radius: 8px;
    gridline-color: #ecf0f1;
    selection-background-color: #3498db;
    selection-color: white;
    font-size: 13px;
}

QTableView::item {
    padding: 8px 12px;
}

QHeaderView::section {
    background-color: #f8f9fa;
    color: #2c3e50;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 12px;
    border: none;
    border-bottom: 2px solid #dcdde1;
}

QHeaderView::section:hover {
    background-color: #e8e9ed;
}

/* === Группы === */
QGroupBox {
    background-color: white;
    border: 1px solid #dcdde1;
    border-radius: 8px;
    margin-top: 12px;
    padding: 16px;
    padding-top: 28px;
    font-size: 13px;
    font-weight: 500;
    color: #2c3e50;
}

QGroupBox::title {
    color: #2c3e50;
    font-weight: 600;
    padding: 0 8px;
}

/* === Скроллбары === */
QScrollBar:vertical {
    background-color: #f1f2f6;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #bdc3c7;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background-color: #95a5a6;
}

/* === Статусбар === */
QStatusBar {
    background-color: #f8f9fa;
    border-top: 1px solid #dcdde1;
    color: #636e72;
    font-size: 12px;
    padding: 4px 12px;
}

/* === Текстовая метка === */
QLabel {
    color: #2c3e50;
    font-size: 13px;
}

/* === Сообщения === */
QMessageBox {
    background-color: #f5f6fa;
}

QMessageBox QLabel {
    font-size: 13px;
    color: #2c3e50;
}

/* === Разделители === */
QFrame[frameShape="4"] {  /* HLine */
    color: #dcdde1;
}

/* === Tooltip === */
QToolTip {
    background-color: #2c3e50;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
}
"""


def apply_theme(app) -> None:
    """Применяет стилизацию к QApplication.

    Args:
        app: Экземпляр QApplication.
    """
    app.setStyleSheet(MAIN_STYLE)