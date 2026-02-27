import asyncio
from aiogram import Bot, Dispatcher, types, F

# O'ZGARUVCHILARNI TO'LDIRING
API_TOKEN = '83526344577:AAGUbPMUTERa96zdovgofzkN_xL2L4kBg94'
ADMIN_ID = 12345678  # Telegramdan @userinfobot orqali ID'ngizni olib yozing

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Vaqtinchalik baza (Bot o'chsa o'chib ketadi, lekin test uchun qulay)
# Haqiqiy botda SQLite ishlatishimiz kerak bo'ladi
movies_db = {}

@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    await message.answer("🎬 Kino kodini yuboring!")

# ADMIN UCHUN: Kino qo'shish tartibi
# 1. Kinoni botga yuborasiz (Caption/Izohiga kodini yozasiz)
@dp.message(F.video & (F.from_user.id == ADMIN_ID))
async def add_movie(message: types.Message):
    if message.caption:
        code = message.caption.strip()
        movies_db[code] = message.video.file_id
        await message.reply(f"✅ Tayyor! {code} kodi bilan kino saqlandi.")
    else:
        await message.reply("⚠️ Iltimos, videoning 'izoh' (caption) qismiga kino kodini yozing!")

# FOYDALANUVCHILAR UCHUN: Kod orqali topish
@dp.message(F.text)
async def get_movie(message: types.Message):
    code = message.text.strip()
    if code in movies_db:
        file_id = movies_db[code]
        await bot.send_video(chat_id=message.chat.id, video=file_id, caption=f"🎬 Kod: {code}\n@SizningKanalingiz")
    else:
        await message.answer("❌ Bu kod bilan kino topilmadi.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
