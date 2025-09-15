import time
from collections import defaultdict

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_CHAT_ID
from handlers.filters import IsAdminChatFilter
from keyboards.common import get_on_start_keyboard
from states import OrderCar
from utils.utils import  handle_retry
from utils.texts import OrderSteps, ClientReplies, ButtonText

client_cmd_router = Router(name="client_cmd_handlers")
client_cmd_router.message.filter(~IsAdminChatFilter(ADMIN_CHAT_ID))

last_start_calls = defaultdict(float)


# Команда /start
@client_cmd_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # Проверяем, был ли вызов менее 2 секунд назад
    user_id = message.from_user.id
    current_time = time.time()

    if current_time - last_start_calls[user_id] < 2:
        return

    last_start_calls[user_id] = current_time

    current_state = await state.get_state()

    if current_state:
        state_to_message = {
            "OrderCar:name": OrderSteps.NAME,
            "OrderCar:phone": OrderSteps.PHONE,
            "OrderCar:email": OrderSteps.EMAIL,
            "OrderCar:car_model": OrderSteps.MODEL,
            "OrderCar:budget": OrderSteps.BUDGET,
        }

        current_step = state_to_message.get(current_state)

        data = await state.get_data()
        await message.answer(
            f"{data["name"]} {ClientReplies.WELCOME_BACK} {current_step}"
        )
    else:
        await message.answer(
            text=ClientReplies.START,
            reply_markup=get_on_start_keyboard(),
        )

# Команда /help - справка
@client_cmd_router.message(F.text == ButtonText.HELP)
@client_cmd_router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=ClientReplies.HELP)


# Команда /cancel - отмена заявки
@client_cmd_router.message(F.text == ButtonText.CANCEL)
@client_cmd_router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(ClientReplies.CANCEL_NO_ORDERS)
        return
    await state.clear()
    await message.answer(ClientReplies.CANCEL_SUCCESS)

# Команда /retry - заполнить заявку заново при ошибке
@client_cmd_router.message(F.text == ButtonText.RETRY)
@client_cmd_router.message(Command("retry"))
async def cmd_retry(message: Message, state: FSMContext):
    await handle_retry(message.chat.id, state, message.bot)



# Команда /order - начало оформления заявки
@client_cmd_router.message(F.text == ButtonText.ORDER)
@client_cmd_router.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext):
    await state.set_state(OrderCar.name)
    await message.answer(
        f"📝 Итак, начнем! 📝\n\n"
        f"Давайте оформим заявку на автомобиль!\n\n"
        f"{OrderSteps.NAME}"
    )