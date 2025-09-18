from aiogram import Bot
from aiogram.fsm.context import FSMContext

from config import ADMIN_CHAT_ID
import logging

from database.models import Order
from keyboards.common import get_admin_order_keyboard
from states import OrderCar
from utils.texts import ClientReplies

logger = logging.getLogger(__name__)


async def send_admin_notification(bot: Bot, order: Order):
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

        await bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=admin_message,
            reply_markup=get_admin_order_keyboard(order_id=order.id),
        )
        logger.info(f"Новая заявка от пользователя {order.user_id}")

    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления админу: {e}")


async def handle_retry(
    chat_id: int, state: FSMContext, bot: Bot, message_id: int = None
):
    current_state = await state.get_state()

    if current_state is None:
        error_text = ClientReplies.RETRY_NO_ORDERS
        if message_id:
            await bot.edit_message_text(error_text, chat_id, message_id)
        else:
            await bot.send_message(chat_id, error_text)
        return False

    await state.clear()
    await state.set_state(OrderCar.name)

    success_text = ClientReplies.RETRY_SUCCESS
    if message_id:
        await bot.edit_message_text(
            chat_id=chat_id, message_id=message_id, text=success_text
        )
    else:
        await bot.send_message(chat_id, success_text)
    return True


def parse_order_id(text: str) -> int | None:
    """
    Извлекает ID заявки из текста команды.
    Возвращает int, если получилось, иначе None.
    Пример:
        "/order 15" -> 15
        "/order abc" -> None
    """
    parts = text.split()
    if len(parts) < 2:
        return None
    if not parts[1].isdigit():
        return None
    return int(parts[1])


def format_order_detail(order) -> str:
    """
    Формирует текст для показа деталей заявки.
    """
    return (
        f"📋 {'Детали заявки'} #{order.id}\n\n"
        f"👤 {'Клиент:'} {order.name}\n"
        f"📞 {'Телефон:'} {order.phone}\n"
        f"📧 {'Email:'} {order.email}\n"
        f"🚗 {'Автомобиль:'} {order.car_model}\n"
        f"💰 {'Бюджет:'} {order.budget} USD\n"
        f"⏰ {'Создана:'} {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"📊 {'Статус:'} {order.status}"
    )
