from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import datetime
import random
import logging
from typing import Dict, Any

from storage import (
    get_user_data,
    update_water,
    update_sleep,
    update_steps,
    add_achievement,
    get_water_history,
    get_sleep_history,
    get_activity_history,
    get_workout_data,
    get_streak_data,
    get_mood_data,
    add_workout
)

logger = logging.getLogger(__name__)

PHYSICAL_TIPS = {
    'hydration': [
        "Вода помогает поддерживать температуру тела, смазывать суставы и транспортировать питательные вещества.",
        "Пить воду нужно маленькими глотками в течение дня, а не большими порциями за раз.",
        "Добавьте в воду лимон или огурец для вкуса и дополнительных витаминов.",
        "Пейте воду за 30 минут до еды - это улучшает пищеварение.",
        "Вода ускоряет обмен веществ - это помогает в поддержании веса.",
        "Недостаток воды может вызывать головную боль и усталость.",
        "Пейте больше воды в жаркую погоду и при физических нагрузках."
    ],
    'sleep': [
        "Создайте режим сна - ложитесь и вставайте в одно и то же время каждый день.",
        "Избегайте экранов за 1 час до сна - синий свет подавляет выработку мелатонина.",
        "Температура в комнате 18-22°C - идеальна для здорового сна.",
        "Регулярные физические нагрузки улучшают качество сна.",
        "Избегайте кофеина и алкоголя перед сном.",
        "Попробуйте расслабляющие техники перед сном: медитацию, дыхательные упражнения.",
        "Темнота и тишина способствуют выработке мелатонина - гормона сна."
    ],
    'exercise': [
        "Регулярные физические нагрузки укрепляют иммунитет и улучшают настроение.",
        "Даже 10 минут активности в день приносят пользу здоровью.",
        "Старайтесь двигаться каждые 30-60 минут, если работаете за компьютером.",
        "Разминка перед тренировкой снижает риск травм.",
        "Постепенное увеличение нагрузки - ключ к прогрессу.",
        "Дыхание во время тренировки должно быть ровным и контролируемым.",
        "После тренировки обязательно делайте растяжку."
    ],
    'nutrition': [
        "Ешьте регулярно - 3-4 раза в день небольшими порциями.",
        "Увеличьте потребление овощей и фруктов до 5 порций в день.",
        "Выбирайте цельнозерновые продукты вместо обработанных.",
        "Ограничьте потребление сахара и соли.",
        "Планируйте приемы пищи заранее - это помогает избежать фастфуда.",
        "Перекусывайте полезными продуктами: орехами, фруктами, йогуртом.",
        "Пейте воду перед едой - это помогает контролировать аппетит."
    ],
    'posture': [
        "Проверяйте свою осанку каждые 30 минут - плечи назад, живот втянут.",
        "Используйте эргономичное рабочее место - монитор на уровне глаз.",
        "Делайте перерывы каждые 45-60 минут для разминки спины и шеи.",
        "Спите на ортопедическом матрасе - это поддерживает позвоночник.",
        "Укрепляйте мышцы спины и пресс для поддержания правильной осанки.",
        "Ходите с прямой спиной - это улучшает дыхание и уверенность.",
        "Избегайте ношения тяжелых сумок на одном плече."
    ],
    'recovery': [
        "После интенсивных тренировок делайте дни восстановления.",
        "Массаж и растяжка помогают снять мышечное напряжение.",
        "Адекватный сон - важнейшая часть восстановления после тренировок.",
        "Пейте больше воды после физических нагрузок.",
        "Включайте в рацион продукты с высоким содержанием белка.",
        "Слушайте свое тело - не игнорируйте усталость и боль.",
        "Релаксация и медитация снижают уровень стресса и ускоряют восстановление."
    ],
    'motivation': [
        "Ставьте конкретные, измеримые цели - это помогает сохранить мотивацию.",
        "Отмечайте даже маленькие успехи - они ведут к большим результатам.",
        "Найдите тренировочного партнера - это повышает ответственность.",
        "Создайте поддерживающую среду - окружите себя позитивными людями.",
        "Планируйте активности, которые вам нравятся - это делает движение приятным.",
        "Отдыхайте и восстанавливайтесь - это не слабость, а необходимость.",
        "Помните, что прогресс требует времени - будьте терпеливы к себе."
    ]
}

