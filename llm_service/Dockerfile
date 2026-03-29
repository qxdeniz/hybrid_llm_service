FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование приложения
COPY app.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Копирование Python модуля
COPY ../llm_module ./llm_module

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
