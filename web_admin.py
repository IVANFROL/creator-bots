from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from sqlalchemy.orm import Session
from database import get_db, User, Bot, Generation, create_tables
from config import Config
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import uuid

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # В продакшене используйте случайный ключ

class AdminService:
    def __init__(self):
        pass
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """Получает статистику системы"""
        total_users = db.query(User).count()
        premium_users = db.query(User).filter(User.is_premium == True).count()
        total_bots = db.query(Bot).count()
        active_bots = db.query(Bot).filter(Bot.status == 'active').count()
        
        # Статистика за последние 30 дней
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_users = db.query(User).filter(User.created_at >= thirty_days_ago).count()
        recent_bots = db.query(Bot).filter(Bot.created_at >= thirty_days_ago).count()
        recent_generations = db.query(Generation).filter(Generation.created_at >= thirty_days_ago).count()
        
        # Статистика доходов (имитация)
        monthly_revenue = premium_users * 299  # 299₽ за Premium
        total_revenue = monthly_revenue * 12  # Годовая выручка
        
        return {
            "total_users": total_users,
            "premium_users": premium_users,
            "total_bots": total_bots,
            "active_bots": active_bots,
            "recent_users": recent_users,
            "recent_bots": recent_bots,
            "recent_generations": recent_generations,
            "monthly_revenue": monthly_revenue,
            "total_revenue": total_revenue
        }
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Получает список пользователей"""
        users = db.query(User).offset(skip).limit(limit).all()
        
        result = []
        for user in users:
            user_data = {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_premium": user.is_premium,
                "free_generations_used": user.free_generations_used,
                "premium_generations_used": user.premium_generations_used,
                "created_at": user.created_at.isoformat(),
                "last_activity": user.last_activity.isoformat() if user.last_activity else None,
                "bots_count": len(user.bots),
                "is_admin": user.telegram_id in Config.ADMIN_USER_IDS
            }
            result.append(user_data)
        
        return result
    
    def get_bots(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Получает список ботов"""
        bots = db.query(Bot).offset(skip).limit(limit).all()
        
        result = []
        for bot in bots:
            bot_data = {
                "id": bot.id,
                "name": bot.name,
                "description": bot.description,
                "status": bot.status,
                "owner_id": bot.owner_id,
                "owner_username": bot.owner.username if bot.owner else None,
                "created_at": bot.created_at.isoformat(),
                "last_updated": bot.last_updated.isoformat() if bot.last_updated else None
            }
            result.append(bot_data)
        
        return result
    
    def get_generations(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Получает список генераций"""
        generations = db.query(Generation).offset(skip).limit(limit).all()
        
        result = []
        for gen in generations:
            gen_data = {
                "id": gen.id,
                "user_id": gen.user_id,
                "bot_id": gen.bot_id,
                "prompt": gen.prompt,
                "status": gen.status,
                "created_at": gen.created_at.isoformat(),
                "completed_at": gen.completed_at.isoformat() if gen.completed_at else None,
                "user_username": gen.user.username if gen.user else None,
                "bot_name": gen.bot.name if gen.bot else None
            }
            result.append(gen_data)
        
        return result
    
    def get_recent_users(self, db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Получает последних пользователей"""
        users = db.query(User).order_by(User.created_at.desc()).limit(limit).all()
        return self.get_users(db, 0, limit)
    
    def get_recent_bots(self, db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Получает последних ботов"""
        bots = db.query(Bot).order_by(Bot.created_at.desc()).limit(limit).all()
        return self.get_bots(db, 0, limit)
    
    def get_recent_generations(self, db: Session, limit: int = 5) -> List[Dict[str, Any]]:
        """Получает последние генерации"""
        generations = db.query(Generation).order_by(Generation.created_at.desc()).limit(limit).all()
        return self.get_generations(db, 0, limit)

# Маршруты
@app.route("/")
def dashboard():
    """Главная страница - Dashboard"""
    try:
        db = next(get_db())
        admin_service = AdminService()
        stats = admin_service.get_statistics(db)
        recent_users = admin_service.get_recent_users(db, limit=5)
        recent_bots = admin_service.get_recent_bots(db, limit=5)
        recent_generations = admin_service.get_recent_generations(db, limit=5)
        
        return render_template("dashboard.html", 
            stats=stats,
            recent_users=recent_users,
            recent_bots=recent_bots,
            recent_generations=recent_generations
        )
    except Exception as e:
        logger.error(f"Ошибка в dashboard: {e}")
        return render_template("error.html", error="Ошибка загрузки dashboard")
    finally:
        db.close()

@app.route("/users")
def users():
    """Страница управления пользователями"""
    try:
        db = next(get_db())
        admin_service = AdminService()
        users_list = admin_service.get_users(db)
        
        return render_template("users.html", users=users_list)
    except Exception as e:
        logger.error(f"Ошибка в users: {e}")
        return render_template("error.html", error="Ошибка загрузки пользователей")
    finally:
        db.close()

@app.route("/bots")
def bots():
    """Страница управления ботами"""
    try:
        db = next(get_db())
        admin_service = AdminService()
        bots_list = admin_service.get_bots(db)
        
        return render_template("bots.html", bots=bots_list)
    except Exception as e:
        logger.error(f"Ошибка в bots: {e}")
        return render_template("error.html", error="Ошибка загрузки ботов")
    finally:
        db.close()

@app.route("/generations")
def generations():
    """Страница истории генераций"""
    try:
        db = next(get_db())
        admin_service = AdminService()
        generations_list = admin_service.get_generations(db)
        
        return render_template("generations.html", generations=generations_list)
    except Exception as e:
        logger.error(f"Ошибка в generations: {e}")
        return render_template("error.html", error="Ошибка загрузки генераций")
    finally:
        db.close()

@app.route("/monetization")
def monetization():
    """Страница монетизации"""
    try:
        db = next(get_db())
        admin_service = AdminService()
        stats = admin_service.get_statistics(db)
        
        return render_template("monetization.html", stats=stats)
    except Exception as e:
        logger.error(f"Ошибка в monetization: {e}")
        return render_template("error.html", error="Ошибка загрузки монетизации")
    finally:
        db.close()

@app.route("/admins")
def admins():
    """Страница управления админами"""
    try:
        db = next(get_db())
        admin_service = AdminService()
        users_list = admin_service.get_users(db)
        admins_list = [user for user in users_list if user.get('is_admin', False)]
        
        return render_template("admins.html", admins=admins_list, all_users=users_list)
    except Exception as e:
        logger.error(f"Ошибка в admins: {e}")
        return render_template("error.html", error="Ошибка загрузки админов")
    finally:
        db.close()

@app.route("/user-management")
def user_management():
    """Страница управления попытками и подписками"""
    try:
        return render_template("user_management.html")
    except Exception as e:
        logger.error(f"Ошибка в user_management: {e}")
        return render_template("error.html", error="Ошибка загрузки страницы управления")

@app.route("/bot/<int:bot_id>")
def bot_details(bot_id):
    """Детали конкретного бота"""
    try:
        db = next(get_db())
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        
        if not bot:
            return render_template("error.html", error="Бот не найден")
        
        bot_data = {
            "id": bot.id,
            "name": bot.name,
            "description": bot.description,
            "status": bot.status,
            "token": bot.token,
            "generated_code": bot.generated_code,
            "owner_id": bot.owner_id,
            "owner_username": bot.owner.username if bot.owner else None,
            "created_at": bot.created_at.isoformat(),
            "last_updated": bot.last_updated.isoformat() if bot.last_updated else None
        }
        
        return render_template("bot_details.html", bot=bot_data)
    except Exception as e:
        logger.error(f"Ошибка в bot_details: {e}")
        return render_template("error.html", error="Ошибка загрузки деталей бота")
    finally:
        db.close()

# API маршруты
@app.route("/api/stats")
def api_stats():
    """API для получения статистики"""
    try:
        db = next(get_db())
        admin_service = AdminService()
        stats = admin_service.get_statistics(db)
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Ошибка в api_stats: {e}")
        return jsonify({"error": "Ошибка получения статистики"}), 500
    finally:
        db.close()

@app.route("/api/users/<int:user_id>/toggle-status", methods=["POST"])
def api_toggle_user_status(user_id):
    """API для переключения статуса пользователя"""
    try:
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404
        
        # Здесь можно добавить логику блокировки/разблокировки
        # user.is_blocked = not user.is_blocked
        # db.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Ошибка в api_toggle_user_status: {e}")
        return jsonify({"error": "Ошибка изменения статуса"}), 500
    finally:
        db.close()

@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    """API для удаления пользователя"""
    try:
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404
        
        # Удаляем пользователя и связанные данные
        db.delete(user)
        db.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Ошибка в api_delete_user: {e}")
        return jsonify({"error": "Ошибка удаления пользователя"}), 500
    finally:
        db.close()

@app.route("/api/bots/<int:bot_id>/toggle-status", methods=["POST"])
def api_toggle_bot_status(bot_id):
    """API для переключения статуса бота"""
    try:
        db = next(get_db())
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        
        if not bot:
            return jsonify({"error": "Бот не найден"}), 404
        
        # Переключаем статус
        if bot.status == 'active':
            bot.status = 'inactive'
        else:
            bot.status = 'active'
        
        db.commit()
        
        return jsonify({"success": True, "status": bot.status})
    except Exception as e:
        logger.error(f"Ошибка в api_toggle_bot_status: {e}")
        return jsonify({"error": "Ошибка изменения статуса бота"}), 500
    finally:
        db.close()

@app.route("/api/bots/<int:bot_id>", methods=["DELETE"])
def api_delete_bot(bot_id):
    """API для удаления бота"""
    try:
        db = next(get_db())
        bot = db.query(Bot).filter(Bot.id == bot_id).first()
        
        if not bot:
            return jsonify({"error": "Бот не найден"}), 404
        
        # Удаляем бота
        db.delete(bot)
        db.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Ошибка в api_delete_bot: {e}")
        return jsonify({"error": "Ошибка удаления бота"}), 500
    finally:
        db.close()

@app.route("/api/admins", methods=["POST"])
def api_add_admin():
    """API для добавления админа"""
    try:
        data = request.get_json()
        telegram_id = data.get('telegram_id')
        
        if not telegram_id:
            return jsonify({"error": "Telegram ID не указан"}), 400
        
        # Добавляем в конфиг
        if telegram_id not in Config.ADMIN_USER_IDS:
            Config.ADMIN_USER_IDS.append(telegram_id)
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Ошибка в api_add_admin: {e}")
        return jsonify({"error": "Ошибка добавления админа"}), 500

@app.route("/api/admins/<int:telegram_id>", methods=["DELETE"])
def api_remove_admin(telegram_id):
    """API для удаления админа"""
    try:
        if telegram_id in Config.ADMIN_USER_IDS:
            Config.ADMIN_USER_IDS.remove(telegram_id)
        
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Ошибка в api_remove_admin: {e}")
        return jsonify({"error": "Ошибка удаления админа"}), 500

@app.route("/api/payments")
def api_payments():
    """API для получения данных о платежах"""
    try:
        db = next(get_db())
        admin_service = AdminService()
        stats = admin_service.get_statistics(db)
        
        # Имитация данных о платежах
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
    finally:
        db.close()

@app.route("/api/users/search", methods=["POST"])
def api_search_user():
    """API для поиска пользователя по Telegram никнейму"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({"error": "Никнейм не указан"}), 400
        
        # Убираем @ если есть
        if username.startswith('@'):
            username = username[1:]
        
        db = next(get_db())
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404
        
        user_data = {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_premium": user.is_premium,
            "free_generations_used": user.free_generations_used,
            "premium_generations_used": user.premium_generations_used,
            "free_generations_limit": user.free_generations_limit,
            "premium_generations_limit": user.premium_generations_limit,
            "premium_expires_at": user.premium_expires_at.isoformat() if user.premium_expires_at else None,
            "created_at": user.created_at.isoformat(),
            "last_activity": user.last_activity.isoformat() if user.last_activity else None
        }
        
        return jsonify({"success": True, "user": user_data})
    except Exception as e:
        logger.error(f"Ошибка в api_search_user: {e}")
        return jsonify({"error": "Ошибка поиска пользователя"}), 500
    finally:
        db.close()

@app.route("/api/users/<int:user_id>/add-generations", methods=["POST"])
def api_add_generations(user_id):
    """API для добавления попыток пользователю"""
    try:
        data = request.get_json()
        free_generations = data.get('free_generations', 0)
        premium_generations = data.get('premium_generations', 0)
        
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404
        
        # Добавляем попытки
        if free_generations > 0:
            user.free_generations_limit += free_generations
        
        if premium_generations > 0:
            user.premium_generations_limit += premium_generations
        
        db.commit()
        
        return jsonify({
            "success": True,
            "message": f"Добавлено {free_generations} бесплатных и {premium_generations} премиум попыток",
            "user": {
                "free_generations_limit": user.free_generations_limit,
                "premium_generations_limit": user.premium_generations_limit
            }
        })
    except Exception as e:
        logger.error(f"Ошибка в api_add_generations: {e}")
        return jsonify({"error": "Ошибка добавления попыток"}), 500
    finally:
        db.close()

@app.route("/api/users/<int:user_id>/set-premium", methods=["POST"])
def api_set_premium(user_id):
    """API для установки премиум подписки"""
    try:
        data = request.get_json()
        days = data.get('days', 30)  # По умолчанию 30 дней
        is_premium = data.get('is_premium', True)
        
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404
        
        if is_premium:
            # Устанавливаем премиум подписку
            user.is_premium = True
            user.premium_expires_at = datetime.utcnow() + timedelta(days=days)
            user.premium_generations_limit = 50  # Сбрасываем лимит
            user.premium_generations_used = 0  # Сбрасываем использованные
        else:
            # Убираем премиум подписку
            user.is_premium = False
            user.premium_expires_at = None
        
        db.commit()
        
        return jsonify({
            "success": True,
            "message": f"Премиум подписка {'установлена' if is_premium else 'отменена'} на {days} дней",
            "user": {
                "is_premium": user.is_premium,
                "premium_expires_at": user.premium_expires_at.isoformat() if user.premium_expires_at else None
            }
        })
    except Exception as e:
        logger.error(f"Ошибка в api_set_premium: {e}")
        return jsonify({"error": "Ошибка установки премиум подписки"}), 500
    finally:
        db.close()

@app.route("/api/users/<int:user_id>/reset-generations", methods=["POST"])
def api_reset_generations(user_id):
    """API для сброса использованных попыток"""
    try:
        data = request.get_json()
        reset_free = data.get('reset_free', True)
        reset_premium = data.get('reset_premium', True)
        
        db = next(get_db())
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404
        
        if reset_free:
            user.free_generations_used = 0
        
        if reset_premium:
            user.premium_generations_used = 0
        
        db.commit()
        
        return jsonify({
            "success": True,
            "message": "Использованные попытки сброшены",
            "user": {
                "free_generations_used": user.free_generations_used,
                "premium_generations_used": user.premium_generations_used
            }
        })
    except Exception as e:
        logger.error(f"Ошибка в api_reset_generations: {e}")
        return jsonify({"error": "Ошибка сброса попыток"}), 500
    finally:
        db.close()

if __name__ == "__main__":
    # Создаем таблицы при запуске
    create_tables()
    
    # Инициализируем тестовые данные для локальной разработки
    try:
        from init_db import init_database
        init_database()
    except Exception as e:
        print(f"Ошибка инициализации БД: {e}")
    
    # Запускаем Flask приложение
    app.run(host="0.0.0.0", port=8001, debug=True)