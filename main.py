import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F

# Railway Variables-dan tokenni olamiz
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 906441402 # Sizning ID-ingiz

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- MA'LUMOTLAR BAZASI BILAN ISHLASH ---
def init_db():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            code TEXT PRIMARY KEY,
            file_id TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_movie_to_db(code, file_id):
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO movies (code, file_id) VALUES (?, ?)", (code, file_id))
    conn.commit()
    conn.close()

def get_movie_from_db(code):
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT file_id FROM movies WHERE code = ?", (code,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None
# ---------------------------------------

@dp.message(F.text == "/start")
async def start_command(message: types.Message):
    await message.answer("🎬 Salom! Kino kodini yuboring, men sizga kinoni topib beraman!")

# ADMIN UCHUN: Kino qo'shish
@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def add_movie_handler(message: types.Message):
    if message.caption:
        code = message.caption.strip()
        add_movie_to_db(code, message.video.file_id)
        await message.reply(f"✅ Baza yangilandi! Kino kodi: **{code}**\nEndi bot o'chsa ham bu kino o'chib ketmaydi.")
    else:
        await message.reply("⚠️ Videoni yuborishda izoh (caption) qismiga kod yozishni unutdingiz!")

# FOYDALANUVCHILAR UCHUN: Kino topish
@dp.message(F.text)
async def get_movie_handler(message: types.Message):
    code = message.text.strip()
    file_id = get_movie_from_db(code)
    
    if file_id:
        await bot.send_video(chat_id=message.chat.id, video=file_id, caption=f"🎬 Kino kodi: {code}")
    elif not code.startswith('/'):
        await message.answer("❌ Bu kod bilan kino topilmadi.")

async def main():
    init_db() # Bot yoqilganda baza yaratiladi
    print("Bot SQLite bilan ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
