from aiogram import Bot
from config import ADMIN_CHAT_ID
import logging

logger = logging.getLogger(__name__)


async def send_admin_notification(bot: Bot, data: dict, user_id: int):
    """Функция для отправки уведомления админу"""
    try:
        admin_message = (
            "🚗 НОВАЯ ЗАЯВКА НА АВТОМОБИЛЬ!\n\n"
            f"👤 Имя: {data['name']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"📧 Email: {data['email']}\n"
            f"🚗 Марка/Модель: {data['car_model']}\n"
            f"💰 Бюджет: {data['budget']} USD\n\n"
            f"🆔 ID пользователя: {user_id}"
        )

        await bot.send_message(ADMIN_CHAT_ID, admin_message)
        logger.info(f"Новая заявка от пользователя {user_id}")

    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления админу: {e}")