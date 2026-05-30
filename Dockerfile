FROM python:3.11-slim

# Установка системных зависимостей: Tesseract OCR (рус+анг), OpenGL для PyQt5, xvfb для headless
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-rus \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["xvfb-run", "python", "-m", "app.main"]