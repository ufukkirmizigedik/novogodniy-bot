from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove


b1 = KeyboardButton('/Регистрация')
a1 = KeyboardButton('/Выбирай')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.add(b1),kb_client.add(a1)


