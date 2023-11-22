from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,ReplyKeyboardRemove


b1 = KeyboardButton('/Регистрация')
a1 = KeyboardButton('/Выбирай')
c1 = KeyboardButton('Москва')
d1 = KeyboardButton('Новосибирск')
e1 = KeyboardButton('Самара')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)
kb_client.add(b1),kb_client.add(a1)


gorod_tus = ReplyKeyboardMarkup(resize_keyboard=True)
gorod_tus.add(c1),gorod_tus.add(d1),gorod_tus.add(e1)