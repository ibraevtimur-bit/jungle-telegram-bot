import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))  # в Railway переменной ADMIN_CHAT_ID поставь свой chat_id

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Кнопки
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("🍽 Меню"))
keyboard.add(KeyboardButton("📅 Забронировать стол"))
keyboard.add(KeyboardButton("📍 Локация"))

# Состояния (очень простая логика)
WAITING_BOOKING = set()  # тут храним user_id, кто сейчас вводит бронь


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    await message.answer(
        "🌿 Добро пожаловать в Jungle Family Club!\n\nВыберите действие:",
        reply_markup=keyboard
    )


@dp.message_handler(commands=["menu"])
async def menu_command(message: types.Message):
    await message.answer("Наше меню скоро появится! 🍽")


@dp.message_handler(lambda m: m.text == "🍽 Меню")
async def menu_button(message: types.Message):
    await message.answer("Наше меню скоро появится! 🍽")


@dp.message_handler(commands=["location"])
async def location_command(message: types.Message):
    await message.answer("Мы находимся в Ташкенте. Скоро добавим карту. 📍")


@dp.message_handler(lambda m: m.text == "📍 Локация")
async def location_button(message: types.Message):
    await message.answer("Мы находимся в Ташкенте. Скоро добавим карту. 📍")


@dp.message_handler(commands=["booking"])
async def booking_command(message: types.Message):
    WAITING_BOOKING.add(message.from_user.id)
    await message.answer(
        "📅 Напишите бронь одним сообщением в формате:\n"
        "Дата, время, количество гостей, имя, телефон\n\n"
        "Пример:\n25 марта 19:00, 6 гостей, Алексей, +998901234567"
    )


@dp.message_handler(lambda m: m.text == "📅 Забронировать стол")
async def booking_button(message: types.Message):
    WAITING_BOOKING.add(message.from_user.id)
    await message.answer(
        "📅 Напишите бронь одним сообщением в формате:\n"
        "Дата, время, количество гостей, имя, телефон\n\n"
        "Пример:\n25 марта 19:00, 6 гостей, Алексей, +998901234567"
    )


@dp.message_handler()
async def any_message_handler(message: types.Message):
    # Если человек НЕ в режиме брони — ничего не делаем (чтобы не спамил бот)
    if message.from_user.id not in WAITING_BOOKING:
        return

    WAITING_BOOKING.discard(message.from_user.id)

    # Отправляем админу
    if ADMIN_ID != 0:
        await bot.send_message(
            ADMIN_ID,
            f"📅 Новая бронь!\n\n"
            f"От: {message.from_user.full_name} (@{message.from_user.username})\n"
            f"Текст:\n{message.text}"
        )

    await message.answer("✅ Спасибо! Бронь принята. Мы скоро свяжемся с вами.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
