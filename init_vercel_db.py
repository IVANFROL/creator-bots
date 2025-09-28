#!/usr/bin/env python3
"""
Скрипт инициализации базы данных для Vercel
"""

import os
from database import create_tables, User, Bot, Generation, SessionLocal
from datetime import datetime, timedelta
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_vercel_database():
    """Инициализирует базу данных для Vercel"""
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
        logger.info("✅ База данных успешно инициализирована для Vercel")
        
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации базы данных: {e}")
        raise

if __name__ == "__main__":
    init_vercel_database()
