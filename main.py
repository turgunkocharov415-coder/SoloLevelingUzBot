import os
import asyncio
import sqlite3
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandObject, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = os.getenv("BOT_TOKEN")
# ADMIN_ID ni o'zingizniki bilan tekshiring
ADMIN_ID = 8203513150  

# KANAL VA BOT LINKLARI
CHANNEL_ID = "@My_AnimeChannel" 
BOT_USER = "SoloLevelingUzBot"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- BAZA ---
def init_db():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS movies (code TEXT PRIMARY KEY, file_id TEXT)")
    conn.commit()
    conn.close()

def get_movie(code):
    try:
        conn = sqlite3.connect("movies.db")
        cursor = conn.cursor()
        cursor.execute("SELECT file_id FROM movies WHERE code = ?", (code,))
        res = cursor.fetchone()
        conn.close()
        return res[0] if res else None
    except:
        return None

# --- MENYULAR ---
def get_main_menu():
    kb = [[KeyboardButton(text="1-FASL"), KeyboardButton(text="2-FASL")],
          [KeyboardButton(text="3-FASL")], [KeyboardButton(text="📢 Kanalimiz")]]
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

# --- BUYRUQLAR ---
@dp.message(Command("start"))
async def start_command(message: types.Message, command: CommandObject):
    if command.args == "season1":
        await message.answer("✨ 1-fasl qismlarini tanlang:", reply_markup=get_parts_menu("1", 10))
    else:
        await message.answer("🎬 Salom! Kerakli faslni tanlang 👇", reply_markup=get_main_menu())

# --- VIDEO YUBORISH ---
@dp.message(F.text.contains("-fasl") & F.text.contains("-qism"))
async def send_video_part(message: types.Message):
    numbers = re.findall(r'\d+', message.text)
    if len(numbers) >= 2:
        season, part = numbers[0], numbers[1]
        search_code = f"{season}_{part}"
        file_id = get_movie(search_code)
        
        if file_id:
            try:
                await bot.send_video(chat_id=message.chat.id, video=file_id, 
                                     caption=f"🎬 1-fasl {part}-qism\n\n@My_AnimeChannel")
            except Exception as e:
                await message.answer(f"❌ Xato: {e}")
        else:
            await message.answer(f"⚠️ Bu qism bazada yo'q. (Kod: {search_code})")

# --- ADMIN: VIDEO SAQLASH ---
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
