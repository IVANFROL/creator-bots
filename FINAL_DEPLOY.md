# 🚀 Финальное развертывание Bot Creator

## 📋 Данные сервера
- **IP:** 217.25.90.191
- **Пользователь:** root
- **Пароль:** uN4e#C*8rMv.ET

## ⚡ Быстрое развертывание

### 1. Подключение к серверу
```bash
ssh root@217.25.90.191
# Пароль: uN4e#C*8rMv.ET
```

### 2. Автоматическое развертывание
```bash
# Скачиваем скрипт
wget https://raw.githubusercontent.com/IVANFROL/creator-bots/main/deploy_to_server.sh
chmod +x deploy_to_server.sh
./deploy_to_server.sh
```

### 3. Настройка токенов
```bash
# Редактируем .env файл
nano /opt/creator-bots/.env
```

**Замените:**
- `YOUR_TELEGRAM_BOT_TOKEN_HERE` на ваш токен бота
- `YOUR_OPENAI_API_KEY_HERE` на ваш OpenAI ключ

### 4. Перезапуск сервиса
```bash
systemctl restart bot-creator
```

## 🎯 Результат

- **Веб-админка:** http://217.25.90.191
- **Telegram бот:** работает в фоне
- **Статус:** `systemctl status bot-creator`

## 🔧 Управление

```bash
# Статус
systemctl status bot-creator

# Логи
journalctl -u bot-creator -f

# Перезапуск
systemctl restart bot-creator
```

## ✅ Готово!

Система полностью развернута и готова к использованию! 🎉
