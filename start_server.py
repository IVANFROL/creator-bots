#!/usr/bin/env python3
"""
Скрипт запуска Bot Creator на сервере
Запускает бота и веб-админку
"""

import asyncio
import threading
import subprocess
import sys
import os
from main import main as run_bot
from web_admin import app as admin_app
from config import Config
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_admin_panel():
    """Запускает веб-админку"""
    try:
        logger.info("🌐 Запускаем веб-админку...")
        admin_app.run(host="0.0.0.0", port=8001, debug=False)
    except Exception as e:
        logger.error(f"Ошибка запуска веб-админки: {e}")

def run_telegram_bot():
    """Запускает Telegram бота"""
    try:
        logger.info("🤖 Запускаем Telegram бота...")
        run_bot()
    except Exception as e:
        logger.error(f"Ошибка запуска бота: {e}")

def init_database():
    """Инициализирует базу данных"""
    from database import create_tables
    from init_db import init_database as init_db_func
    
    # Создаем таблицы
    create_tables()
    logger.info("📊 База данных инициализирована")
    
    # Инициализируем тестовые данные
    try:
        init_db_func()
        logger.info("✅ Тестовые данные загружены")
    except Exception as e:
        logger.warning(f"⚠️ Ошибка загрузки тестовых данных: {e}")

def main():
    """Основная функция для запуска бота и админ-панели"""
    print("🚀 Запуск Bot Creator")
    print("=" * 50)
    
    # Проверяем переменные окружения
    if not Config.TELEGRAM_BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN не установлен!")
        print("Создайте файл .env с вашими токенами")
        sys.exit(1)
    
    if not Config.OPENAI_API_KEY:
        print("❌ OPENAI_API_KEY не установлен!")
        print("Создайте файл .env с вашими токенами")
        sys.exit(1)
    
    # Инициализируем базу данных
    init_database()
    
    print("\n📋 Доступные сервисы:")
    print("🤖 Telegram Bot: Работает в фоне")
    print("🌐 Web Admin: http://0.0.0.0:8001")
    print("📊 Database: SQLite (bot_creator.db)")
    
    print("\n🎯 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Запускаем админ-панель в отдельном потоке
    admin_thread = threading.Thread(target=run_admin_panel)
    admin_thread.daemon = True
    admin_thread.start()
    
    # Запускаем Telegram бота в основном потоке
    try:
        run_telegram_bot()
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервисов...")
        sys.exit(0)

if __name__ == "__main__":
    main()
