import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

if not ADMIN_CHAT_ID:
    raise ValueError("ADMIN_CHAT_ID не найден в переменных окружения")