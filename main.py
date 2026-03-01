import os
import asyncio
import psycopg2
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 8203513150  
CHANNEL_ID = "@My_AnimeChannel" 

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- BAZA BILAN ISHLASH ---
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            code TEXT PRIMARY KEY, 
            file_id TEXT, 
            title TEXT
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def get_uploaded_parts(season_num):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code FROM movies WHERE code LIKE %s", (f"{season_num}_%",))
    codes = cursor.fetchall()
    cursor.close()
    conn.close()
    parts = []
    for c in codes:
        try:
            parts.append(int(c[0].split('_')[1]))
        except: continue
    return sorted(list(set(parts)))

def get_movie_data(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, title FROM movies WHERE code = %s", (code,))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res if res else (None, None)

# --- MENYULAR ---
def get_main_menu():
    kb = [
        [KeyboardButton(text="1-FASL"), KeyboardButton(text="2-FASL")],
        [KeyboardButton(text="3-FASL")],
        [KeyboardButton(text="📢 Kanalimiz")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# Eng muhim o'zgarish: Inline tugmalar orqali aniq kod yuborish
def get_inline_menu(season_num):
    parts = get_uploaded_parts(season_num)
    if not parts: return None
    
    keyboard = []
    row = []
    for p in parts:
        # Tugma matni chiroyli, lekin orqasidagi 'callback_data' aniq (masalan: "get_1_1")
        row.append(InlineKeyboardButton(text=f"🎬 {p}-qism", callback_data=f"get_{season_num}_{p}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- BOT LOGIKASI ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🎬 Salom! Kerakli faslni tanlang 👇", reply_markup=get_main_menu())

@dp.message(F.text.in_(["1-FASL", "2-FASL", "3-FASL"]))
async def show_season(message: types.Message):
    season = "".join(filter(str.isdigit, message.text))
    menu = get_inline_menu(season)
    if menu:
        await message.answer(f"✨ {season}-fasl qismlari:", reply_markup=menu)
    else:
        await message.answer(f"⚠️ {season}-fasl uchun hali video yuklanmagan.")

# Inline tugma bosilganda videoni yuborish
@dp.callback_query(F.data.startswith("get_"))
async def send_movie(callback: types.CallbackQuery):
    code = callback.data.replace("get_", "") # "get_1_1" -> "1_1"
    f_id, title = get_movie_data(code)
    
    if f_id:
        nums = code.split("_")
        cap = f"🎬 **Anime:** {title}\n🎞 **{nums[0]}-fasl {nums[1]}-qism**\n\n{CHANNEL_ID}"
        await callback.message.answer_video(video=f_id, caption=cap, parse_mode="Markdown")
        await callback.answer()
    else:
        await callback.answer("⚠️ Video topilmadi!", show_alert=True)

@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def save_video(message: types.Message):
    if message.caption:
        # Yuklash: "1_1 Solo Leveling"
        parts = message.caption.split(maxsplit=1)
        code = parts[0]
        title = parts[1] if len(parts) > 1 else "Solo Leveling"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO movies (code, file_id, title) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (code) DO UPDATE SET file_id = EXCLUDED.file_id, title = EXCLUDED.title
        """, (code, message.video.file_id, title))
        conn.commit()
        cursor.close()
        conn.close()
        await message.reply(f"✅ Saqlandi!\nKod: {code}\nNomi: {title}")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
