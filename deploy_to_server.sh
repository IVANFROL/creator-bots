#!/bin/bash

# Скрипт автоматического развертывания на сервере
# Использование: ./deploy_to_server.sh

SERVER_IP="217.25.90.191"
SERVER_USER="root"
SERVER_PASS="uN4e#C*8rMv.ET"
PROJECT_NAME="creator-bots"

echo "🚀 Развертывание Bot Creator на сервере $SERVER_IP"
echo "=================================================="

# Функция для выполнения команд на сервере
run_on_server() {
    sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "$1"
}

# Функция для копирования файлов на сервер
copy_to_server() {
    sshpass -p "$SERVER_PASS" scp -o StrictHostKeyChecking=no -r "$1" "$SERVER_USER@$SERVER_IP:$2"
}

echo "📦 Подготовка сервера..."

# Обновляем систему и устанавливаем необходимые пакеты
run_on_server "apt update && apt upgrade -y"
run_on_server "apt install -y python3 python3-pip python3-venv git nginx ufw sshpass"

echo "📁 Клонирование проекта..."

# Удаляем старую версию если есть
run_on_server "rm -rf /opt/$PROJECT_NAME"

# Клонируем проект
run_on_server "git clone https://github.com/IVANFROL/creator-bots.git /opt/$PROJECT_NAME"

echo "🔧 Настройка проекта..."

# Переходим в директорию проекта
run_on_server "cd /opt/$PROJECT_NAME"

# Создаем виртуальное окружение
run_on_server "cd /opt/$PROJECT_NAME && python3 -m venv venv"

# Активируем виртуальное окружение и устанавливаем зависимости
run_on_server "cd /opt/$PROJECT_NAME && source venv/bin/activate && pip install -r requirements.txt"

echo "🔑 Настройка переменных окружения..."

# Создаем .env файл на сервере
run_on_server "cat > /opt/$PROJECT_NAME/.env << 'EOF'
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
ADMIN_USER_IDS=1704897414,6491802621
DATABASE_URL=sqlite:///bot_creator.db
EOF"

echo "📊 Инициализация базы данных..."

# Инициализируем базу данных
run_on_server "cd /opt/$PROJECT_NAME && source venv/bin/activate && python3 init_db.py"

echo "🔧 Настройка systemd сервиса..."

# Создаем systemd сервис
run_on_server "cat > /etc/systemd/system/bot-creator.service << 'EOF'
[Unit]
Description=Bot Creator Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/$PROJECT_NAME
Environment=PATH=/opt/$PROJECT_NAME/venv/bin
ExecStart=/opt/$PROJECT_NAME/venv/bin/python start_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"

# Перезагружаем systemd и запускаем сервис
run_on_server "systemctl daemon-reload"
run_on_server "systemctl enable bot-creator"
run_on_server "systemctl start bot-creator"

echo "🌐 Настройка Nginx..."

# Создаем конфигурацию Nginx
run_on_server "cat > /etc/nginx/sites-available/bot-creator << 'EOF'
server {
    listen 80;
    server_name $SERVER_IP;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF"

# Активируем конфигурацию
run_on_server "ln -sf /etc/nginx/sites-available/bot-creator /etc/nginx/sites-enabled/"
run_on_server "rm -f /etc/nginx/sites-enabled/default"
run_on_server "nginx -t && systemctl reload nginx"

echo "🔥 Настройка файрвола..."

# Настраиваем файрвол
run_on_server "ufw allow ssh"
run_on_server "ufw allow 80"
run_on_server "ufw allow 443"
run_on_server "ufw --force enable"

echo "✅ Проверка статуса..."

# Проверяем статус сервиса
run_on_server "systemctl status bot-creator --no-pager"

echo "🎉 Развертывание завершено!"
echo "=================================================="
echo "🌐 Веб-админка: http://$SERVER_IP"
echo "🤖 Telegram бот: @your_bot_username"
echo "📊 Статус: systemctl status bot-creator"
echo "📝 Логи: journalctl -u bot-creator -f"
echo "🔄 Перезапуск: systemctl restart bot-creator"
echo "=================================================="