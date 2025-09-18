from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from config import ADMIN_CHAT_ID
import logging

from database.core import Database
from database.service import OrderService
from utils.filters import IsAdminChatFilter
from keyboards.common import get_admin_order_keyboard
from utils.texts import ClientReplies, AdminReplies
from utils.utils import parse_order_id, format_order_detail

logger = logging.getLogger(__name__)

admin_cmd_router = Router(name="admin_cmd_handlers")
admin_cmd_router.message.filter(IsAdminChatFilter(ADMIN_CHAT_ID))


@admin_cmd_router.message(Command("admin"))
async def cmd_admin(message: Message):

    await message.answer(text=AdminReplies.ADMIN_CMDS, parse_mode="HTML")


@admin_cmd_router.message(Command("id"))
async def cmd_id(message: Message):
    await message.answer(f"🆔 ID этого чата: <code>{message.chat.id}</code>")


@admin_cmd_router.message(Command("orders"))
async def cmd_orders(message: Message, db: Database):
    service = OrderService(db.async_session_factory)
    try:
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
        await message.answer(
            f"{ClientReplies.ERROR_ALERT}\n\n Описание ошибки: {e}", show_alert=True
        )


@admin_cmd_router.message(Command("order"))
async def cmd_order_detail(message: Message, db: Database):
    order_id = parse_order_id(message.text)
    if not order_id:
        await message.answer(
            text=AdminReplies.WRONG_ORDER_ID,
            parse_mode="HTML",
        )
        return
    service = OrderService(db.async_session_factory)
    try:
        order = await service.get_order_by_id(order_id=order_id)
        if not order:
            await message.answer(
                text=AdminReplies.ORDER_NOT_FOUND,
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
        await message.answer(
            f"{ClientReplies.ERROR_ALERT}\n\n Описание ошибки: {e}", show_alert=True
        )
