
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery


class IsAdminChatFilter(Filter):
    def __init__(self, admin_chat_id: int):
        # Убедитесь, что admin_chat_id - число, а не строка
        self.admin_chat_id = int(admin_chat_id) if isinstance(admin_chat_id, str) else admin_chat_id

    async def __call__(self, update: Message | CallbackQuery) -> bool:
        chat_id = None
        if isinstance(update, Message):
            chat_id = update.chat.id
        elif isinstance(update, CallbackQuery):
            chat_id = update.message.chat.id

        return chat_id == self.admin_chat_id