
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer("🌿 Добро пожаловать в Jungle Restaurant!")

@dp.message_handler()
async def echo_handler(message: types.Message):
    await message.answer(f"Вы написали: {message.text}")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
