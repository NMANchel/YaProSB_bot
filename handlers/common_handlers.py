import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import LOGO_PATH
from database import db  
from storage import ensure_user  

logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user = update.effective_user
    user_id = user.id
    username = user.username or user.first_name
    first_name = user.first_name
    last_name = user.last_name
    
    logger.info(f"Пользователь {user_id} ({username}) запустил бота командой /start")
    

    ensure_user(user_id)
    
    welcome_text = f"""
✨ *Привет, {username}! Добро пожаловать в YAProSB!* ✨

*YAProSB* — это *Я Проектирую Свое Благополучие* 🤲

Я — твой цифровой наставник, который поможет тебе найти баланс 
в трёх ключевых сферах жизни:

🏃 *ТЕЛО* — здоровые привычки, трекинг активности, питание
• Трекер воды (8 стаканов в день)
• Отслеживание сна и активности
• Челленджи и мотивация

💭 *ДУША* — забота о ментальном здоровье, анти-стресс техники  
• Кнопка SOS для экстренной помощи
• Дыхательные практики 4-7-8
• Дневник настроения
• Техники релаксации

🌱 *РАЗВИТИЕ* — учеба, общение, самореализация
• Таймер Pomodoro для продуктивности
• Планировщик задач
• Тесты на сильные стороны
• Советы по коммуникации

*🎯 Наша философия:*
Баланс — это не про идеал каждый день. 
Баланс — это про гармонию между твоими потребностями *сейчас*.

*🚀 Как начать:*
1. Выбери раздел ниже, который сейчас для тебя важен
2. Исследуй доступные инструменты (все они бесплатны!)
3. Начни с малого — 1 стакан воды или 5 минут дыхания
4. Возвращайся ежедневно для отслеживания прогресса

*💫 Помни:* Маленькие шаги каждый день ведут к большим изменениям! 

👇 *Выбери, с чего начнём сегодня:*
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🏃 ТЕЛО", callback_data="physical"),
            InlineKeyboardButton("💭 ДУША", callback_data="mental"),
        ],
        [
            InlineKeyboardButton("🌱 РАЗВИТИЕ", callback_data="social"),
            InlineKeyboardButton("ℹ️ О ПРОЕКТЕ", callback_data="about"),
        ],
        [
            InlineKeyboardButton("📊 МОЙ ПРОГРЕСС", callback_data="progress"),
            InlineKeyboardButton("🎯 ЧЕЛЛЕНДЖИ НЕДЕЛИ", callback_data="challenge"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        if os.path.exists(LOGO_PATH):
            with open(LOGO_PATH, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=welcome_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
                logger.info(f"Отправлено приветственное сообщение с логотипом для {user_id}")
        else:
            await update.message.reply_text(
                welcome_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            logger.info(f"Отправлено приветственное сообщение без логотипа для {user_id}")
            
    except Exception as e:
        logger.error(f"Ошибка при отправке приветственного сообщения: {e}")
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    logger.info(f"Пользователь {user.id} запросил помощь")
    
    help_text = """
🆘 *ПОМОЩЬ И ПОДДЕРЖКА*

*📋 Основные команды:*
/start - Запустить бота, показать главное меню
/help - Показать это сообщение справки  
/menu - Вернуться в главное меню

*🎮 Как пользоваться ботом:*
1. Нажми /start или используй кнопки меню
2. Выбери один из трёх разделов:
   • 🏃 *Тело* — трекер воды, сна, активности
   • 💭 *Душа* — анти-стресс практики, настроение
   • 🌱 *Развитие* — таймеры, планирование, тесты
3. Изучи доступные инструменты в каждом разделе
4. Используй их регулярно для лучшего эффекта

*❓ Частые вопросы:*

*Вопрос:* Мои данные сохраняются?
*Ответ:* Да! Все твои данные (трекер воды, настроение, прогресс) сохраняются в базе данных и доступны в любое время.

*Вопрос:* Это бесплатно?
*Ответ:* Абсолютно! Бот создан для поддержки молодежи и полностью бесплатен.

*Вопрос:* Как часто стоит пользоваться ботом?
*Ответ:* Рекомендуем заходить 1-2 раза в день:
• Утром: поставить цели на день, отметить сон
• Вечером: подвести итоги, отметить выполненные привычки

*Вопрос:* Можно ли делиться результатами?
*Ответ:* Конечно! Ты можешь делиться скриншотами своего прогресса с друзьями.

