from aiogram import Bot
from aiogram.fsm.context import FSMContext

from config import ADMIN_CHAT_ID
import logging

from database.models import Order
from states import OrderCar

logger = logging.getLogger(__name__)


async def send_admin_notification(bot: Bot, order: Order):
    """Функция для отправки уведомления админу"""
    try:
        admin_message = (
            "🚗 НОВАЯ ЗАЯВКА НА АВТОМОБИЛЬ!\n\n"
            f"👤 Имя: {order.name}\n"
            f"📞 Телефон: {order.phone}\n"
            f"📧 Email: {order.email}\n"
            f"🏙 Город: {order.city}\n"
            f"🚗 Марка/Модель: {order.car_model}\n"
            f"💰 Бюджет: {order.budget} RUB\n\n"
            f"🆔 ID пользователя: {order.user_id}"
        )

        await bot.send_message(ADMIN_CHAT_ID, admin_message)
        logger.info(f"Новая заявка от пользователя {order.user_id}")

    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления админу: {e}")


async def handle_retry(chat_id: int, state: FSMContext, bot: Bot, message_id: int = None):
    """Универсальная обработка перезапуска"""
    current_state = await state.get_state()

    if current_state is None:
        error_text = "Нет заявок в процессе заполнения. Для новой заявки нажмите /order"
        if message_id:
            await bot.edit_message_text(error_text, chat_id, message_id)
        else:
            await bot.send_message(chat_id, error_text)
        return False

    await state.clear()
    await state.set_state(OrderCar.name)

    success_text = (
        "🔄 Заявка сброшена 🔄\n\n"
        "Начинаем заполнение заявки заново!\n"
        "Пожалуйста, введите ваше имя:"
    )

    if message_id:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=success_text
        )
    else:
        await bot.send_message(chat_id, success_text)
    return True