# 🚀 Развертывание Bot Creator на сервере

## 📋 Требования

- **ОС:** Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **Python:** 3.10+
- **RAM:** 512MB+ (рекомендуется 1GB+)
- **Диск:** 1GB+ свободного места
- **Порты:** 8001 (веб-админка)

## ⚡ Быстрое развертывание

### 1. Подготовка сервера

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Устанавливаем Git
sudo apt install git -y
```

### 2. Клонирование проекта

```bash
# Клонируем репозиторий
git clone https://github.com/IVANFROL/creator-bots.git
cd creator-bots

# Создаем виртуальное окружение
python3 -m venv venv
source venv/bin/activate
```

### 3. Настройка переменных окружения

```bash
# Создаем файл .env
nano .env
```

**Содержимое .env:**
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
OPENAI_API_KEY=your_openai_api_key_here
ADMIN_USER_IDS=your_telegram_id_1,your_telegram_id_2
DATABASE_URL=sqlite:///bot_creator.db
```

### 4. Запуск

```bash
# Делаем скрипт исполняемым
chmod +x deploy.sh

# Запускаем развертывание
./deploy.sh
```

## 🐳 Развертывание с Docker

### 1. Установка Docker

```bash
# Устанавливаем Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Устанавливаем Docker Compose
sudo apt install docker-compose -y
```

### 2. Настройка

```bash
# Создаем .env файл
nano .env
```

### 3. Запуск

```bash
# Запускаем контейнер
docker-compose up -d

# Проверяем статус
docker-compose ps
```

## 🔧 Ручная установка

### 1. Установка зависимостей

```bash
pip3 install -r requirements.txt
```

### 2. Инициализация базы данных

```bash
python3 init_db.py
```

### 3. Запуск сервисов

```bash
# Запуск бота и веб-админки
python3 start_server.py
```

## 🌐 Настройка веб-сервера (Nginx)

### 1. Установка Nginx

```bash
sudo apt install nginx -y
```

### 2. Создание конфигурации

```bash
sudo nano /etc/nginx/sites-available/bot-creator
```

**Содержимое конфигурации:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Активация конфигурации

```bash
sudo ln -s /etc/nginx/sites-available/bot-creator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 Настройка SSL (Let's Encrypt)

```bash
# Устанавливаем Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получаем SSL сертификат
sudo certbot --nginx -d your-domain.com
```

## 🚀 Автозапуск (Systemd)

### 1. Создание сервиса

```bash
sudo nano /etc/systemd/system/bot-creator.service
```

**Содержимое сервиса:**
```ini
[Unit]
Description=Bot Creator Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/creator-bots
Environment=PATH=/home/ubuntu/creator-bots/venv/bin
ExecStart=/home/ubuntu/creator-bots/venv/bin/python start_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Активация сервиса

```bash
sudo systemctl daemon-reload
sudo systemctl enable bot-creator
sudo systemctl start bot-creator
sudo systemctl status bot-creator
```

## 📊 Мониторинг

### Проверка статуса

```bash
# Статус сервиса
sudo systemctl status bot-creator

# Логи
sudo journalctl -u bot-creator -f

# Проверка портов
netstat -tlnp | grep 8001
```

### Перезапуск

```bash
sudo systemctl restart bot-creator
```

## 🔧 Обновление

```bash
# Останавливаем сервис
sudo systemctl stop bot-creator

# Обновляем код
git pull origin main

# Устанавливаем новые зависимости
pip3 install -r requirements.txt

# Запускаем сервис
sudo systemctl start bot-creator
```

## 📱 Доступ к системе

После развертывания система будет доступна по адресу:

- **Веб-админка:** http://your-server:8001
- **API:** http://your-server:8001/api/stats

## 🛡️ Безопасность

### 1. Настройка файрвола

```bash
# Разрешаем SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 2. Регулярные обновления

```bash
# Автоматические обновления безопасности
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 📋 Чек-лист развертывания

- [ ] Сервер подготовлен (Python 3.10+, RAM 512MB+)
- [ ] Проект склонирован
- [ ] .env файл создан с токенами
- [ ] Зависимости установлены
- [ ] База данных инициализирована
- [ ] Сервис запущен
- [ ] Веб-админка доступна
- [ ] Nginx настроен (опционально)
- [ ] SSL сертификат установлен (опционально)
- [ ] Автозапуск настроен (опционально)

## 🆘 Устранение неполадок

### Проблема: Сервис не запускается

```bash
# Проверяем логи
sudo journalctl -u bot-creator -f

# Проверяем .env файл
cat .env

# Проверяем зависимости
pip3 list | grep flask
```

### Проблема: Веб-админка недоступна

```bash
# Проверяем порт
netstat -tlnp | grep 8001

# Проверяем файрвол
sudo ufw status
```

### Проблема: База данных

```bash
# Пересоздаем базу данных
rm bot_creator.db
python3 init_db.py
```

## 📞 Поддержка

При возникновении проблем:

1. Проверьте логи: `sudo journalctl -u bot-creator -f`
2. Проверьте статус: `sudo systemctl status bot-creator`
3. Проверьте порты: `netstat -tlnp | grep 8001`
4. Проверьте .env файл: `cat .env`

**Система готова к развертыванию на любом сервере!** 🎉
