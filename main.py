import os
import asyncio
import sqlite3
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandObject, Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8203513150  # Sizning ID-ingiz

# BU YERNI O'ZINGIZNIKI BILAN ALMASHTIRING:
CHANNEL_ID = "@My_AnimeChannel"  # Kanalingiz yuzernami
BOT_USER = "SoloLevelingUzBot"   # Botingiz yuzernami (@ belgisiz)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- BAZA BILAN ISHLASH ---
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
    except Exception:
        return None

# --- ASOSIY MENYULAR ---
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

# --- START BUYRUG'I ---
@dp.message(Command("start"))
async def start_command(message: types.Message, command: CommandObject):
    if command.args == "season1":
        await message.answer("✨ 1-fasl qismlarini tanlang:", reply_markup=get_parts_menu("1", 10))
    else:
        await message.answer("🎬 Salom! Kerakli faslni tanlang 👇", reply_markup=get_main_menu())

# --- ADMIN: KANALGA TUGMALI RASM YUBORISH ---
@dp.message(F.photo & (F.from_user.id == ADMIN_ID))
async def admin
