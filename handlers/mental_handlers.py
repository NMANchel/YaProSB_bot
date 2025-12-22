from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import datetime
import random
import logging
from typing import Optional

from storage import (
    set_mood,
    get_mood_data,
    add_achievement,
    get_user_data,
    ensure_user,
    get_mood_history,
    get_mood_stats,
    get_sleep_data,
    add_mood_note,
    get_workout_data,
    get_meditation_data
)

logger = logging.getLogger(__name__)

async def mental_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        ensure_user(user_id)
        
        user_data = get_user_data(user_id)
        mood_data = get_mood_data(user_id)
        
        mood_today = mood_data.get('today_mood', 'Не отмечено')
        
        menu_text = f"""
💭 *РАЗДЕЛ "ДУША" - ПСИХОЛОГИЧЕСКОЕ ЗДОРОВЬЕ*

*📊 ТВОЯ СТАТИСТИКА (из БД):*
• 📅 Настроение сегодня: {mood_today}
• 🔥 Дней с отметкой настроения: {get_mood_stats(user_id).get('days_with_mood', 0)}

*🎯 ВЫБЕРИ НАПРАВЛЕНИЕ:*

*📊 ДНЕВНИК НАСТРОЕНИЯ*
• Отмечай свое настроение каждый день
• Следи за паттернами и изменениями

*🎭 ДЫХАТЕЛЬНАЯ ПРАКТИКА*
• Техника 4-7-8 для расслабления
• Снижение стресса и тревожности

*🆘 SOS - СРОЧНАЯ ПОМОЩЬ*
• Экстренная помощь при тревоге
• Техники заземления и успокоения

*🧘 МЕДИТАЦИИ*
• 5-минутные сессии для расслабления
• Развитие осознанности

*💤 ТЕХНИКИ ДЛЯ СНА*
• Релаксация перед сном
• Улучшение качества сна

*📈 СТАТИСТИКА*
• Отслеживай свой прогресс
• Анализируй паттерны настроения
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 ДНЕВНИК НАСТРОЕНИЯ", callback_data="mood_tracker"),
                InlineKeyboardButton("🎭 ДЫХАТЕЛЬНАЯ ПРАКТИКА", callback_data="breathing_practice"),
            ],
            [
                InlineKeyboardButton("🆘 SOS ПОМОЩЬ", callback_data="sos_help"),
            ],
            [
                InlineKeyboardButton("💤 ТЕХНИКИ СНА", callback_data="sleep_techniques"),
                InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="mental_stats"),
            ],
            [
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=menu_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в mental_menu_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке данных. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def mood_tracker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    mood_text = """
📊 *ДНЕВНИК НАСТРОЕНИЯ*

*Какое у тебя сегодня настроение?*

