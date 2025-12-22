import os
import sys
import asyncio
import logging
import signal
from datetime import datetime

from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config import BOT_TOKEN
from handlers.common_handlers import (
    start_command,
    help_command,
    about_command,
    handle_main_menu,
    back_to_main_handler,
    unknown_command,
    progress_handler,
    challenge_handler,
    detailed_stats_handler,
    all_achievements_handler,
)
from handlers.physical_handlers import (
    physical_menu_handler,
    water_track_handler,
    water_stats_handler,
    sleep_track_handler,
    sleep_less5_handler,
    sleep_5_6_handler,
    sleep_7_8_handler,
    sleep_8_9_handler,
    sleep_6_7_handler,
    sleep_9plus_handler,
    add_steps_handler,
    steps_10kplus_handler,
    steps_less5k_handler,
    steps_5k_7k_handler,
    steps_7k_9k_handler,
    quick_workout_handler,
    workout_completed_handler,
    physical_tips_handler,
    tips_hydration_handler,
    tips_sleep_handler,
    tips_exercise_handler,
    tips_random_handler,
    tips_nutrition_handler,
    tips_posture_handler,
    tips_recovery_handler,
    tips_motivation_handler,
    physical_stats_handler,
    sleep_stats_handler,
    activity_stats_handler,
    workout_stats_handler,
    physical_achievements_handler,
    physical_charts_handler,
    export_physical_data_handler,
)
from handlers.mental_handlers import (
    mental_menu_handler,
    mood_tracker_handler,
    sos_help_handler,
    breathing_practice_handler,
    mood_great_handler,
    mood_good_handler,
    mood_ok_handler,
    mood_bad_handler,
    mood_terrible_handler,
    mood_tired_handler,
    mood_thoughtful_handler,
    mood_calm_handler,
    mood_stats_handler,
    mental_stats_handler,
    mood_add_note_handler,
    sleep_techniques_handler,
    handle_mood_note_text,
)
from handlers.social_handlers import (
    social_menu_handler,
    pomodoro_menu_handler,
    pomodoro_start_handler,
    pomodoro_set_task_handler,
    pomodoro_pause_handler,
    pomodoro_resume_handler,
    pomodoro_stop_handler,
    pomodoro_complete_handler,
    pomodoro_stats_handler,
    pomodoro_history_handler,
    habits_menu_handler,
    habit_create_handler,
    habit_toggle_handler,
    habit_stats_handler,
    goals_menu_handler,
    social_tips_handler,
    social_tips_random_handler,
    social_stats_handler,
    social_about_handler,
    tips_pomodoro_handler,
    tips_habits_handler,
    tips_goals_handler,
    tips_time_handler,
    tips_learning_handler,
    tips_communication_handler,
    tips_selfcare_handler,
    handle_pomodoro_task_text,
    handle_habit_name_text,
    handle_habit_description_text,
)

def setup_logging():
    
    logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(
                filename=os.path.join(logs_dir, f'bot_{datetime.now().strftime("%Y%m%d")}.log'),
                encoding='utf-8'
            ),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

logger = setup_logging()

async def post_init(application: Application) -> None:
    
    try:
        bot = await application.bot.get_me()
        
        logger.info("=" * 60)
        logger.info(f"🤖 Бот инициализирован: @{bot.username}")
        logger.info(f"📛 Имя: {bot.first_name}")
        logger.info(f"🆔 ID: {bot.id}")
        logger.info(f"🚀 Бот готов к работе с SQLite базой данных!")
        logger.info("=" * 60)
        
        print("\n" + "=" * 60)
        print("🎯 YAProSB_bot - Бот для баланса благополучия")
        print("=" * 60)
        print(f"👤 Имя бота: {bot.first_name}")
        print(f"🔗 Username: @{bot.username}")
        print(f"📅 Запуск: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"💾 База данных: SQLite (yaprosb_bot.db)")
        print("=" * 60)
        print("✅ Бот успешно запущен!")
        print(f"📱 Откройте Telegram: https://t.me/{bot.username}")
        print("\n⏸️  Для остановки нажмите Ctrl+C")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"Ошибка в post_init: {e}")
        print(f"⚠️ Внимание: {e}")

