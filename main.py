import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from database import User, Bot, Generation, create_tables, SessionLocal
from ai_service import AIService
from config import Config
import os
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotCreatorBot:
    def __init__(self):
        self.ai_service = AIService()
        self.db = SessionLocal()
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        user_id = user.id
        
        # Регистрируем пользователя в базе данных
        db_user = self.db.query(User).filter(User.telegram_id == user_id).first()
        if not db_user:
            db_user = User(
                telegram_id=user_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            self.db.add(db_user)
            self.db.commit()
        
        welcome_text = f"""
🤖 <b>Добро пожаловать в Bot Creator!</b>

Привет, {user.first_name}! Я помогу тебе создать собственного Telegram бота с помощью ИИ.

<b>Что я умею:</b>
• Создавать ботов по твоему описанию
• Генерировать готовый код
• Настраивать развертывание
• Предоставлять инструкции

<b>Лимиты:</b>
• 🆓 Бесплатно: {Config.FREE_GENERATIONS} генерации
• 💎 Premium: {Config.PREMIUM_GENERATIONS_PER_MONTH} генераций в месяц

<b>Твоя статистика:</b>
• Использовано бесплатных: {db_user.free_generations_used}/{Config.FREE_GENERATIONS}
• Premium статус: {'✅' if db_user.is_premium else '❌'}

Выбери действие:
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Создать бота", callback_data="create_bot")],
            [InlineKeyboardButton("📋 Мои боты", callback_data="my_bots")],
            [InlineKeyboardButton("💎 Premium", callback_data="premium")],
            [InlineKeyboardButton("ℹ️ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def create_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик создания бота"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        db_user = self.db.query(User).filter(User.telegram_id == user_id).first()
        
        # Проверяем лимиты
        if not db_user.is_premium and db_user.free_generations_used >= Config.FREE_GENERATIONS:
            await query.edit_message_text(
                "❌ <b>Лимит исчерпан!</b>\n\n"
                "Ты использовал все бесплатные генерации. "
                "Оформи Premium подписку для продолжения работы!",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💎 Оформить Premium", callback_data="premium")]])
            )
            return
        
        await query.edit_message_text(
            "🤖 <b>Создание нового бота</b>\n\n"
            "Опиши, какого бота ты хочешь создать:\n\n"
            "<i>Например:</i>\n"
            "• Бот для интернет-магазина с каталогом товаров\n"
            "• Бот поддержки с системой тикетов\n"
            "• Новостной бот с рассылками\n"
            "• Игровой бот с викторинами\n\n"
            "Просто напиши свое описание в следующем сообщении!",
            parse_mode='HTML'
        )
        
        # Устанавливаем состояние ожидания описания
        context.user_data['waiting_for_description'] = True
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        if context.user_data.get('waiting_for_description'):
            await self.process_bot_description(update, context)
        else:
            await update.message.reply_text(
                "Используй команды из меню или /start для начала работы! 🤖"
            )
    
    async def process_bot_description(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка описания бота от пользователя"""
        description = update.message.text
        user_id = update.effective_user.id
        
        # Убираем состояние ожидания
        context.user_data['waiting_for_description'] = False
        
        # Показываем процесс генерации
        processing_msg = await update.message.reply_text(
            "🔄 <b>Генерирую бота...</b>\n\n"
            "Это может занять несколько минут. Пожалуйста, подожди! ⏳",
            parse_mode='HTML'
        )
        
        try:
            # Определяем тип бота
            bot_type = self.ai_service.analyze_bot_requirements(description)
            
            # Генерируем код бота
            result = self.ai_service.generate_bot_code(description, bot_type)
            
            if result['status'] == 'error':
                await processing_msg.edit_text(
                    f"❌ <b>Ошибка генерации</b>\n\n{result['error']}\n\nПопробуй еще раз!",
                    parse_mode='HTML'
                )
                return
            
            # Сохраняем в базу данных
            db_user = self.db.query(User).filter(User.telegram_id == user_id).first()
            
            # Создаем запись о боте
            new_bot = Bot(
                name=f"Bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=result['description'],
                owner_id=db_user.id,
                generated_code=result['main_code'],
                status='created'
            )
            self.db.add(new_bot)
            
            # Создаем запись о генерации
            generation = Generation(
                user_id=db_user.id,
                bot_id=new_bot.id,
                prompt=description,
                generated_code=result['main_code'],
                status='completed',
                completed_at=datetime.utcnow()
            )
            self.db.add(generation)
            
            # Обновляем счетчик генераций
            if db_user.is_premium:
                db_user.premium_generations_used += 1
            else:
                db_user.free_generations_used += 1
            
            self.db.commit()
            
            # Отправляем результат
            await self.send_generated_bot(update, context, new_bot, result)
            
        except Exception as e:
            logger.error(f"Error generating bot: {e}")
            await processing_msg.edit_text(
                "❌ <b>Произошла ошибка</b>\n\nПопробуй еще раз или обратись в поддержку!",
                parse_mode='HTML'
            )
    
    async def send_generated_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE, bot: Bot, result: dict):
        """Отправляет сгенерированный бот пользователю"""
        bot_info = f"""
✅ <b>Бот успешно создан!</b>

<b>Название:</b> {bot.name}
<b>Описание:</b> {result['description']}
<b>Тип:</b> {bot.status}

<b>Что включено:</b>
• Основной код бота
• Конфигурационные файлы
• Requirements.txt
• README с инструкциями
        """
        
        keyboard = [
            [InlineKeyboardButton("📥 Скачать код", callback_data=f"download_{bot.id}")],
            [InlineKeyboardButton("🚀 Развернуть", callback_data=f"deploy_{bot.id}")],
            [InlineKeyboardButton("📋 Мои боты", callback_data="my_bots")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(bot_info, parse_mode='HTML', reply_markup=reply_markup)
        
        # Отправляем код как файл
        code_text = f"# {bot.name}\n# {result['description']}\n\n{result['main_code']}"
        await update.message.reply_document(
            document=code_text.encode(),
            filename=f"{bot.name}.py",
            caption="📄 Основной код бота"
        )
    
    async def my_bots(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показывает список ботов пользователя"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        db_user = self.db.query(User).filter(User.telegram_id == user_id).first()
        
        if not db_user or not db_user.bots:
            await query.edit_message_text(
                "📋 <b>Мои боты</b>\n\n"
                "У тебя пока нет созданных ботов.\n"
                "Создай свой первый бот!",
                parse_mode='HTML',
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚀 Создать бота", callback_data="create_bot")]])
            )
            return
        
        bots_text = "📋 <b>Мои боты</b>\n\n"
        keyboard = []
        
        for i, bot in enumerate(db_user.bots[:5], 1):  # Показываем первые 5 ботов
            status_emoji = "✅" if bot.status == "active" else "⏸️" if bot.status == "inactive" else "❌"
            bots_text += f"{i}. {status_emoji} <b>{bot.name}</b>\n"
            bots_text += f"   {bot.description[:50]}...\n"
            bots_text += f"   <i>Создан: {bot.created_at.strftime('%d.%m.%Y')}</i>\n\n"
            
            keyboard.append([InlineKeyboardButton(f"🔧 {bot.name}", callback_data=f"bot_details_{bot.id}")])
        
        keyboard.append([InlineKeyboardButton("🚀 Создать новый", callback_data="create_bot")])
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(bots_text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def premium(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик Premium подписки"""
        query = update.callback_query
        await query.answer()
        
        premium_text = """
💎 <b>Premium подписка</b>

<b>Преимущества Premium:</b>
• 🚀 {premium_gens} генераций в месяц
• ⚡ Приоритетная обработка
• 🛠️ Расширенные шаблоны
• 📞 Приоритетная поддержка
• 🔧 Автоматическое развертывание

<b>Стоимость:</b> 299₽/месяц

<b>Способы оплаты:</b>
• Банковская карта
• СБП
• ЮMoney
• QIWI
        """.format(premium_gens=Config.PREMIUM_GENERATIONS_PER_MONTH)
        
        keyboard = [
            [InlineKeyboardButton("💳 Оплатить", callback_data="pay_premium")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(premium_text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик помощи"""
        query = update.callback_query
        await query.answer()
        
        help_text = """
ℹ️ <b>Помощь</b>

<b>Как создать бота:</b>
1. Нажми "Создать бота"
2. Опиши, что должен делать бот
3. Получи готовый код
4. Разверни на сервере

<b>Примеры описаний:</b>
• "Бот для интернет-магазина с каталогом товаров и корзиной"
• "Бот поддержки с системой тикетов и FAQ"
• "Новостной бот с рассылками и категориями"
• "Игровой бот с викторинами и рейтингом"

<b>Поддержка:</b> @support_username
        """
        
        keyboard = [[InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(help_text, parse_mode='HTML', reply_markup=reply_markup)
    
    async def back_to_main(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Возврат в главное меню"""
        query = update.callback_query
        await query.answer()
        
        # Имитируем команду /start
        await self.start(update, context)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        data = query.data
        
        if data == "create_bot":
            await self.create_bot(update, context)
        elif data == "my_bots":
            await self.my_bots(update, context)
        elif data == "premium":
            await self.premium(update, context)
        elif data == "help":
            await self.help(update, context)
        elif data == "back_to_main":
            await self.back_to_main(update, context)
        elif data.startswith("download_"):
            bot_id = int(data.split("_")[1])
            await self.download_bot(update, context, bot_id)
        elif data.startswith("deploy_"):
            bot_id = int(data.split("_")[1])
            await self.deploy_bot(update, context, bot_id)
        elif data.startswith("bot_details_"):
            bot_id = int(data.split("_")[2])
            await self.show_bot_details(update, context, bot_id)
    
    async def download_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE, bot_id: int):
        """Скачивание кода бота"""
        query = update.callback_query
        await query.answer()
        
        bot = self.db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            await query.edit_message_text("❌ Бот не найден!")
            return
        
        # Отправляем код как файл
        code_text = f"# {bot.name}\n# {bot.description}\n\n{bot.generated_code}"
        await query.message.reply_document(
            document=code_text.encode(),
            filename=f"{bot.name}.py",
            caption=f"📄 Код бота: {bot.name}"
        )
    
    async def deploy_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE, bot_id: int):
        """Развертывание бота"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🚀 <b>Развертывание бота</b>\n\n"
            "Эта функция в разработке. Пока что скачай код и разверни самостоятельно!\n\n"
            "Инструкции по развертыванию будут добавлены в ближайшее время.",
            parse_mode='HTML'
        )
    
    async def show_bot_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE, bot_id: int):
        """Показывает детали бота"""
        query = update.callback_query
        await query.answer()
        
        bot = self.db.query(Bot).filter(Bot.id == bot_id).first()
        if not bot:
            await query.edit_message_text("❌ Бот не найден!")
            return
        
        status_emoji = "✅" if bot.status == "active" else "⏸️" if bot.status == "inactive" else "❌"
        
        details_text = f"""
🔧 <b>Детали бота</b>

<b>Название:</b> {bot.name}
<b>Описание:</b> {bot.description}
<b>Статус:</b> {status_emoji} {bot.status}
<b>Создан:</b> {bot.created_at.strftime('%d.%m.%Y %H:%M')}
<b>Обновлен:</b> {bot.last_updated.strftime('%d.%m.%Y %H:%M')}
        """
        
        keyboard = [
            [InlineKeyboardButton("📥 Скачать", callback_data=f"download_{bot.id}")],
            [InlineKeyboardButton("🚀 Развернуть", callback_data=f"deploy_{bot.id}")],
            [InlineKeyboardButton("◀️ Назад к списку", callback_data="my_bots")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(details_text, parse_mode='HTML', reply_markup=reply_markup)

def main():
    """Основная функция запуска бота"""
    # Создаем таблицы в базе данных
    create_tables()
    
    # Создаем экземпляр бота
    bot_creator = BotCreatorBot()
    
    # Создаем приложение
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", bot_creator.start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_creator.handle_message))
    application.add_handler(CallbackQueryHandler(bot_creator.button_callback))
    
    # Запускаем бота
    print("🤖 Bot Creator запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()
