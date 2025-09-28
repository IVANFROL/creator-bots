#!/usr/bin/env python3
"""
Скрипт инициализации базы данных с тестовыми данными
"""

from database import create_tables, User, Bot, Generation, SessionLocal
from datetime import datetime, timedelta
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Инициализирует базу данных с тестовыми данными"""
    try:
        # Создаем таблицы
        create_tables()
        logger.info("📊 Таблицы базы данных созданы")
        
        # Создаем сессию
        db = SessionLocal()
        
        # Проверяем, есть ли уже данные
        if db.query(User).count() > 0:
            logger.info("📊 База данных уже содержит данные")
            db.close()
            return
        
        # Создаем тестовых пользователей
        users_data = [
            {
                "telegram_id": 1704897414,
                "username": "admin_user",
                "first_name": "Админ",
                "last_name": "Пользователь",
                "is_premium": True,
                "free_generations_used": 2,
                "premium_generations_used": 5,
                "free_generations_limit": 2,
                "premium_generations_limit": 50,
                "premium_expires_at": datetime.utcnow() + timedelta(days=30)
            },
            {
                "telegram_id": 6491802621,
                "username": "ilya_ttr",
                "first_name": "Илья",
                "last_name": "Тестер",
                "is_premium": True,
                "free_generations_used": 2,
                "premium_generations_used": 3,
                "free_generations_limit": 2,
                "premium_generations_limit": 50,
                "premium_expires_at": datetime.utcnow() + timedelta(days=15)
            },
            {
                "telegram_id": 123456789,
                "username": "test_user1",
                "first_name": "Тест",
                "last_name": "Пользователь1",
                "is_premium": False,
                "free_generations_used": 1,
                "premium_generations_used": 0,
                "free_generations_limit": 2,
                "premium_generations_limit": 0,
                "premium_expires_at": None
            },
            {
                "telegram_id": 987654321,
                "username": "test_user2",
                "first_name": "Тест",
                "last_name": "Пользователь2",
                "is_premium": False,
                "free_generations_used": 2,
                "premium_generations_used": 0,
                "free_generations_limit": 2,
                "premium_generations_limit": 0,
                "premium_expires_at": None
            },
            {
                "telegram_id": 555666777,
                "username": "premium_user",
                "first_name": "Премиум",
                "last_name": "Пользователь",
                "is_premium": True,
                "free_generations_used": 2,
                "premium_generations_used": 8,
                "free_generations_limit": 2,
                "premium_generations_limit": 50,
                "premium_expires_at": datetime.utcnow() + timedelta(days=7)
            }
        ]
        
        users = []
        for user_data in users_data:
            user = User(**user_data)
            users.append(user)
            db.add(user)
        
        db.commit()
        logger.info(f"👥 Создано {len(users)} пользователей")
        
        # Создаем тестовых ботов
        bots_data = [
            {
                "name": "Помощник по программированию",
                "description": "Бот помогает с вопросами по программированию",
                "token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "owner_id": users[0].id,
                "status": "active",
                "generated_code": "print('Hello, World!')"
            },
            {
                "name": "Консультант по бизнесу",
                "description": "Бот консультирует по вопросам бизнеса",
                "token": "2345678901:BCDEFGHIJKLMNOPQRSTUVWXYZ",
                "owner_id": users[1].id,
                "status": "active",
                "generated_code": "def business_advice(): pass"
            },
            {
                "name": "Помощник по изучению языков",
                "description": "Бот помогает изучать иностранные языки",
                "token": "3456789012:CDEFGHIJKLMNOPQRSTUVWXYZ",
                "owner_id": users[2].id,
                "status": "inactive",
                "generated_code": "def language_lesson(): pass"
            },
            {
                "name": "Финансовый советник",
                "description": "Бот дает советы по финансам",
                "token": "4567890123:DEFGHIJKLMNOPQRSTUVWXYZ",
                "owner_id": users[3].id,
                "status": "active",
                "generated_code": "def financial_advice(): pass"
            },
            {
                "name": "Фитнес-тренер",
                "description": "Бот помогает с тренировками",
                "token": "5678901234:EFGHIJKLMNOPQRSTUVWXYZ",
                "owner_id": users[4].id,
                "status": "active",
                "generated_code": "def workout_plan(): pass"
            }
        ]
        
        bots = []
        for bot_data in bots_data:
            bot = Bot(**bot_data)
            bots.append(bot)
            db.add(bot)
        
        db.commit()
        logger.info(f"🤖 Создано {len(bots)} ботов")
        
        # Создаем тестовые генерации
        generations_data = [
            {
                "user_id": users[0].id,
                "bot_id": bots[0].id,
                "prompt": "Создай бота для помощи с программированием",
                "generated_code": "def programming_helper(): pass",
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=5),
                "completed_at": datetime.utcnow() - timedelta(days=5)
            },
            {
                "user_id": users[1].id,
                "bot_id": bots[1].id,
                "prompt": "Создай бота-консультанта по бизнесу",
                "generated_code": "def business_consultant(): pass",
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=4),
                "completed_at": datetime.utcnow() - timedelta(days=4)
            },
            {
                "user_id": users[2].id,
                "bot_id": bots[2].id,
                "prompt": "Создай бота для изучения английского",
                "generated_code": "def english_teacher(): pass",
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=3),
                "completed_at": datetime.utcnow() - timedelta(days=3)
            },
            {
                "user_id": users[3].id,
                "bot_id": bots[3].id,
                "prompt": "Создай бота-финансового советника",
                "generated_code": "def financial_advisor(): pass",
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=2),
                "completed_at": datetime.utcnow() - timedelta(days=2)
            },
            {
                "user_id": users[4].id,
                "bot_id": bots[4].id,
                "prompt": "Создай бота-фитнес-тренера",
                "generated_code": "def fitness_trainer(): pass",
                "status": "completed",
                "created_at": datetime.utcnow() - timedelta(days=1),
                "completed_at": datetime.utcnow() - timedelta(days=1)
            },
            {
                "user_id": users[0].id,
                "bot_id": None,
                "prompt": "Создай бота для управления задачами",
                "generated_code": None,
                "status": "pending",
                "created_at": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "user_id": users[1].id,
                "bot_id": None,
                "prompt": "Создай бота для заказа еды",
                "generated_code": None,
                "status": "failed",
                "created_at": datetime.utcnow() - timedelta(hours=1)
            }
        ]
        
        generations = []
        for gen_data in generations_data:
            generation = Generation(**gen_data)
            generations.append(generation)
            db.add(generation)
        
        db.commit()
        logger.info(f"📝 Создано {len(generations)} генераций")
        
        db.close()
        logger.info("✅ База данных успешно инициализирована с тестовыми данными")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")
        raise

if __name__ == "__main__":
    init_database()
