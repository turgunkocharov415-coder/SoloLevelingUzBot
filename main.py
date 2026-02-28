import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Railway Variables-dan tokenni olamiz
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 906441402  # BU YERGA O'Z ID-INGIZNI YOZING!

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

# --- REPLY KEYBOARD (RASMDAGI KABI MENYU) ---
def get_main_menu():
    kb = [
        [KeyboardButton(text="📢OVOZ KASTING")],
        [KeyboardButton(text="1-FASL"), KeyboardButton(text="2-Fasl")],
        [KeyboardButton(text="3-FASL"), KeyboardButton(text="4-Fasl")],
        [KeyboardButton(text="⬅️ Orqaga"), KeyboardButton(text="⬆️ Asosiy Menyu")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- BUYRUQLAR ---
@dp.message(F.text == "/start")
async def start_command(message: types.Message):
    await message.answer(
        "Kerakli faslni tanlang 👇", 
        reply_markup=get_main_menu()
    )

# FASLLAR BOSILGANDA ISHLOVCHI QISM
@dp.message(F.text.in_(["1-FASL", "2-Fasl", "3-FASL", "4-Fasl"]))
async def send_season(message: types.Message):
    # Tugma matnini kodga aylantiramiz (masalan: "1-FASL" -> "f1")
    code_map = {
        "1-FASL": "f1",
        "2-Fasl": "f2",
        "3-FASL": "f3",
        "4-Fasl": "f4"
    }
    code = code_map.get(message.text)
    file_id = get_movie(code)
    
    if file_id:
        await message.answer_video(video=file_id, caption=f"🎬 {message.text} marhamat!")
    else:
        await message.answer(f"⚠️ {message.text} hali bazaga yuklanmagan.")

# ADMIN: Kino qo'shish (f1, f2, f3 kodlari bilan saqlang)
@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def add_movie(message: types.Message):
    if message.caption:
        code = message.caption.strip()
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (code, message.video.file_id))
        conn.commit()
        conn.close()
        await message.reply(f"✅ Baza yangilandi! Kod: {code}")
    else:
        await message.reply("⚠️ Videoni yuborishda izohiga kod (masalan: f1) yozing!")

# ADMIN: O'chirish (/del kod)
@dp.message(F.text.startswith("/del ") & (F.from_user.id == ADMIN_ID))
async def delete_movie(message: types.Message):
    code = message.text.split(" ")[1]
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE code = ?", (code,))
    conn.commit()
    conn.close()
    await message.reply(f"🗑 {code} o'chirildi.")

# FOYDALANUVCHI: Kod orqali qidirish
@dp.message(F.text)
async def search_movie(message: types.Message):
    file_id = get_movie(message.text.strip())
    if file_id:
        await message.answer_video(video=file_id)
    elif not message.text.startswith("/"):
        pass # Noto'g'ri matn yozilsa bot indamaydi

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
