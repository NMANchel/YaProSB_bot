from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
import datetime
import random
import logging
import asyncio
from typing import Dict, Any, Optional

from storage import (
    add_pomodoro_session,
    get_pomodoro_stats,
    add_habit,
    get_habits,
    update_habit_completion,
    get_habit_streaks,
    save_goal,
    get_goals,
    update_goal_progress,
    get_achievements,
    add_achievement,
    get_user_data,
    ensure_user,
    get_pomodoro_history,
    get_workout_data,
    get_social_overview
)

logger = logging.getLogger(__name__)

SOCIAL_TIPS = {
    'pomodoro': [
        "Работай 25 минут, отдыхай 5 минут - это оптимальный цикл.",
        "Используй Pomodoro для сложных задач, которые хочется отложить.",
        "После 4 Pomodoro делай длинный перерыв - 15-30 минут.",
        "Создай список задач перед началом Pomodoro сессии.",
        "Используй таймер вместо телефона - меньше отвлечений.",
        "Делай Pomodoro в одно и то же время - формируется привычка.",
        "Планируй Pomodoro сессии заранее - эффективнее использовать время."
    ],
    'habits': [
        "Начинай с малого - лучше 1 раз в день, чем 10 раз в неделю.",
        "Создай триггер для привычки - связывай с другим действием.",
        "Отмечай выполнение привычки сразу после выполнения.",
        "Не пропускай два дня подряд - это ломает привычку.",
        "Создай поддерживающую среду для привычки.",
        "Отмечай прогресс в привычках - это мотивирует.",
        "Планируй вознаграждение за выполнение привычки."
    ],
    'goals': [
        "Цели должны быть SMART: конкретные, измеримые, достижимые, релевантные, ограниченные по времени.",
        "Разбивай большие цели на маленькие шаги.",
        "Отмечай промежуточные результаты - это поддерживает мотивацию.",
        "Планируй шаги к цели на неделю вперед.",
        "Объявляй цели кому-то - это повышает ответственность.",
        "Регулярно пересматривай свои цели.",
        "Отмечай прогресс по целям каждый день."
    ],
    'time': [
        "Планируй день с вечера - это экономит утро.",
        "Используй правило 2 минут - если задача занимает менее 2 минут, делай сразу.",
        "Разделяй задачи на срочные и важные.",
        "Выделяй время на важные, но не срочные задачи.",
        "Используй техники управления временем: Pomodoro, матрица Эйзенхауэра.",
        "Создай расписание дня - помогает структурировать время.",
        "Устанавливай дедлайны для задач - повышает фокус."
    ],
    'learning': [
        "Используй метод интервального повторения для обучения.",
        "Разбивай сложные темы на маленькие части.",
        "Объясняй изученное кому-то - это закрепляет знания.",
        "Делай короткие перерывы во время обучения.",
        "Используй визуализацию для запоминания информации.",
        "Планируй время для обучения - делай это регулярно.",
        "Отмечай прогресс в обучении - мотивирует продолжать."
    ],
    'communication': [
        "Слушай активно - задавай вопросы и подтверждай понимание.",
        "Будь конкретен в общении - избегай двусмысленности.",
        "Используй 'я-высказывания' для выражения чувств.",
        "Практикуй эмпатию - старайся понять другую точку зрения.",
        "Обратная связь должна быть конкретной и конструктивной.",
        "Избегай критики личности - критикуй действия.",
        "Будь открытым для обратной связи."
    ],
    'selfcare': [
        "Выделяй время для себя каждый день - хотя бы 10 минут.",
        "Практикуй благодарность - помогает поддерживать позитив.",
        "Заботься о физическом здоровье - это основа продуктивности.",
        "Делай перерывы в работе - это повышает эффективность.",
        "Планируй отдых - как и работу.",
        "Ограничивай потребление негативной информации.",
        "Практикуй осознанность - помогает быть в моменте."
    ]
}

pomodoro_sessions = {}  

async def social_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        ensure_user(user_id)
        
        user_data = get_user_data(user_id)
        social_overview = get_social_overview(user_id)
        
        pomodoro_count = social_overview['pomodoro']['total_sessions']
        habit_count = social_overview['habits']['total_count']
        goal_count = social_overview['goals']['total_count']
        
        menu_text = f"""
🌱 *РАЗДЕЛ \"РАЗВИТИЕ\" - СОЦИАЛЬНОЕ БЛАГОПОЛУЧИЕ*

*📊 ТВОЯ СТАТИСТИКА (из БД):*
• 🍅 Pomodoro сессий: {pomodoro_count}
• 🎯 Привычек: {habit_count}
• 🎯 Целей: {goal_count}

*🎯 ВЫБЕРИ НАПРАВЛЕНИЕ:*

*🍅 ТАЙМЕР POMODORO*
• Улучшение продуктивности
• Фокус на важных задачах
• Регулярные перерывы

*🎯 ТРЕКЕР ПРИВЫЧЕК*
• Формирование полезных привычек
• Отслеживание прогресса
• Стрики и мотивация

*🎯 SMART ЦЕЛИ*
• Постановка и отслеживание целей
• Прогресс в процентах
• Дедлайны и задачи

*💡 ПОЛЕЗНЫЕ СОВЕТЫ*
• Получай рекомендации по развитию
• Повышай эффективность
• Учись заботиться о себе
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🍅 Pomodoro", callback_data="pomodoro_menu"),
                InlineKeyboardButton("🎯 Привычки", callback_data="habits_menu"),
            ],
            [
                InlineKeyboardButton("🎯 Цели", callback_data="goals_menu"),
                InlineKeyboardButton("💡 Советы", callback_data="social_tips"),
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data="social_stats"),
                InlineKeyboardButton("ℹ️ О разделе", callback_data="social_about"),
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
        logger.error(f"Ошибка в social_menu_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке данных. Попробуйте позже.",
            parse_mode='Markdown'
        )

async def pomodoro_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        pomodoro_stats = get_pomodoro_stats(user_id)
        
        menu_text = f"""