async def physical_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        user_data = get_user_data(user_id)
        
        water_today = user_data['water_today']
        sleep_hours = user_data['sleep_hours']
        steps_today = user_data['steps_today']
        
        menu_text = f"""
🏃 *РАЗДЕЛ "ТЕЛО" - ФИЗИЧЕСКОЕ ЗДОРОВЬЕ*

*📊 ТВОЯ СТАТИСТИКА (из БД):*
• 💧 Вода: {water_today}/8 стаканов сегодня
• 😴 Сон: {sleep_hours:.1f} часов вчера
• 👣 Шаги: {steps_today} сегодня

*🎯 ВЫБЕРИ НАПРАВЛЕНИЕ:*

*💧 ОТСЛЕЖИВАНИЕ ВОДЫ*
• Отмечай каждый стакан воды
• Следи за прогрессом и получай достижения

*😴 ОТСЛЕЖИВАНИЕ СНА*
• Отмечай качество и продолжительность сна
• Получай рекомендации по улучшению сна

*👣 СЧЕТЧИК ШАГОВ*
• Добавляй свои шаги каждый день
• Следи за прогрессом к цели в 10000 шагов

*⚡ БЫСТРЫЕ ТРЕНИРОВКИ*
• 15-минутные зарядки дома
• Нет времени? Это для тебя!

*📊 СТАТИСТИКА И СОВЕТЫ*
• Смотри свой прогресс
• Получай полезные советы по здоровью
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💧 ТРЕКЕР ВОДЫ", callback_data="water_track"),
                InlineKeyboardButton("😴 ОТСЛЕЖИВАНИЕ СНА", callback_data="sleep_track"),
            ],
            [
                InlineKeyboardButton("👣 СЧЕТЧИК ШАГОВ", callback_data="add_steps"),
                InlineKeyboardButton("⚡ БЫСТРАЯ ЗАРЯДКА", callback_data="quick_workout"),
            ],
            [
                InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="physical_stats"),
                InlineKeyboardButton("🎯 ПОЛЕЗНЫЕ СОВЕТЫ", callback_data="physical_tips"),
            ],
            [
                InlineKeyboardButton("🏆 ДОСТИЖЕНИЯ", callback_data="physical_achievements"),
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
        logger.error(f"Ошибка в physical_menu_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке данных. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def water_track_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        update_water(user_id, 1)
        
        user_data = get_user_data(user_id)
        water_count = user_data['water_today']
        
        if water_count == 1:
            message = "💧 Первый стакан воды сегодня! Отличное начало!"
            achievement = "💧 Первый стакан"
        elif water_count == 2:
            message = "💧 Второй стакан! Продолжай в том же духе!"
        elif water_count == 3:
            message = "💧 Третий стакан! Ты на правильном пути!"
        elif water_count == 4:
            message = "💧 Половина нормы! Молодец!"
            achievement = "💧 Полпути к норме"
        elif water_count == 5:
            message = "💧 Пятый стакан! Ты супер!"
        elif water_count == 6:
            message = "💧 Шестой стакан! Уже близко к цели!"
        elif water_count == 7:
            message = "💧 Седьмой стакан! Один шаг до цели!"
        elif water_count >= 8:
            message = "💧 Восемь стаканов! Норма выполнена! Поздравляем! 🎉"
            achievement = "💧 Норма воды выполнена"
        else:
            message = f"💧 Стакан добавлен! Всего сегодня: {water_count}/8"
        
        if 'achievement' in locals():
            add_achievement(user_id, achievement)
        
        tip = random.choice(PHYSICAL_TIPS['hydration'])
        
        water_text = f"""
{message}

*💡 СОВЕТ ДНЯ:*
{tip}

*📊 ТВОЯ СТАТИСТИКА:*
• 💧 Вода: {water_count}/8 стаканов сегодня
• 💧 Всего за неделю: {sum([day['amount'] for day in get_water_history(user_id, 7)])} стаканов

*🎯 РЕКОМЕНДАЦИИ:*
• Пейте воду маленькими глотками
• Добавьте лимон или огурец для вкуса
• Пейте воду перед едой

