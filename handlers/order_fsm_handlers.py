from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from utils.texts import OrderSteps
from keyboards.common import get_phone_keyboard, get_send_order_keyboard
from states import OrderCar


router = Router(name="order_fsm_handlers")

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
        await message.answer(f"⚠️ {data['name']}, пожалуйста, введите корректный номер телефона:")
        return

    await state.update_data(phone=phone)
    await state.set_state(OrderCar.email)
    await message.answer(OrderSteps.EMAIL)


@router.message(OrderCar.email, F.text)
async def process_email(message: Message, state: FSMContext):
    data = await state.get_data()
    email = message.text.strip()
    # Простая валидация email
    if '@' not in email or '.' not in email:
        await message.answer(f"⚠️ {data['name']}, пожалуйста, введите корректный email:")
        return

    await state.update_data(email=email)
    await state.set_state(OrderCar.city)
    await message.answer(OrderSteps.CITY)


@router.message(OrderCar.city, F.text)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(OrderCar.car_model)
    await message.answer(OrderSteps.MODEL)


@router.message(OrderCar.car_model, F.text)
async def process_car_model(message: Message, state: FSMContext):
    await state.update_data(car_model=message.text)
    await state.set_state(OrderCar.budget)
    await message.answer(OrderSteps.BUDGET)


@router.message(OrderCar.budget, F.text)
async def process_budget(message: Message, state: FSMContext, bot):
    data = await state.get_data()

    budget = message.text.strip()
    # Проверяем, содержит ли бюджет цифры
    if not any(char.isdigit() for char in budget):
        await message.answer(f"⚠️ {data['name']}, пожалуйста, введите бюджет цифрами:")
        return

    await state.update_data(budget=budget)

    data = await state.get_data()

    confirmation_text = (
        "🚗 *Давайте проверим вашу заявку перед отправкой!*\n\n"
        f"👤 *Имя:* {data['name']}\n"
        f"📞 *Телефон:* {data['phone']}\n"
        f"📧 *Email:* {data['email']}\n"
        f"🏙 *Город:* {data['city']}\n"
        f"🚗 *Марка/Модель:* {data['car_model']}\n"
        f"💰 *Бюджет:* {data['budget']} USD\n\n"
        "_Выберите действие:_"
    )

    await message.answer(
        confirmation_text,
        parse_mode="Markdown",
        reply_markup=get_send_order_keyboard()
    )
