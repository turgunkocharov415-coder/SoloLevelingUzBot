import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 906441402 # BU YERGA O'Z ID-INGIZNI QAYTA YOZING!

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

# --- TUGMALAR (KEYBOARD) ---
def get_seasons_keyboard():
    buttons = [
        [InlineKeyboardButton(text="1-Fasl", callback_data="season_1"),
         InlineKeyboardButton(text="2-Fasl", callback_data="season_2")],
        [InlineKeyboardButton(text="3-Fasl", callback_data="season_3")],
        [InlineKeyboardButton(text="📢 Kanalimiz", url="https://t.me/SizningKanalingiz")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# --- BUYRUQLAR ---
@dp.message(F.text == "/start")
async def start_command(message: types.Message):
    await message.answer("👋 Salom! Kerakli faslni tanlang:", reply_markup=get_seasons_keyboard())

# Tugma bosilganda ishlovchi qism
@dp.callback_query(F.data.startswith("season_"))
async def season_callback(callback: types.CallbackQuery):
    season_num = callback.data.split("_")[1]
    # Har bir fasl uchun bazaga avvaldan 'f1', 'f2', 'f3' kodli kinolarni yuklab qo'yishingiz kerak
    file_id = get_movie(f"f{season_num}") 
    
    if file_id:
        await callback.message.answer_video(video=file_id, caption=f"🎬 {season_num}-fasl marhamat!")
    else:
        await callback.answer("⚠️ Bu fasl hali yuklanmagan!", show_alert=True)

# ADMIN: Kino qo'shish
@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def add_movie(message: types.Message):
    if message.caption:
        code = message.caption.strip()
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO movies VALUES (?, ?)", (code, message.video.file_id))
        conn.commit()
        conn.close()
        await message.reply(f"✅ Saqlandi! Kod: {code}")

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
        await message.answer("❌ Topilmadi.")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
