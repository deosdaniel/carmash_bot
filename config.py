import logging
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

DATABASE_URL = os.getenv('DATABASE_URL')
DB_ECHO = os.getenv('DB_ECHO')


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

if not ADMIN_CHAT_ID:
    raise ValueError("ADMIN_CHAT_ID не найден в переменных окружения")



def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt='%Y-%m-%d %H:%M:%S',
        format="[%(asctime)s.%(msecs)03d]  %(module)s:%(lineno)d %(levelname)s - %(message)s"
    )

    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    if DB_ECHO == "True":
        sqlalchemy_logger.setLevel(logging.INFO)
    else:
        sqlalchemy_logger.setLevel(logging.WARNING)