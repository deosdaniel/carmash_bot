from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery


class IsAdminChatFilter(Filter):
    def __init__(self, admin_chat_id: int, admin_thread_id: int | None = None):
        # Убедись, что id корректные
        self.admin_chat_id = int(admin_chat_id)
        self.admin_thread_id = int(admin_thread_id) if admin_thread_id else None

    async def __call__(self, update: Message | CallbackQuery) -> bool:
        if isinstance(update, Message):
            chat_id = update.chat.id
            thread_id = update.message_thread_id
        elif isinstance(update, CallbackQuery):
            chat_id = update.message.chat.id
            thread_id = update.message.message_thread_id
        else:
            return False

        if chat_id != self.admin_chat_id:
            return False

        if self.admin_thread_id is not None:
            return thread_id == self.admin_thread_id

        return True
