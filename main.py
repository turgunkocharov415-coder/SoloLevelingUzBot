import os
import asyncio
import sqlite3
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8203513150  # Sizning ID-ingiz
CHANNEL_ID = "@My_AnimeChannel" # O'zingizniki bilan almashtiring

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- BAZA FUNKSIYALARI ---
def init_db():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS movies (code TEXT PRIMARY KEY, file_id TEXT)")
    conn.commit()
    conn.close()

def get_movie(code):
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT file_id FROM movies WHERE code = ?", (code,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

# --- MENYULAR ---
def get_main_menu():
    kb = [
        [KeyboardButton(text="1-FASL"), KeyboardButton(text="2-FASL")],
        [KeyboardButton(text="3-FASL")],
        [KeyboardButton(text="📢 Kanalimiz")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_parts_menu(season_num, total_parts):
    buttons = []
    row = []
    for i in range(1, total_parts + 1):
        row.append(KeyboardButton(text=f"{season_num}-fasl {i}-qism"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([KeyboardButton(text="⬅️ Orqaga")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# --- XABARLAR VA TUGMALAR ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("🎬 Salom! Kerakli faslni tanlang 👇", reply_markup=get_main_menu())

@dp.message(F.text.in_(["1-FASL", "2-FASL", "3-FASL"]))
async def show_parts(message: types.Message):
    # Bu yerda tugma bosilganda qismlar ro'yxati chiqishi ta'minlanadi
    season = "".join(filter(str.isdigit, message.text))
    await message.answer(f"✨ {season}-fasl qismlarini tanlang:", reply_markup=get_parts_menu(season, 10))

@dp.message(F.text == "⬅️ Orqaga")
async def back_to_main(message: types.Message):
    await message.answer("Asosiy menyu:", reply_markup=get_main_menu())

@dp.message(F.text.contains("-fasl") & F.text.contains("-qism"))
async def send_video_part(message: types.Message):
    numbers = re.findall(r'\d+', message.text)
    if len(numbers) >= 2:
        search_code = f"{numbers[0]}_{numbers[1]}"
        file_id = get_movie(search_code)
        if file_id:
            await message.answer_video(video=file_id, caption=f"🎞 {numbers[0]}-fasl {numbers[1]}-qism\n\n{CHANNEL_ID}")
        else:
            await message.answer(f"⚠️ Bu qism yuklanmagan. (Kod: {search_code})")

@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def add_video(message: types.Message):
    if message.caption:
        code = message.caption.strip()
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (code, message.video.file_id))
        conn.commit()
        conn.close()
        await message.reply(f"✅ Saqlandi! Kod: {code}")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
