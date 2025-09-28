import openai
from typing import Dict, Any
from config import Config
import json
import re

class AIService:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    
    def generate_bot_code(self, user_prompt: str, bot_type: str = "general") -> Dict[str, Any]:
        """
        Генерирует код бота на основе пользовательского запроса
        """
        try:
            system_prompt = self._get_system_prompt(bot_type)
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            generated_content = response.choices[0].message.content
            
            # Извлекаем код из ответа
            code = self._extract_code_from_response(generated_content)
            
            # Генерируем дополнительные файлы
            additional_files = self._generate_additional_files(user_prompt, bot_type)
            
            return {
                "main_code": code,
                "additional_files": additional_files,
                "description": self._extract_description(generated_content),
                "requirements": self._extract_requirements(generated_content),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }
    
    def _get_system_prompt(self, bot_type: str) -> str:
        """Генерирует системный промпт для создания бота"""
        base_prompt = """
        Ты - эксперт по созданию Telegram ботов. Создай профессиональный код бота на Python с использованием библиотеки python-telegram-bot.
        
        Требования:
        1. Используй современный синтаксис python-telegram-bot (версия 20+)
        2. Добавь обработку ошибок
        3. Включи логирование
        4. Создай структурированный код с классами
        5. Добавь конфигурационный файл
        6. Включи requirements.txt
        7. Добавь README.md с инструкциями
        
        Верни код в формате:
        ```python
        # main.py
        [код бота]
        ```
        
        ```python
        # config.py
        [конфигурация]
        ```
        
        ```txt
        # requirements.txt
        [зависимости]
        ```
        
        ```markdown
        # README.md
        [инструкции]
        ```
        """
        
        if bot_type == "ecommerce":
            base_prompt += "\n\nСпециально для e-commerce бота добавь:\n- Каталог товаров\n- Корзину\n- Обработку заказов\n- Интеграцию с платежными системами"
        elif bot_type == "support":
            base_prompt += "\n\nСпециально для support бота добавь:\n- Систему тикетов\n- FAQ\n- Переадресацию к операторам\n- Базу знаний"
        elif bot_type == "news":
            base_prompt += "\n\nСпециально для news бота добавь:\n- Парсинг новостей\n- Категории\n- Подписки\n- Рассылки"
        
        return base_prompt
    
    def _extract_code_from_response(self, response: str) -> str:
        """Извлекает код из ответа AI"""
        # Ищем код между ```python и ```
        python_pattern = r'```python\s*\n(.*?)\n```'
        matches = re.findall(python_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0]
        
        # Если не найден python блок, ищем любой код
        code_pattern = r'```\s*\n(.*?)\n```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0]
        
        return response
    
    def _extract_description(self, response: str) -> str:
        """Извлекает описание бота из ответа"""
        # Простое извлечение описания - первые несколько строк до кода
        lines = response.split('\n')
        description_lines = []
        
        for line in lines:
            if line.strip().startswith('```'):
                break
            if line.strip():
                description_lines.append(line.strip())
        
        return ' '.join(description_lines[:3])  # Первые 3 строки
    
    def _extract_requirements(self, response: str) -> list:
        """Извлекает зависимости из requirements.txt"""
        requirements_pattern = r'```txt\s*\n(.*?)\n```'
        matches = re.findall(requirements_pattern, response, re.DOTALL)
        
        if matches:
            return [line.strip() for line in matches[0].split('\n') if line.strip()]
        
        # Стандартные зависимости
        return [
            "python-telegram-bot==20.7",
            "python-dotenv==1.0.0",
            "requests==2.31.0"
        ]
    
    def _generate_additional_files(self, user_prompt: str, bot_type: str) -> Dict[str, str]:
        """Генерирует дополнительные файлы для бота"""
        additional_files = {}
        
        # Генерируем config.py
        config_content = f'''import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
'''
        additional_files['config.py'] = config_content
        
        # Генерируем .env.example
        env_content = '''BOT_TOKEN=your_bot_token_here
WEBHOOK_URL=https://yourdomain.com/webhook
HOST=0.0.0.0
PORT=8000
DEBUG=False
'''
        additional_files['.env.example'] = env_content
        
        return additional_files
    
    def analyze_bot_requirements(self, user_prompt: str) -> str:
        """Анализирует требования пользователя и определяет тип бота"""
        prompt_lower = user_prompt.lower()
        
        if any(word in prompt_lower for word in ['магазин', 'товар', 'заказ', 'корзина', 'ecommerce', 'e-commerce']):
            return "ecommerce"
        elif any(word in prompt_lower for word in ['поддержка', 'support', 'помощь', 'тикет', 'faq']):
            return "support"
        elif any(word in prompt_lower for word in ['новости', 'news', 'рассылка', 'канал']):
            return "news"
        else:
            return "general"
