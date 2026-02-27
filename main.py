import os
import asyncio
from aiogram import Bot, Dispatcher, types, F

# Railway Variables-dan tokenni olamiz
API_TOKEN = os.getenv("83526344577:AAGUbPMUTERa96zdovgofzkN_xL2L4kBg94")

# DIQQAT: Bu yerga o'zingizning Telegram ID-ingizni yozing (@userinfobot orqali olish mumkin)
ADMIN_ID = 906441402  # Misol: 512345678

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Kinolar bazasi (Vaqtinchalik: Bot o'chib yonsa tozalanadi)
movies_db = {}

# /start buyrug'i uchun
@dp.message(F.text == "/start")
async def start_command(message: types.Message):
    await message.answer("👋 Salom! Men  kino topuvchi botman.\n\nKino kodini yuboring!")

# ADMIN UCHUN: Kino qo'shish (Video yuborib, izohiga kod yozasiz)
@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def add_movie_handler(message: types.Message):
    if message.caption:
        code = message.caption.strip()
        movies_db[code] = message.video.file_id
        await message.reply(f"✅ Yangi kino saqlandi!\nKod: {code}")
    else:
        await message.reply("⚠️ Iltimos, videoni yuborishda izoh (caption) qismiga kino kodini yozing!")

# FOYDALANUVCHILAR UCHUN: Kino topish
@dp.message(F.text)
async def get_movie_handler(message: types.Message):
    code = message.text.strip()
    
    if code in movies_db:
        file_id = movies_db[code]
        await bot.send_video(
            chat_id=message.chat.id, 
            video=file_id, 
            caption=f"🎬 Kino kodi: {code}\n\nMarhamat, tomosha qiling!"
        )
    elif not code.startswith('/'):
        await message.answer("❌ Afsuski, bu kod bilan kino topilmadi. Qaytadan tekshirib ko'ring.")

async def main():
    print("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
