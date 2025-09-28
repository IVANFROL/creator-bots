# 🚀 Ручное развертывание на сервере

## 📋 Команды для выполнения на сервере

Подключитесь к серверу:
```bash
ssh root@217.25.90.191
# Пароль: uN4e#C*8rMv.ET
```

### 1. Подготовка сервера
```bash
# Обновляем систему
apt update && apt upgrade -y

# Устанавливаем необходимые пакеты
apt install -y python3 python3-pip python3-venv git nginx ufw

# Устанавливаем sshpass для автоматизации
apt install -y sshpass
```

### 2. Клонирование проекта
```bash
# Удаляем старую версию если есть
rm -rf /opt/creator-bots

# Клонируем проект
git clone https://github.com/IVANFROL/creator-bots.git /opt/creator-bots

# Переходим в директорию
cd /opt/creator-bots
```

### 3. Настройка Python окружения
```bash
# Создаем виртуальное окружение
python3 -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
```bash
# Создаем .env файл
cat > .env << 'EOF'
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
OPENAI_API_KEY=YOUR_OPENAI_API_KEY_HERE
ADMIN_USER_IDS=1704897414,6491802621
DATABASE_URL=sqlite:///bot_creator.db
EOF
```

### 5. Инициализация базы данных
```bash
# Инициализируем базу данных
python3 init_db.py
```

### 6. Настройка systemd сервиса
```bash
# Создаем systemd сервис
cat > /etc/systemd/system/bot-creator.service << 'EOF'
[Unit]
Description=Bot Creator Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/creator-bots
Environment=PATH=/opt/creator-bots/venv/bin
ExecStart=/opt/creator-bots/venv/bin/python start_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Перезагружаем systemd
systemctl daemon-reload

# Включаем автозапуск
systemctl enable bot-creator

# Запускаем сервис
systemctl start bot-creator
```

### 7. Настройка Nginx
```bash
# Создаем конфигурацию Nginx
cat > /etc/nginx/sites-available/bot-creator << 'EOF'
server {
    listen 80;
    server_name 217.25.90.191;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Активируем конфигурацию
ln -sf /etc/nginx/sites-available/bot-creator /etc/nginx/sites-enabled/

# Удаляем дефолтную конфигурацию
rm -f /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
nginx -t

# Перезагружаем Nginx
systemctl reload nginx
```

### 8. Настройка файрвола
```bash
# Настраиваем файрвол
ufw allow ssh
ufw allow 80
ufw allow 443
ufw --force enable
```

### 9. Проверка работы
```bash
# Проверяем статус сервиса
systemctl status bot-creator

# Проверяем логи
journalctl -u bot-creator -f

# Проверяем порты
netstat -tlnp | grep 8001
```

## 🎯 Результат

После выполнения всех команд:

- **Веб-админка:** http://217.25.90.191
- **Telegram бот:** работает в фоне
- **База данных:** SQLite в /opt/creator-bots/bot_creator.db
- **Логи:** journalctl -u bot-creator -f

## 🔧 Управление сервисом

```bash
# Запуск
systemctl start bot-creator

# Остановка
systemctl stop bot-creator

# Перезапуск
systemctl restart bot-creator

# Статус
systemctl status bot-creator

# Логи
journalctl -u bot-creator -f
```

## 🆘 Устранение неполадок

### Проблема: Сервис не запускается
```bash
# Проверяем логи
journalctl -u bot-creator -f

# Проверяем .env файл
cat /opt/creator-bots/.env

# Проверяем зависимости
cd /opt/creator-bots && source venv/bin/activate && pip list
```

### Проблема: Веб-админка недоступна
```bash
# Проверяем порт
netstat -tlnp | grep 8001

# Проверяем Nginx
systemctl status nginx

# Проверяем файрвол
ufw status
```

### Проблема: База данных
```bash
# Пересоздаем базу данных
cd /opt/creator-bots
rm bot_creator.db
python3 init_db.py
systemctl restart bot-creator
```