import os
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Railway Variables
API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 8203513150  # O'z ID-ingizni bu yerga yozing!

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- MA'LUMOTLAR BAZASI ---
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

# --- ASOSIY MENYU ---
def get_main_menu():
    kb = [
        [KeyboardButton(text="1-FASL"), KeyboardButton(text="2-FASL")],
        [KeyboardButton(text="3-FASL")],
        [KeyboardButton(text="📢 Kanalimiz")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

# --- QISMLAR MENYUSI ---
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
@dp.message(F.text == "/start")
async def start_command(message: types.Message):
    await message.answer("🎬 Salom! Kerakli faslni tanlang 👇", reply_markup=get_main_menu())

@dp.message(F.text == "⬅️ Orqaga")
async def back_to_main(message: types.Message):
    await message.answer("Asosiy menyu:", reply_markup=get_main_menu())

@dp.message(F.text == "📢 Kanalimiz")
async def channel_link(message: types.Message):
    await message.answer("Bizning rasmiy kanalimiz: \nhttps://t.me/My_AnimeChannel")

# FASL TANLANGANDA QISMLARNI CHIQARISH
@dp.message(F.text.in_(["1-FASL", "2-FASL", "3-FASL"]))
async def show_parts(message: types.Message):
    season = message.text.split("-")[0]
    # Qismlar sonini shu yerda to'g'irlashingiz mumkin:
    parts_count = {"1": 10, "2": 13, "3": 15}
    count = parts_count.get(season, 10)
    await message.answer(f"✨ {season}-fasl qismlarini tanlang:", reply_markup=get_parts_menu(season, count))

# --- VIDEONI CHIQARIB BERISH (RASMDAGIDEK FORMATDA) ---
@dp.message(F.text.contains("-fasl ") & F.text.contains("-qism"))
async def send_video_part(message: types.Message):
    data = message.text.replace("-fasl", "").replace("-qism", "").split()
    season, part = data[0], data[1]
    code = f"{season}_{part}"
    
    file_id = get_movie(code)
    
    if file_id:
        # RASMDAGI KABI MATN VA KANAL LINKI:
        caption_text = (
            f"🎬 **Anime:** Solo Leveling\n"
            f"🎞 **{season}-fasl {part}-qism**\n"
            f"🇺🇿 **Tili:** O'zbek Tilida\n\n"
            f"Asosiy Kanal 👇👇\n"
            f"@My_AnimeChannel 📌"
        )
        await message.answer_video(
            video=file_id, 
            caption=caption_text, 
            parse_mode="Markdown"
        )
    else:
        await message.answer("⚠️ Bu qism hali yuklanmagan yoki bazada yo'q.")

# ADMIN: Video yuklash (Masalan: 1_1 kodi bilan)
@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def add_movie_handler(message: types.Message):
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
