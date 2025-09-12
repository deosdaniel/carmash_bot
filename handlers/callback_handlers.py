from aiogram import Router, F, Bot
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from states import OrderCar
from utils import send_admin_notification, handle_retry

callback_router = Router()


# Обработчик подтверждения заявки
@callback_router.callback_query(F.data == "confirm", StateFilter(OrderCar.budget))
async def process_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot):
    # Получаем данные из состояния
    data = await state.get_data()
    user_id = callback.from_user.id

    # Отправляем уведомление админу
    await send_admin_notification(bot, data, user_id)

    # Очищаем состояние
    await state.clear()

    # Отправляем подтверждение пользователю
    await callback.message.edit_text(
        "✅ Ваша заявка успешно отправлена!\n\n"
        "Наш менеджер свяжется с вами в ближайшее время для уточнения деталей.\n\n"
        "Для новой заявки нажмите /order",
        reply_markup=None
    )

    await callback.answer()


# Обработчик исправления заявки
@callback_router.callback_query(F.data == "retry", StateFilter(OrderCar.budget))
async def process_retry(callback: CallbackQuery, state: FSMContext):
    await handle_retry(callback.message.chat.id, state, callback.bot, callback.message.message_id)

    await callback.answer()

@callback_router.callback_query(F.data == "cancel", StateFilter(OrderCar.budget))
async def process_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Заявка отменена.\n\n"
        "Если передумаете - нажмите /order для новой заявки"
    )
    await callback.answer()