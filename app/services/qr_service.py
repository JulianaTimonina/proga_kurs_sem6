import json
import os
from typing import Optional


class QrService:
    """Сервис для генерации и удаления QR-кодов книг.

    QR-код содержит JSON с id книги и ISBN.
    """

    def __init__(self, output_dir: str = "data/qr_codes"):
        """Инициализация QR-сервиса.

        Args:
            output_dir: Директория для сохранения QR-кодов.
        """
        self._output_dir = output_dir

    def generate_qr(
        self,
        book_id: int,
        isbn: Optional[str],
        output_dir: Optional[str] = None,
    ) -> Optional[str]:
        """Генерирует QR-код с JSON-данными книги.

        Данные в QR: {"id": <book_id>, "isbn": <isbn или null>}

        Args:
            book_id: ID книги.
            isbn: ISBN книги (может быть None).
            output_dir: Переопределение директории вывода (опционально).

        Returns:
            Путь к созданному PNG-файлу или None при ошибке.
        """
        try:
            import qrcode
        except ImportError:
            return None

        try:
            dir_path = output_dir or self._output_dir
            os.makedirs(dir_path, exist_ok=True)

            # Формируем данные для QR
            qr_data = json.dumps({"id": book_id, "isbn": isbn}, ensure_ascii=False)

            # Генерируем QR-код
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)

            # Создаём изображение
            img = qr.make_image(fill_color="black", back_color="white")

            # Сохраняем файл
            filename = f"qr_book_{book_id}.png"
            filepath = os.path.join(dir_path, filename)
            img.save(filepath)

            return filepath

        except Exception:
            return None

    def delete_qr(self, qr_path: str) -> None:
        """Удаляет файл QR-кода с диска.

        Args:
            qr_path: Путь к файлу QR-кода.
        """
        try:
            if qr_path and os.path.exists(qr_path):
                os.remove(qr_path)
        except OSError:
            pass  # Игнорируем ошибки удаления файла