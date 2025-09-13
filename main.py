import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN, ADMIN_CHAT_ID, configure_logging
from handlers import client_handlers, admin_handlers, callback_handlers

# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Включаем роутеры
dp.include_router(client_handlers.router)
dp.include_router(admin_handlers.router)
dp.include_router(callback_handlers.callback_router)


async def on_startup():
    try:
        # Отправляем сообщение админу при запуске бота
        await bot.send_message(ADMIN_CHAT_ID, "🤖 Бот запущен и готов к работе!")
        logger.info(msg="Bot is running")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения админу: {e}")

async def on_shutdown():
    try:
        # Отправляем сообщение админу при запуске бота
        await bot.send_message(ADMIN_CHAT_ID, "🤖 Бот остановлен!")
        logger.info(msg="Bot is shut down")
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения админу: {e}")

async def main():
    # Запускаем бота с обработкой событий
    configure_logging(level=logging.INFO)
    try:
        await on_startup()
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка в работе бота: {e}")
    finally:
        await on_shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())