from select import select

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.markdown import hbold, hlink
from sqlalchemy import update, select
from config import ADMIN_CHAT_ID
import logging

from database.core import Database
from database.models import Order
from handlers.filters import IsAdminChatFilter
from keyboards.common import get_admin_order_keyboard
from utils.texts import ClientReplies, OrderStatus


logger = logging.getLogger(__name__)

admin_router = Router(name="admin_handlers")

admin_router.message.filter(IsAdminChatFilter(ADMIN_CHAT_ID))
admin_router.callback_query.filter(IsAdminChatFilter(ADMIN_CHAT_ID))


@admin_router.message(Command("admin"))
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


@admin_router.message(Command("id"))
async def cmd_id(message: Message):
    """Показывает ID текущего чата"""
    await message.answer(f"🆔 ID этого чата: <code>{message.chat.id}</code>")


@admin_router.callback_query(F.data.startswith("call_"))
async def handle_call_action(callback: CallbackQuery, db: Database):
    try:
        order_id = int(callback.data.split("_")[1])
        async with db.get_session() as session:
            # Получаем заявку из БД
            order = await session.get(Order, order_id)
            await callback.answer(f"Звоним клиенту: {order.phone}")
        logger.info(f"☎️ Звонок клиенту")
    except Exception as e:
        logger.error(f"Error in call client action: {e}")
        await callback.answer(ClientReplies.ERROR_ALERT, show_alert=True)
    finally:

        await callback.answer()


@admin_router.callback_query(F.data.startswith("complete_"))
async def handle_complete_action(callback: CallbackQuery, db: Database):
    try:
        order_id = int(callback.data.split("_")[1])
        async with db.get_session() as session:
            await session.execute(
                update(Order)
                .where(Order.id == order_id)
                .values(status=OrderStatus.COMPLETED)
            )
            await session.commit()

        await callback.answer("Заявка завершена!")
        await callback.message.edit_text(
            f"✅ {callback.message.text}\n\n🏁 Заявка принята администратором",
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error in complete order action: {e}")
        await callback.answer(ClientReplies.ERROR_ALERT, show_alert=True)
    finally:
        await callback.answer()


@admin_router.callback_query(F.data.startswith("drop_"))
async def handle_drop_order(callback: CallbackQuery, db: Database):
    try:
        order_id = int(callback.data.split("_")[1])
        async with db.get_session() as session:
            await session.execute(
                update(Order)
                .where(Order.id == order_id)
                .values(status=OrderStatus.REJECTED)
            )
            await session.commit()
        await callback.answer("Заявка закрыта!")
        await callback.message.edit_text(
            f"❌ {callback.message.text}\n\n🏁 Заявка закрыта администратором",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in drop order action: {e}")
        await callback.answer(ClientReplies.ERROR_ALERT, show_alert=True)
    finally:
        await callback.answer()

@admin_router.message(Command("orders"))
async def cmd_orders(message: Message, db: Database):
    try:
        async with db.get_session() as session:
            orders = await session.execute(select(Order).order_by(Order.created_at.desc()))
            orders_list = orders.scalars().all()
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

@admin_router.message(Command("order"))
async def cmd_order_detail(message: Message, db: Database):
    try:
        order_id = int(message.text.split()[1])
        async with db.get_session() as session:
            order = await session.get(Order, order_id)
            if not order:
                await message.answer("Не нашли заявку по этому номеру 😔\n\n"
                                     "Использование: /order <ID_заявки>")
                return

            detail_text = (
                f"📋 {hbold('Детали заявки')} #{order.id}\n\n"
                f"👤 {hbold('Клиент:')} {order.name}\n"
                f"📞 {hbold('Телефон:')} {hlink(order.phone, f'tel:{order.phone}')}\n"
                f"📧 {hbold('Email:')} {order.email}\n"
                f"🚗 {hbold('Автомобиль:')} {order.car_model}\n"
                f"💰 {hbold('Бюджет:')} {order.budget} USD\n"
                f"⏰ {hbold('Создана:')} {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
                f"📊 {hbold('Статус:')} {order.status}"
            )
            await message.answer(detail_text, parse_mode="HTML", reply_markup=get_admin_order_keyboard(order_id=order.id))
    except Exception as e:
        logger.error(f"Error in order detail action: {e}")

        await message.answer(ClientReplies.ERROR_ALERT, show_alert=True)


#
#@router.message(Command("restart"))
#async def cmd_restart(message: Message):
#    """Перезапуск бота"""
#    if not is_admin(message.chat.id):
#        return
#
#    await message.answer("🔄 Перезапускаю бота...")
#    logger.info("Бот перезапущен по команде админа")
#    # Здесь можно добавить логику перезапуска
#
#
#@router.message(Command("stop"))
#async def cmd_stop(message: Message):
#    """Остановка бота"""
#    if not is_admin(message.chat.id):
#        return
#
#    await message.answer("🛑 Останавливаю бота...")
#    logger.info("Бот остановлен по команде админа")
#    # sys.exit(0) - лучше не использовать, может вызвать проблемы