Выбери эмодзи, которое соответствует твоему состоянию:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("😊 Отлично", callback_data="mood_great"),
            InlineKeyboardButton("🙂 Хорошо", callback_data="mood_good"),
        ],
        [
            InlineKeyboardButton("😐 Нормально", callback_data="mood_ok"),
            InlineKeyboardButton("😕 Не очень", callback_data="mood_bad"),
        ],
        [
            InlineKeyboardButton("😢 Плохо", callback_data="mood_terrible"),
            InlineKeyboardButton("😴 Устал(а)", callback_data="mood_tired"),
        ],
        [
            InlineKeyboardButton("🤔 Задумчивый", callback_data="mood_thoughtful"),
            InlineKeyboardButton("😌 Спокойный", callback_data="mood_calm"),
        ],
        [
            InlineKeyboardButton("📝 Добавить заметку", callback_data="mood_add_note"),
            InlineKeyboardButton("📊 Статистика", callback_data="mood_stats"),
        ],
        [
            InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=mood_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def mood_great_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        set_mood(user_id, "Отлично", "😊")
        
        add_achievement(user_id, "😊 Отличное настроение")
        
        mood_stats = get_mood_stats(user_id)
        mood_history = get_mood_history(user_id, days=7)
        
        great_days = sum(1 for day in mood_history if day['mood'] == 'Отлично')
        
        response_text = f"""
😊 *ОТЛИЧНО!*

*📊 ТВОЯ СТАТИСТИКА:*
• 📅 Отличных дней за неделю: {great_days}
• 📅 Всего дней с отметкой: {mood_stats.get('days_with_mood', 0)}

*🎉 ПОЗДРАВЛЕНИЕ:*
Ты в отличном настроении! Так держать!

*🎯 РЕКОМЕНДАЦИИ:*
• Поделись хорошим настроением с кем-то
• Запиши, что именно поднимает тебе настроение
• Продолжай практиковать то, что работает
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика", callback_data="mood_stats"),
                InlineKeyboardButton("🎯 Случайный совет", callback_data="mental_tips_random"),
            ],
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в mood_great_handler: {e}")
        fallback_text = """
😊 *ОТЛИЧНО!*
Спасибо, что поделился(ась) отличным настроением!
Так держать! 💪
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=fallback_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def mood_good_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        set_mood(user_id, "Хорошо", "🙂")
        
        mood_stats = get_mood_stats(user_id)
        mood_history = get_mood_history(user_id, days=7)
        
        good_days = sum(1 for day in mood_history if day['mood'] == 'Хорошо')
        
        response_text = f"""
🙂 *ХОРОШО*

*📊 ТВОЯ СТАТИСТИКА:*
• 📅 Хороших дней за неделю: {good_days}
• 📅 Всего дней с отметкой: {mood_stats.get('days_with_mood', 0)}

*👍 ХОРОШЕЕ НАСТРОЕНИЕ:*
Хорошее настроение - это уже шаг вперед!

*🎯 РЕКОМЕНДАЦИИ:*
• Продолжай отмечать свое настроение
• Обрати внимание на то, что помогает поддерживать хорошее настроение
• Благодари себя за каждый день
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика", callback_data="mood_stats"),
                InlineKeyboardButton("🎯 Случайный совет", callback_data="mental_tips_random"),
            ],
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в mood_good_handler: {e}")
        fallback_text = """
🙂 *ХОРОШО*
Спасибо, что отметил(а) свое настроение!
Хорошее настроение - это уже шаг вперед! 👍
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=fallback_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def mood_ok_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        set_mood(user_id, "Нормально", "😐")
        
        mood_stats = get_mood_stats(user_id)
        mood_history = get_mood_history(user_id, days=7)
        
        days_with_mood = mood_stats.get('days_with_mood', 0)
        ok_days = sum(1 for day in mood_history if day['mood'] == 'Нормально')
        
        response_text = f"""
😐 *НОРМАЛЬНО*

*📊 ТВОЯ СТАТИСТИКА:*
• 📅 Нормальных дней за неделю: {ok_days}
• 📅 Всего дней с отметкой: {days_with_mood}

*💡 НЕЙТРАЛЬНОЕ НАСТРОЕНИЕ:*
Нейтральное настроение тоже нормально. 
Не каждый день может быть особенным — и это ок!

*🎯 РЕКОМЕНДАЦИИ:*
• Это нормально, когда день просто идет своим чередом
• Попробуй добавить что-то приятное в этот день
• Не забывай отмечать свое состояние
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика настроений", callback_data="mood_stats"),
                InlineKeyboardButton("🎯 Случайный совет", callback_data="mental_tips_random"),
            ],
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в mood_ok_handler: {e}")
        response_text = """
😐 *НОРМАЛЬНО.*
Нейтральное настроение тоже нормально. Не каждый день может быть особенным — и это ок!

*🎯 РЕКОМЕНДАЦИИ:*
• Это нормально, когда день просто идет своим чередом
• Попробуй добавить что-то приятное в этот день
        """
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика настроений", callback_data="mood_stats"),
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
            ],
            [
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def mood_bad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        set_mood(user_id, "Не очень", "😕")
        
        mood_stats = get_mood_stats(user_id)
        mood_history = get_mood_history(user_id, days=7)
        
        bad_days = sum(1 for day in mood_history if day['mood'] in ['Не очень', 'Плохо'])
        
        response_text = f"""
😕 *НЕ ОЧЕНЬ*

*📊 ТВОЯ СТАТИСТИКА:*
• 📅 Плохих дней за неделю: {bad_days}
• 📅 Всего дней с отметкой: {mood_stats.get('days_with_mood', 0)}

*🤗 СПАСИБО:*
Спасибо, что отметил(а) свое состояние.

*🆘 ЧТО МОЖЕТ ПОМОЧЬ СЕЙЧАС:*
• 🧘 *Дыхание 4-7-8*: вдох на 4, задержка на 7, выдох на 8
• 💧 *Вода*: выпей стакан прохладной воды
• 🎵 *Музыка*: послушай успокаивающую музыку
• 📝 *Заметка*: запиши, что беспокоит

*🎯 НЕ ЗАБУДЬ:*
Ты не один(а), и это состояние пройдет.
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🎭 Дыхательная практика", callback_data="breathing_practice"),
                InlineKeyboardButton("🆘 SOS помощь", callback_data="sos_help"),
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data="mood_stats"),
                InlineKeyboardButton("🎯 Случайный совет", callback_data="mental_tips_random"),
            ],
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в mood_bad_handler: {e}")
        fallback_text = """
😕 *НЕ ОЧЕНЬ.*
Спасибо, что отметил(а) свое состояние.
*🆘 ЧТО МОЖЕТ ПОМОЧЬ СЕЙЧАС:*
• 🧘 *Дыхание 4-7-8*: вдох на 4, задержка на 7, выдох на 8
• 💧 *Вода*: выпей стакан прохладной воды
• 🎵 *Музыка*: послушай успокаивающую музыку
*🎯 НЕ ЗАБУДЬ:*
Ты не один(а), и это состояние пройдет.
        """
        keyboard = [
            [
                InlineKeyboardButton("🎭 Дыхательная практика", callback_data="breathing_practice"),
                InlineKeyboardButton("🆘 SOS помощь", callback_data="sos_help"),
            ],
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=fallback_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def mood_terrible_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        set_mood(user_id, "Плохо", "😢")
        
        add_achievement(user_id, "😢 Честно отметил плохое настроение")
        
        mood_stats = get_mood_stats(user_id)
        mood_history = get_mood_history(user_id, days=7)
        
        terrible_days = sum(1 for day in mood_history if day['mood'] == 'Плохо')
        
        response_text = f"""
😢 *ПЛОХО*

*📊 ТВОЯ СТАТИСТИКА:*
• 📅 Плохих дней за неделю: {terrible_days}
• 📅 Всего дней с отметкой: {mood_stats.get('days_with_mood', 0)}

*🤗 СПАСИБО:*
Спасибо, что поделился(ась). Возьми паузу, подыши.

*🆘 СРОЧНАЯ ПОМОЩЬ:*
• 🧘 *Дыхание 4-7-8* - успокаивает нервную систему
• 🆘 *SOS помощь* - техники заземления
• 📞 *Горячая линия* - если нужна помощь специалиста

*💙 ТЫ СПРАВИШЬСЯ:*
Это состояние пройдет. Не стесняйся просить о помощи.
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🆘 SOS помощь", callback_data="sos_help"),
                InlineKeyboardButton("🎭 Дыхательная практика", callback_data="breathing_practice"),
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data="mood_stats"),
                InlineKeyboardButton("🎯 Случайный совет", callback_data="mental_tips_random"),
            ],
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в mood_terrible_handler: {e}")
        await query.edit_message_text(
            text="😢 *ПЛОХО.*\nСпасибо, что поделился(ась). Возьми паузу, подыши.\n💙 Ты справишься.",
            parse_mode='Markdown'
        )

async def mood_tired_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        set_mood(user_id, "Устал(а)", "😴")
        
        sleep_data = get_sleep_data(user_id)
        mood_stats = get_mood_stats(user_id)
        
        response_text = f"""
😴 *УСТАЛ(А)*

*📊 ТВОЯ СТАТИСТИКА:*
• 📅 Среднее качество сна: {sleep_data.get('avg_quality', 0)}/5
• 📅 Всего дней с отметкой: {mood_stats.get('days_with_mood', 0)}

*🤗 СПАСИБО:*
Спасибо, что отметил(а) усталость.

*💡 ЧТО МОЖНО СДЕЛАТЬ:*
• 🧘 *Дыхание 4-7-8* - для расслабления
• 💧 *Вода* - для бодрости
• 🚶 *Прогулка* - свежий воздух бодрит
• 🛋️ *Отдых* - дай себе передышку

*🎯 НЕ ЗАБУДЬ:*
Твое тело и разум нуждаются в отдыхе.
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🎭 Дыхательная практика", callback_data="breathing_practice"),
                InlineKeyboardButton("😴 Отметить сон", callback_data="sleep_track"),
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data="mood_stats"),
                InlineKeyboardButton("🎯 Случайный совет", callback_data="mental_tips_random"),
            ],
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в mood_tired_handler: {e}")
        await query.edit_message_text(
            text="😴 *УСТАЛ(А)*\nСпасибо, что отметил(а) усталость.\n*💡 ПОМНИ:*\nТвое тело и разум нуждаются в отдыхе.",
            parse_mode='Markdown'
        )

