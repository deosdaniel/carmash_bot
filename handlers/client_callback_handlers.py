import logging

from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from config import ADMIN_CHAT_ID
from database.core import Database
from database.schemas import OrderCreateSchema
from database.service import OrderService
from utils.filters import IsAdminChatFilter
from states import OrderCar
from utils.texts import ClientReplies
from utils.utils import send_admin_notification, handle_retry

client_callback_router = Router(name="client_callback_handlers")
client_callback_router.callback_query.filter(~IsAdminChatFilter(ADMIN_CHAT_ID))

logger = logging.getLogger(__name__)


@client_callback_router.callback_query(
    F.data == "confirm", StateFilter(OrderCar.budget)
)
async def process_confirm(
    callback: CallbackQuery, state: FSMContext, bot: Bot, db: Database
):
    service = OrderService(db.async_session_factory)
    data = await state.get_data()
    user = callback.from_user
    try:
        order = await service.create_order(
            OrderCreateSchema(user_id=user.id, username=user.username, **data)
        )
    except Exception as e:
        logger.error(f"Ошибка в process_confirm: {e}")
        await callback.answer(ClientReplies.ERROR_ALERT, show_alert=True)
        return

    logger.info(f"✅ Заявка #{order.id} сохранена в БД")

    await send_admin_notification(bot, order)
    await callback.message.edit_text(ClientReplies.CONFIRM_INLINE, reply_markup=None)
    await state.clear()
    await callback.answer()


@client_callback_router.callback_query(F.data == "retry", StateFilter(OrderCar.budget))
async def process_retry(callback: CallbackQuery, state: FSMContext):
    try:
        await handle_retry(
            callback.message.chat.id, state, callback.bot, callback.message.message_id
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в process_retry: {e}")
        await callback.answer(ClientReplies.ERROR_ALERT, show_alert=True)


@client_callback_router.callback_query(F.data == "cancel", StateFilter(OrderCar.budget))
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await callback.message.edit_text(ClientReplies.CANCEL_INLINE, reply_markup=None)
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в process_cancel: {e}")
        await callback.answer(ClientReplies.ERROR_ALERT, show_alert=True)
