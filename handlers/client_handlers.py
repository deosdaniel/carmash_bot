import time
from collections import defaultdict

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.common import ButtonText, get_on_start_keyboard, get_phone_keyboard, send_order
from states import OrderCar
from utils import  handle_retry

router = Router()

last_start_calls = defaultdict(float)

class OrderSteps:
    NAME = "Пожалуйста, введите ваше имя:"
    PHONE = "📞 Введите ваш номер телефона или нажмите кнопку ниже:"
    EMAIL = "✅ Супер, двигаемся далее!\n\n 📧 Введите ваш email:"
    CITY = "✅ Отлично, К следующему шагу!\n\n 🏙 Введите город, откуда вы обращаетесь:"
    MODEL = "✅ Здорово, мы почти закончили\n\n🚗 Введите желаемую марку и/или модель автомобиля:"
    BUDGET = "✅ Финальный штрих\n\n💰 Введите ваш бюджет (в RUB):"

# Команда /start
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # Проверяем, был ли вызов менее 2 секунд назад
    user_id = message.from_user.id
    current_time = time.time()

    if current_time - last_start_calls[user_id] < 2:
        return

    last_start_calls[user_id] = current_time


    current_state = await state.get_state()

    if current_state:
        # Короткое уведомление + подсказка что делать дальше
        state_to_message = {
            "OrderCar:name": OrderSteps.NAME,
            "OrderCar:phone": OrderSteps.PHONE,
            "OrderCar:email": OrderSteps.EMAIL,
            "OrderCar:car_model": OrderSteps.MODEL,
            "OrderCar:budget": OrderSteps.BUDGET,
        }

        current_step = state_to_message.get(current_state, "продолжите заполнение")

        data = await state.get_data()
        await message.answer(
            f"🚗 {data["name"]}, добро пожаловать обратно, Мы скучали!\n\n"
            f"⚠ У вас есть незавершенная заявка.\n\n"
            f"❔ Чтобы начать заново - /retry\n"
            f"❔ Чтобы отменить - /cancel\n"
            f"❔ Помощь по работе бота - /help\n\n"
            f"✅ Если хотите продолжить заполнять текущую заявку:\n\n"
            f"{current_step}"
        )
    else:
        await message.answer(
            text="🚗 Добро пожаловать в бот Carmash!\n\n"
            "Оформить заявку - нажмите /order\n"
            "Ошиблись? Заполните заявку заново - нажмите /retry\n"
            "Для отмены в любой момент - нажмите /cancel\n"
            "Помощь по работе бота - /help",
            reply_markup=get_on_start_keyboard(),
        )

# Команда /help - справка
@router.message(F.text == ButtonText.HELP)
@router.message(Command("help"))
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text="🚗 Команды бота 🚗\n\n"
        "/order - Оформить заявку\n"
        "/retry - Заполнить заново (при ошибке)\n"
        "/cancel - Для отмены в любой момент \n"
        "/help - Справка по работе бота",)


# Команда /cancel - отмена заявки
@router.message(F.text == ButtonText.CANCEL)
@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных заявок.")
        return
    await state.clear()
    await message.answer("Заявка отменена. Для новой заявки нажмите /order")

# Команда /retry - заполнить заявку заново при ошибке
@router.message(F.text == ButtonText.RETRY)
@router.message(Command("retry"))
async def cmd_retry(message: Message, state: FSMContext):
    await handle_retry(message.chat.id, state, message.bot)



# Команда /order - начало оформления заявки
@router.message(F.text == ButtonText.ORDER)
@router.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext):
    await state.set_state(OrderCar.name)
    await message.answer(
        f"📝 Итак, начнем! 📝\n\n"
        f"Давайте оформим заявку на автомобиль!\n\n"
        f"{OrderSteps.NAME}"
    )



# Обработка имени
@router.message(OrderCar.name, F.text)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip().lower().capitalize()
    await state.update_data(name=name)
    await state.set_state(OrderCar.phone)

    await state.update_data(name=name)

    await state.set_state(OrderCar.phone)
    msg = f"✅ {name}, очень приятно познакомиться!\n\n"
    msg += OrderSteps.PHONE
    await message.answer(msg,
        reply_markup=get_phone_keyboard(),
    )


# Обработка телефона
@router.message(OrderCar.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):

    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(OrderCar.email)
    await message.answer(OrderSteps.EMAIL,
        reply_markup=None
    )


@router.message(OrderCar.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):

    data = await state.get_data()

    # Простая валидация номера телефона
    phone = message.text.strip()
    if not any(char.isdigit() for char in phone) or len(phone) < 5:
        await message.answer(f"⚠ {data['name']}, пожалуйста, введите корректный номер телефона:")
        return

    await state.update_data(phone=phone)
    await state.set_state(OrderCar.email)
    await message.answer(OrderSteps.EMAIL)


# Обработка email
@router.message(OrderCar.email, F.text)
async def process_email(message: Message, state: FSMContext):
    data = await state.get_data()
    email = message.text.strip()
    # Простая валидация email
    if '@' not in email or '.' not in email:
        await message.answer(f"⚠ {data['name']}, пожалуйста, введите корректный email:")
        return

    await state.update_data(email=email)
    await state.set_state(OrderCar.car_model)
    await message.answer(OrderSteps.MODEL)


# Обработка марки/модели
@router.message(OrderCar.car_model, F.text)
async def process_car_model(message: Message, state: FSMContext):
    await state.update_data(car_model=message.text)
    await state.set_state(OrderCar.budget)
    await message.answer(OrderSteps.BUDGET)


# Обработка бюджета
@router.message(OrderCar.budget, F.text)
async def process_budget(message: Message, state: FSMContext, bot):
    data = await state.get_data()

    budget = message.text.strip()
    # Проверяем, содержит ли бюджет цифры
    if not any(char.isdigit() for char in budget):
        await message.answer(f"⚠ {data['name']}, пожалуйста, введите бюджет цифрами:")
        return

    await state.update_data(budget=budget)

    data = await state.get_data()

    confirmation_text = (
        "🚗 *Давайте проверим вашу заявку перед отправкой!*\n\n"
        f"👤 *Имя:* {data['name']}\n"
        f"📞 *Телефон:* {data['phone']}\n"
        f"📧 *Email:* {data['email']}\n"
        f"🚗 *Марка/Модель:* {data['car_model']}\n"
        f"💰 *Бюджет:* {data['budget']} USD\n\n"
        "_Выберите действие:_"
    )

    await message.answer(
        confirmation_text,
        parse_mode="Markdown",
        reply_markup=send_order()
    )