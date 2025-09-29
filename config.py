import logging
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
ADMIN_THREAD_ID = os.getenv("ADMIN_THREAD_ID")

DATABASE_URL = os.getenv("DATABASE_URL")
DB_ECHO = os.getenv("DB_ECHO")


if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

if not ADMIN_CHAT_ID:
    raise ValueError("ADMIN_CHAT_ID не найден в переменных окружения")


def configure_logging(level=logging.INFO):
    logging.basicConfig(
        level=level,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="[%(asctime)s.%(msecs)03d]  %(module)s:%(lineno)d %(levelname)s - %(message)s",
    )
    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("dispatcher").setLevel(logging.WARNING)
    logging.getLogger("aiogram.client.session").setLevel(logging.WARNING)

    sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
    if DB_ECHO == "true":
        sqlalchemy_logger.setLevel(logging.INFO)
    else:
        sqlalchemy_logger.setLevel(logging.WARNING)