async def error_handler(update: object, context) -> None:
    
    logger.error(f"Произошла ошибка при обработке обновления: {context.error}", exc_info=context.error)
    
    try:
        if update and hasattr(update, 'effective_chat'):
            error_message = """
😕 *Упс, произошла ошибка*

Не волнуйся, это не твоя вина!
Попробуй выполнить одно из следующих действий:

1. Перезапустить бота командой `/start`
2. Подождать несколько минут и повторить
3. Если ошибка повторяется, сообщи о ней

А пока можешь вернуться в меню:
            """
            
            from telegram import InlineKeyboardMarkup, InlineKeyboardButton
            keyboard = [[InlineKeyboardButton("🔙 В ГЛАВНОЕ МЕНЮ", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if update.callback_query:
                await update.callback_query.message.reply_text(
                    text=error_message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            elif update.message:
                await update.message.reply_text(
                    text=error_message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            
            logger.info(f"Отправлено сообщение об ошибке пользователю {update.effective_chat.id}")
            
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение об ошибке: {e}")

def setup_application() -> Application:
    
    logger.info("Создание приложения бота...")
    
    try:
        if not BOT_TOKEN:
            logger.error("Токен бота не найден!")
            print("❌ ОШИБКА: Токен бота не найден!")
            sys.exit(1)
        
        application = Application.builder().token(BOT_TOKEN).build()
        logger.info("Приложение бота создано успешно")
        
        return application
        
    except Exception as e:
        logger.error(f"Ошибка при создании приложения: {e}")
        raise

def setup_handlers(application: Application) -> None:
    
    logger.info("Настройка обработчиков...")
    
    # ==================== КОМАНДЫ ====================
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", handle_main_menu))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("stats", progress_handler))
    
    # ==================== ГЛАВНОЕ МЕНЮ ====================
    application.add_handler(CallbackQueryHandler(physical_menu_handler, pattern='^physical$'))
    application.add_handler(CallbackQueryHandler(mental_menu_handler, pattern='^mental$'))
    application.add_handler(CallbackQueryHandler(social_menu_handler, pattern='^social$'))
    application.add_handler(CallbackQueryHandler(back_to_main_handler, pattern='^back_to_main$'))
    
    # ==================== ДОПОЛНИТЕЛЬНЫЕ КНОПКИ ====================
    application.add_handler(CallbackQueryHandler(about_command, pattern='^about$'))
    application.add_handler(CallbackQueryHandler(progress_handler, pattern='^progress$'))
    application.add_handler(CallbackQueryHandler(challenge_handler, pattern='^challenge$'))
    application.add_handler(CallbackQueryHandler(help_command, pattern='^help$'))
    application.add_handler(CallbackQueryHandler(detailed_stats_handler, pattern='^detailed_stats$'))
    application.add_handler(CallbackQueryHandler(all_achievements_handler, pattern='^all_achievements$'))
    
    # ==================== БЛОК "ТЕЛО" ====================
    application.add_handler(CallbackQueryHandler(water_track_handler, pattern='^water_track$'))
    application.add_handler(CallbackQueryHandler(water_stats_handler, pattern='^water_stats$'))
    application.add_handler(CallbackQueryHandler(sleep_track_handler, pattern='^sleep_track$'))
    application.add_handler(CallbackQueryHandler(add_steps_handler, pattern='^add_steps$'))
    application.add_handler(CallbackQueryHandler(quick_workout_handler, pattern='^quick_workout$'))
    application.add_handler(CallbackQueryHandler(workout_completed_handler, pattern='^workout_completed$'))
    
    # Обработчики сна
    application.add_handler(CallbackQueryHandler(sleep_less5_handler, pattern='^sleep_less5$'))
    application.add_handler(CallbackQueryHandler(sleep_5_6_handler, pattern='^sleep_5_6$'))
    application.add_handler(CallbackQueryHandler(sleep_6_7_handler, pattern='^sleep_6_7$'))
    application.add_handler(CallbackQueryHandler(sleep_7_8_handler, pattern='^sleep_7_8$'))
    application.add_handler(CallbackQueryHandler(sleep_8_9_handler, pattern='^sleep_8_9$'))
    application.add_handler(CallbackQueryHandler(sleep_9plus_handler, pattern='^sleep_9plus$'))
    
    # Обработчики шагов
    application.add_handler(CallbackQueryHandler(steps_less5k_handler, pattern='^steps_less5k$'))
    application.add_handler(CallbackQueryHandler(steps_5k_7k_handler, pattern='^steps_5k_7k$'))
    application.add_handler(CallbackQueryHandler(steps_7k_9k_handler, pattern='^steps_7k_9k$'))
    application.add_handler(CallbackQueryHandler(steps_10kplus_handler, pattern='^steps_10kplus$'))
    
    # Полезные советы
    application.add_handler(CallbackQueryHandler(physical_tips_handler, pattern='^physical_tips$'))
    application.add_handler(CallbackQueryHandler(tips_hydration_handler, pattern='^tips_hydration$'))
    application.add_handler(CallbackQueryHandler(tips_sleep_handler, pattern='^tips_sleep$'))
    application.add_handler(CallbackQueryHandler(tips_exercise_handler, pattern='^tips_exercise$'))
    application.add_handler(CallbackQueryHandler(tips_nutrition_handler, pattern='^tips_nutrition$'))
    application.add_handler(CallbackQueryHandler(tips_posture_handler, pattern='^tips_posture$'))
    application.add_handler(CallbackQueryHandler(tips_recovery_handler, pattern='^tips_recovery$'))
    application.add_handler(CallbackQueryHandler(tips_motivation_handler, pattern='^tips_motivation$'))
    application.add_handler(CallbackQueryHandler(tips_random_handler, pattern='^tips_random$'))
    
    # Статистика физического здоровья
    application.add_handler(CallbackQueryHandler(physical_stats_handler, pattern='^physical_stats$'))
    application.add_handler(CallbackQueryHandler(sleep_stats_handler, pattern='^sleep_stats$'))
    application.add_handler(CallbackQueryHandler(activity_stats_handler, pattern='^activity_stats$'))
    application.add_handler(CallbackQueryHandler(workout_stats_handler, pattern='^workout_stats$'))
    application.add_handler(CallbackQueryHandler(physical_achievements_handler, pattern='^physical_achievements$'))
    application.add_handler(CallbackQueryHandler(physical_charts_handler, pattern='^physical_charts$'))
    application.add_handler(CallbackQueryHandler(export_physical_data_handler, pattern='^export_physical_data$'))
    
    # ==================== БЛОК "ДУША" ====================
    application.add_handler(CallbackQueryHandler(mood_tracker_handler, pattern='^mood_tracker$'))
    application.add_handler(CallbackQueryHandler(sos_help_handler, pattern='^sos_help$'))
    application.add_handler(CallbackQueryHandler(breathing_practice_handler, pattern='^breathing_practice$'))
    
    # Обработчики дневника настроения
    application.add_handler(CallbackQueryHandler(mood_great_handler, pattern='^mood_great$'))
    application.add_handler(CallbackQueryHandler(mood_good_handler, pattern='^mood_good$'))
    application.add_handler(CallbackQueryHandler(mood_ok_handler, pattern='^mood_ok$'))
    application.add_handler(CallbackQueryHandler(mood_bad_handler, pattern='^mood_bad$'))
    application.add_handler(CallbackQueryHandler(mood_terrible_handler, pattern='^mood_terrible$'))
    application.add_handler(CallbackQueryHandler(mood_tired_handler, pattern='^mood_tired$'))
    application.add_handler(CallbackQueryHandler(mood_thoughtful_handler, pattern='^mood_thoughtful$'))
    application.add_handler(CallbackQueryHandler(mood_calm_handler, pattern='^mood_calm$'))
    application.add_handler(CallbackQueryHandler(mood_stats_handler, pattern='^mood_stats$'))
    
    # Ментальное здоровье - дополнительные функции
    application.add_handler(CallbackQueryHandler(mental_stats_handler, pattern='^mental_stats$'))
    application.add_handler(CallbackQueryHandler(mood_add_note_handler, pattern='^mood_add_note$'))
    application.add_handler(CallbackQueryHandler(sleep_techniques_handler, pattern='^sleep_techniques$'))
    
    # ==================== БЛОК "РАЗВИТИЕ" (SOCIAL) ====================
    # Основное меню и информация
    application.add_handler(CallbackQueryHandler(social_menu_handler, pattern='^social$'))
    application.add_handler(CallbackQueryHandler(social_about_handler, pattern='^social_about$'))
    application.add_handler(CallbackQueryHandler(social_stats_handler, pattern='^social_stats$'))
    
    # Pomodoro таймер
    application.add_handler(CallbackQueryHandler(pomodoro_menu_handler, pattern='^pomodoro_menu$'))
    application.add_handler(CallbackQueryHandler(pomodoro_start_handler, pattern='^pomodoro_start$'))
    application.add_handler(CallbackQueryHandler(pomodoro_set_task_handler, pattern='^pomodoro_set_task$'))
    application.add_handler(CallbackQueryHandler(pomodoro_pause_handler, pattern='^pomodoro_pause$'))
    application.add_handler(CallbackQueryHandler(pomodoro_resume_handler, pattern='^pomodoro_resume$'))
    application.add_handler(CallbackQueryHandler(pomodoro_stop_handler, pattern='^pomodoro_stop$'))
    application.add_handler(CallbackQueryHandler(pomodoro_complete_handler, pattern='^pomodoro_complete$'))
    application.add_handler(CallbackQueryHandler(pomodoro_stats_handler, pattern='^pomodoro_stats$'))
    application.add_handler(CallbackQueryHandler(pomodoro_history_handler, pattern='^pomodoro_history$'))
    
    # Трекер привычек
    application.add_handler(CallbackQueryHandler(habits_menu_handler, pattern='^habits_menu$'))
    application.add_handler(CallbackQueryHandler(habit_create_handler, pattern='^habit_create$'))
    application.add_handler(CallbackQueryHandler(habit_stats_handler, pattern='^habit_stats$'))
    
    # SMART цели
    application.add_handler(CallbackQueryHandler(goals_menu_handler, pattern='^goals_menu$'))
    
    # Библиотека советов по развитию
    application.add_handler(CallbackQueryHandler(social_tips_handler, pattern='^social_tips$'))
    application.add_handler(CallbackQueryHandler(social_tips_random_handler, pattern='^social_tips_random$'))
    application.add_handler(CallbackQueryHandler(tips_pomodoro_handler, pattern='^tips_pomodoro$'))
    application.add_handler(CallbackQueryHandler(tips_habits_handler, pattern='^tips_habits$'))
    application.add_handler(CallbackQueryHandler(tips_goals_handler, pattern='^tips_goals$'))
    application.add_handler(CallbackQueryHandler(tips_time_handler, pattern='^tips_time$'))
    application.add_handler(CallbackQueryHandler(tips_learning_handler, pattern='^tips_learning$'))
    application.add_handler(CallbackQueryHandler(tips_communication_handler, pattern='^tips_communication$'))
    application.add_handler(CallbackQueryHandler(tips_selfcare_handler, pattern='^tips_selfcare$'))
    
    # Динамические обработчики привычек (pattern с переменной частью)
    application.add_handler(CallbackQueryHandler(habit_toggle_handler, pattern='^habit_toggle_'))
    
    # ==================== ТЕКСТОВЫЕ СООБЩЕНИЯ ====================
    # Обработчик текстовых заметок к настроению
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        handle_mood_note_text
    ))
    
    # Обработчик текстовых заданий для Pomodoro
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_pomodoro_task_text
    ))
    
    # Обработчик названий привычек
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_habit_name_text
    ))
    
    # Обработчик описаний привычек
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_habit_description_text
    ))
    
    # Обработчик неизвестных сообщений (должен быть последним)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, 
        unknown_command
    ))
    
    # ==================== ОБРАБОТЧИК ОШИБОК ====================
    application.add_error_handler(error_handler)
    
    logger.info("Все обработчики успешно зарегистрированы")

