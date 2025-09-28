#!/usr/bin/env python3
"""
Скрипт для тестирования всех функций веб-админки
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_page(url, expected_text, page_name):
    """Тестирует загрузку страницы"""
    try:
        response = requests.get(f"{BASE_URL}{url}")
        if response.status_code == 200 and expected_text in response.text:
            print(f"✅ {page_name} - OK")
            return True
        else:
            print(f"❌ {page_name} - Ошибка (код: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ {page_name} - Ошибка: {e}")
        return False

def test_api(url, method="GET", data=None, api_name=""):
    """Тестирует API"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{url}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{url}", json=data)
        
        if response.status_code == 200:
            print(f"✅ API {api_name} - OK")
            return True
        else:
            print(f"❌ API {api_name} - Ошибка (код: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API {api_name} - Ошибка: {e}")
        return False

def main():
    print("🧪 Тестирование Bot Creator Admin")
    print("=" * 50)
    
    # Тестируем страницы
    print("\n📱 Тестирование страниц:")
    pages = [
        ("/", "Dashboard", "Главная страница"),
        ("/users", "Пользователи", "Страница пользователей"),
        ("/bots", "Боты", "Страница ботов"),
        ("/generations", "Генерации", "Страница генераций"),
        ("/monetization", "Монетизация", "Страница монетизации"),
        ("/user-management", "Управление пользователями", "Управление попытками"),
        ("/admins", "Админы", "Страница админов")
    ]
    
    page_results = []
    for url, expected_text, name in pages:
        result = test_page(url, expected_text, name)
        page_results.append(result)
        time.sleep(0.5)  # Небольшая пауза между запросами
    
    # Тестируем API
    print("\n🔌 Тестирование API:")
    api_tests = [
        ("/api/stats", "GET", None, "Статистика"),
        ("/api/payments", "GET", None, "Платежи"),
        ("/api/users/search", "POST", {"username": "ilya_ttr"}, "Поиск пользователя")
    ]
    
    api_results = []
    for url, method, data, name in api_tests:
        result = test_api(url, method, data, name)
        api_results.append(result)
        time.sleep(0.5)
    
    # Результаты
    print("\n📊 Результаты тестирования:")
    print("=" * 50)
    
    pages_ok = sum(page_results)
    pages_total = len(page_results)
    print(f"Страницы: {pages_ok}/{pages_total} работают")
    
    api_ok = sum(api_results)
    api_total = len(api_results)
    print(f"API: {api_ok}/{api_total} работают")
    
    total_ok = pages_ok + api_ok
    total_total = pages_total + api_total
    print(f"Общий результат: {total_ok}/{total_total} тестов пройдено")
    
    if total_ok == total_total:
        print("\n🎉 Все тесты пройдены! Система готова к демонстрации!")
    else:
        print(f"\n⚠️  {total_total - total_ok} тестов не пройдено. Проверьте систему.")
    
    print("\n🌐 Веб-админка доступна по адресу: http://localhost:8001")
    print("📝 Скрипт для демонстрации: demo_script.md")

if __name__ == "__main__":
    main()
