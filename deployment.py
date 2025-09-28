import os
import subprocess
import shutil
from pathlib import Path
from database import Bot, SessionLocal
from config import Config
import logging

logger = logging.getLogger(__name__)

class BotDeploymentService:
    def __init__(self):
        self.db = SessionLocal()
        self.templates_dir = Path(Config.BOT_TEMPLATES_DIR)
        self.generated_dir = Path(Config.GENERATED_BOTS_DIR)
        
        # Создаем директории если их нет
        self.templates_dir.mkdir(exist_ok=True)
        self.generated_dir.mkdir(exist_ok=True)
    
    def create_bot_package(self, bot: Bot) -> str:
        """Создает пакет для развертывания бота"""
        try:
            # Создаем директорию для бота
            bot_dir = self.generated_dir / f"bot_{bot.id}"
            bot_dir.mkdir(exist_ok=True)
            
            # Создаем основные файлы
            self._create_main_file(bot, bot_dir)
            self._create_config_file(bot, bot_dir)
            self._create_requirements_file(bot, bot_dir)
            self._create_readme_file(bot, bot_dir)
            self._create_docker_files(bot, bot_dir)
            self._create_deployment_scripts(bot, bot_dir)
            
            # Обновляем статус бота
            bot.status = 'ready_for_deployment'
            self.db.commit()
            
            return str(bot_dir)
            
        except Exception as e:
            logger.error(f"Error creating bot package: {e}")
            bot.status = 'error'
            self.db.commit()
            raise
    
    def _create_main_file(self, bot: Bot, bot_dir: Path):
        """Создает основной файл бота"""
        main_file = bot_dir / "main.py"
        
        # Если есть сгенерированный код, используем его
        if bot.generated_code:
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(bot.generated_code)
        else:
            # Создаем базовый шаблон
            template = self._get_basic_bot_template()
            with open(main_file, 'w', encoding='utf-8') as f:
                f.write(template)
    
    def _create_config_file(self, bot: Bot, bot_dir: Path):
        """Создает конфигурационный файл"""
        config_file = bot_dir / "config.py"
        
        config_content = f'''import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Дополнительные настройки
    ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
'''
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
    
    def _create_requirements_file(self, bot: Bot, bot_dir: Path):
        """Создает файл зависимостей"""
        requirements_file = bot_dir / "requirements.txt"
        
        requirements = [
            "python-telegram-bot==20.7",
            "python-dotenv==1.0.0",
            "requests==2.31.0",
            "aiohttp==3.9.1",
            "gunicorn==21.2.0"
        ]
        
        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(requirements))
    
    def _create_readme_file(self, bot: Bot, bot_dir: Path):
        """Создает README файл с инструкциями"""
        readme_file = bot_dir / "README.md"
        
        readme_content = f'''# {bot.name}

{bot.description}

## Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```env
BOT_TOKEN=your_bot_token_here
WEBHOOK_URL=https://yourdomain.com/webhook
HOST=0.0.0.0
PORT=8000
DEBUG=False
ADMIN_IDS=123456789,987654321
```

### 3. Запуск бота
```bash
python main.py
```

## Развертывание с Docker

### 1. Сборка образа
```bash
docker build -t {bot.name.lower()}_bot .
```

### 2. Запуск контейнера
```bash
docker run -d --name {bot.name.lower()}_bot --env-file .env {bot.name.lower()}_bot
```

## Развертывание на сервере

### 1. Загрузка файлов
Загрузите все файлы на ваш сервер.

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка systemd сервиса
Создайте файл `/etc/systemd/system/{bot.name.lower()}_bot.service`:
```ini
[Unit]
Description={bot.name} Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 4. Запуск сервиса
```bash
sudo systemctl enable {bot.name.lower()}_bot
sudo systemctl start {bot.name.lower()}_bot
```

## Мониторинг

Проверьте статус бота:
```bash
sudo systemctl status {bot.name.lower()}_bot
```

Просмотр логов:
```bash
sudo journalctl -u {bot.name.lower()}_bot -f
```
'''
        
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _create_docker_files(self, bot: Bot, bot_dir: Path):
        """Создает Docker файлы"""
        # Dockerfile
        dockerfile = bot_dir / "Dockerfile"
        dockerfile_content = '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