async def shutdown(application: Application) -> None:
    
    logger.info("Завершение работы бота...")
    
    try:
        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
        for task in tasks:
            task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        await application.stop()
        await application.shutdown()
        
        logger.info("Бот успешно остановлен")
        
        try:
            from database import db
            if hasattr(db, 'close_connections'):
                db.close_connections()
                logger.info("Соединения с базой данных закрыты")
        except ImportError:
            pass
        
    except Exception as e:
        logger.error(f"Ошибка при завершении работы: {e}")

def check_dependencies() -> bool:
    
    logger.info("Проверка зависимостей...")
    
    if not os.path.exists('.env'):
        print("❌ ФАЙЛ .env НЕ НАЙДЕН!")
        print("Создайте файл .env в папке проекта с содержимым:")
        print("BOT_TOKEN=ваш_токен_от_BotFather")
        return False
    
    if not os.path.exists('.env.example'):
        print("⚠️ ФАЙЛ .env.example не найден, создаем...")
        try:
            with open('.env.example', 'w') as f:
                f.write("BOT_TOKEN=your_bot_token_here\n")
        except Exception as e:
            print(f"❌ Не удалось создать .env.example: {e}")
    
    required_dirs = ['handlers', 'assets', 'logs', 'backups']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)
                logger.info(f"Создана папка: {dir_name}")
            except Exception as e:
                logger.error(f"Не удалось создать папку {dir_name}: {e}")
                print(f"❌ Не удалось создать папку {dir_name}")
                return False
    
    required_files = [
        'config.py',
        'database.py',
        'storage.py',
        'requirements.txt',
        'handlers/__init__.py',
        'handlers/common_handlers.py',
        'handlers/physical_handlers.py',
        'handlers/mental_handlers.py',
        'handlers/social_handlers.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ ОТСУТСТВУЮТ НЕОБХОДИМЫЕ ФАЙЛЫ:")
        for file in missing_files:
            print(f"   - {file}")
        print("\nСоздайте недостающие файлы или проверьте структуру проекта")
        return False
    
    try:
        from database import db
        db.init_database()
        logger.info("База данных проверена/создана")
    except ImportError as e:
        print(f"❌ Не удалось импортировать database.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при работе с базой данных: {e}")
        return False
    
    try:
        from config import BOT_TOKEN
        if not BOT_TOKEN or BOT_TOKEN == "ваш_токен_от_BotFather":
            print("❌ ТОКЕН БОТА НЕ НАСТРОЕН!")
            print("Откройте файл .env и замените 'ваш_токен_от_BotFather' на реальный токен")
            return False
    except ImportError:
        print("❌ Не удалось импортировать config.py")
        return False
    
    logger.info("Все зависимости проверены успешно")
    return True

def check_python_version() -> bool:
    import sys
    if sys.version_info < (3, 8):
        print("❌ Необходима версия Python 3.8 или выше!")
        print(f"   У вас установлена: {sys.version}")
        return False
    return True

def check_requirements():
    required_packages = [
        ('python-telegram-bot', 'telegram'),
        ('python-dotenv', 'dotenv'),
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            if import_name == 'telegram':
                import telegram
            elif import_name == 'dotenv':
                from dotenv import load_dotenv
            logger.info(f"✅ {package_name} установлен")
        except ImportError:
            missing_packages.append(package_name)
            logger.warning(f"❌ {package_name} не найден")
    
    try:
        import sqlite3
        logger.info("✅ sqlite3 доступен")
    except ImportError:
        logger.error("❌ sqlite3 не доступен (это критическая ошибка)")
        missing_packages.append("sqlite3")
    
    if missing_packages:
        print("❌ ОТСУТСТВУЮТ ЗАВИСИМОСТИ:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nУстановите зависимости командой:")
        print("pip install -r requirements.txt")
        return False
    
    logger.info("✅ Все зависимости установлены успешно")
    return True

async def backup_database():
    try:
        from database import db
        if hasattr(db, 'create_backup'):
            backup_path = db.create_backup()
            logger.info(f"Создана резервная копия базы данных: {backup_path}")
    except Exception as e:
        logger.error(f"Ошибка при создании резервной копии: {e}")

async def main() -> None:
    
    try:
        if not check_python_version():
            sys.exit(1)
        
        if not check_dependencies():
            sys.exit(1)
        
        if not check_requirements():
            sys.exit(1)
        
        await backup_database()
        
        application = setup_application()
        
        setup_handlers(application)
        
        application.post_init = post_init
        
        logger.info("Запуск бота...")
        
        await application.initialize()
        await application.start()
        
        await application.updater.start_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
        stop_event = asyncio.Event()
        
        def signal_handler():
            logger.info("Получен сигнал завершения")
            stop_event.set()
        
        try:
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGINT, signal_handler)
            loop.add_signal_handler(signal.SIGTERM, signal_handler)
        except (ImportError, NotImplementedError) as e:
            logger.warning(f"Не удалось настроить обработку сигналов: {e}")
        
        await stop_event.wait()
        
        await shutdown(application)
        
    except KeyboardInterrupt:
        logger.info("Работа бота прервана пользователем (Ctrl+C)")
        print("\n🛑 Работа бота прервана пользователем")
        
        try:
            if 'application' in locals():
                await shutdown(application)
        except Exception as e:
            logger.error(f"Ошибка при завершении работы: {e}")
        
    except Exception as e:
        logger.error(f"Критическая ошибка при работе бота: {e}", exc_info=True)
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        
        
        try:
            if 'application' in locals():
                await shutdown(application)
        except Exception as inner_e:
            logger.error(f"Ошибка при аварийном завершении: {inner_e}")
        
        sys.exit(1)
