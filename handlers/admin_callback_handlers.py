import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery
from sqlalchemy import update

from config import ADMIN_CHAT_ID, ADMIN_THREAD_ID
from database.core import Database
from database.models import Order
from utils.filters import IsAdminChatFilter
from utils.texts import ClientReplies, OrderStatus

logger = logging.getLogger(__name__)

admin_callback_router = Router(name="admin_callback_handlers")
admin_callback_router.callback_query.filter(
    IsAdminChatFilter(ADMIN_CHAT_ID, ADMIN_THREAD_ID)
)


@admin_callback_router.callback_query(F.data.startswith("call_"))
async def handle_call_action(callback: CallbackQuery, db: Database):
    try:
        order_id = int(callback.data.split("_")[1])
        async with db.async_session_factory() as session:
            order = await session.get(Order, order_id)
            await callback.answer(f"Звоним клиенту: {order.phone}")
        logger.info(f"☎️ Звонок клиенту")
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in call client action: {e}")
        await callback.answer(ClientReplies.ERROR_ALERT, show_alert=True)


@admin_callback_router.callback_query(F.data.startswith("complete_"))
async def handle_complete_action(callback: CallbackQuery, db: Database):
    try:
        order_id = int(callback.data.split("_")[1])
        async with db.async_session_factory() as session:
            await session.execute(
                update(Order)
                .where(Order.id == order_id)
                .values(status=OrderStatus.COMPLETED)
            )
            await session.commit()

        await callback.answer("Заявка завершена!")
        await callback.message.edit_text(
            f"✅ {callback.message.text}\n\n🏁 Заявка принята администратором",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Error in complete order action: {e}")
        await callback.answer(ClientReplies.ERROR_ALERT, show_alert=True)


@admin_callback_router.callback_query(F.data.startswith("drop_"))
async def handle_drop_order(callback: CallbackQuery, db: Database):
    try:
        order_id = int(callback.data.split("_")[1])
        async with db.async_session_factory as session:
            await session.execute(
                update(Order)
                .where(Order.id == order_id)
                .values(status=OrderStatus.REJECTED)
            )
            await session.commit()
        await callback.answer("Заявка закрыта!")
        await callback.message.edit_text(
            f"❌ {callback.message.text}\n\n🏁 Заявка закрыта администратором",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.error(f"Error in drop order action: {e}")
        await callback.answer(ClientReplies.ERROR_ALERT, show_alert=True)