🍅 *ТАЙМЕР POMODORO*

*📊 ТВОЯ СТАТИСТИКА:*
• 🍅 Сегодня: {pomodoro_stats['today_pomodoros']} сессий
• 🍅 Всего: {pomodoro_stats['total_pomodoros']} сессий
• ⏰ Всего времени: {pomodoro_stats['total_time']} минут

*🎯 НАЧНИ СЕССИЮ:*
• 25 минут работы → 5 минут отдыха
• Фокус на одной задаче
• Минимум отвлечений

*💡 ПОЛЕЗНЫЕ СОВЕТЫ:*
• Планируй задачу перед началом сессии
• Используй таймер вместо телефона
• Делай перерыв между сессиями
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🍅 НАЧАТЬ СЕССИЮ", callback_data="pomodoro_start"),
                InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
            ],
            [
                InlineKeyboardButton("📜 История", callback_data="pomodoro_history"),
                InlineKeyboardButton("🎯 Советы Pomodoro", callback_data="tips_pomodoro"),
            ],
            [
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
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
        logger.error(f"Ошибка в pomodoro_menu_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке данных Pomodoro.",
            parse_mode='Markdown'
        )

async def pomodoro_start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        if user_id in pomodoro_sessions and pomodoro_sessions[user_id]['is_active']:
            await query.edit_message_text(
                text="⚠️ *У тебя уже есть активная Pomodoro сессия!*",
                parse_mode='Markdown'
            )
            return
        
        task = context.user_data.get('current_pomodoro_task', 'Без задачи')
        
        pomodoro_sessions[user_id] = {
            'state': 'work',
            'remaining': 25 * 60,  
            'task': task,
            'is_active': True,
            'is_paused': False,
            'start_time': datetime.datetime.now(),
            'session_id': None
        }
        
        response_text = f"""
🍅 *POMODORO СЕССИЯ НАЧАТА!*

*⏰ ВРЕМЯ СЕССИИ:*
• 25 минут работы
• 5 минут отдыха после

*🎯 ЗАДАЧА:*
{task}

*💡 СОВЕТ:*
{random.choice(SOCIAL_TIPS['pomodoro'])}

*🎯 ПОСЛЕ СЕССИИ:*
• Отметь выполнение
• Сделай перерыв
• Оценить результат
        """
        
        keyboard = [
            [
                InlineKeyboardButton("✅ ЗАВЕРИТЬ СЕССИЮ", callback_data="pomodoro_complete"),
                InlineKeyboardButton("⏸️ ПАУЗА", callback_data="pomodoro_pause"),
            ],
            [
                InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
                InlineKeyboardButton("🎯 Назначить задачу", callback_data="pomodoro_set_task"),
            ],
            [
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        asyncio.create_task(run_pomodoro_timer(context, query, user_id))
        
    except Exception as e:
        logger.error(f"Ошибка в pomodoro_start_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при запуске Pomodoro сессии.",
            parse_mode='Markdown'
        )

async def run_pomodoro_timer(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    global pomodoro_sessions
    
    last_update_time = datetime.datetime.now()
    
    while user_id in pomodoro_sessions and pomodoro_sessions[user_id]['is_active']:
        await asyncio.sleep(1)
        
        if pomodoro_sessions[user_id]['is_paused']:
            continue
            
        pomodoro_sessions[user_id]['remaining'] -= 1
        
        current_time = datetime.datetime.now()
        if (current_time - last_update_time).total_seconds() >= 10:
            remaining_minutes = pomodoro_sessions[user_id]['remaining'] // 60
            remaining_seconds = pomodoro_sessions[user_id]['remaining'] % 60
            
            state = pomodoro_sessions[user_id]['state']
            task = pomodoro_sessions[user_id]['task']
            
            if state == 'work':
                title = "🍅 *РАБОЧАЯ СЕССИЯ*"
                advice = "*Фокусируйся на задаче!*"
            else:
                title = "☕ *ПЕРЕРЫВ*"
                advice = "*Отдохни и восстанови силы!*"
            
            response_text = f"""
{title}

*⏰ ОСТАВШЕЕСЯ ВРЕМЯ:*
• {remaining_minutes:02d}:{remaining_seconds:02d}

*🎯 ТЕКУЩАЯ ЗАДАЧА:*
{task}

{advice}
• Не отвлекайся на другие дела
• Используй это время эффективно
        """
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ ЗАВЕРИТЬ СЕССИЮ", callback_data="pomodoro_complete"),
                    InlineKeyboardButton("⏸️ ПАУЗА", callback_data="pomodoro_pause"),
                ],
                [
                    InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
                    InlineKeyboardButton("🎯 Назначить задачу", callback_data="pomodoro_set_task"),
                ],
                [
                    InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.edit_message_text(
                    text=response_text,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Ошибка при обновлении сообщения Pomodoro: {e}")
            
            last_update_time = current_time
    
    if user_id in pomodoro_sessions:
        if pomodoro_sessions[user_id]['state'] == 'work':
            await complete_work_session(context, query, user_id)
        else:
            await complete_break_session(context, query, user_id)

async def complete_work_session(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    global pomodoro_sessions
    
    if user_id in pomodoro_sessions:
        task_description = pomodoro_sessions[user_id]['task']
        session_id = add_pomodoro_session(user_id, 25, 'work', True, task_description, datetime.date.today().isoformat())
        
        pomodoro_sessions[user_id]['state'] = 'break'
        pomodoro_sessions[user_id]['remaining'] = 5 * 60  
        pomodoro_sessions[user_id]['session_id'] = session_id
        
        try:
            response_text = """
🎉 *РАБОЧИЙ ИНТЕРВАЛ ЗАВЕРШЕН!*

*🍅 Отличная работа! Ты сфокусировался на 25 минут!*

*🔄 НАЧИНАЕМ ПЕРЕРЫВ 5 МИНУТ*

*🎯 ЧТО ДЕЛАТЬ В ПЕРЕРЫВЕ:*
• 👀 Отойди от экрана
• 💧 Выпей воды
• 🏃 Сделай 10 приседаний
• 🌳 Посмотри вдаль
• 🧘 Глубоко вдохни 3 раза

*Таймер перерыва запущен...*
⏱️ *Осталось: 05:00*
        """
            
            keyboard = [
                [
                    InlineKeyboardButton("⏸️ ПАУЗА", callback_data="pomodoro_pause"),
                    InlineKeyboardButton("✅ ЗАВЕРИТЬ СЕССИЮ", callback_data="pomodoro_complete"),
                ],
                [
                    InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
                    InlineKeyboardButton("🎯 Назначить задачу", callback_data="pomodoro_set_task"),
                ],
                [
                    InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка при завершении рабочей сессии: {e}")

async def complete_break_session(context: ContextTypes.DEFAULT_TYPE, query, user_id: int):
    global pomodoro_sessions
    
    if user_id in pomodoro_sessions:
        task_description = pomodoro_sessions[user_id]['task']
        add_pomodoro_session(user_id, 5, 'break', True, task_description, datetime.date.today().isoformat())
        
        pomodoro_sessions[user_id]['is_active'] = False
        
        pomodoro_stats = get_pomodoro_stats(user_id)
        
        try:
            response_text = f"""
✅ *POMODORO СЕССИЯ ЗАВЕРЕНА!*

*🏆 Ты выполнил(а) 1 полный цикл:*
• 25 минут работы
• 5 минут отдыха
• +1 к продуктивности

*📊 РЕЗУЛЬТАТЫ СЕССИИ:*
• 🍅 Выполнено сегодня: {pomodoro_stats['today_pomodoros']}
• 🎯 Прогресс дня: {min(pomodoro_stats['today_pomodoros'] * 25, 100)}%
• 🔥 Всего сессий: {pomodoro_stats['total_pomodoros']}

*💡 РЕКОМЕНДАЦИЯ:*
Оптимально делать 4 Pomodoro утром с перерывами.
После 4 циклов - длинный перерыв 15-30 минут.

*Готов(а) к следующей сессии?*
        """
            
            keyboard = [
                [
                    InlineKeyboardButton("🍅 НОВАЯ СЕССИЯ", callback_data="pomodoro_start"),
                    InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
                ],
                [
                    InlineKeyboardButton("📜 История", callback_data="pomodoro_history"),
                    InlineKeyboardButton("🎯 Назначить задачу", callback_data="pomodoro_set_task"),
                ],
                [
                    InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
                ]
            ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=response_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Ошибка при завершении перерыва: {e}")

async def pomodoro_set_task_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    response_text = """
🎯 *НАЗНАЧЬ ЗАДАЧУ ДЛЯ POMODORO*

*Отправь текст задачи, над которой будешь работать в следующей сессии.*

*Примеры задач:*
• Написать статью
• Подготовить презентацию
• Изучить новую тему
• Решить задачи по учебе
        """
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Статистика Pomodoro", callback_data="pomodoro_stats"),
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_pomodoro_task_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    task_text = update.message.text
    
    try:
        context.user_data['current_pomodoro_task'] = task_text
        
        response_text = f"""
✅ *ЗАДАЧА СОХРАНЕНА!*

*Твоя задача:*
"{task_text}"

*Следующая Pomodoro сессия будет посвящена этой задаче.*

*Начни сессию с помощью кнопки:*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🍅 НАЧАТЬ СЕССИЮ", callback_data="pomodoro_start"),
                InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
            ],
            [
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении задачи Pomodoro: {e}")
        await update.message.reply_text(
            text="❌ Произошла ошибка при сохранении задачи.",
            parse_mode='Markdown'
        )

async def pomodoro_pause_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id in pomodoro_sessions and pomodoro_sessions[user_id]['is_active']:
        paused_time = pomodoro_sessions[user_id]['remaining']
        pomodoro_sessions[user_id]['paused_remaining'] = paused_time
        pomodoro_sessions[user_id]['is_paused'] = True
        
        response_text = """
⏸️ *POMODORO НА ПАУЗЕ*

*⏰ ОСТАВШЕЕСЯ ВРЕМЯ:*
        """
        
        remaining_minutes = paused_time // 60
        remaining_seconds = paused_time % 60
        response_text += f"\n{remaining_minutes:02d}:{remaining_seconds:02d}"
        
        response_text += """
        
*💡 РЕКОМЕНДАЦИИ ВО ВРЕМЯ ПАУЗЫ:*
• Сделай глубокий вдох
• Отвлекись на 30-60 секунд
• Выпей воды
• Сделай короткую растяжку

*🎯 ПРОДОЛЖИТЬ:*
• Нажми "Возобновить" когда будешь готов
• Не забудь вернуться к задаче
        """
    else:
        response_text = """
⏸️ *POMODORO НА ПАУЗЕ*

*Сессия не запущена. Начни новую сессию.*
        """
    
    keyboard = [
        [
            InlineKeyboardButton("▶️ ВОЗОБНОВИТЬ", callback_data="pomodoro_resume"),
            InlineKeyboardButton("⏹️ ОСТАНОВИТЬ", callback_data="pomodoro_stop"),
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
            InlineKeyboardButton("🎯 Назначить задачу", callback_data="pomodoro_set_task"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def pomodoro_resume_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id in pomodoro_sessions and 'paused_remaining' in pomodoro_sessions[user_id]:
        pomodoro_sessions[user_id]['remaining'] = pomodoro_sessions[user_id]['paused_remaining']
        del pomodoro_sessions[user_id]['paused_remaining']
        pomodoro_sessions[user_id]['is_paused'] = False
        
        response_text = """
▶️ *POMODORO ВОЗОБНОВЛЕНО!*

*Продолжай работать над задачей:*
        """
        
        if pomodoro_sessions[user_id].get('task'):
            response_text += f"\n\n*Текущая задача:*\n{pomodoro_sessions[user_id]['task']}"
        
        remaining_minutes = pomodoro_sessions[user_id]['remaining'] // 60
        remaining_seconds = pomodoro_sessions[user_id]['remaining'] % 60
        response_text += f"\n\n*⏰ ОСТАВШЕЕСЯ ВРЕМЯ: {remaining_minutes:02d}:{remaining_seconds:02d}*"
        
    else:
        response_text = """
▶️ *POMODORO ВОЗОБНОВЛЕНО!*

*Начни новую сессию.*
        """
    
    keyboard = [
        [
            InlineKeyboardButton("✅ ЗАВЕРИТЬ СЕССИЮ", callback_data="pomodoro_complete"),
            InlineKeyboardButton("⏸️ ПАУЗА", callback_data="pomodoro_pause"),
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
            InlineKeyboardButton("🎯 Назначить задачу", callback_data="pomodoro_set_task"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def pomodoro_stop_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id in pomodoro_sessions:
        pomodoro_sessions[user_id]['is_active'] = False
    
    response_text = """
⏹️ *POMODORO СЕССИЯ ОСТАНОВЛЕНА*

*Сессия не была завершена полностью, но ты можешь:*

*🎯 ВАРИАНТЫ:*
• Начать новую сессию
• Отметить частичное выполнение
• Назначить новую задачу
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🍅 НАЧАТЬ НОВУЮ СЕССИЮ", callback_data="pomodoro_start"),
            InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
        ],
        [
            InlineKeyboardButton("🎯 Назначить задачу", callback_data="pomodoro_set_task"),
            InlineKeyboardButton("🎯 Советы Pomodoro", callback_data="tips_pomodoro"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def pomodoro_complete_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        if user_id in pomodoro_sessions and pomodoro_sessions[user_id]['is_active']:
            task_description = pomodoro_sessions[user_id]['task']
            duration = 25 if pomodoro_sessions[user_id]['state'] == 'work' else 5
            session_type = pomodoro_sessions[user_id]['state']
            
            session_id = add_pomodoro_session(user_id, duration, session_type, True, task_description, datetime.date.today().isoformat())
            
            pomodoro_sessions[user_id]['is_active'] = False
        else:
            task_description = context.user_data.get('current_pomodoro_task', 'Без задачи')
            session_id = add_pomodoro_session(user_id, 25, 'work', True, task_description, datetime.date.today().isoformat())
        
        add_achievement(user_id, "🍅 Pomodoro сессия завершена")
        
        pomodoro_stats = get_pomodoro_stats(user_id)
        
        response_text = f"""
✅ *POMODORO СЕССИЯ ЗАВЕРЕНА!*

*📊 ТВОЯ СТАТИСТИКА:*
• 🍅 Сегодня: {pomodoro_stats['today_pomodoros']} сессий
• 🍅 Всего: {pomodoro_stats['total_pomodoros']} сессий
• ⏰ Всего времени: {pomodoro_stats['total_time']} минут

*🎯 ЗАДАЧА:*
{task_description}

*🎉 ПОЗДРАВЛЕНИЕ:*
Ты успешно завершил(а) Pomodoro сессию!
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🍅 НАЧАТЬ НОВУЮ СЕССИЮ", callback_data="pomodoro_start"),
                InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
            ],
            [
                InlineKeyboardButton("📜 История", callback_data="pomodoro_history"),
                InlineKeyboardButton("🎯 Назначить задачу", callback_data="pomodoro_set_task"),
            ],
            [
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в pomodoro_complete_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при завершении сессии.",
            parse_mode='Markdown'
        )

async def pomodoro_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        pomodoro_stats = get_pomodoro_stats(user_id)
        pomodoro_history = get_pomodoro_history(user_id, days=7)
        
        total_sessions = pomodoro_stats['total_pomodoros']
        total_time = pomodoro_stats['total_time']
        today_sessions = pomodoro_stats['today_pomodoros']
        
        stats_text = f"""
📊 *СТАТИСТИКА POMODORO*

*📊 ОБЩАЯ СТАТИСТИКА:*
• 🍅 Всего сессий: {total_sessions}
• ⏰ Всего времени: {total_time} минут
• 🍅 Сегодня: {today_sessions} сессий

*🎯 ПРОГРЕСС ЗА 7 ДНЕЙ:*
"""
        
        for day in pomodoro_history:
            date = day['date']
            duration = day['duration']
            session_type = day['session_type']
            completed = "✅" if day['completed'] else "❌"
            stats_text += f"• {date}: {completed} {duration} мин ({session_type})\n"
        
        tip = random.choice(SOCIAL_TIPS['pomodoro'])
        stats_text += f"\n*💡 СОВЕТ:* {tip}"
        
        keyboard = [
            [
                InlineKeyboardButton("🍅 Pomodoro", callback_data="pomodoro_start"),
                InlineKeyboardButton("📜 История", callback_data="pomodoro_history"),
            ],
            [
                InlineKeyboardButton("🎯 Назначить задачу", callback_data="pomodoro_set_task"),
                InlineKeyboardButton("🎯 Советы Pomodoro", callback_data="tips_pomodoro"),
            ],
            [
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в pomodoro_stats_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке статистики Pomodoro.",
            parse_mode='Markdown'
        )

async def pomodoro_history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        pomodoro_history = get_pomodoro_history(user_id, days=30)
        
        if not pomodoro_history:
            response_text = "📋 *ИСТОРИЯ POMODORO*\n\nПока нет завершенных сессий. Начни Pomodoro сессию!"
        else:
            response_text = "📋 *ИСТОРИЯ POMODORO (последние 30 дней)*\n\n"
            
            for session in pomodoro_history[:10]:  
                date = session['date']
                duration = session['duration']
                session_type = session['session_type']
                completed = "✅" if session['completed'] else "❌"
                task = session['task_description'] if session['task_description'] else "Без задачи"
                
                response_text += f"• {date} - {completed} {duration} мин ({session_type})\n"
                response_text += f"  Задача: {task}\n\n"
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
                InlineKeyboardButton("🍅 Pomodoro", callback_data="pomodoro_start"),
            ],
            [
                InlineKeyboardButton("🎯 Назначить задачу", callback_data="pomodoro_set_task"),
                InlineKeyboardButton("🎯 Советы Pomodoro", callback_data="tips_pomodoro"),
            ],
            [
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в pomodoro_history_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке истории Pomodoro.",
            parse_mode='Markdown'
        )

async def habits_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        habits = get_habits(user_id)
        habit_streaks = get_habit_streaks(user_id)
        
        menu_text = f"""
🎯 *ТРЕКЕР ПРИВЫЧЕК(В разработке)*

*📊 ТВОИ ПРИВЫЧКИ:*
• Всего привычек: {len(habits)}
• Прогресс по привычкам: {habit_streaks.get('total_habits', 0) if habit_streaks else 0}

*🎯 ФУНКЦИИ:*
• Создание новых привычек
• Отслеживание выполнения
• Стрики и мотивация
• Статистика прогресса
        """
        
        keyboard = [
            [
                InlineKeyboardButton("➕ Создать привычку", callback_data="habit_create"),
                InlineKeyboardButton("📊 Статистика", callback_data="habit_stats"),
            ],
            [
                InlineKeyboardButton("🎯 Мои привычки", callback_data="habit_list"),
                InlineKeyboardButton("🎯 Советы по привычкам", callback_data="tips_habits"),
            ],
            [
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
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
        logger.error(f"Ошибка в habits_menu_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке привычек.",
            parse_mode='Markdown'
        )

async def habit_create_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    response_text = """
🎯 *СОЗДАНИЕ НОВОЙ ПРИВЫЧКИ*

*Отправь название привычки, которую хочешь формировать.*

*Примеры:*
• Пить 8 стаканов воды
• Делать зарядку утром
• Читать 10 страниц в день
• Медитировать 5 минут
• Писать дневник
        """
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Статистика привычек", callback_data="habit_stats"),
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]

async def habit_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    response_text = """
🎯 Функция в разработке
        """
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Статистика привычек", callback_data="habit_stats"),
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=response_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_habit_name_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habit_name = update.message.text
    
    try:
        context.user_data['current_habit_name'] = habit_name
        
        response_text = f"""
✅ *НАЗВАНИЕ СОХРАНЕНО!*

*Твоя привычка:*
"{habit_name}"

*Теперь опиши, как именно ты будешь выполнять эту привычку.*
        """
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика привычек", callback_data="habit_stats"),
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка при сохранении названия привычки: {e}")
        await update.message.reply_text(
            text="❌ Произошла ошибка при сохранении названия привычки.",
            parse_mode='Markdown'
        )

async def handle_habit_description_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    habit_description = update.message.text
    
    try:
        habit_name = context.user_data.get('current_habit_name')
        
        if not habit_name:
            await update.message.reply_text(
                text="❌ Сначала укажи название привычки.",
                parse_mode='Markdown'
            )
            return
        
        habit_id = add_habit(user_id, habit_name, habit_description, "daily")
        
        add_achievement(user_id, f"🎯 Создал привычку: {habit_name}")
        
        response_text = f"""
✅ *ПРИВЫЧКА СОЗДАНА!*

*Название:*
{habit_name}

*Описание:*
{habit_description}

*Частота:*
Ежедневно

*🎯 СЛЕДУЙ ИНСТРУКЦИИ:*
• Отмечай выполнение каждый день
• Не пропускай более 2 дней подряд
• Планируй время для привычки
        """
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Отметить выполнение", callback_data=f"habit_toggle_{habit_id}"),
                InlineKeyboardButton("📊 Статистика", callback_data="habit_stats"),
            ],
            [
                InlineKeyboardButton("🎯 Мои привычки", callback_data="habit_list"),
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        
    except Exception as e:
        logger.error(f"Ошибка при создании привычки: {e}")
        await update.message.reply_text(
            text="❌ Произошла ошибка при создании привычки.",
            parse_mode='Markdown'
        )

async def habit_toggle_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    callback_data = query.data
    if callback_data.startswith('habit_toggle_'):
        try:
            habit_id = int(callback_data.split('_')[2])
        except ValueError:
            await query.edit_message_text(
                text="❌ Некорректный ID привычки.",
                parse_mode='Markdown'
            )
            return
    else:
        await query.edit_message_text(
            text="❌ Некорректная команда.",
            parse_mode='Markdown'
        )
        return
    
    try:
        today = datetime.date.today().isoformat()
        update_habit_completion(user_id, habit_id, today, True)
        
        habits = get_habits(user_id)
        habit = next((h for h in habits if h['id'] == habit_id), None)
        
        if habit:
            response_text = f"""
✅ *ПРИВЫЧКА ОТМЕЧЕНА!*

*Название:*
{habit['name']}

*Описание:*
{habit['description']}

*🎯 ПРОГРЕСС:*
• Сегодня выполнено
• Продолжай в том же духе!
            """
        else:
            response_text = "✅ *ПРИВЫЧКА ОТМЕЧЕНА!*\nПродолжай в том же духе!"
        
        keyboard = [
            [
                InlineKeyboardButton("📊 Статистика", callback_data="habit_stats"),
                InlineKeyboardButton("🎯 Мои привычки", callback_data="habit_list"),
            ],
            [
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=response_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в habit_toggle_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при отметке привычки.",
            parse_mode='Markdown'
        )

async def habit_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        habit_stats = get_habit_streaks(user_id)
        habits = get_habits(user_id)
        
        stats_text = f"""
📊 *СТАТИСТИКА ПРИВЫЧЕК*

*📊 ОБЩАЯ СТАТИСТИКА:*
• Всего привычек: {len(habits)}
• Активных привычек: {len(habits)}
"""
        
        for habit in habits:
            stats_text += f"\n• {habit['name']}\n"
            stats_text += f"  Описание: {habit['description']}\n"
            stats_text += f"  Частота: {habit['frequency']}\n"
        
        tip = random.choice(SOCIAL_TIPS['habits'])
        stats_text += f"\n*💡 СОВЕТ:* {tip}"
        
        keyboard = [
            [
                InlineKeyboardButton("🎯 Создать привычку", callback_data="habit_create"),
                InlineKeyboardButton("🎯 Мои привычки", callback_data="habit_list"),
            ],
            [
                InlineKeyboardButton("🎯 Советы по привычкам", callback_data="tips_habits"),
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в habit_stats_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке статистики привычек.",
            parse_mode='Markdown'
        )

async def goals_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        goals = get_goals(user_id)
        
        menu_text = f"""
🎯 *SMART ЦЕЛИ*

*📊 ТВОИ ЦЕЛИ:*
• Всего целей: {len(goals)}
• Активных целей: {len([g for g in goals if g['status'] == 'active'])}

*🎯 ФУНКЦИИ:*
• Постановка целей по SMART
• Отслеживание прогресса
• Дедлайны и задачи
• Мотивация и достижения
        """
        
        keyboard = [
            [
                InlineKeyboardButton("➕ Создать цель", callback_data="goal_create"),
                InlineKeyboardButton("📊 Статистика", callback_data="goal_stats"),
            ],
            [
                InlineKeyboardButton("🎯 Мои цели", callback_data="goal_list"),
                InlineKeyboardButton("🎯 Советы по целям", callback_data="tips_goals"),
            ],
            [
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
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
        logger.error(f"Ошибка в goals_menu_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке целей.",
            parse_mode='Markdown'
        )

async def social_tips_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tips_text = """
💡 *ПОЛЕЗНЫЕ СОВЕТЫ ПО РАЗВИТИЮ*

*Выбери категорию советов:*

*🍅 Pomodoro*
• Техники продуктивности
• Фокус и концентрация
• Управление временем

*🎯 Привычки*
• Формирование привычек
• Поддержание мотивации
• Стрики и прогресс

*🎯 Цели*
• Постановка целей
• SMART подход
• План действий

*⏰ Управление временем*
• Планирование дня
• Приоритезация задач
• Баланс работы и отдыха

*📚 Обучение*
• Эффективные методы
• Запоминание информации
• Развитие навыков

*💬 Коммуникация*
• Общение и взаимодействие
• Обратная связь
• Работа в команде

*🧘 Самоуход*
• Баланс и восстановление
• Забота о себе
• Психологическое здоровье

*🎲 СЛУЧАЙНЫЙ СОВЕТ*
• Получи совет из любой категории
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🍅 Pomodoro", callback_data="tips_pomodoro"),
            InlineKeyboardButton("🎯 Привычки", callback_data="tips_habits"),
        ],
        [
            InlineKeyboardButton("🎯 Цели", callback_data="tips_goals"),
            InlineKeyboardButton("⏰ Время", callback_data="tips_time"),
        ],
        [
            InlineKeyboardButton("📚 Обучение", callback_data="tips_learning"),
            InlineKeyboardButton("💬 Коммуникация", callback_data="tips_communication"),
        ],
        [
            InlineKeyboardButton("🧘 Самоуход", callback_data="tips_selfcare"),
            InlineKeyboardButton("🎲 Случайный", callback_data="social_tips_random"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def social_tips_random_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    all_tips = []
    for category_tips in SOCIAL_TIPS.values():
        all_tips.extend(category_tips)
    
    random_tip = random.choice(all_tips)
    
    category = ""
    for cat, tips in SOCIAL_TIPS.items():
        if random_tip in tips:
            category = cat
            break
    
    category_names = {
        'pomodoro': '🍅 Pomodoro',
        'habits': '🎯 Привычки',
        'goals': '🎯 Цели',
        'time': '⏰ Управление временем',
        'learning': '📚 Обучение',
        'communication': '💬 Коммуникация',
        'selfcare': '🧘 Самоуход'
    }
    
    category_name = category_names.get(category, '🎯 Разное')
    
    tips_text = f"""
🎲 *СЛУЧАЙНЫЙ СОВЕТ*

*Категория: {category_name}*

*💡 СОВЕТ:*
{random_tip}

*🎯 КАК ПРИМЕНИТЬ:*
• Прочитай совет внимательно
• Подумай, как он может помочь тебе
• Попробуй внедрить в свою жизнь
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🎲 Ещё случайный", callback_data="social_tips_random"),
            InlineKeyboardButton("🎯 Категории", callback_data="social_tips"),
        ],
        [
            InlineKeyboardButton("🎯 Pomodoro", callback_data="tips_pomodoro"),
            InlineKeyboardButton("🎯 Привычки", callback_data="tips_habits"),
        ],
        [
            InlineKeyboardButton("🎯 Цели", callback_data="tips_goals"),
            InlineKeyboardButton("⏰ Время", callback_data="tips_time"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def social_stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    try:
        social_overview = get_social_overview(user_id)
        pomodoro_stats = get_pomodoro_stats(user_id)
        workout_data = get_workout_data(user_id)
        
        stats_text = f"""
📈 *СТАТИСТИКА РАЗВИТИЯ*

*🍅 POMODORO:*
• Всего сессий: {social_overview['pomodoro']['total_sessions']}
• Всего времени: {social_overview['pomodoro']['total_duration']} минут
• Сегодня: {pomodoro_stats['today_pomodoros']} сессий

*🎯 ПРИВЫЧКИ:*
• Всего привычек: {social_overview['habits']['total_count']}

*🎯 ЦЕЛИ:*
• Всего целей: {social_overview['goals']['total_count']}
• Достигнуто: {social_overview['goals']['completed_count']}

*💪 ТРЕНИРОВКИ:*
• Всего: {workout_data['total_workouts']}
• Всего минут: {workout_data['total_minutes']}
        """
        
        keyboard = [
            [
                InlineKeyboardButton("🍅 Pomodoro", callback_data="pomodoro_stats"),
                InlineKeyboardButton("🎯 Привычки", callback_data="habit_stats"),
            ],
            [
                InlineKeyboardButton("🎯 Цели", callback_data="goal_stats"),
                InlineKeyboardButton("🎯 Советы", callback_data="social_tips"),
            ],
            [
                InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        logger.error(f"Ошибка в social_stats_handler: {e}")
        await query.edit_message_text(
            text="❌ Произошла ошибка при загрузке статистики.",
            parse_mode='Markdown'
        )

async def social_about_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    about_text = """
ℹ️ *О РАЗДЕЛЕ "РАЗВИТИЕ"*

*🎯 НАША МИССИЯ:*
Помочь тебе развиваться, формировать полезные привычки и достигать целей.

*🌱 СОЦИАЛЬНОЕ БЛАГОПОЛУЧИЕ:*
• Развитие навыков
• Образование и обучение
• Коммуникация
• Самореализация

*🎯 ВОЗМОЖНОСТИ РАЗДЕЛА:*
• Таймер Pomodoro для продуктивности
• Трекер привычек с системой стриков
• SMART цели с отслеживанием прогресса
• Полезные советы по развитию
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🎯 Pomodoro", callback_data="pomodoro_menu"),
            InlineKeyboardButton("🎯 Привычки", callback_data="habits_menu"),
        ],
        [
            InlineKeyboardButton("🎯 Цели", callback_data="goals_menu"),
            InlineKeyboardButton("💡 Советы", callback_data="social_tips"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
            InlineKeyboardButton("🏠 ГЛАВНОЕ МЕНЮ", callback_data="back_to_main"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=about_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_pomodoro_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(SOCIAL_TIPS['pomodoro'])
    
    tips_text = f"""
🍅 *СОВЕТЫ ПО POMODORO*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИКИ POMODORO:*
• Работай 25 минут, отдыхай 5 минут
• Используй таймер вместо телефона
• Планируй задачи перед сессией
• Делай перерыв после 4 сессий
• Сосредоточься на одной задаче
• Минимизируй отвлечения
• Отмечай завершенные сессии
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🍅 Pomodoro", callback_data="pomodoro_start"),
            InlineKeyboardButton("📊 Статистика", callback_data="pomodoro_stats"),
        ],
        [
            InlineKeyboardButton("🎯 Случайный совет", callback_data="social_tips_random"),
            InlineKeyboardButton("🎯 Категории", callback_data="social_tips"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_habits_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(SOCIAL_TIPS['habits'])
    
    tips_text = f"""
🎯 *СОВЕТЫ ПО ПРИВЫЧКАМ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИКИ ФОРМИРОВАНИЯ ПРИВЫЧЕК:*
• Начинай с малого - лучше 1 раз в день
• Создай триггер для привычки
• Отмечай выполнение сразу
• Не пропускай два дня подряд
• Создай поддерживающую среду
• Отмечай прогресс в привычках
• Планируй вознагражение
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🎯 Создать привычку", callback_data="habit_create"),
            InlineKeyboardButton("📊 Статистика", callback_data="habit_stats"),
        ],
        [
            InlineKeyboardButton("🎯 Случайный совет", callback_data="social_tips_random"),
            InlineKeyboardButton("🎯 Категории", callback_data="social_tips"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_goals_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(SOCIAL_TIPS['goals'])
    
    tips_text = f"""
🎯 *СОВЕТЫ ПО ЦЕЛЯМ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИКИ ПОСТАНОВКИ ЦЕЛЕЙ:*
• Цели должны быть SMART
• Разбивай большие цели на шаги
• Отмечай промежуточные результаты
• Планируй шаги к цели заранее
• Объявляй цели кому-то
• Регулярно пересматривай цели
• Отмечай прогресс по целям
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🎯 Создать цель", callback_data="goal_create"),
            InlineKeyboardButton("📊 Статистика", callback_data="goal_stats"),
        ],
        [
            InlineKeyboardButton("🎯 Случайный совет", callback_data="social_tips_random"),
            InlineKeyboardButton("🎯 Категории", callback_data="social_tips"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_time_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(SOCIAL_TIPS['time'])
    
    tips_text = f"""
⏰ *СОВЕТЫ ПО УПРАВЛЕНИЮ ВРЕМЕНЕМ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИКИ УПРАВЛЕНИЯ ВРЕМЕНЕМ:*
• Планируй день с вечера
• Используй правило 2 минут
• Разделяй задачи на срочные и важные
• Выделяй время на важные задачи
• Используй тайминги и методы
• Создай расписание дня
• Устанавливай дедлайны
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🍅 Pomodoro", callback_data="pomodoro_start"),
            InlineKeyboardButton("📊 Статистика", callback_data="social_stats"),
        ],
        [
            InlineKeyboardButton("🎯 Случайный совет", callback_data="social_tips_random"),
            InlineKeyboardButton("🎯 Категории", callback_data="social_tips"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_learning_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(SOCIAL_TIPS['learning'])
    
    tips_text = f"""
📚 *СОВЕТЫ ПО ОБУЧЕНИЮ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИКИ ЭФФЕКТИВНОГО ОБУЧЕНИЯ:*
• Используй метод интервального повторения
• Разбивай темы на части
• Объясняй изученное кому-то
• Делай короткие перерывы
• Используй визуализацию
• Планируй время для обучения
• Отмечай прогресс в обучении
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🎯 Советы", callback_data="social_tips"),
            InlineKeyboardButton("📊 Статистика", callback_data="social_stats"),
        ],
        [
            InlineKeyboardButton("🎯 Случайный совет", callback_data="social_tips_random"),
            InlineKeyboardButton("🎯 Категории", callback_data="social_tips"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_communication_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(SOCIAL_TIPS['communication'])
    
    tips_text = f"""
💬 *СОВЕТЫ ПО КОММУНИКАЦИИ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИКИ ЭФФЕКТИВНОЙ КОММУНИКАЦИИ:*
• Слушай активно - задавай вопросы
• Будь конкретен в общении
• Используй 'я-высказывания'
• Практикуй эмпатию
• Давай конкретную обратную связь
• Избегай критики личности
• Будь открытым для обратной связи
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🎯 Советы", callback_data="social_tips"),
            InlineKeyboardButton("📊 Статистика", callback_data="social_stats"),
        ],
        [
            InlineKeyboardButton("🎯 Случайный совет", callback_data="social_tips_random"),
            InlineKeyboardButton("🎯 Категории", callback_data="social_tips"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def tips_selfcare_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    tip = random.choice(SOCIAL_TIPS['selfcare'])
    
    tips_text = f"""
🧘 *СОВЕТЫ ПО САМОУХОДУ*

*💡 СОВЕТ ДНЯ:*
{tip}

*🎯 ПРАКТИКИ ЗАБОТЫ О СЕБЕ:*
• Выделяй время для себя
• Практикуй благодарность
• Заботься о физическом здоровье
• Делай перерывы в работе
• Планируй отдых
• Ограничивай негативную информацию
• Практикуй осознанность
        """
    
    keyboard = [
        [
            InlineKeyboardButton("🎯 Советы", callback_data="social_tips"),
            InlineKeyboardButton("📊 Статистика", callback_data="social_stats"),
        ],
        [
            InlineKeyboardButton("🎯 Случайный совет", callback_data="social_tips_random"),
            InlineKeyboardButton("🎯 Категории", callback_data="social_tips"),
        ],
        [
            InlineKeyboardButton("🌱 В РАЗДЕЛ РАЗВИТИЕ", callback_data="social"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=tips_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

__all__ = [
    'social_menu_handler',
    'pomodoro_menu_handler',
    'pomodoro_start_handler',
    'pomodoro_set_task_handler',
    'pomodoro_pause_handler',
    'pomodoro_resume_handler',
    'pomodoro_stop_handler',
    'pomodoro_complete_handler',
    'pomodoro_stats_handler',
    'pomodoro_history_handler',
    'habits_menu_handler',
    'habit_create_handler',
    'habit_toggle_handler',
    'habit_stats_handler',
    'goals_menu_handler',
    'social_tips_handler',
    'social_tips_random_handler',
    'social_stats_handler',
    'social_about_handler',
    'tips_pomodoro_handler',
    'tips_habits_handler',
    'tips_goals_handler',
    'tips_time_handler',
    'tips_learning_handler',
    'tips_communication_handler',
    'tips_selfcare_handler',
    'handle_pomodoro_task_text',
    'handle_habit_name_text',
    'handle_habit_description_text',
]
