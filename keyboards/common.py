from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


class ButtonText:
    ORDER = "🚗 Оформить заявку"
    RETRY = "🔄 Заполнить заново"
    CANCEL = "❌ Отмена"
    HELP = "❓ Справка"
    SEND_PHONE = "📞Оставить свой номер из Telegram"


def get_on_start_keyboard() -> ReplyKeyboardMarkup:
    button_order = KeyboardButton(text=ButtonText.ORDER)
    button_help = KeyboardButton(text=ButtonText.HELP)
    button_retry = KeyboardButton(text=ButtonText.RETRY)
    button_cancel = KeyboardButton(text=ButtonText.CANCEL)
    buttons_first_row = [button_order, button_help]
    buttons_second_row = [button_retry, button_cancel]
    markup = ReplyKeyboardMarkup(keyboard=[buttons_first_row, buttons_second_row], one_time_keyboard=True)
    return markup

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    button_phone = KeyboardButton(text=ButtonText.SEND_PHONE, request_contact=True)
    buttons = [button_phone]
    markup = ReplyKeyboardMarkup(keyboard=[buttons], one_time_keyboard=True, resize_keyboard=True)
    return markup

def send_order() -> InlineKeyboardMarkup:
    button_send = InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm")
    button_retry = InlineKeyboardButton(text="🔄 Исправить", callback_data="retry")
    button_cancel = InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")
    buttons_row_first = [button_send]
    buttons_row_second = [button_retry, button_cancel]
    return InlineKeyboardMarkup(inline_keyboard=[buttons_row_first, buttons_row_second])