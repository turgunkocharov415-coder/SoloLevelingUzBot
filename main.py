import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 906441402  # O'z ID-ingizni tekshirib yozing!

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

# --- MENYULAR (KEYBOARDS) ---
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
        if len(row) == 3: # Har qatorda 3 tadan tugma
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([KeyboardButton(text="⬅️ Orqaga")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# --- BUYRUQLAR ---
@dp.message(F.text == "/start")
async def start_command(message: types.Message):
    await message.answer("🎬 Salom! Kerakli faslni tanlang 👇", reply_markup=get_main_menu())

@dp.message(F.text == "⬅️ Orqaga")
async def back_to_main(message: types.Message):
    await message.answer("Asosiy menyu:", reply_markup=get_main_menu())

# FASL TANLANGANDA QISMLARNI CHIQARISH
@dp.message(F.text.in_(["1-FASL", "2-FASL", "3-FASL"]))
async def show_parts(message: types.Message):
    season = message.text.split("-")[0] # "1", "2" yoki "3" ni oladi
    
    # Har bir faslda nechta qism borligini shu yerda belgilaysiz:
    parts_count = {"1": 10, "2": 13, "3": 15} 
    count = parts_count.get(season, 10)
    
    await message.answer(f"✨ {season}-fasl qismlarini tanlang:", 
                         reply_markup=get_parts_menu(season, count))

# QISM TANLANGANDA VIDEONI YUBORISH
@dp.message(F.text.contains("-fasl ") & F.text.contains("-qism"))
async def send_video_part(message: types.Message):
    # Matndan kodni yasaymiz: "1-fasl 5-qism" -> "1_5"
    text = message.text.replace("-fasl", "").replace("-qism", "").split()
    code = f"{text[0]}_{text[1]}"
    
    file_id = get_movie(code)
    if file_id:
        await message.answer_video(video=file_id, caption=f"🎬 {message.text}")
    else:
        await message.answer("⚠️ Bu qism hali yuklanmagan.")

# ADMIN: Video yuklash (Masalan: 1_1, 1_2 ko'rinishida yuklang)
@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def add_movie_handler(message: types.Message):
    if message.caption:
        code = message.caption.strip()
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (code, message.video.file_id))
        conn.commit()
        conn.close()
        await message.reply(f"✅ Baza yangilandi! Kod: {code}")
    else:
        await message.reply("⚠️ Izohga kodni (masalan: 1_1) yozing!")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