async def mood_thoughtful_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        set_mood(user_id, "Задумчивый", "🤔")
        
        mood_stats = get_mood_stats(user_id)
        
        response_text = f"""
🤔 *ЗАДУМЧИВЫЙ*

*📊 ТВОЯ СТАТИСТИКА:*
• 📅 Всего дней с отметкой: {mood_stats.get('days_with_mood', 0)}

*💡 ЗАДУМЧИВОСТЬ:*
Задумчивость — признак работы ума.
Может быть, ты над чем-то размышляешь или ищешь ответы?

*🎯 ВОПРОС ДЛЯ РАЗМЫШЛЕНИЯ:*
"Что действительно важно для меня прямо сейчас?"

*💡 ЧТО МОЖЕТ ПОМОЧЬ:*
• 📝 *Записать мысли* на бумагу
• 🚶 *Сделать прогулку* - помогает в размышлениях
• 🎨 *Заняться творчеством* - выражение эмоций
• 📖 *Почитать вдохновляющую книгу*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📝 Записать мысли", callback_data="mood_add_note"),
                InlineKeyboardButton("📊 Статистика", callback_data="mood_stats"),
            ],
            [
                InlineKeyboardButton("🎯 Случайный совет", callback_data="mental_tips_random"),
                InlineKeyboardButton("🎭 Дыхательная практика", callback_data="breathing_practice"),
            ],
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в mood_thoughtful_handler: {e}")
        fallback_text = """
