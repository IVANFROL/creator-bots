#!/bin/bash

# Скрипт развертывания Bot Creator на сервере

echo "🚀 Развертывание Bot Creator"
echo "=========================="

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "Создайте файл .env с вашими токенами:"
    echo "TELEGRAM_BOT_TOKEN=your_token_here"
    echo "OPENAI_API_KEY=your_key_here"
    echo "ADMIN_USER_IDS=your_telegram_id"
    exit 1
fi

# Создаем необходимые директории
mkdir -p bot_templates
mkdir -p generated_bots
mkdir -p static/css
mkdir -p static/js
mkdir -p templates

# Устанавливаем зависимости
echo "📦 Установка зависимостей..."
pip3 install -r requirements.txt

# Инициализируем базу данных
echo "📊 Инициализация базы данных..."
python3 init_db.py

# Запускаем сервис
echo "🎯 Запуск Bot Creator..."
echo "Веб-админка будет доступна по адресу: http://your-server:8001"
echo "Для остановки нажмите Ctrl+C"

python3 start_server.py
