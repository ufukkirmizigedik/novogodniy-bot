
import logging
from aiogram import Bot, Dispatcher, executor, types
import sqlite3
from aiogram.dispatcher.filters.state import StatesGroup,State
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import time
import aiogram.utils.markdown as md
from aiogram.dispatcher import filters
from buttons import kb_client


storage = MemoryStorage()

API_TOKEN = 'TOKEN HERE'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot,storage=storage)


base = sqlite3.connect('bks.db')
cur = base.cursor()
if base:
    print('Data base connected')
base.execute('CREATE TABLE IF NOT EXISTS workers(user_id INTEGER, fio TEXT,adres TEXT)')
base.execute('CREATE TABLE IF NOT EXISTS Chosen(user_id INTEGER,fio TEXT,adres TEXT,chooser_id INTEGER)')
base.execute('CREATE TABLE IF NOT EXISTS Result(Sender TEXT,Receiver TEXT)')
base.commit()



class Plan(StatesGroup):
    plan = State()
    plan1 = State()


""" *****************************************    НАЧИНАЕМ   ******************************************"""
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я - Новогодний Бот 🎅 \nЯ создан для организации новогоднего обмена подарками среди сотрудников.\nВот как это работает:\n 1. Сначала, каждый сотрудник должен зарегистрироваться, отправив свои данные.\n 2. После окончания регистрации, все сотрудники могут нажать на кнопку 'Выбирай' и случайным образом выбрать имя и адрес другого сотрудника.\n 3. Затем, каждый сотрудник отправит подарок другому сотруднику, которого выбрал.\n 4. Таким образом, все сотрудники получат новогодний подарок и сделают друг другу праздник незабываемым 🎁 \nДля начала регистрации, используйте команду /Регистрация.\nЕсли у вас есть какие-либо вопросы или нужна помощь, не стесняйтесь обращаться! С Новым Годом! 🎉",reply_markup=kb_client)

"""  *****************************************   Регистрация   **************************************    """
@dp.message_handler(commands = "Регистрация")
async def send_plan(message: types.Message):
    user_id = message.from_user.id
    base = sqlite3.connect('bks.db')
    cur = base.cursor()
    registered_users = [row[0] for row in cur.execute("SELECT user_id FROM workers").fetchall()]
    chosen_users = [row[0] for row in cur.execute("SELECT chooser_id FROM Chosen").fetchall()]

    if user_id in chosen_users:
        await message.answer("Вы уже участвовали, спасибо за участие!")
    elif user_id in registered_users:
        await message.answer('Вы уже зарегистрированы!')
    else:
        await message.answer('Напишите ваше ФИО?')
        await Plan.plan.set()

@dp.message_handler(state=Plan.plan)
async def plan_sale(message: types.Message,state:FSMContext):
    async with state.proxy() as pla :
        pla['plan'] = message.text
        time.sleep(1)
        await Plan.next()
        await message.answer('Напишите ваш почтовые адрес?')

@dp.message_handler(state=Plan.plan1)
async def plan_ems(message: types.Message,state:FSMContext):
    async with state.proxy() as pla :
        pla['plan1'] = message.text
        time.sleep(1)
        sqlite3.connect('bks.db')
        fio = pla['plan']
        adres = pla['plan1']
        id_user = message.from_user.id
        cur = base.cursor()
        cur.execute("INSERT INTO workers VALUES (?,?,?)",(id_user,fio,adres,))
        base.commit()
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('ID сотрудника : ', md.bold(id_user)),
                md.text('ФИО сотрудника:', pla['plan']),
                md.text('Адрес сотрудника:',pla['plan1']),
                sep='\n'))
        await message.answer('Спасибо за регистрацию! Ваше ФИО и адрес зарегистрированы.')
        await state.finish()



@dp.message_handler(commands=["Выбирай"])
async def choose(message: types.Message):

    user = message.from_user.id
    base = sqlite3.connect('bks.db')
    cur = base.cursor()


    all_id = [row[0] for row in cur.execute("SELECT chooser_id FROM Chosen").fetchall()]


    if user in all_id:
        await message.answer("Вы уже выбрали")
    else:
        kisi = cur.execute("SELECT user_id,fio, adres FROM workers WHERE user_id != ? ORDER BY RANDOM() LIMIT 1", (user,)).fetchone()
        user_id,fio,adres = kisi

        await message.answer(f"ID-Сотрудника:{user_id}\nФИО-Сотрудника:{fio}\nАдрес Сотрудника:{adres}")
        secilen = cur.execute("INSERT INTO Chosen VALUES (?,?,?,?)",(user_id,fio,adres,user,))
        gonderen = cur.execute("SELECT fio FROM workers WHERE user_id = ?",(user,)).fetchone()
        print(gonderen)
        print(kisi[1])
        sonuc = cur.execute("INSERT INTO Result VALUES (?,?)",(gonderen[0],kisi[1],))
        #cur.execute("DELETE FROM workers WHERE user_id = ?",(user_id,))
        base.commit()
        await message.answer('Cпасибо за участие!')



@dp.message_handler(filters.IDFilter(user_id=1353075505),commands="Delete_all")
async def udalit(message:types.message):

    base = sqlite3.connect('bks.db')
    cur = base.cursor()
    cur.execute("DELETE FROM workers").fetchall()
    cur.execute("DELETE FROM Chosen").fetchall()
    cur.execute("DELETE FROM Result").fetchall()
    base.commit()
    await message.answer("Все данные удалины!")





"""" ******************** Только Админ ******************************* """

@dp.message_handler(filters.IDFilter(user_id=1353075505),commands = "Admin")
async def admin_panel(message:types.Message):
    await message.answer('Добрый день, Admin! Что хотели бы сделать? Обращаю Ваше внимание , что для создания нового плана на месяц или для его корректировки, необходимо удалить введенные ранее данные с помощью /Delete_all')



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
