from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.markdown import hbold, hlink
from config import ADMIN_CHAT_ID
import logging

from database.core import Database
from database.repository import OrderRepository
from database.service import OrderService
from utils.filters import IsAdminChatFilter
from keyboards.common import get_admin_order_keyboard
from utils.texts import ClientReplies
from utils.utils import parse_order_id, format_order_detail

logger = logging.getLogger(__name__)

admin_cmd_router = Router(name="admin_cmd_handlers")
admin_cmd_router.message.filter(IsAdminChatFilter(ADMIN_CHAT_ID))


@admin_cmd_router.message(Command("admin"))
async def cmd_admin(message: Message):

    await message.answer(
        "👨‍💼 <b>Панель администратора</b>\n\n"
        "📊 <b>Доступные команды:</b>\n"
        "/id - получить ID этого чата\n"
        "/orders - получить список всех заявок\n"
        "/order <номер_заявки> - получить инфо по кокретной заявке\n\n"
        "⚙️ <b>Управление ботом:</b>\n"
        "/restart - перезапустить бота\n"
        "/stop - остановить бота\n\n"
        "💡 <i>Все команды работают только в этом чате</i>"
    )


@admin_cmd_router.message(Command("id"))
async def cmd_id(message: Message):
    await message.answer(f"🆔 ID этого чата: <code>{message.chat.id}</code>")


@admin_cmd_router.message(Command("orders"))
async def cmd_orders(message: Message, db: Database):
    try:
        async with db.async_session_factory() as session:
            service = OrderService(session)
            orders_list = await service.get_all_orders()
            if not orders_list:
                await message.answer("Заявок пока нет")
                return
            response = "📋 Список всех заявок:\n\n"
            for order in orders_list:
                response += f"#{order.id} | {order.name} | {order.phone} | {order.city} | {order.car_model} | {order.status}\n"
            await message.answer(response)
    except Exception as e:
        logger.error(f"Error in get orders action: {e}")
        await message.answer(ClientReplies.ERROR_ALERT, show_alert=True)


@admin_cmd_router.message(Command("order"))
async def cmd_order_detail(message: Message, db: Database):
    order_id = parse_order_id(message.text)
    if not order_id:
        await message.answer(
            "❌ <b>Неверный формат ID</b>\n\n"
            "Использование команды:\n"
            "/order ID_заявки\n"
            "Пример: <code>/order 15</code>",
            parse_mode="HTML",
        )
        return
    try:

        async with db.async_session_factory() as session:
            service = OrderService(session)
            order = await service.get_order_by_id(order_id=order_id)
            if not order:
                await message.answer(
                    "❌ <b>Заявка не найдена</b>\n\n"
                    f"Заявка с ID #{order_id} не существует.\n"
                    "Проверьте правильность ID или используйте /orders для списка всех заявок.",
                    parse_mode="HTML",
                )
                return
            detail_text = format_order_detail(order)
        await message.answer(
            detail_text,
            parse_mode="HTML",
            reply_markup=get_admin_order_keyboard(order_id=order.id),
        )
    except Exception as e:
        logger.error(f"Error in order detail action: {e}")
        await message.answer(ClientReplies.ERROR_ALERT, show_alert=True)
