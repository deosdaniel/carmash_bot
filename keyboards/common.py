from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


class ButtonText:
    ORDER = "Оставить заявку"
    CANCEL = "Отмена"
    HELP = "Справка"
    RETRY = "Заполнить заново"


def get_on_start_keyboard() -> ReplyKeyboardMarkup:
    button_order = KeyboardButton(text="Оставить заявку")
    button_help = KeyboardButton(text="Справка")
    button_retry = KeyboardButton(text="Заполнить заново")
    button_cancel = KeyboardButton(text="Отмена")
    buttons_first_row = [button_order, button_help]
    buttons_second_row = [button_retry, button_cancel]
    markup = ReplyKeyboardMarkup(keyboard=[buttons_first_row, buttons_second_row], resize_keyboard=True, one_time_keyboard=True)
    return markup

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    button_phone = KeyboardButton(text="📞Оставить свой номер из Telegram", request_contact=True)
    buttons = [button_phone]
    markup = ReplyKeyboardMarkup(keyboard=[buttons], one_time_keyboard=True, resize_keyboard=True)
    return markup

def get_help_keyboard() -> InlineKeyboardMarkup:
    button_order = InlineKeyboardButton(text="Оставить заявку",
                                        callback_data="Оставить заявку")
    button_retry = InlineKeyboardButton(text="Заполнить заново",
                                        callback_data="Заполнить заново")
    button_cancel = InlineKeyboardButton(text="Отмена",
                                       callback_data="Отмена")
    button_help = InlineKeyboardButton(text="Справка",
                                       callback_data="Справка")
    row = [button_order, button_retry, button_cancel, button_help]
    rows = [row]
    markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return markup
