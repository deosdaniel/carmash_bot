from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import ADMIN_CHAT_ID
import logging

router = Router()
logger = logging.getLogger(__name__)


def is_admin(chat_id: int) -> bool:
    """Проверяет, является ли чат админским"""
    return str(chat_id) == ADMIN_CHAT_ID


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.chat.id):
        return

    await message.answer(
        "👨‍💼 <b>Панель администратора</b>\n\n"
        "📊 <b>Доступные команды:</b>\n"
        "/stats - статистика заявок\n"
        "/users - количество пользователей\n"
        "/broadcast - рассылка сообщений\n"
        "/id - получить ID этого чата\n\n"
        "⚙️ <b>Управление ботом:</b>\n"
        "/restart - перезапустить бота\n"
        "/stop - остановить бота\n\n"
        "💡 <i>Все команды работают только в этом чате</i>"
    )


@router.message(Command("id"))
async def cmd_id(message: Message):
    """Показывает ID текущего чата"""
    if not is_admin(message.chat.id):
        return

    await message.answer(f"🆔 ID этого чата: <code>{message.chat.id}</code>")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Статистика бота"""
    if not is_admin(message.chat.id):
        return

    # Здесь можно добавить реальную статистику из БД
    stats_text = (
        "📊 <b>Статистика бота</b>\n\n"
        "👥 Пользователей: 150\n"
        "🚗 Заявок сегодня: 12\n"
        "✅ Одобренных: 8\n"
        "⏳ В обработке: 4\n"
        "📅 Всего заявок: 89"
    )
    await message.answer(stats_text)


@router.message(Command("users"))
async def cmd_users(message: Message):
    """Информация о пользователях"""
    if not is_admin(message.chat.id):
        return

    users_info = (
        "👥 <b>Информация о пользователях</b>\n\n"
        "🌍 Всего пользователей: 150\n"
        "🆕 Новых за сегодня: 5\n"
        "📱 Активных за неделю: 34\n"
        "🚗 Сделали заявки: 89\n"
        "📊 Конверсия: 59.3%"
    )
    await message.answer(users_info)


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    """Начало процесса рассылки"""
    if not is_admin(message.chat.id):
        return

    await message.answer(
        "📢 <b>Рассылка сообщений</b>\n\n"
        "Отправьте сообщение для рассылки всем пользователям:\n"
        "(текст, фото, документ - что угодно)"
    )
    # Здесь можно установить состояние для рассылки


@router.message(Command("restart"))
async def cmd_restart(message: Message):
    """Перезапуск бота"""
    if not is_admin(message.chat.id):
        return

    await message.answer("🔄 Перезапускаю бота...")
    logger.info("Бот перезапущен по команде админа")
    # Здесь можно добавить логику перезапуска


@router.message(Command("stop"))
async def cmd_stop(message: Message):
    """Остановка бота"""
    if not is_admin(message.chat.id):
        return

    await message.answer("🛑 Останавливаю бота...")
    logger.info("Бот остановлен по команде админа")
    # sys.exit(0) - лучше не использовать, может вызвать проблемы