from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

load_dotenv()

API_KEY = os.getenv("API_KEY")

EMAIL_HOSTNAME = os.getenv("EMAIL_HOSTNAME")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

DATE_BASE_CONNECT = {"host": os.getenv("DB_IP"), 
             "user": "user", 
             "password": os.getenv("DB_PASSWORD"), 
             "database": "schoolhub"}


bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))




import logging
from logging.handlers import RotatingFileHandler

# Создаем логгер
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Форматтер с единой структурой
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Основной обработчик для всех логов
all_logs_handler = RotatingFileHandler(
    'logs/all_logs.log',
    maxBytes=5*1024*1024,  # 5 MB
    backupCount=3,
    encoding='utf-8'
)
all_logs_handler.setFormatter(formatter)

# Обработчик только для ошибок
error_handler = RotatingFileHandler(
    'logs/errors.log',
    maxBytes=5*1024*1024,
    backupCount=3,
    encoding='utf-8'
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# Консольный обработчик (опционально)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Добавляем все обработчики
logger.addHandler(all_logs_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)
