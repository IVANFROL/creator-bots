# 🚀 Развертывание на Vercel

## Подготовка к деплою

### 1. Настройка переменных окружения в Vercel

Перейдите в настройки проекта в Vercel и добавьте следующие переменные окружения:

```bash
# Обязательные переменные
TELEGRAM_BOT_TOKEN=ваш_telegram_bot_token
OPENAI_API_KEY=ваш_openai_api_key
ADMIN_USER_IDS=1704897414,6491802621

# Опциональные переменные
DATABASE_URL=sqlite:///bot_creator.db
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### 2. Структура проекта для Vercel

Проект уже настроен для Vercel с файлом `vercel.json`:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "web_admin.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "web_admin.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.10"
  }
}
```

### 3. Развертывание

1. **Подключите GitHub репозиторий к Vercel:**
   - Зайдите на [vercel.com](https://vercel.com)
   - Нажмите "New Project"
   - Выберите репозиторий `IVANFROL/creator-bots`
   - Нажмите "Deploy"

2. **Настройте переменные окружения:**
   - В настройках проекта перейдите в "Environment Variables"
   - Добавьте все необходимые переменные
   - Перезапустите деплой

3. **Проверьте деплой:**
   - Vercel автоматически создаст URL для вашего проекта
   - Веб-админка будет доступна по этому URL

## 🔧 Локальная разработка

### Запуск локально

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/IVANFROL/creator-bots.git
cd creator-bots
```

2. **Создайте файл .env:**
```bash
cp env.example .env
# Отредактируйте .env с вашими API ключами
```

3. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

4. **Инициализируйте базу данных:**
```bash
python3 init_db.py
```

5. **Запустите веб-админку:**
```bash
python3 web_admin.py
```

6. **Запустите Telegram бота:**
```bash
python3 main.py
```

## 📱 Использование

### Веб-админка

После развертывания веб-админка будет доступна по URL Vercel:

- **Dashboard** - `/` - статистика и обзор
- **Пользователи** - `/users` - управление пользователями
- **Боты** - `/bots` - управление ботами
- **Генерации** - `/generations` - история генераций
- **Монетизация** - `/monetization` - настройки платежей
- **Управление пользователями** - `/user-management` - добавление попыток и подписок
- **Админы** - `/admins` - управление администраторами

### API

Все API маршруты доступны по базовому URL Vercel:

```bash
# Поиск пользователя
POST https://your-app.vercel.app/api/users/search
{
  "username": "telegram_username"
}

# Добавление попыток
POST https://your-app.vercel.app/api/users/{user_id}/add-generations
{
  "free_generations": 10,
  "premium_generations": 20
}
```

## 🔐 Безопасность

- Все API ключи хранятся в переменных окружения Vercel
- Админские функции защищены проверкой Telegram ID
- База данных SQLite создается автоматически при первом запуске

## 🐛 Отладка

### Логи Vercel

Просматривайте логи в панели Vercel:
- Перейдите в проект
- Откройте вкладку "Functions"
- Выберите функцию и просмотрите логи

### Локальная отладка

```bash
# Запуск с отладкой
python3 web_admin.py

# Проверка переменных окружения
python3 -c "from config import Config; print(Config.TELEGRAM_BOT_TOKEN)"
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в Vercel
2. Убедитесь, что все переменные окружения установлены
3. Проверьте, что API ключи действительны
4. Обратитесь к администратору системы
