# 🚀 Развертывание на Vercel

## Пошаговая инструкция

### 1. Подготовка базы данных

**Важно:** Vercel не поддерживает SQLite. Нужна PostgreSQL база данных.

#### Вариант 1: Supabase (Рекомендуется)
1. Перейдите на [supabase.com](https://supabase.com)
2. Создайте новый проект
3. Скопируйте строку подключения из Settings > Database
4. Формат: `postgresql://user:password@host:port/database`

#### Вариант 2: Neon
1. Перейдите на [neon.tech](https://neon.tech)
2. Создайте новый проект
3. Скопируйте строку подключения

### 2. Развертывание на Vercel

1. **Перейдите на [vercel.com](https://vercel.com)**
2. **Нажмите "New Project"**
3. **Выберите репозиторий `IVANFROL/creator-bots`**
4. **Нажмите "Deploy"**

### 3. Настройка переменных окружения

В настройках проекта Vercel добавьте:

```bash
# Обязательные переменные
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
ADMIN_USER_IDS=your_telegram_id_1,your_telegram_id_2

# База данных (замените на вашу строку подключения)
DATABASE_URL=postgresql://user:password@host:port/database

# Опциональные
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

### 4. Проверка развертывания

После деплоя:
1. Откройте URL вашего проекта
2. Веб-админка должна загрузиться
3. База данных инициализируется автоматически

## 🔧 Структура проекта для Vercel

```
creator-bots/
├── api/
│   └── index.py          # Точка входа для Vercel
├── templates/            # HTML шаблоны
├── static/              # CSS и JS файлы
├── web_admin.py         # Flask приложение
├── database.py          # Модели БД
├── init_vercel_db.py    # Инициализация БД для Vercel
├── vercel.json          # Конфигурация Vercel
└── requirements.txt     # Python зависимости
```

## 📱 После развертывания

### Веб-админка будет доступна по URL Vercel:

- **Dashboard** - `/` - статистика
- **Пользователи** - `/users` - управление пользователями
- **Боты** - `/bots` - управление ботами
- **Генерации** - `/generations` - история генераций
- **Монетизация** - `/monetization` - настройки платежей
- **Управление пользователями** - `/user-management` - добавление попыток
- **Админы** - `/admins` - управление администраторами

### API доступно по базовому URL:

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

## 🐛 Решение проблем

### Ошибка базы данных
- Убедитесь, что `DATABASE_URL` правильно настроен
- Проверьте, что база данных доступна

### Ошибка 500
- Проверьте логи в Vercel Dashboard
- Убедитесь, что все переменные окружения установлены

### Ошибка импорта
- Убедитесь, что все зависимости в `requirements.txt`

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи в Vercel Dashboard
2. Убедитесь, что база данных работает
3. Проверьте переменные окружения
4. Обратитесь к администратору

## 🎯 Готово!

После выполнения всех шагов у вас будет:
- ✅ Веб-админка на Vercel
- ✅ PostgreSQL база данных
- ✅ API для управления пользователями
- ✅ Система попыток и подписок
- ✅ Красивый интерфейс