import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_CHAT_ID, DATABASE_URL, configure_logging
from database.core import Database
from handlers import admin_cmd_handlers, admin_callback_handlers, order_fsm_handlers, client_callback_handlers, client_cmd_handlers
from utils.commands_setup import set_user_commands, set_admin_commands

# Настройка логирования
logger = logging.getLogger(__name__)


async def on_startup(bot: Bot):
    try:
        await set_user_commands(bot)
        await set_admin_commands(bot, ADMIN_CHAT_ID)

        await bot.send_message(ADMIN_CHAT_ID, "🤖 Бот запущен и готов к работе!")
        logger.info(msg="Bot is running")
    except Exception as e:
        logger.error(f"Error sending message to Admin chat: {e}")

async def on_shutdown(bot: Bot):
    try:
        await bot.send_message(ADMIN_CHAT_ID, "🤖 Бот остановлен!")
        logger.info(msg="Bot is shut down")
    except Exception as e:
        logger.error(f"Error sending message to Admin chat: {e}")

async def main():
    configure_logging(level=logging.INFO)

    # Инициализация бота
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Инициализация БД
    db = Database(DATABASE_URL)
    await db.create_tables()
    logger.info("Database initialized successfully")

    # Инициализация диспетчера
    dp = Dispatcher(bot=bot, db=db)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(admin_cmd_handlers.admin_cmd_router)
    dp.include_router(admin_callback_handlers.admin_callback_router)
    dp.include_router(client_cmd_handlers.client_cmd_router)
    dp.include_router(order_fsm_handlers.router)
    dp.include_router(client_callback_handlers.client_callback_router)

    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"TG Bot error: {e}")


if __name__ == "__main__":
    asyncio.run(main())