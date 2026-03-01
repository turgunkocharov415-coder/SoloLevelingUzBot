import os
import asyncio
import psycopg2
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# --- SOZLAMALAR ---
API_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = 8203513150  
CHANNEL_ID = "@My_AnimeChannel" # Kanalingiz username-ini tekshirib oling

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# --- BAZA BILAN ISHLASH ---
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS movies (code TEXT PRIMARY KEY, file_id TEXT, title TEXT)")
    conn.commit()
    cursor.close()
    conn.close()

def get_movie_data(code):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, title FROM movies WHERE code = %s", (code,))
    res = cursor.fetchone()
    cursor.close()
    conn.close()
    return res if res else (None, None)

def get_uploaded_parts(season_num):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code FROM movies WHERE code LIKE %s", (f"{season_num}_%",))
    codes = cursor.fetchall()
    cursor.close()
    conn.close()
    parts = []
    for c in codes:
        try: parts.append(int(c[0].split('_')[1]))
        except: continue
    return sorted(list(set(parts)))

# --- MENYULAR ---
def get_main_menu():
    kb = [[KeyboardButton(text="1-FASL"), KeyboardButton(text="2-FASL")],
          [KeyboardButton(text="3-FASL")],
          [KeyboardButton(text="📢 Kanalimiz")]]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_inline_menu(season_num):
    parts = get_uploaded_parts(season_num)
    if not parts: return None
    keyboard = []
    row = []
    for p in parts:
        row.append(InlineKeyboardButton(text=f"🎬 {p}-qism", callback_data=f"get_{season_num}_{p}"))
        if len(row) == 3:
            keyboard.append(row); row = []
    if row: keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- BOT LOGIKASI ---

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    args = message.text.split()
    if len(args) > 1:
        param = args[1]
        if "_" in param:
            f_id, title = get_movie_data(param)
            if f_id:
                cap = f"<b>🎬 Anime:</b> {title}\n<b>🎞 {param.split('_')[0]}-fasl {param.split('_')[1]}-qism</b>\n\n{CHANNEL_ID}"
                await message.answer_video(video=f_id, caption=cap, parse_mode="HTML")
                return
        if param.isdigit():
            menu = get_inline_menu(param)
            if menu:
                await message.answer(f"✨ {param}-fasl qismlari yuklangan. Tanlang:", reply_markup=menu)
                return
    await message.answer("🎬 Salom! Kerakli faslni tanlang 👇", reply_markup=get_main_menu())

# --- ADMIN UCHUN: KANALGA POST YUBORISH ---
@dp.message(F.photo & (F.from_user.id == ADMIN_ID))
async def post_to_channel(message: types.Message):
    if message.caption and message.caption.startswith("POST"):
        # Format: POST 1 (1-fasl uchun tugmali post yuboradi)
        try:
            season = message.caption.split()[1]
            btn_url = f"https://t.me/SoloLevelingUzBot?start={season}" # To'g'ri username
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"🎬 {season}-faslni ko'rish", url=btn_url)]
            ])
            await bot.send_photo(chat_id=CHANNEL_ID, photo=message.photo[-1].file_id, 
                                caption=f"✨ <b>Solo Leveling: {season}-fasl</b>\n\nBarcha qismlarni bot orqali tomosha qiling!", 
                                reply_markup=kb, parse_mode="HTML")
            await message.reply("✅ Post kanalga yuborildi!")
        except:
            await message.reply("❌ Xato! Format: rasm tagiga 'POST 1' deb yozing.")

@dp.message(F.text == "📢 Kanalimiz")
async def open_channel(message: types.Message):
    url = f"https://t.me/{CHANNEL_ID.replace('@', '')}"
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Obuna bo'lish 🚀", url=url)]])
    await message.answer(f"<b>{CHANNEL_ID}</b> kanalimizga xush kelibsiz!", reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data.startswith("get_"))
async def send_movie_callback(callback: types.CallbackQuery):
    code = callback.data.replace("get_", "")
    f_id, title = get_movie_data(code)
    if f_id:
        cap = f"<b>🎬 Anime:</b> {title}\n<b>🎞 {code.split('_')[0]}-fasl {code.split('_')[1]}-qism</b>\n\n{CHANNEL_ID}"
        await callback.message.answer_video(video=f_id, caption=cap, parse_mode="HTML")
        await callback.answer()

@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def save_video(message: types.Message):
    if message.caption:
        parts = message.caption.split(maxsplit=1)
        code, title = parts[0], parts[1] if len(parts) > 1 else "Kino"
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movies (code, file_id, title) VALUES (%s, %s, %s) ON CONFLICT (code) DO UPDATE SET file_id = EXCLUDED.file_id, title = EXCLUDED.title", (code, message.video.file_id, title))
        conn.commit(); cursor.close(); conn.close()
        await message.reply(f"✅ Saqlandi! Kod: {code}")

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
