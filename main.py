import asyncio
from aiogram import Bot, Dispatcher, types, F

API_TOKEN = 'TOKENINGIZNI_SHU_YERGA_YOZING'
ADMIN_ID = 12345678  # O'zingizning Telegram ID'ngizni yozing

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Kino bazasi: "kod": "file_id"
MOVIES_DB = {
    "101": "BAACAgIAAxkBAA...", # Bu yerda haqiqiy file_id bo'ladi
}

@dp.message(F.text == "/start")
async def start_cmd(message: types.Message):
    await message.answer("Salom! Kino kodini yuboring va men uni topib beraman.")

# Admin uchun file_id olish (Kino faylini botga yuborsangiz ID beradi)
@dp.message(F.video)
async def get_file_id(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(f"Kino yuklandi!\nFile ID: `{message.video.file_id}`", parse_mode="MarkdownV2")

# Kod orqali kinoni topish
@dp.message()
async def send_movie(message: types.Message):
    code = message.text
    if code in MOVIES_DB:
        file_id = MOVIES_DB[code]
        await bot.send_video(chat_id=message.chat.id, video=file_id, caption=f"🎬 Kod: {code}\nMarhamat, tomosha qiling!")
    else:
        await message.answer("Bunday kodli kino topilmadi. ❌")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