*Вопрос:* Что делать, если бот не отвечает?
*Ответ:*
1. Проверь интернет-соединение
2. Перезапусти бота командой /start
3. Если проблема повторяется, сообщи об этом

*💡 Совет:* Используй бота как личный дневник благополучия. 
Регулярность важнее идеальности!

👇 *Вернуться в меню:*
    """
    
    keyboard = [[InlineKeyboardButton("🔙 В ГЛАВНОЕ МЕНЮ", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    logger.info(f"Отправлена справка для пользователя {user.id}")

async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user = update.effective_user
    logger.info(f"Пользователь {user.id} запросил главное меню")
    
    ensure_user(user.id)
    
    menu_text = """
🏠 *ГЛАВНОЕ МЕНЮ YAProSB*

Помни о балансе трёх сфер:
• 🏃 *Тело* требует движения, отдыха и правильного питания
• 💭 *Душа* нуждается в заботе, внимании и отдыхе  
• 🌱 *Развитие* жаждет роста, обучения и реализации

*🎯 Сегодняшний фокус:*
Сделай хотя бы одно действие в каждой сфере:
1. Выпей стакан воды (Тело)
2. Сделай дыхательное упражнение (Душа)
3. Запланируй одну важную задачу (Развитие)

*Что важно для тебя сегодня?*
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🏃 ТЕЛО", callback_data="physical"),
            InlineKeyboardButton("💭 ДУША", callback_data="mental"),
        ],
        [
            InlineKeyboardButton("🌱 РАЗВИТИЕ", callback_data="social"),
            InlineKeyboardButton("📊 ПРОГРЕСС", callback_data="progress"),
        ],
        [
            InlineKeyboardButton("ℹ️ О ПРОЕКТЕ", callback_data="about"),
            InlineKeyboardButton("🆘 ПОМОЩЬ", callback_data="help"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            text=menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    logger.info(f"Показано главное меню для пользователя {user.id}")

async def back_to_main_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    await query.answer()  
    
    user = update.effective_user
    logger.info(f"Пользователь {user.id} вернулся в главное меню")
    
    return_text = """
🏠 *Возвращаемся в главное меню...*

*✨ Напоминание о балансе:*
Ты уникален, и твои потребности могут меняться день ото дня.
Сегодня тебе может быть важнее отдохнуть, а завтра — поработать.
Слушай себя и выбирай то, что нужно именно сейчас.

*🌱 Маленький совет:*
Попробуй сегодня сделать что-то из каждого раздела, 
даже если это будет всего 5 минут.

*Что выберешь сегодня?*
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🏃 ТЕЛО", callback_data="physical"),
            InlineKeyboardButton("💭 ДУША", callback_data="mental"),
        ],
        [
            InlineKeyboardButton("🌱 РАЗВИТИЕ", callback_data="social"),
            InlineKeyboardButton("📊 ПРОГРЕСС", callback_data="progress"),
        ],
        [
            InlineKeyboardButton("ℹ️ О ПРОЕКТЕ", callback_data="about"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=return_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    user = update.effective_user
    logger.info(f"Пользователь {user.id} запросил информацию о проекте")
    
    about_text = """
ℹ️ *О ПРОЕКТЕ YAProSB*

*YAProSB* — *Я Проектирую Свое Благополучие*

*🎯 Наша миссия:*
Помочь современной молодежи воспринимать здоровье целостно, 
а не фрагментарно. Не только спорт или только питание, 
а баланс тела, души и развития.

*🤔 Проблема, которую мы решаем:*
Многие воспринимают здоровье фрагментарно:
• Кто-то думает только о теле (спорт, питание)
• Кто-то — только о ментальном здоровье
• Кто-то забывает про социализацию и развитие

Мы верим, что настоящее благополучие — это баланс трёх элементов:

*🔴 ТЕЛО (Физическое здоровье)*
• Здоровые привычки
• Активный образ жизни
• Правильное питание
• Достаточный сон

*🟡 ДУША (Психологическое здоровье)*  
• Эмоциональное благополучие
• Управление стрессом
• Позитивное мышление

*🟢 РАЗВИТИЕ (Социальное здоровье)*
• Обучение и рост
• Социальные связи
• Самореализация
• Цели и смыслы

*👥 Для кого этот бот:*
• Для подростков и молодёжи 14-25 лет
• Для тех, кто хочет начать заботиться о себе
• Для ищущих баланс в жизни
• Для всех, кому нужен цифровой друг-наставник

*❤️ Философия:*
Мы не верим в перфекционизм. 
Мы верим в прогресс, маленькие шаги и заботу о себе каждый день.

*👇 Вернуться в меню:*
    """
    
    keyboard = [[InlineKeyboardButton("🔙 В ГЛАВНОЕ МЕНЮ", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            about_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(
            text=about_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_message = update.message.text if update.message else "N/A"
    
    logger.info(f"Пользователь {user.id} отправил неизвестное сообщение: {user_message}")
    
    unknown_text = """
🤔 *Кажется, я не совсем понял...*

Я умею работать с:
• ✅ Кнопками меню (нажимай на них)
• ✅ Командами (пиши со slash: /команда)

*📋 Основные команды:*
/start - Запустить бота сначала
/help - Показать справку
/menu - Показать главное меню

*💡 Совет:* Лучше использовать кнопки — так удобнее!

*Или просто выбери направление ниже:*
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🏃 ТЕЛО", callback_data="physical"),
            InlineKeyboardButton("💭 ДУША", callback_data="mental"),
        ],
        [
            InlineKeyboardButton("🌱 РАЗВИТИЕ", callback_data="social"),
            InlineKeyboardButton("🔁 /start", callback_data="restart"),
        ],
        [
            InlineKeyboardButton("ℹ️ О ПРОЕКТЕ", callback_data="about"),
            InlineKeyboardButton("🆘 ПОМОЩЬ", callback_data="help"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        unknown_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def progress_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    
    logger.info(f"Пользователь {user_id} запросил свой прогресс")
    
    from storage import get_all_user_data
    user_data = get_all_user_data(user_id)
    
    water_today = user_data['water_today']
    water_progress = min(water_today, 8)
    water_bar = "▰" * water_progress + "▱" * (8 - water_progress)
    
    sleep_hours = user_data['sleep_hours']
    sleep_progress = min(int(sleep_hours), 8)
    sleep_bar = "▰" * sleep_progress + "▱" * (8 - sleep_progress)
    
    steps_today = user_data.get('steps_today', 0)
    steps_progress = min(steps_today // 1000, 10)  # 10 сегментов для 10000 шагов
    steps_bar = "▰" * steps_progress + "▱" * (10 - steps_progress)
    
    achievements = []
    
    if water_today >= 8:
        achievements.append("💧 Норма воды сегодня выполнена!")
    elif water_today >= 4:
        achievements.append(f"💦 {water_today}/8 стаканов воды")
    
    if sleep_hours >= 7:
        achievements.append("😴 Хороший сон сегодня!")
    elif sleep_hours > 0:
        achievements.append(f"😴 Сон: {sleep_hours:.1f} часов")
    
    if user_data.get('mood_today'):
        achievements.append(f"{user_data.get('emoji_today', '')} Настроение сегодня отмечено")
    
    if user_data.get('pomodoro_today', 0) > 0:
        achievements.append(f"🍅 {user_data['pomodoro_today']} Pomodoro сегодня")
    
    if user_data.get('streak_days', 0) >= 3:
        achievements.append(f"🔥 Стрик: {user_data['streak_days']} дней подряд!")
    
    if not achievements:
        achievements.append("🎯 Начни отслеживать привычки!")
    
    progress_text = f"""
📊 *ТВОЙ ПРОГРЕСС*

*🏃 ФИЗИЧЕСКОЕ ЗДОРОВЬЕ:*
• 💧 Вода: {water_today}/8 стаканов сегодня
{water_bar}
• 😴 Сон: {sleep_hours:.1f}/8 часов сегодня  
{sleep_bar}
• 👣 Шаги: {steps_today}/10000 сегодня
{steps_bar}
• 🔥 Дней подряд активность: {user_data.get('streak_days', 0)}

*💭 ПСИХОЛОГИЧЕСКОЕ ЗДОРОВЬЕ:*
• 📅 Настроение сегодня: {user_data.get('emoji_today', '')} {user_data.get('mood_today', 'Не отмечено')}
• 📊 Среднее настроение за неделю: {user_data.get('avg_mood', 'Не оценено')}
• 📈 Дней с отметкой настроения: {user_data.get('mood_days', 0)}

*🌱 РАЗВИТИЕ И РОСТ:*
• 🍅 Pomodoro сегодня: {user_data.get('pomodoro_today', 0)}
• ✅ Всего Pomodoro: {user_data.get('pomodoro_count', 0)}
• 🎯 Задач завершено: 0 (скоро)

*🏆 ДОСТИЖЕНИЯ:*
"""
    
    for achievement in achievements:
        progress_text += f"• {achievement}\n"
    
    progress_text += "\n*💡 СОВЕТ НА СЕГОДНЯ:*\n"
    

    if water_today < 4:
        progress_text += "Выпей ещё воды! Это улучшит концентрацию. 💧\n"
    elif sleep_hours < 6:
        progress_text += "Позаботься о сне сегодня. Хороший сон = энергия! 😴\n"
    elif not user_data.get('mood_today'):
        progress_text += "Отметь своё настроение в дневнике настроения. 📊\n"
    elif user_data.get('pomodoro_today', 0) == 0:
        progress_text += "Попробуй Pomodoro для продуктивной работы! 🍅\n"
    else:
        progress_text += "Отличный прогресс! Продолжай в том же духе! 🌟\n"
    
    keyboard = [
        [
            InlineKeyboardButton("💧 Добавить воду", callback_data="water_track"),
            InlineKeyboardButton("😴 Отметить сон", callback_data="sleep_track"),
        ],
        [
            InlineKeyboardButton("📊 Дневник настроения", callback_data="mood_tracker"),
            InlineKeyboardButton("🍅 Pomodoro", callback_data="pomodoro_start"),
        ],
        [
            InlineKeyboardButton("👣 Добавить шаги", callback_data="add_steps"),
            InlineKeyboardButton("📈 Подробная статистика", callback_data="detailed_stats"),
        ],
        [InlineKeyboardButton("🔙 В ГЛАВНОЕ МЕНЮ", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=progress_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def challenge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    logger.info(f"Пользователь {user.id} запросил челленджи")
    

    from storage import get_user_data
    user_data = get_user_data(user_id)
    
    challenge_text = f"""
🎯 *НЕДЕЛЬНЫЕ ЧЕЛЛЕНДЖИ*

*🏃 ЧЕЛЛЕНДЖ "ТЕЛО":*
💧 *Гидратация на 7 дней*
Выпивать 8 стаканов воды каждый день в течение недели.
• 📅 Прогресс: {user_data['water_total'] // 8} недель с нормой воды
• 🎯 Текущая неделя: {user_data['water_today']}/8 стаканов сегодня

🏆 *Награда:* Виртуальный значок "Мастер гидратации"

*💭 ЧЕЛЛЕНДЖ "ДУША":*
🎭 *7 дней осознанного дыхания*
Выполнять дыхательную практику 4-7-8 каждый день.
• 📅 Дней с практикой: {user_data.get('breathing_days', 0)}
• 🎯 Сегодня: {'✅' if user_data.get('breathing_today', False) else '❌'}

🏆 *Награда:* Виртуальный значок "Мастер спокойствия"

*🌱 ЧЕЛЛЕНДЖ "РАЗВИТИЕ":*
🍅 *7 Pomodoro за неделю*
Выполнить 7 рабочих интервалов по 25 минут.
• 🍅 Выполнено: {user_data.get('pomodoro_week', 0)}/7
• ⏱️ Время работы: {user_data.get('pomodoro_time', 0)} мин

🏆 *Награда:* Виртуальный значок "Мастер фокуса"

*🎮 Как участвовать:*
1. Выбери челлендж (или несколько)
2. Выполняй условия каждый день
3. Отмечай прогресс в соответствующем разделе
4. Получи награду в конце недели!

*💫 Бонус:* Если выполнишь все три челленджа, 
получишь специальный значок "Мастер баланса"!

👇 *Начать челлендж:*
    """
    
    keyboard = [
        [InlineKeyboardButton("💧 НАЧАТЬ ЧЕЛЛЕНДЖ ВОДЫ", callback_data="water_challenge_start")],
        [InlineKeyboardButton("🎭 НАЧАТЬ ЧЕЛЛЕНДЖ ДЫХАНИЯ", callback_data="breathing_challenge_start")],
        [InlineKeyboardButton("🍅 НАЧАТЬ ЧЕЛЛЕНДЖ POMODORO", callback_data="pomodoro_challenge_start")],
        [
            InlineKeyboardButton("📊 МОЙ ПРОГРЕСС", callback_data="progress"),
            InlineKeyboardButton("🔙 В ГЛАВНОЕ МЕНЮ", callback_data="back_to_main")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=challenge_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def detailed_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from database import db
    overview = db.get_user_overview(user_id)
    
    if not overview:
        await query.edit_message_text(
            text="❌ Данные не найдены. Начни использовать бота!",
            parse_mode='Markdown'
        )
        return
    
    stats_text = f"""
📈 *ПОДРОБНАЯ СТАТИСТИКА*

*🏃 ФИЗИЧЕСКОЕ ЗДОРОВЬЕ:*
• 💧 Вода сегодня: {overview['water']['today']}/8 стаканов
• 💧 Всего выпито: {overview['water']['total']} стаканов
• 💧 Дней с нормой: {overview['water'].get('days_with_goal', 0)}
• 💧 Текущий стрик воды: {overview['water'].get('streak', 0)} дней

• 😴 Сон сегодня: {overview['sleep']['today_hours']:.1f} часов
• 😴 Качество сна: {overview['sleep']['today_quality']}/5
• 😴 Средний сон: {overview['sleep']['avg_hours']:.1f} часов
• 😴 Среднее качество: {overview['sleep']['avg_quality']:.1f}/5

• 👣 Шаги сегодня: {overview['activity']['today_steps']}
• 👣 Всего шагов: {overview['activity']['total_steps']:,}
• 👣 Активных дней: {overview['activity']['active_days']}
• 👣 Тренировки сегодня: {overview['activity']['today_workout']} мин

*💭 ПСИХОЛОГИЧЕСКОЕ ЗДОРОВЬЕ:*
• 📅 Настроение сегодня: {overview['mood'].get('today_emoji', '')} {overview['mood'].get('today_mood', 'Не отмечено')}
• 📊 Дней с отметкой настроения: {overview['mood']['days_with_mood']}
• 📈 Частое настроение: {', '.join(set(overview['mood'].get('mood_history', [])[:3])) or 'Нет данных'}

*🌱 РАЗВИТИЕ И РОСТ:*
• 🍅 Pomodoro сегодня: {overview['pomodoro']['today_completed']}
• ✅ Всего Pomodoro: {overview['pomodoro']['total_completed']}
• ⏱️ Общее время работы: {overview['pomodoro']['total_time']} мин
• 📅 Дней с Pomodoro: {overview['pomodoro']['days_with_pomodoro']}

*🎯 ОБЩАЯ СТАТИСТИКА:*
• 🔥 Общий стрик: {overview['streak_days']} дней
• 📅 Последняя активность: {overview['last_active'][:10]}
• 🏆 Достижений: {len(overview['achievements'])}
    """
    
    keyboard = [
        [InlineKeyboardButton("📊 ГРАФИК ПРОГРЕССА", callback_data="progress_chart")],
        [InlineKeyboardButton("📋 ЭКСПОРТ ДАННЫХ", callback_data="export_data")],
        [
            InlineKeyboardButton("🔙 К ПРОГРЕССУ", callback_data="progress"),
            InlineKeyboardButton("🏠 В МЕНЮ", callback_data="back_to_main")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=stats_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def all_achievements_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    from storage import get_achievements
    achievements = get_achievements(user_id, limit=20)
    
    if not achievements:
        achievements_text = "🎯 *ТВОИ ДОСТИЖЕНИЯ*\n\nУ тебя пока нет достижений. Начни использовать бота и получи свои первые награды!"
    else:
        achievements_text = "🎯 *ТВОИ ДОСТИЖЕНИЯ*\n\n"
        for i, achievement in enumerate(achievements, 1):
            achievements_text += f"{i}. {achievement}\n"
    
    achievements_text += "\n*💡 Совет:* Достижения разблокируются автоматически при выполнении привычек!"
    
    keyboard = [
        [InlineKeyboardButton("📊 МОЙ ПРОГРЕСС", callback_data="progress")],
        [InlineKeyboardButton("🔙 В ГЛАВНОЕ МЕНЮ", callback_data="back_to_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=achievements_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

__all__ = [
    'start_command',
    'help_command', 
    'handle_main_menu',
    'back_to_main_handler',
    'about_command',
    'unknown_command',
    'progress_handler',
    'challenge_handler',
    'detailed_stats_handler',
    'all_achievements_handler'
]