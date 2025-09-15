import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScope, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_CHAT_ID, DATABASE_URL, configure_logging
from database.core import Database
from middleware.db_middleware import DbMiddleware
from handlers import admin_cmd_handlers, admin_callback_handlers, order_fsm_handlers, client_callback_handlers, client_cmd_handlers


# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

# Включаем роутеры

dp.include_router(admin_cmd_handlers.admin_cmd_router)
dp.include_router(admin_callback_handlers.admin_callback_router)
dp.include_router(client_cmd_handlers.client_cmd_router)
dp.include_router(order_fsm_handlers.router)
dp.include_router(client_callback_handlers.client_callback_router)


async def on_startup():
    try:
        admin_commands = [
            BotCommand(command="orders", description="📊 Список заявок"),
        ]
        await bot.set_my_commands(admin_commands, BotCommandScopeChat(chat_id=ADMIN_CHAT_ID))
        # Отправляем сообщение админу при запуске бота
        await bot.send_message(ADMIN_CHAT_ID, "🤖 Бот запущен и готов к работе!")
        logger.info(msg="Bot is running")
    except Exception as e:
        logger.error(f"Error sending message to Admin chat: {e}")

async def on_shutdown():
    try:
        # Отправляем сообщение админу при запуске бота
        await bot.send_message(ADMIN_CHAT_ID, "🤖 Бот остановлен!")
        logger.info(msg="Bot is shut down")
    except Exception as e:
        logger.error(f"Error sending message to Admin chat: {e}")

async def main():
    configure_logging(level=logging.INFO)

    db = Database(DATABASE_URL)
    await db.create_tables()
    dp.update.outer_middleware(DbMiddleware(db))
    logger.info("Database initialized successfully")

    try:
        await on_startup()
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"TG Bot error: {e}")
    finally:
        await on_shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())