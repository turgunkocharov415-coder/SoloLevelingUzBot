import os
import asyncio
import psycopg2
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
    parts = [int(c[0].split('_')[1]) for c in codes if '_' in c[0]]
    return sorted(parts)

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

def get_dynamic_menu(season_num):
    parts = get_uploaded_parts(season_num)
    if not parts:
        return None
    
    buttons = []
    row = []
    for p in parts:
        row.append(KeyboardButton(text=f"{season_num}-fasl {p}-qism"))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([KeyboardButton(text="⬅️ Orqaga")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# --- BOT FUNKSIYALARI ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("🎬 Salom! Kerakli faslni tanlang 👇", reply_markup=get_main_menu())

@dp.message(F.text.in_(["1-FASL", "2-FASL", "3-FASL"]))
async def show_season(message: types.Message):
    season = "".join(filter(str.isdigit, message.text))
    menu = get_dynamic_menu(season)
    if menu:
        await message.answer(f"✨ {season}-fasldagi yuklangan qismlar:", reply_markup=menu)
    else:
        await message.answer(f"⚠️ {season}-fasl uchun hali hech narsa yuklanmagan.")

@dp.message(F.text == "⬅️ Orqaga")
async def go_back(message: types.Message):
    await message.answer("Asosiy menyu:", reply_markup=get_main_menu())

@dp.message(F.text.contains("-fasl") & F.text.contains("-qism"))
async def send_video(message: types.Message):
    nums = re.findall(r'\d+', message.text)
    if len(nums) >= 2:
        code = f"{nums[0]}_{nums[1]}"
        f_id, title = get_movie_data(code)
        if f_id:
            cap = f"🎬 **BAKI HANMA:** {title}\n🎞 **{nums[0]}-fasl {nums[1]}-qism**\n\n{CHANNEL_ID}"
            await message.answer_video(video=f_id, caption=cap, parse_mode="Markdown")

@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def save_video(message: types.Message):
    if message.caption:
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
        await message.reply(f"✅ Baza abadiy saqladi!\nKod: {code}")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