🤔 *ЗАДУМЧИВЫЙ.*
Задумчивость — признак работы ума.
Может быть, ты над чем-то размышляешь или ищешь ответы?
*💡 ЧТО МОЖЕТ ПОМОЧЬ:*
• 📝 Записать мысли на бумагу
• 🚶 Сделать прогулку
• 🎨 Заняться творчеством
• 📖 Почитать вдохновляющую книгу
*🎯 ВОПРОС ДЛЯ РАЗМЫШЛЕНИЯ:*
"Что действительно важно для меня прямо сейчас?"
        """
        keyboard = [
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text=fallback_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

async def mood_calm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        set_mood(user_id, "Спокойный", "😌")
        
        add_achievement(user_id, "😌 Спокойствие и умиротворение")
        
        mood_stats = get_mood_stats(user_id)
        
        response_text = f"""
😌 *СПОКОЙНЫЙ*

*📊 ТВОЯ СТАТИСТИКА:*
• 📅 Всего дней с отметкой: {mood_stats.get('days_with_mood', 0)}

*💡 СПОКОЙСТВО:*
Спокойствие - это состояние внутреннего равновесия.
Цени этот момент и будь в нем.

*🎯 РЕКОМЕНДАЦИИ:*
• 🧘 *Продолжай практиковать осознанность*
• 📚 *Чтение* - укрепляет спокойствие
• 🌿 *Природа* - помогает сохранить равновесие
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🎭 Дыхательная практика", callback_data="breathing_practice"),
                InlineKeyboardButton("📊 Статистика", callback_data="mood_stats"),
            ],
            [
                InlineKeyboardButton("🎯 Случайный совет", callback_data="mental_tips_random"),
                InlineKeyboardButton("🎭 Дыхательная практика", callback_data="breathing_practice"),
            ],
            [
                InlineKeyboardButton("🔙 К выбору настроения", callback_data="mood_tracker"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в mood_calm_handler: {e}")
        await query.edit_message_text(
            text="😌 *СПОКОЙНЫЙ*\nСпасибо, что отметил(а) спокойное настроение.\n*💡 ПОМНИ:*\nСпокойствие - это сила, а не слабость.",
            parse_mode='Markdown'
        )

async def mood_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        mood_stats = get_mood_stats(user_id)
        mood_history = get_mood_history(user_id, days=7)
        
        total_days = mood_stats.get('days_with_mood', 0)
        most_common_moods = mood_stats.get('most_common_moods', [])
        
        stats_text = f"""
📊 *СТАТИСТИКА НАСТРОЕНИЙ*

*📊 ОБЩАЯ СТАТИСТИКА:*
• 📅 Дней с отметкой настроения: {total_days}
• 🎭 Частые настроения: {', '.join(most_common_moods[:3]) if most_common_moods else 'Пока не отмечено'}

*🎯 ТВОЙ ПРОГРЕСС:*
"""
        
        for day in mood_history:
            date = day['date']
            mood = day['mood']
            emoji = day['emoji']
            stats_text += f"• {date}: {emoji} {mood}\n"
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Полная статистика", callback_data="mental_stats"),
                InlineKeyboardButton("📝 Добавить заметку", callback_data="mood_add_note"),
            ],
            [
                InlineKeyboardButton("📊 Дневник настроений", callback_data="mood_tracker"),
                InlineKeyboardButton("🎭 Дыхательная практика", callback_data="breathing_practice"),
            ],
            [
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в mood_stats_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке статистики настроений. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def breathing_practice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        add_achievement(user_id, "🎭 Выполнил дыхательную практику")
        
        response_text = """
🎭 *ДЫХАТЕЛЬНАЯ ПРАКТИКА 4-7-8*

*🎯 ТЕХНИКА:*
1. 🧘 Сядь удобно, расслабься
2. 💨 Закрой рот, вдохни через нос на 4 секунды
3. 🛑 Задержи дыхание на 7 секунд
4. 💨 Медленно выдохни через рот на 8 секунд
5. 🔄 Повтори 3-4 раза

*💡 ПОЛЬЗА:*
• Снижает тревожность
• Успокаивает нервную систему
• Помогает расслабиться

*🎯 КОГДА ПРИМЕНЯТЬ:*
• При стрессе
• Перед сном
• Когда чувствуешь тревогу
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Мои практики", callback_data="breathing_stats"),
                InlineKeyboardButton("🎯 Полезные советы", callback_data="mental_tips"),
            ],
            [
                InlineKeyboardButton("💤 Техники для сна", callback_data="sleep_techniques"),
                InlineKeyboardButton("📊 Статистика", callback_data="mental_stats"),
            ],
            [
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в breathing_practice_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при выполнении дыхательной практики. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def sos_help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        from storage import add_sos_usage
        add_sos_usage(user_id)
        
        response_text = """
🆘 *SOS ПОМОЩЬ - СРОЧНАЯ ПОДДЕРЖКА*

*Если ты чувствуешь сильную тревогу или панику, используй эти техники:*

*🎯 ТЕХНИКА ЗАЗЕМЛЕНИЯ 5-4-3-2-1:*
• 🔢 Назови 5 вещей, которые видишь
• 🔢 Назови 4 вещи, которых можешь коснуться
• 🔢 Назови 3 вещи, которые слышишь
• 🔢 Назови 2 вещи, которые чувствуешь запахом
• 🔢 Назови 1 вещь, которую можешь попробовать на вкус

*🎭 ДЫХАНИЕ 4-7-8:*
• 💨 Вдох на 4 секунды
• 🛑 Задержка на 7 секунд
• 💨 Выдох на 8 секунд

*💡 АФФИРМАЦИИ:*
• "Я в безопасности"
• "Это чувство пройдет"
• "Я справлюсь с этим"

*📞 ЕСЛИ НУЖНА ПОМОЩЬ:*
• Позвони близкому человеку
• Обратись к специалисту
• Позвони на горячую линию
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🎭 Дыхательная практика", callback_data="breathing_practice"),
                InlineKeyboardButton("📊 Статистика", callback_data="mental_stats"),
            ],
            [
                InlineKeyboardButton("🎯 Полезные советы", callback_data="mental_tips"),
                InlineKeyboardButton("💤 Техники для сна", callback_data="sleep_techniques"),
            ],
            [
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в sos_help_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при получении SOS помощи. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def meditation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        add_achievement(user_id, "🧘 Попробовал медитацию")
        
        meditation_data = get_meditation_data(user_id)
        
        response_text = f"""
🧘 *МЕДИТАЦИИ*

*📊 ТВОЯ СТАТИСТИКА:*
• ⏰ Сегодня: {meditation_data.get('today_minutes', 0)} минут
• 📅 Всего сессий: {meditation_data.get('total_sessions', 0)}
• ⏰ Всего минут: {meditation_data.get('total_minutes', 0)}

*🎯 5-МИНУТНАЯ МЕДИТАЦИЯ:*
1. 🧘 Сядь удобно, спина прямая
2. 🧠 Сосредоточься на дыхании
3. 🌿 Вдох и выдох - будь в моменте
4. 🧘 Если мысли приходят - отпусти их

*🎯 КОГДА ПРИМЕНЯТЬ:*
• Утром для начала дня
• После стресса
• Перед сном
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика медитаций", callback_data="meditation_stats"),
                InlineKeyboardButton("🎭 Дыхательная практика", callback_data="breathing_practice"),
            ],
            [
                InlineKeyboardButton("🎯 Полезные советы", callback_data="mental_tips"),
                InlineKeyboardButton("💤 Техники для сна", callback_data="sleep_techniques"),
            ],
            [
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в meditation_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при выполнении медитации. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def mood_add_note_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    response_text = """
📝 *ДОБАВИТЬ ЗАМЕТКУ К НАСТРОЕНИЮ*

*Отправь текст заметки, который поможет тебе вспомнить, что происходило сегодня.*

*Эта заметка будет сохранена и доступна в истории настроений.*
    """
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Статистика настроений", callback_data="mood_stats"),
            InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_mood_note_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    note_text = update.message.text
    
    try:
        add_mood_note(user_id, note_text)
        
        add_achievement(user_id, "📝 Добавил заметку к настроению")
        
        response_text = f"""
✅ *ЗАМЕТКА СОХРАНЕНА!*

*Твоя заметка:*
"{note_text}"

*Заметка сохранена и будет доступна в истории настроений.*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика настроений", callback_data="mood_stats"),
                InlineKeyboardButton("🎭 Дневник настроений", callback_data="mood_tracker"),
            ],
            [
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении заметки: {e}")
        await update.message.reply_text(
            text="❌ Произошла ошибка при сохранении заметки. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def sleep_techniques_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    response_text = """
💤 *ТЕХНИКИ ДЛЯ СНА*

*💡 ВЕЧЕРНИЙ РИТУАЛ (за 1 час до сна):*
1. 📱 Убери гаджеты
2. 📚 Почитай бумажную книгу
3. 🧘 Сделай дыхательные упражнения
4. 🛀 Прими теплый душ

*🎭 РЕЛАКСАЦИОННЫЕ ТЕХНИКИ:*
• Дыхание 4-7-8 перед сном
• Прогрессивная мышечная релаксация
• Визуализация спокойного места

*🎯 РЕКОМЕНДАЦИИ:*
• Температура в комнате 18-22°C
• Темное и тихое пространство
• Регулярный режим сна
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🎭 Дыхательная практика", callback_data="breathing_practice"),
            InlineKeyboardButton("📊 Статистика", callback_data="mental_stats"),
        ],
        [
            InlineKeyboardButton("😴 Отметить сон", callback_data="sleep_track"),
            InlineKeyboardButton("🎯 Полезные советы", callback_data="mental_tips"),
        ],
        [
            InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def mental_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        mood_data = get_mood_data(user_id)
        mood_stats = get_mood_stats(user_id)
        meditation_data = get_meditation_data(user_id)
        sleep_data = get_sleep_data(user_id)
        workout_data = get_workout_data(user_id)
        
        stats_text = f"""
📈 *ПОЛНАЯ СТАТИСТИКА МЕНТАЛЬНОГО ЗДОРОВЬЯ*

*📊 НАСТРОЕНИЕ:*
• 📅 Дней с отметкой: {mood_stats.get('days_with_mood', 0)}
• 🎭 Частые настроения: {', '.join(mood_stats.get('most_common_moods', [])[:3]) if mood_stats.get('most_common_moods') else 'Пока не отмечено'}

*😴 СОН:*
• ⏰ Среднее: {sleep_data.get('avg_hours', 0):.1f} часов/ночь
• 🌙 Качество: {sleep_data.get('avg_quality', 0):.1f}/5

*🧘 МЕДИТАЦИИ:*
• ⏰ Сегодня: {meditation_data.get('today_minutes', 0)} минут
• 📅 Всего сессий: {meditation_data.get('total_sessions', 0)}
• ⏰ Всего минут: {meditation_data.get('total_minutes', 0)}

*💪 ТРЕНИРОВКИ:*
• 🏃 Всего: {workout_data.get('total_workouts', 0)}
• ⏰ Минут: {workout_data.get('total_minutes', 0)}

*💡 РЕКОМЕНДАЦИИ:*
• Продолжай отмечать настроение
• Практикуй дыхание и расслабление
• Следи за качеством сна
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика настроений", callback_data="mood_stats"),
                InlineKeyboardButton("🎭 Дыхательные практики", callback_data="breathing_stats"),
            ],
            [
                InlineKeyboardButton("😴 Статистика сна", callback_data="sleep_stats"),
                InlineKeyboardButton("🧘 Статистика медитаций", callback_data="meditation_stats"),
            ],
            [
                InlineKeyboardButton("📋 Экспорт данных", callback_data="export_mental_data"),
                InlineKeyboardButton("🔙 В РАЗДЕЛ ДУША", callback_data="mental"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в mental_stats_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке статистики. Попробуйте позже.",
            parse_mode='Markdown'
        )

__all__ = [
    'mental_menu_handler',
    'mood_tracker_handler',
    'mood_great_handler',
    'mood_good_handler',
    'mood_ok_handler',
    'mood_bad_handler',
    'mood_terrible_handler',
    'mood_tired_handler',
    'mood_thoughtful_handler',
    'mood_calm_handler',
    'mood_stats_handler',
    'breathing_practice_handler',
    'sos_help_handler',
    'meditation_handler',
    'mood_add_note_handler',
    'handle_mood_note_text',
    'sleep_techniques_handler',
    'mental_stats_handler',
]