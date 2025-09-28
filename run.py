#!/usr/bin/env python3
"""
Скрипт запуска Bot Creator
Запускает основной бот и админ-панель
"""

import asyncio
import threading
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
    """Запускает веб-админку в отдельном потоке"""
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
    """Инициализирует базу данных с тестовыми данными"""
    from database import create_tables, User, Bot, Generation, SessionLocal
    from datetime import datetime, timedelta
    
    # Создаем таблицы
    create_tables()
    logger.info("📊 База данных инициализирована")
    
    # Создаем сессию
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже данные
        if db.query(User).count() > 0:
            logger.info("📊 База данных уже содержит данные")
            return
        
        # Создаем тестовых пользователей
        test_users = [
            User(
                telegram_id=1704897414,
                username="ilya_ttr",
                first_name="Илья",
                last_name="Админ",
                is_premium=True,
                free_generations_used=2,
                premium_generations_used=5,
                created_at=datetime.utcnow() - timedelta(days=5)
            ),
            User(
                telegram_id=6491802621,
                username="ilya_ttr",
                first_name="Илья",
                last_name="Пользователь",
                is_premium=True,
                free_generations_used=2,
                premium_generations_used=3,
                created_at=datetime.utcnow() - timedelta(days=10)
            ),
            User(
                telegram_id=123456789,
                username="test_user",
                first_name="Тест",
                last_name="Пользователь",
                is_premium=False,
                free_generations_used=1,
                created_at=datetime.utcnow() - timedelta(days=3)
            )
        ]
        
        for user in test_users:
            db.add(user)
        
        db.commit()
        logger.info("👥 Тестовые пользователи созданы")
        
        # Создаем тестовых ботов
        test_bots = [
            Bot(
                name="EcommerceBot_20241201_143022",
                description="Бот для интернет-магазина с каталогом товаров и корзиной",
                token="1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                owner_id=1,
                status="active",
                generated_code="# Ecommerce Bot Code\nprint('Hello from Ecommerce Bot!')",
                created_at=datetime.utcnow() - timedelta(days=3)
            ),
            Bot(
                name="SupportBot_20241201_150145",
                description="Бот поддержки с системой тикетов и FAQ",
                token="9876543210:ZYXWVUTSRQPONMLKJIHGFEDCBA",
                owner_id=2,
                status="created",
                generated_code="# Support Bot Code\nprint('Hello from Support Bot!')",
                created_at=datetime.utcnow() - timedelta(days=1)
            )
        ]
        
        for bot in test_bots:
            db.add(bot)
        
        db.commit()
        logger.info("🤖 Тестовые боты созданы")
        
        # Создаем тестовые генерации
        test_generations = [
            Generation(
                user_id=1,
                bot_id=1,
                prompt="Создай бота для интернет-магазина с каталогом товаров, корзиной и обработкой заказов",
                generated_code="# Ecommerce Bot Code\nprint('Hello from Ecommerce Bot!')",
                status="completed",
                created_at=datetime.utcnow() - timedelta(days=3),
                completed_at=datetime.utcnow() - timedelta(days=3, minutes=5)
            ),
            Generation(
                user_id=2,
                bot_id=2,
                prompt="Нужен бот поддержки с системой тикетов, FAQ и переадресацией к операторам",
                generated_code="# Support Bot Code\nprint('Hello from Support Bot!')",
                status="completed",
                created_at=datetime.utcnow() - timedelta(days=1),
                completed_at=datetime.utcnow() - timedelta(days=1, minutes=3)
            )
        ]
        
        for generation in test_generations:
            db.add(generation)
        
        db.commit()
        logger.info("⚡ Тестовые генерации созданы")
        
        # Выводим статистику
        total_users = db.query(User).count()
        premium_users = db.query(User).filter(User.is_premium == True).count()
        total_bots = db.query(Bot).count()
        active_bots = db.query(Bot).filter(Bot.status == 'active').count()
        total_generations = db.query(Generation).count()
        
        print(f"""
        📊 База данных инициализирована успешно!
        
        Статистика:
        • Пользователей: {total_users}
        • Premium пользователей: {premium_users}
        • Ботов: {total_bots}
        • Активных ботов: {active_bots}
        • Генераций: {total_generations}
        """)
        
    finally:
        db.close()

def main():
    """Основная функция запуска"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    🤖 BOT CREATOR 🤖                        ║
    ║                                                              ║
    ║  Профессиональный сервис создания Telegram ботов с ИИ        ║
    ║                                                              ║
    ║  Запускаем сервисы:                                          ║
    ║  • Telegram бот: Работает в Telegram                        ║
    ║  • Веб-админка: http://localhost:8001                       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Инициализируем базу данных
    init_database()
    
    # Запускаем веб-админку в отдельном потоке
    admin_thread = threading.Thread(target=run_admin_panel, daemon=True)
    admin_thread.start()
    
    # Небольшая задержка для запуска админки
    import time
    time.sleep(2)
    
    # Запускаем Telegram бота в основном потоке
    try:
        run_telegram_bot()
    except KeyboardInterrupt:
        logger.info("👋 Остановка сервисов...")
        print("\n👋 Bot Creator остановлен. До свидания!")

if __name__ == "__main__":
    main()
