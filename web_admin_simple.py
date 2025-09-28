from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

class AdminService:
    def __init__(self):
        pass
    
    def get_demo_data(self):
        """Возвращает демонстрационные данные для работы без базы данных"""
        return {
            "stats": {
                "total_users": 5,
                "premium_users": 3,
                "total_bots": 5,
                "active_bots": 4,
                "recent_users": 2,
                "recent_bots": 3,
                "recent_generations": 7,
                "monthly_revenue": 897,
                "total_revenue": 10764
            },
            "users": [
                {
                    "id": 1,
                    "telegram_id": 1704897414,
                    "username": "admin_user",
                    "first_name": "Админ",
                    "last_name": "Пользователь",
                    "is_premium": True,
                    "free_generations_used": 2,
                    "premium_generations_used": 5,
                    "created_at": "2024-01-15T10:30:00Z",
                    "last_activity": "2024-01-15T10:30:00Z",
                    "bots_count": 2,
                    "is_admin": True
                },
                {
                    "id": 2,
                    "telegram_id": 6491802621,
                    "username": "ilya_ttr",
                    "first_name": "Илья",
                    "last_name": "Тестер",
                    "is_premium": True,
                    "free_generations_used": 2,
                    "premium_generations_used": 3,
                    "created_at": "2024-01-14T15:45:00Z",
                    "last_activity": "2024-01-14T15:45:00Z",
                    "bots_count": 1,
                    "is_admin": True
                }
            ],
            "bots": [
                {
                    "id": 1,
                    "name": "Помощник по программированию",
                    "description": "Бот помогает с вопросами по программированию",
                    "status": "active",
                    "owner_username": "admin_user",
                    "created_at": "2024-01-15T10:30:00Z",
                    "last_updated": "2024-01-15T10:30:00Z"
                },
                {
                    "id": 2,
                    "name": "Консультант по бизнесу",
                    "description": "Бот консультирует по вопросам бизнеса",
                    "status": "active",
                    "owner_username": "ilya_ttr",
                    "created_at": "2024-01-14T15:45:00Z",
                    "last_updated": "2024-01-14T15:45:00Z"
                }
            ],
            "generations": [
                {
                    "id": 1,
                    "user_username": "admin_user",
                    "bot_name": "Помощник по программированию",
                    "prompt": "Создай бота для помощи с программированием",
                    "status": "completed",
                    "created_at": "2024-01-15T10:30:00Z",
                    "completed_at": "2024-01-15T10:30:00Z"
                },
                {
                    "id": 2,
                    "user_username": "ilya_ttr",
                    "bot_name": "Консультант по бизнесу",
                    "prompt": "Создай бота-консультанта по бизнесу",
                    "status": "completed",
                    "created_at": "2024-01-14T15:45:00Z",
                    "completed_at": "2024-01-14T15:45:00Z"
                }
            ]
        }

# Маршруты
@app.route("/")
def dashboard():
    """Главная страница - Dashboard"""
    try:
        admin_service = AdminService()
        demo_data = admin_service.get_demo_data()
        
        return render_template("dashboard.html", 
            stats=demo_data["stats"],
            recent_users=demo_data["users"][:2],
            recent_bots=demo_data["bots"][:2],
            recent_generations=demo_data["generations"][:2]
        )
    except Exception as e:
        logger.error(f"Ошибка в dashboard: {e}")
        return render_template("error.html", error="Ошибка загрузки dashboard")

@app.route("/users")
def users():
    """Страница управления пользователями"""
    try:
        admin_service = AdminService()
        demo_data = admin_service.get_demo_data()
        
        return render_template("users.html", users=demo_data["users"])
    except Exception as e:
        logger.error(f"Ошибка в users: {e}")
        return render_template("error.html", error="Ошибка загрузки пользователей")

@app.route("/bots")
def bots():
    """Страница управления ботами"""
    try:
        admin_service = AdminService()
        demo_data = admin_service.get_demo_data()
        
        return render_template("bots.html", bots=demo_data["bots"])
    except Exception as e:
        logger.error(f"Ошибка в bots: {e}")
        return render_template("error.html", error="Ошибка загрузки ботов")

@app.route("/generations")
def generations():
    """Страница истории генераций"""
    try:
        admin_service = AdminService()
        demo_data = admin_service.get_demo_data()
        
        return render_template("generations.html", generations=demo_data["generations"])
    except Exception as e:
        logger.error(f"Ошибка в generations: {e}")
        return render_template("error.html", error="Ошибка загрузки генераций")

@app.route("/monetization")
def monetization():
    """Страница монетизации"""
    try:
        admin_service = AdminService()
        demo_data = admin_service.get_demo_data()
        
        return render_template("monetization.html", stats=demo_data["stats"])
    except Exception as e:
        logger.error(f"Ошибка в monetization: {e}")
        return render_template("error.html", error="Ошибка загрузки монетизации")

@app.route("/admins")
def admins():
    """Страница управления админами"""
    try:
        admin_service = AdminService()
        demo_data = admin_service.get_demo_data()
        admins_list = [user for user in demo_data["users"] if user.get('is_admin', False)]
        
        return render_template("admins.html", admins=admins_list, all_users=demo_data["users"])
    except Exception as e:
        logger.error(f"Ошибка в admins: {e}")
        return render_template("error.html", error="Ошибка загрузки админов")

@app.route("/user-management")
def user_management():
    """Страница управления попытками и подписками"""
    try:
        return render_template("user_management.html")
    except Exception as e:
        logger.error(f"Ошибка в user_management: {e}")
        return render_template("error.html", error="Ошибка загрузки страницы управления")

# API маршруты
@app.route("/api/stats")
def api_stats():
    """API для получения статистики"""
    try:
        admin_service = AdminService()
        demo_data = admin_service.get_demo_data()
        return jsonify(demo_data["stats"])
    except Exception as e:
        logger.error(f"Ошибка в api_stats: {e}")
        return jsonify({"error": "Ошибка получения статистики"}), 500

@app.route("/api/payments")
def api_payments():
    """API для получения данных о платежах"""
    try:
        admin_service = AdminService()
        demo_data = admin_service.get_demo_data()
        stats = demo_data["stats"]
        
        payments_data = {
            "total_revenue": stats["total_revenue"],
            "monthly_revenue": stats["monthly_revenue"],
            "premium_users": stats["premium_users"],
            "conversion_rate": (stats["premium_users"] / max(stats["total_users"], 1)) * 100,
            "recent_payments": [
                {
                    "id": 1,
                    "user_id": 1,
                    "amount": 299,
                    "currency": "RUB",
                    "status": "completed",
                    "created_at": "2024-01-15T10:30:00Z"
                },
                {
                    "id": 2,
                    "user_id": 2,
                    "amount": 299,
                    "currency": "RUB",
                    "status": "completed",
                    "created_at": "2024-01-14T15:45:00Z"
                }
            ]
        }
        
        return jsonify(payments_data)
    except Exception as e:
        logger.error(f"Ошибка в api_payments: {e}")
        return jsonify({"error": "Ошибка получения данных о платежах"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)
