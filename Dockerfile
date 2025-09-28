FROM python:3.11-slim

# Устанавливаем системные зависимости и обновляем пакеты
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директории для логов и данных
RUN mkdir -p logs bot_templates generated_bots

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 botcreator && chown -R botcreator:botcreator /app
USER botcreator

# Открываем порты
EXPOSE 8000 8001

# Команда по умолчанию
CMD ["python", "run.py"]
