from web_admin import app, create_tables
from init_vercel_db import init_vercel_database

# Инициализируем базу данных при первом запуске
try:
    create_tables()
    init_vercel_database()
except Exception as e:
    print(f"Ошибка инициализации БД: {e}")

# Экспортируем Flask приложение для Vercel
handler = app