'''
        
        with open(dockerfile, 'w', encoding='utf-8') as f:
            f.write(dockerfile_content)
        
        # docker-compose.yml
        compose_file = bot_dir / "docker-compose.yml"
        compose_content = f'''version: '3.8'

services:
  {bot.name.lower()}_bot:
    build: .
    container_name: {bot.name.lower()}_bot
    restart: unless-stopped
    env_file:
      - .env
    ports:
      - "8000:8000"
    volumes:
      - ./logs:/app/logs
'''
        
        with open(compose_file, 'w', encoding='utf-8') as f:
            f.write(compose_content)
    
    def _create_deployment_scripts(self, bot: Bot, bot_dir: Path):
        """Создает скрипты для развертывания"""
        # Скрипт для быстрого развертывания
        deploy_script = bot_dir / "deploy.sh"
        deploy_content = f'''#!/bin/bash

# Скрипт развертывания {bot.name}

echo "🚀 Начинаем развертывание {bot.name}..."

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден! Создайте его на основе .env.example"
    exit 1
fi

# Устанавливаем зависимости
echo "📦 Устанавливаем зависимости..."
pip install -r requirements.txt

# Создаем директорию для логов
mkdir -p logs

# Запускаем бота
echo "🤖 Запускаем бота..."
python main.py
'''
        
        with open(deploy_script, 'w', encoding='utf-8') as f:
            f.write(deploy_content)
        
        # Делаем скрипт исполняемым
        os.chmod(deploy_script, 0o755)
        
        # Скрипт для systemd
        systemd_script = bot_dir / "install_systemd.sh"
        systemd_content = f'''#!/bin/bash

# Установка {bot.name} как systemd сервиса

BOT_NAME="{bot.name.lower()}_bot"
SERVICE_FILE="/etc/systemd/system/$BOT_NAME.service"
CURRENT_DIR=$(pwd)

echo "🔧 Создаем systemd сервис для $BOT_NAME..."

# Создаем сервис файл
sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description={bot.name} Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем сервис
sudo systemctl enable $BOT_NAME

echo "✅ Сервис $BOT_NAME создан и включен!"
echo "Для запуска используйте: sudo systemctl start $BOT_NAME"
echo "Для проверки статуса: sudo systemctl status $BOT_NAME"
'''
        
        with open(systemd_script, 'w', encoding='utf-8') as f:
            f.write(systemd_content)
        
        os.chmod(systemd_script, 0o755)
    
    def _get_basic_bot_template(self) -> str:
        """Возвращает базовый шаблон бота"""
        return '''import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import Config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        f"Привет! Я бот, созданный с помощью Bot Creator.\\n"
        f"Твой ID: {update.effective_user.id}"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "Доступные команды:\\n"
        "/start - Начать работу\\n"
        "/help - Показать помощь"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Эхо-функция"""
    await update.message.reply_text(update.message.text)

def main():
    """Основная функция"""
    # Создаем приложение
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Запускаем бота
    print("Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()
'''
    
    def create_zip_package(self, bot: Bot) -> str:
        """Создает ZIP архив с ботом"""
        try:
            bot_dir = self.create_bot_package(bot)
            zip_path = f"{bot_dir}.zip"
            
            # Создаем ZIP архив
            shutil.make_archive(bot_dir, 'zip', bot_dir)
            
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating ZIP package: {e}")
            raise
    
    def get_deployment_status(self, bot_id: int) -> dict:
        """Возвращает статус развертывания бота"""
        bot = self.db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            return {"error": "Bot not found"}
        
        return {
            "bot_id": bot.id,
            "name": bot.name,
            "status": bot.status,
            "created_at": bot.created_at.isoformat(),
            "last_updated": bot.last_updated.isoformat()
        }
