from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

async def set_user_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать работу"),
        BotCommand(command="order", description="Оформить заявку"),
        BotCommand(command="cancel", description="Отмена"),
        BotCommand(command="retry", description="Заполнить заново"),
        BotCommand(command="help", description="Справка"),
    ]
    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())

async def set_admin_commands(bot: Bot, admin_chat_id: int):
    commands = [
        BotCommand(command="orders", description="Список всех заявок"),
        BotCommand(command="order", description="Детали заявки по ID"),
        BotCommand(command="stats", description="Статистика заявок"),
        BotCommand(command="users", description="Количество пользователей"),
        BotCommand(command="admin", description="Панель администратора"),
        BotCommand(command="id", description="ID этого чата"),
    ]
    await bot.set_my_commands(
        commands=commands,
        scope=BotCommandScopeChat(chat_id=admin_chat_id)
    )
