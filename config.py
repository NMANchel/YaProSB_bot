import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
LOGO_PATH = 'assets/logo.png'
DB_PATH = 'yaprosb_bot.db'
BACKUP_DIR = 'backups'
LOG_DIR = 'logs'
LOG_LEVEL = 'INFO'