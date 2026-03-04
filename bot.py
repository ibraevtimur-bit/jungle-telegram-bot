import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("🍽 Меню"))
keyboard.add(KeyboardButton("📅 Забронировать стол"))
keyboard.add(KeyboardButton("📍 Локация"))

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(
        "🌿 Добро пожаловать в Jungle Family Club!\n\nВыберите действие:",
        reply_markup=keyboard
    )

@dp.message_handler(lambda message: message.text == "🍽 Меню")
async def menu_handler(message: types.Message):
    await message.answer("Наше меню скоро появится!")

@dp.message_handler(lambda message: message.text == "📅 Забронировать стол")
async def booking_handler(message: types.Message):
    await message.answer("Напишите дату, время и количество гостей.")

@dp.message_handler(lambda message: message.text == "📍 Локация")
async def location_handler(message: types.Message):
    await message.answer("Мы находимся в Ташкенте. Скоро добавим карту.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
