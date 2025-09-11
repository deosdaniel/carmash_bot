from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from states import OrderCar
from utils import send_admin_notification

router = Router()


# Команда /start
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "🚗 Добро пожаловать в бот для заказа автомобилей из Японии/Кореи!\n\n"
        "Для оформления заявки нажмите /order\n"
        "Для отмены в любой момент нажмите /cancel"
    )


# Команда /order - начало оформления заявки
@router.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext):
    await state.set_state(OrderCar.name)
    await message.answer(
        "📝 Давайте оформим заявку на автомобиль!\n\n"
        "Пожалуйста, введите ваше имя:"
    )


# Команда /cancel - отмена заявки
@router.message(Command("cancel"))
@router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активных заявок.")
        return

    await state.clear()
    await message.answer("Заявка отменена. Для новой заявки нажмите /order")


# Обработка имени
@router.message(OrderCar.name, F.text)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderCar.phone)

    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📞 Отправить номер телефона", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "📞 Теперь введите ваш номер телефона или нажмите кнопку ниже:",
        reply_markup=phone_keyboard
    )


# Обработка телефона
@router.message(OrderCar.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(OrderCar.email)
    await message.answer(
        "📧 Введите ваш email:",
        reply_markup=None
    )


@router.message(OrderCar.phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    # Простая валидация номера телефона
    phone = message.text.strip()
    if not any(char.isdigit() for char in phone) or len(phone) < 5:
        await message.answer("Пожалуйста, введите корректный номер телефона:")
        return

    await state.update_data(phone=phone)
    await state.set_state(OrderCar.email)
    await message.answer("📧 Введите ваш email:")


# Обработка email
@router.message(OrderCar.email, F.text)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()
    # Простая валидация email
    if '@' not in email or '.' not in email:
        await message.answer("Пожалуйста, введите корректный email:")
        return

    await state.update_data(email=email)
    await state.set_state(OrderCar.car_model)
    await message.answer("🚗 Введите марку и модель автомобиля:")


# Обработка марки/модели
@router.message(OrderCar.car_model, F.text)
async def process_car_model(message: Message, state: FSMContext):
    await state.update_data(car_model=message.text)
    await state.set_state(OrderCar.budget)
    await message.answer("💰 Введите ваш бюджет (в USD):")


# Обработка бюджета
@router.message(OrderCar.budget, F.text)
async def process_budget(message: Message, state: FSMContext, bot):
    budget = message.text.strip()
    # Проверяем, содержит ли бюджет цифры
    if not any(char.isdigit() for char in budget):
        await message.answer("Пожалуйста, введите бюджет цифрами:")
        return

    await state.update_data(budget=budget)

    # Получаем все данные
    data = await state.get_data()

    # Отправляем сообщение админу
    await send_admin_notification(bot, data, message.from_user.id)

    # Очищаем состояние
    await state.clear()

    await message.answer(
        "✅ Ваша заявка успешно отправлена!\n"
        "Наш менеджер свяжется с вами в ближайшее время.\n\n"
        "Для новой заявки нажмите /order"
    )