*Твоя информация сохранена в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💧 ЕЩЕ СТАКАН", callback_data="water_track"),
                InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="water_stats"),
            ],
            [
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=water_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в water_track_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при добавлении воды. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def water_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        user_data = get_user_data(user_id)
        water_history = get_water_history(user_id, 7)
        
        total_week = sum([day['amount'] for day in water_history])
        days_with_goal = sum([1 for day in water_history if day['amount'] >= 8])
        avg_daily = total_week / 7 if water_history else 0
        
        stats_text = f"""
💧 *СТАТИСТИКА ПОТРЕБЛЕНИЯ ВОДЫ*

*📊 ОБЩАЯ СТАТИСТИКА:*
• 💧 Всего за неделю: {total_week} стаканов
• 💧 В среднем в день: {avg_daily:.1f} стаканов
• 💧 Дней с нормой воды: {days_with_goal}/7
• 💧 Текущий стрик: {get_streak_data(user_id)['water_streak']} дней

*🎯 ТВОЙ ПРОГРЕСС:*
"""
        
        for day in water_history:
            date = day['date']
            amount = day['amount']
            progress_bar = "▰" * amount + "▱" * (8 - amount)
            stats_text += f"• {date}: {amount}/8 {progress_bar}\n"
        
        tip = random.choice(PHYSICAL_TIPS['hydration'])
        stats_text += f"\n*💡 СОВЕТ:* {tip}"
        
        keyboard = [
            [
                InlineKeyboardButton("💧 ДОБАВИТЬ ВОДУ", callback_data="water_track"),
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ],
            [
                InlineKeyboardButton("📊 ПОЛНАЯ СТАТИСТИКА", callback_data="physical_stats"),
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в water_stats_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке статистики воды. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def sleep_track_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    sleep_text = """
😴 *ОТСЛЕЖИВАНИЕ СНА*

*Сколько часов ты спал(а) сегодня ночью?*

Выбери продолжительность сна:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("😴 <5 часов", callback_data="sleep_less5"),
            InlineKeyboardButton("😴 5-6 часов", callback_data="sleep_5_6"),
        ],
        [
            InlineKeyboardButton("😴 6-7 часов", callback_data="sleep_6_7"),
            InlineKeyboardButton("😴 7-8 часов", callback_data="sleep_7_8"),
        ],
        [
            InlineKeyboardButton("😴 8-9 часов", callback_data="sleep_8_9"),
            InlineKeyboardButton("😴 >9 часов", callback_data="sleep_9plus"),
        ],
        [
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=sleep_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def sleep_less5_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        update_sleep(user_id, 4.5, 2)  
        
        user_data = get_user_data(user_id)
        sleep_history = get_sleep_history(user_id, days=7)
        streak_data = get_streak_data(user_id)
        
        sleep_tip = random.choice(PHYSICAL_TIPS['sleep'])
        
        low_sleep_days = sum([1 for day in sleep_history if day['hours'] < 6])
        
        response_text = f"""
😴 *Менее 5 часов сна*

*📊 ТВОЯ СТАТИСТИКА:*
• 😴 Всего дней с малым сном: {low_sleep_days}
• 😴 Текущий стрик сна: {streak_data['sleep_streak']} дней

*⚠️ ПРЕДУПРЕЖДЕНИЕ:*
Такое количество сна недостаточно для полноценного восстановления организма.

*💡 СОВЕТ:*
{sleep_tip}

*🎯 РЕКОМЕНДАЦИИ:*
1. 🕐 Постарайся ложиться спать раньше
2. 📱 Избегай гаджетов за час до сна
3. 🌙 Создай темную и тихую обстановку
4. ☕ Ограничь потребление кофеина вечером

*Твой сон сохранен в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 СТАТИСТИКА СНА", callback_data="sleep_stats"),
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ],
            [
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в sleep_less5_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при сохранении данных о сне. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def sleep_5_6_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        update_sleep(user_id, 5.5, 3) 
        
        user_data = get_user_data(user_id)
        sleep_history = get_sleep_history(user_id, days=7)
        streak_data = get_streak_data(user_id)
        
        sleep_tip = random.choice(PHYSICAL_TIPS['sleep'])
        
        response_text = f"""
😴 *5-6 часов сна*

*📊 ТВОЯ СТАТИСТИКА:*
• 😴 Среднее качество сна: {sum([day['quality'] for day in sleep_history]) / len(sleep_history) if sleep_history else 3:.1f}/5
• 😴 Текущий стрик сна: {streak_data['sleep_streak']} дней

*⚠️ ВАЖНО:*
Это количество сна ближе к норме, но все еще недостаточно для полного восстановления.

*💡 СОВЕТ:*
{sleep_tip}

*🎯 РЕКОМЕНДАЦИИ:*
1. 🕐 Постепенно увеличивай время сна
2. 🛏️ Создай комфортные условия для сна
3. 📅 Соблюдай режим сна
4. 🧘 Попробуй расслабляющие техники перед сном

*Твой сон сохранен в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 СТАТИСТИКА СНА", callback_data="sleep_stats"),
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ],
            [
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в sleep_5_6_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при сохранении данных о сне. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def sleep_6_7_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        update_sleep(user_id, 6.5, 4)  
        
        user_data = get_user_data(user_id)
        sleep_history = get_sleep_history(user_id, days=7)
        streak_data = get_streak_data(user_id)
        
        sleep_tip = random.choice(PHYSICAL_TIPS['sleep'])
        
        response_text = f"""
😴 *6-7 часов сна*

*📊 ТВОЯ СТАТИСТИКА:*
• 😴 Среднее качество сна: {sum([day['quality'] for day in sleep_history]) / len(sleep_history) if sleep_history else 3:.1f}/5
• 😴 Текущий стрик сна: {streak_data['sleep_streak']} дней

*👍 ХОРОШО:*
Это количество сна ближе к рекомендуемой норме.

*💡 СОВЕТ:*
{sleep_tip}

*🎯 РЕКОМЕНДАЦИИ:*
1. 🕐 Продолжай соблюдать режим
2. 🌙 Улучшай условия для сна
3. 🧘 Практикуй расслабление перед сном
4. ☕ Ограничивай кофеин вечером

*Твой сон сохранен в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 СТАТИСТИКА СНА", callback_data="sleep_stats"),
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ],
            [
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в sleep_6_7_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при сохранении данных о сне. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def sleep_7_8_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        update_sleep(user_id, 7.5, 5)  
        
        user_data = get_user_data(user_id)
        sleep_history = get_sleep_history(user_id, days=7)
        streak_data = get_streak_data(user_id)
        
        sleep_tip = random.choice(PHYSICAL_TIPS['sleep'])
        
        add_achievement(user_id, "😴 Качественный сон 7-8 часов")
        
        response_text = f"""
😴 *7-8 часов сна - ОТЛИЧНО!*

*📊 ТВОЯ СТАТИСТИКА:*
• 😴 Среднее качество сна: {sum([day['quality'] for day in sleep_history]) / len(sleep_history) if sleep_history else 3:.1f}/5
• 😴 Текущий стрик сна: {streak_data['sleep_streak']} дней

*🎉 ПОЗДРАВЛЕНИЕ:*
Ты достиг(ла) рекомендуемой нормы сна! Это здорово для твоего здоровья.

*💡 СОВЕТ:*
{sleep_tip}

*🎯 РЕКОМЕНДАЦИИ:*
1. 🕐 Продолжай соблюдать режим
2. 🌙 Поддерживай комфортные условия для сна
3. 🧘 Практикуй расслабление перед сном
4. 🏃 Совмещай с физической активностью

*Твой сон сохранен в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 СТАТИСТИКА СНА", callback_data="sleep_stats"),
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ],
            [
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в sleep_7_8_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при сохранении сна. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def sleep_8_9_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        update_sleep(user_id, 8.5, 5) 
        
        user_data = get_user_data(user_id)
        sleep_history = get_sleep_history(user_id, days=7)
        streak_data = get_streak_data(user_id)
        
        sleep_tip = random.choice(PHYSICAL_TIPS['sleep'])
        
        add_achievement(user_id, "😴 Длинный здоровый сон 8-9 часов")
        
        response_text = f"""
😴 *8-9 часов сна - ПРЕКРАСНО!*

*📊 ТВОЯ СТАТИСТИКА:*
• 😴 Среднее качество сна: {sum([day['quality'] for day in sleep_history]) / len(sleep_history) if sleep_history else 3:.1f}/5
• 😴 Текущий стрик сна: {streak_data['sleep_streak']} дней

*🎉 ПОЗДРАВЛЕНИЕ:*
Ты спишь даже больше рекомендуемой нормы - это замечательно для восстановления!

*💡 СОВЕТ:*
{sleep_tip}

*🎯 РЕКОМЕНДАЦИИ:*
1. 🕐 Продолжай соблюдать режим
2. 🌙 Поддерживай комфортные условия для сна
3. 🧘 Практикуй расслабление перед сном
4. 🏃 Совмещай с физической активностью

*Твой сон сохранен в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 СТАТИСТИКА СНА", callback_data="sleep_stats"),
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ],
            [
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в sleep_8_9_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при сохранении сна. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def sleep_9plus_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        update_sleep(user_id, 10.0, 4)  
        
        user_data = get_user_data(user_id)
        sleep_history = get_sleep_history(user_id, days=7)
        streak_data = get_streak_data(user_id)
        
        sleep_tip = random.choice(PHYSICAL_TIPS['sleep'])
        
        response_text = f"""
😴 *Более 9 часов сна*

*📊 ТВОЯ СТАТИСТИКА:*
• 😴 Среднее качество сна: {sum([day['quality'] for day in sleep_history]) / len(sleep_history) if sleep_history else 3:.1f}/5
• 😴 Текущий стрик сна: {streak_data['sleep_streak']} дней

*⚠️ ВНИМАНИЕ:*
Длинный сон может быть признаком усталости или других проблем со здоровьем.

*💡 СОВЕТ:*
{sleep_tip}

*🎯 РЕКОМЕНДАЦИИ:*
1. 🕐 Попробуй нормализовать режим сна
2. 🏃 Увеличь физическую активность днем
3. 🌞 Проводи время на солнце утром
4. 🧘 Практикуй расслабление перед сном

*Твой сон сохранен в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 СТАТИСТИКА СНА", callback_data="sleep_stats"),
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ],
            [
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в sleep_9plus_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при сохранении сна. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def add_steps_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    steps_text = """
👣 *СЧЕТЧИК ШАГОВ*

*Сколько шагов ты сделал(а) сегодня?*

Выбери диапазон:
    """
    
    keyboard = [
        [
            InlineKeyboardButton("🐢 <5000 шагов", callback_data="steps_less5k"),
            InlineKeyboardButton("🚶 5000-7499 шагов", callback_data="steps_5k_7k"),
        ],
        [
            InlineKeyboardButton("🏃 7500-9999 шагов", callback_data="steps_7k_9k"),
            InlineKeyboardButton("🏆 10000+ шагов", callback_data="steps_10kplus"),
        ],
        [
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=steps_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def steps_less5k_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        update_steps(user_id, 3000, 0)
        
        exercise_tip = random.choice(PHYSICAL_TIPS['exercise'])
        
        response_text = f"""
🐢 *Менее 5000 шагов*

*📊 ТВОЯ СТАТИСТИКА:*
• 👣 Всего шагов сегодня: 3000
• 👣 Цель: 10000 шагов

*💡 СОВЕТ:*
{exercise_tip}

*🎯 РЕКОМЕНДАЦИИ:*
1. 🚶 Сделай короткую прогулку после обеда
2. 🏃 Поднимись по лестнице вместо лифта
3. 🚴 Прокатись на велосипеде или самокате
4. 🏀 Поиграй в активные игры

*Твоя активность сохранена в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в steps_less5k_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при сохранении активности. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def steps_5k_7k_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        update_steps(user_id, 6500, 0)
        
        exercise_tip = random.choice(PHYSICAL_TIPS['exercise'])
        
        response_text = f"""
🚶 *5000-7499 шагов*

*📊 ТВОЯ СТАТИСТИКА:*
• 👣 Всего шагов сегодня: 6500
• 👣 Цель: 10000 шагов

*💡 СОВЕТ:*
{exercise_tip}

*🎯 РЕКОМЕНДАЦИИ:*
1. 🚶 Продолжай прогулки после обеда
2. 🏃 Добавь утреннюю зарядку
3. 🚴 Увеличь время активности
4. 🏃 Пробеги или быстрая ходьба

*Твоя активность сохранена в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в steps_5k_7k_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при сохранении активности. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def steps_7k_9k_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        update_steps(user_id, 8500, 0)
        
        exercise_tip = random.choice(PHYSICAL_TIPS['exercise'])
        
        response_text = f"""
🏃 *7500-9999 шагов — отлично!*

*📊 ТВОЯ СТАТИСТИКА:*
• 👣 Всего шагов сегодня: 8500
• 👣 Цель: 10000 шагов

*💡 СОВЕТ:*
{exercise_tip}

Ты почти у цели! Всего 1000-2500 шагов до заветных 10000!

*Твоя активность сохранена в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в steps_7k_9k_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при сохранении активности. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def steps_10kplus_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        update_steps(user_id, 12000, 0)
        
        add_achievement(user_id, "🏃 10000 шагов выполнены")
        
        exercise_tip = random.choice(PHYSICAL_TIPS['exercise'])
        
        response_text = f"""
🏆 *10000+ шагов — ПОЗДРАВЛЕНИЕ!*

*📊 ТВОЯ СТАТИСТИКА:*
• 👣 Всего шагов сегодня: 12000
• 👣 Цель: 10000 шагов

*🎉 ДОСТИЖЕНИЕ ПОЛУЧЕНО:*
• 🏃 10000 шагов выполнены

*💡 СОВЕТ:*
{exercise_tip}

Ты достиг(ла) цели! Так держать!

*Твоя активность сохранена в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в steps_10kplus_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при сохранении активности. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def quick_workout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        exercise_tip = random.choice(PHYSICAL_TIPS['exercise'])
        
        user_id = query.from_user.id
        workout_data = get_workout_data(user_id)
        
        workout_text = f"""
⚡ *БЫСТРАЯ 15-МИНУТНАЯ ЗАРЯДКА*

*📊 ТВОЯ СТАТИСТИКА ТРЕНИРОВОК (из БД):*
• 💪 Всего тренировок: {workout_data['total_workouts']}
• ⏰ Всего минут: {workout_data['total_minutes']}
• 📅 Дней с тренировками: {workout_data['days_with_workout']}

*🎯 КОМПЛЕКС УПРАЖНЕНИЙ:*
1. 🏃 Приседания - 30 секунд
2. 🏃 Отжимания (или на коленях) - 30 секунд
3. 🏃 Планка - 30 секунд
4. 🏃 Выпады - 30 секунд
5. 🏃 Прыжки - 30 секунд
6. 🏃 Повторить 2-3 раза

*💡 СОВЕТ:*
{exercise_tip}

*🎯 РЕКОМЕНДАЦИИ:*
• Выполняй комплекс 2-3 раза в неделю
• Слушай свое тело
• Не забывай про разминку
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💪 ЗАВЕРШИТЬ ТРЕНИРОВКУ", callback_data="workout_completed"),
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ],
            [
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=workout_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в quick_workout_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке зарядки. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def workout_completed_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        add_workout(user_id, "Quick workout", 15, 100)  
        
        add_achievement(user_id, "💪 Быстрая тренировка выполнена")
        
        exercise_tip = random.choice(PHYSICAL_TIPS['exercise'])
        
        response_text = f"""
💪 *ТРЕНИРОВКА ЗАВЕРШЕНА!*

*📊 ТВОЯ СТАТИСТИКА ТРЕНИРОВОК:*
• 💪 Всего тренировок: {get_workout_data(user_id)['total_workouts']}
• ⏰ Всего минут: {get_workout_data(user_id)['total_minutes']}
• 📅 Дней с тренировками: {get_workout_data(user_id)['days_with_workout']}

*🎉 ДОСТИЖЕНИЕ ПОЛУЧЕНО:*
• 💪 Быстрая тренировка выполнена

*💡 СОВЕТ:*
{exercise_tip}

*🎯 НЕ ЗАБЫВАЙ:*
• Не забывай про восстановление
• Слушай свое тело

*Твоя тренировка сохранена в базу данных!*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("⚡ БЫСТРАЯ ЗАРЯДКА", callback_data="quick_workout"),
                InlineKeyboardButton("🎯 СОВЕТЫ ПО ТРЕНИРОВКАМ", callback_data="tips_exercise"),
            ],
            [
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в workout_completed_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при сохранении тренировки. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def physical_tips_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tips_text = """
🎯 *ПОЛЕЗНЫЕ СОВЕТЫ ДЛЯ ТЕЛА*

*Здоровое тело — это не генетика, а ежедневные привычки.*

*Выбери категорию советов:*
    """
    
    keyboard = [
        [
            InlineKeyboardButton("💧 Гидратация", callback_data="tips_hydration"),
            InlineKeyboardButton("😴 Сон", callback_data="tips_sleep"),
        ],
        [
            InlineKeyboardButton("💪 Тренировки", callback_data="tips_exercise"),
            InlineKeyboardButton("🥗 Питание", callback_data="tips_nutrition"),
        ],
        [
            InlineKeyboardButton(" backbone Осанка", callback_data="tips_posture"),
            InlineKeyboardButton("🔄 Восстановление", callback_data="tips_recovery"),
        ],
        [
            InlineKeyboardButton("🔥 Мотивация", callback_data="tips_motivation"),
            InlineKeyboardButton("🎲 Случайный совет", callback_data="tips_random"),
        ],
        [
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_hydration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(PHYSICAL_TIPS['hydration'])
    
    tips_text = f"""
💧 *СОВЕТЫ ПО ГИДРАТАЦИИ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ:*
• Пейте 8 стаканов воды в день
• Начинайте день со стакана воды
• Пейте воду перед едой
• Используйте приложение-напоминание
• Добавляйте в воду лимон или огурец
• Пейте больше в жаркую погоду

*📊 ТВОЯ СТАТИСТИКА ВОДЫ:*
• Всего стаканов за неделю: {sum([day['amount'] for day in get_water_history(query.from_user.id, 7)])}
        """
    
    keyboard = [
        [
            InlineKeyboardButton("💧 ЕЩЕ СОВЕТ ПО ВОДЕ", callback_data="tips_hydration"),
            InlineKeyboardButton("📊 МОЙ ПРОГРЕСС", callback_data="progress"),
        ],
        [
            InlineKeyboardButton("🔙 К ВЫБОРУ КАТЕГОРИЙ", callback_data="physical_tips"),
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_sleep_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(PHYSICAL_TIPS['sleep'])
    
    tips_text = f"""
😴 *СОВЕТЫ ПО СНУ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ:*
• Соблюдайте режим сна
• Избегайте экранов за 1 час до сна
• Поддерживайте температуру 18-22°C
• Создайте темную и тихую обстановку
• Практикуйте расслабление перед сном
• Используйте ортопедический матрас

*📊 ТВОЯ СТАТИСТИКА СНА:*
• Среднее качество сна: {sum([day['quality'] for day in get_sleep_history(query.from_user.id, 7)]) / len(get_sleep_history(query.from_user.id, 7)) if get_sleep_history(query.from_user.id, 7) else 3:.1f}/5
        """
    
    keyboard = [
        [
            InlineKeyboardButton("😴 ЕЩЕ СОВЕТ ПО СНУ", callback_data="tips_sleep"),
            InlineKeyboardButton("📊 МОЙ ПРОГРЕСС", callback_data="progress"),
        ],
        [
            InlineKeyboardButton("🔙 К ВЫБОРУ КАТЕГОРИЙ", callback_data="physical_tips"),
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_exercise_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(PHYSICAL_TIPS['exercise'])
    
    tips_text = f"""
💪 *СОВЕТЫ ПО ТРЕНИРОВКАМ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ:*
• Двигайтесь каждые 30-60 минут
• Регулярные физические нагрузки
• Разминка перед тренировкой
• Постепенное увеличение нагрузки
• Дыхание должно быть ровным
• Обязательно делайте растяжку
• Слушайте свое тело

*📊 ТВОЯ СТАТИСТИКА АКТИВНОСТИ:*
• Всего шагов за неделю: {sum([day['steps'] for day in get_activity_history(query.from_user.id, 7)])}
        """
    
    keyboard = [
        [
            InlineKeyboardButton("💪 ЕЩЕ СОВЕТ ПО ТРЕНИРОВКАМ", callback_data="tips_exercise"),
            InlineKeyboardButton("📊 МОЙ ПРОГРЕСС", callback_data="progress"),
        ],
        [
            InlineKeyboardButton("🔙 К ВЫБОРУ КАТЕГОРИЙ", callback_data="physical_tips"),
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_nutrition_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(PHYSICAL_TIPS['nutrition'])
    
    tips_text = f"""
🥗 *СОВЕТЫ ПО ПИТАНИЮ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ:*
• Ешьте регулярно - 3-4 раза в день
• Увеличьте потребление овощей и фруктов
• Выбирайте цельнозерновые продукты
• Ограничьте потребление сахара и соли
• Планируйте приемы пищи заранее
• Перекусывайте полезными продуктами
• Пейте воду перед едой

*📊 ТВОЯ СТАТИСТИКА АКТИВНОСТИ:*
• Среднее количество шагов: {sum([day['steps'] for day in get_activity_history(query.from_user.id, 7)]) / len(get_activity_history(query.from_user.id, 7)) if get_activity_history(query.from_user.id, 7) else 0:.0f}
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🥗 ЕЩЕ СОВЕТ ПО ПИТАНИЮ", callback_data="tips_nutrition"),
            InlineKeyboardButton("📊 МОЙ ПРОГРЕСС", callback_data="progress"),
        ],
        [
            InlineKeyboardButton("🔙 К ВЫБОРУ КАТЕГОРИЙ", callback_data="physical_tips"),
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_posture_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(PHYSICAL_TIPS['posture'])
    
    tips_text = f"""
 backbone *СОВЕТЫ ПО ОСАНКЕ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ:*
• Проверяйте осанку каждые 30 минут
• Используйте эргономичное рабочее место
• Делайте перерывы каждые 45-60 минут
• Спите на ортопедическом матрасе
• Укрепляйте мышцы спины и пресс
• Ходите с прямой спиной
• Избегайте тяжелых сумок на одном плече

*📊 ТВОЯ СТАТИСТИКА АКТИВНОСТИ:*
• Дней с тренировками: {get_workout_data(query.from_user.id)['days_with_workout']}
        """
    
    keyboard = [
        [
            InlineKeyboardButton(" backbone ЕЩЕ СОВЕТ ПО ОСАНКЕ", callback_data="tips_posture"),
            InlineKeyboardButton("📊 МОЙ ПРОГРЕСС", callback_data="progress"),
        ],
        [
            InlineKeyboardButton("🔙 К ВЫБОРУ КАТЕГОРИЙ", callback_data="physical_tips"),
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_recovery_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(PHYSICAL_TIPS['recovery'])
    
    tips_text = f"""
🔄 *СОВЕТЫ ПО ВОССТАНОВЛЕНИЮ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ:*
• Делайте дни восстановления после тренировок
• Массаж и растяжка для расслабления
• Адекватный сон для восстановления
• Пейте больше воды после нагрузок
• Включайте белок в рацион
• Слушайте свое тело
• Релаксация снижает стресс

*📊 ТВОЯ СТАТИСТИКА:*
• Всего тренировок: {get_workout_data(query.from_user.id)['total_workouts']}
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🔄 ЕЩЕ СОВЕТ ПО ВОССТАНОВЛЕНИЮ", callback_data="tips_recovery"),
            InlineKeyboardButton("📊 МОЙ ПРОГРЕСС", callback_data="progress"),
        ],
        [
            InlineKeyboardButton("🔙 К ВЫБОРУ КАТЕГОРИЙ", callback_data="physical_tips"),
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_motivation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(PHYSICAL_TIPS['motivation'])
    
    tips_text = f"""
🔥 *СОВЕТЫ ПО МОТИВАЦИИ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ:*
• Ставьте конкретные, измеримые цели
• Отмечайте даже маленькие успехи
• Найдите тренировочного партнера
• Создайте поддерживающую среду
• Планируйте активности, которые нравятся
• Отдыхайте и восстанавливайтесь
• Будьте терпеливы к себе

*📊 ТВОЯ СТАТИСТИКА:*
• Дней подряд активность: {get_user_data(query.from_user.id)['streak_days']}
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🔥 ЕЩЕ СОВЕТ ПО МОТИВАЦИИ", callback_data="tips_motivation"),
            InlineKeyboardButton("📊 МОЙ ПРОГРЕСС", callback_data="progress"),
        ],
        [
            InlineKeyboardButton("🔙 К ВЫБОРУ КАТЕГОРИЙ", callback_data="physical_tips"),
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_random_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    all_tips = []
    for category_tips in PHYSICAL_TIPS.values():
        all_tips.extend(category_tips)
    
    tip = random.choice(all_tips)
    
    for category, tips_list in PHYSICAL_TIPS.items():
        if tip in tips_list:
            category_name = {
                'hydration': '💧 Гидратация',
                'sleep': '😴 Сон',
                'exercise': '💪 Тренировки',
                'nutrition': '🥗 Питание',
                'posture': ' backbone Осанка',
                'recovery': '🔄 Восстановление',
                'motivation': '🔥 Мотивация'
            }.get(category, '🎯 Общий')
            break
    
    tips_text = f"""
🎲 *СЛУЧАЙНЫЙ СОВЕТ*

*Категория: {category_name}*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ:*
• Применяйте совет в повседневной жизни
• Делайте небольшие шаги к изменениям
• Следите за прогрессом
• Не бойтесь пробовать новое

*📊 ТВОЯ СТАТИСТИКА:*
• Всего стаканов воды: {get_user_data(query.from_user.id)['water_today']}
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🎲 ЕЩЕ СЛУЧАЙНЫЙ СОВЕТ", callback_data="tips_random"),
            InlineKeyboardButton("📊 МОЙ ПРОГРЕСС", callback_data="progress"),
        ],
        [
            InlineKeyboardButton("🔙 К ВЫБОРУ КАТЕГОРИЙ", callback_data="physical_tips"),
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def physical_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        user_data = get_user_data(user_id)
        water_history = get_water_history(user_id, 7)
        sleep_history = get_sleep_history(user_id, days=7)
        activity_history = get_activity_history(user_id, days=7)
        workout_data = get_workout_data(user_id)
        streak_data = get_streak_data(user_id)
        
        total_week_water = sum([day['amount'] for day in water_history])
        avg_daily_water = total_week_water / 7 if water_history else 0
        days_with_water_goal = sum([1 for day in water_history if day['amount'] >= 8])
        
        avg_sleep_hours = sum([day['hours'] for day in sleep_history]) / len(sleep_history) if sleep_history else 0
        avg_sleep_quality = sum([day['quality'] for day in sleep_history]) / len(sleep_history) if sleep_history else 0
        days_with_good_sleep = sum([1 for day in sleep_history if day['hours'] >= 7])
        
        avg_steps = sum([day['steps'] for day in activity_history]) / len(activity_history) if activity_history else 0
        days_with_active_goal = sum([1 for day in activity_history if day['steps'] >= 10000])
        
        stats_text = f"""
📊 *ПОЛНАЯ СТАТИСТИКА ФИЗИЧЕСКОГО ЗДОРОВЬЯ*

*💧 ВОДА:*
• Всего за неделю: {total_week_water} стаканов
• В среднем в день: {avg_daily_water:.1f} стаканов
• Дней с нормой воды: {days_with_water_goal}/7
• Текущий стрик: {streak_data['water_streak']} дней

*😴 СОН:*
• В среднем: {avg_sleep_hours:.1f} часов/ночь
• Среднее качество: {avg_sleep_quality:.1f}/5
• Дней с нормой сна: {days_with_good_sleep}/7
• Текущий стрик: {streak_data['sleep_streak']} дней

*👣 АКТИВНОСТЬ:*
• В среднем: {int(avg_steps)} шагов/день
• Дней с нормой активности: {days_with_active_goal}/7
• Текущий стрик: {streak_data['activity_streak']} дней

*💪 ТРЕНИРОВКИ:*
• Всего тренировок: {workout_data['total_workouts']}
• Всего минут: {workout_data['total_minutes']}
• Дней с тренировками: {workout_data['days_with_workout']}

*🔥 ОБЩИЙ СТРИК:*
• Дней подряд: {user_data['streak_days']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton("💧 СТАТИСТИКА ВОДЫ", callback_data="water_stats"),
                InlineKeyboardButton("😴 СТАТИСТИКА СНА", callback_data="sleep_stats"),
            ],
            [
                InlineKeyboardButton("🏃 СТАТИСТИКА АКТИВНОСТИ", callback_data="activity_stats"),
                InlineKeyboardButton("💪 СТАТИСТИКА ТРЕНИРОВОК", callback_data="workout_stats"),
            ],
            [
                InlineKeyboardButton("📈 ГРАФИКИ ПРОГРЕССА", callback_data="physical_charts"),
                InlineKeyboardButton("📋 ЭКСПОРТ ДАННЫХ", callback_data="export_physical_data"),
            ],
            [
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в physical_stats_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке статистики.",
            parse_mode='Markdown'
        )

async def sleep_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        sleep_history = get_sleep_history(user_id, 7)
        
        total_nights = len(sleep_history)
        avg_hours = sum([day['hours'] for day in sleep_history]) / total_nights if total_nights > 0 else 0
        avg_quality = sum([day['quality'] for day in sleep_history]) / total_nights if total_nights > 0 else 0
        nights_with_good_sleep = sum([1 for day in sleep_history if day['hours'] >= 7])
        
        stats_text = f"""
😴 *СТАТИСТИКА СНА*

*📊 ОБЩАЯ СТАТИСТИКА:*
• Всего ночей: {total_nights}
• В среднем: {avg_hours:.1f} часов/ночь
• Среднее качество: {avg_quality:.1f}/5
• Ночей с нормой сна: {nights_with_good_sleep}/7

*🎯 ТВОЙ ПРОГРЕСС:*
"""
        
        for day in sleep_history:
            date = day['date']
            hours = day['hours']
            quality = day['quality']
            progress_bar = "▰" * quality + "▱" * (5 - quality)
            stats_text += f"• {date}: {hours:.1f}ч, кач. {quality}/5 {progress_bar}\n"
        
        tip = random.choice(PHYSICAL_TIPS['sleep'])
        stats_text += f"\n*💡 СОВЕТ:* {tip}"
        
        keyboard = [
            [
                InlineKeyboardButton("😴 ОТСЛЕЖИВАНИЕ СНА", callback_data="sleep_track"),
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ],
            [
                InlineKeyboardButton("📊 ПОЛНАЯ СТАТИСТИКА", callback_data="physical_stats"),
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в sleep_stats_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке статистики сна.",
            parse_mode='Markdown'
        )

async def activity_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        activity_history = get_activity_history(user_id, 7)
        
        total_days = len(activity_history)
        avg_steps = sum([day['steps'] for day in activity_history]) / total_days if total_days > 0 else 0
        days_with_goal = sum([1 for day in activity_history if day['steps'] >= 10000])
        
        stats_text = f"""
🏃 *СТАТИСТИКА АКТИВНОСТИ*

*📊 ОБЩАЯ СТАТИСТИКА:*
• Всего дней: {total_days}
• В среднем: {int(avg_steps)} шагов/день
• Дней с нормой: {days_with_goal}/7

*🎯 ТВОЙ ПРОГРЕСС:*
"""
        
        for day in activity_history:
            date = day['date']
            steps = day['steps']
            progress_percent = min(steps // 1000, 10)  # 10 сегментов для 10000 шагов
            progress_bar = "▰" * progress_percent + "▱" * (10 - progress_percent)
            stats_text += f"• {date}: {steps} шагов {progress_bar}\n"
        
        tip = random.choice(PHYSICAL_TIPS['exercise'])
        stats_text += f"\n*💡 СОВЕТ:* {tip}"
        
        keyboard = [
            [
                InlineKeyboardButton("👣 СЧЕТЧИК ШАГОВ", callback_data="add_steps"),
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ],
            [
                InlineKeyboardButton("📊 ПОЛНАЯ СТАТИСТИКА", callback_data="physical_stats"),
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в activity_stats_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке статистики активности.",
            parse_mode='Markdown'
        )

async def workout_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        workout_data = get_workout_data(user_id)
        
        stats_text = f"""
💪 *СТАТИСТИКА ТРЕНИРОВОК*

*📊 ОБЩАЯ СТАТИСТИКА:*
• Всего тренировок: {workout_data['total_workouts']}
• Всего минут: {workout_data['total_minutes']}
• Дней с тренировками: {workout_data['days_with_workout']}
• Среднее: {workout_data['total_minutes'] / workout_data['days_with_workout'] if workout_data['days_with_workout'] > 0 else 0:.1f} мин/день

*🎯 РЕКОМЕНДАЦИИ:*
• Продолжай регулярные тренировки
• Постепенно увеличивай нагрузку
• Не забывай про восстановление
• Слушай свое тело

*💡 СОВЕТ:*
{random.choice(PHYSICAL_TIPS['exercise'])}
        """
        
        keyboard = [
            [
                InlineKeyboardButton("⚡ БЫСТРАЯ ЗАРЯДКА", callback_data="quick_workout"),
                InlineKeyboardButton("🎯 СОВЕТЫ ПО ТРЕНИРОВКАМ", callback_data="tips_exercise"),
            ],
            [
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в workout_stats_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке статистики.",
            parse_mode='Markdown'
        )

async def physical_achievements_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        from storage import get_achievements
        achievements = get_achievements(user_id, limit=20)
        
        if not achievements:
            await query.edit_message_text(
                text="🏆 *Пока нет достижений.*\nНачни отслеживать воду, сон и активность, чтобы получить первые достижения!",
                parse_mode='Markdown'
            )
            return
        
        physical_keywords = ['вода', 'сон', 'шаг', 'тренировк', 'зарядк', 'спорт', 'активн', 'гидра', 'норм', 'цел']
        physical_achievements = []
        for achievement in achievements:
            if any(keyword in achievement.lower() for keyword in physical_keywords):
                physical_achievements.append(achievement)
        
        if not physical_achievements:
            await query.edit_message_text(
                text="🏆 *Пока нет достижений в физическом здоровье.*\nНачни отслеживать воду, сон и активность!",
                parse_mode='Markdown'
            )
            return
        
        stats_text = f"""
🏆 *ТВОИ ДОСТИЖЕНИЯ В ФИЗИЧЕСКОМ ЗДОРОВЬЕ*

*📊 Всего достижений: {len(physical_achievements)}*

*🏅 ТВОИ НАГРАДЫ:*
"""
        
        for i, achievement in enumerate(physical_achievements[:10], 1):
            stats_text += f"• {achievement}\n"
        
        if len(physical_achievements) > 10:
            stats_text += f"*...и еще {len(physical_achievements) - 10} достижений!*"
        
        stats_text += "\n*💡 Продолжай в том же духе! Каждое достижение — это шаг к здоровью!*"
        
        keyboard = [
            [
                InlineKeyboardButton("🎯 ПОЛУЧИТЬ НОВЫЕ ДОСТИЖЕНИЯ", callback_data="physical"),
                InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            ],
            [
                InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в physical_achievements_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке достижений.",
            parse_mode='Markdown'
        )

async def physical_charts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    response_text = """
📈 *ГРАФИКИ ПРОГРЕССА*

*В разработке...*

*🎯 Скоро здесь будут:*
• 📊 Графики потребления воды
• 😴 Диаграммы качества сна
• 🏃 Тренды активности
• 💪 Прогресс тренировок

*💡 А пока можешь посмотреть статистику в табличном виде:*
"""
    
    keyboard = [
        [
            InlineKeyboardButton("💧 СТАТИСТИКА ВОДЫ", callback_data="water_stats"),
            InlineKeyboardButton("😴 СТАТИСТИКА СНА", callback_data="sleep_stats"),
        ],
        [
            InlineKeyboardButton("🏃 СТАТИСТИКА АКТИВНОСТИ", callback_data="activity_stats"),
            InlineKeyboardButton("💪 СТАТИСТИКА ТРЕНИРОВОК", callback_data="workout_stats"),
        ],
        [
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def export_physical_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("📊 ПОЛНАЯ СТАТИСТИКА", callback_data="physical_stats"),
            InlineKeyboardButton("🏆 ДОСТИЖЕНИЯ", callback_data="physical_achievements"),
        ],
        [
            InlineKeyboardButton("🏃 В РАЗДЕЛ ТЕЛО", callback_data="physical"),
            InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    response_text = """
📋 *ЭКСПОРТ ДАННЫХ*

*В разработке...*

*🎯 Доступные опции:*
• 📊 Просмотр полной статистики
• 🏆 Просмотр достижений
• 📈 Статистика по категориям

*Твои данные надежно хранятся в базе данных.*
"""
    
    await query.edit_message_text(
        text=response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

__all__ = [
    'physical_menu_handler',
    'water_track_handler',
    'water_stats_handler',
    'sleep_track_handler',
    'sleep_less5_handler',
    'sleep_5_6_handler',
    'sleep_7_8_handler',
    'sleep_8_9_handler',
    'sleep_6_7_handler',
    'sleep_9plus_handler',
    'add_steps_handler',
    'steps_10kplus_handler',
    'steps_less5k_handler',
    'steps_5k_7k_handler',
    'steps_7k_9k_handler',
    'quick_workout_handler',
    'workout_completed_handler',
    'physical_tips_handler',
    'tips_hydration_handler',
    'tips_sleep_handler',
    'tips_exercise_handler',
    'tips_random_handler',
    'tips_nutrition_handler',
    'tips_posture_handler',
    'tips_recovery_handler',
    'tips_motivation_handler',
    'physical_stats_handler',
    'sleep_stats_handler',
    'activity_stats_handler',
    'workout_stats_handler',
    'physical_achievements_handler',
    'physical_charts_handler',
    'export_physical_data_handler',
]
