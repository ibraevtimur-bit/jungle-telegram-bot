import os
import re
import asyncio
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor


TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))  # твой chat_id (куда приходят брони)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Кнопки
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("🍽 Меню"))
keyboard.add(KeyboardButton("📅 Забронировать стол"))
keyboard.add(KeyboardButton("📍 Локация"))

# Состояние: кто сейчас вводит бронь
WAITING_BOOKING = set()


# --- Парсер брони (русские месяцы) ---
MONTHS_RU = {
    "января": 1, "февраля": 2, "марта": 3, "апреля": 4, "мая": 5, "июня": 6,
    "июля": 7, "августа": 8, "сентября": 9, "октября": 10, "ноября": 11, "декабря": 12
}

BOOKING_RE = re.compile(
    r"^\s*(\d{1,2})\s+([а-яА-ЯёЁ]+)\s+(\d{1,2}:\d{2})\s*,\s*"
    r"(\d+)\s*(?:гостей|гостя|гость)\s*,\s*"
    r"([^,]+?)\s*,\s*"
    r"(\+?\d[\d\s\-()]{7,})\s*$"
)

def parse_booking(text: str):
    """
    Ожидаем формат:
    25 марта 19:00, 6 гостей, Алексей, +998901234567
    """
    m = BOOKING_RE.match(text)
    if not m:
        return None

    day = int(m.group(1))
    month_name = m.group(2).strip().lower().replace("ё", "е")
    time_str = m.group(3).strip()
    guests = int(m.group(4))
    name = m.group(5).strip()
    phone = m.group(6).strip()

    if month_name not in MONTHS_RU:
        return None

    month = MONTHS_RU[month_name]
    hour, minute = map(int, time_str.split(":"))

    # Год: берём текущий. (Если бронь на следующий год — потом расширим)
    now = datetime.now()
    dt = datetime(now.year, month, day, hour, minute)

    # Если дата уже прошла (например, в январе вводят "декабря") — считаем следующий год
    if dt < now - timedelta(days=1):
        dt = datetime(now.year + 1, month, day, hour, minute)

    return {
        "dt": dt,
        "day": day,
        "month_name": month_name,
        "time": time_str,
        "guests": guests,
        "name": name,
        "phone": phone
    }


async def schedule_reminder(chat_id: int, booking_dt: datetime, guests: int, name: str):
    """
    Напоминание за 2 часа до booking_dt
    """
    remind_at = booking_dt - timedelta(hours=2)
    now = datetime.now()
    delay = (remind_at - now).total_seconds()

    # Если до напоминания меньше 0 — не ждём, просто не отправляем
    if delay <= 0:
        return

    await asyncio.sleep(delay)

    # В момент отправки можно ещё раз проверить, что это не очень поздно
    try:
        await bot.send_message(
            chat_id,
            f"⏰ Напоминание: у вас бронь через 2 часа.\n"
            f"📅 Время: {booking_dt.strftime('%d.%m %H:%M')}\n"
            f"👥 Гостей: {guests}\n"
            f"👤 Имя: {name}\n\n"
            f"Если планы изменились — просто напишите сюда."
        )
    except Exception:
        # если пользователь заблокировал бота и т.п.
        pass


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    WAITING_BOOKING.discard(message.from_user.id)
    await message.answer("🌿 Добро пожаловать в Jungle Family Club!\n\nВыберите действие:", reply_markup=keyboard)


# /menu и кнопка "🍽 Меню"
@dp.message_handler(commands=["menu"])
async def menu_command(message: types.Message):
    await message.answer("Наше меню скоро появится! 🍽")

@dp.message_handler(lambda m: m.text == "🍽 Меню")
async def menu_button(message: types.Message):
    await message.answer("Наше меню скоро появится! 🍽")


# /location и кнопка "📍 Локация"
@dp.message_handler(commands=["location"])
async def location_command(message: types.Message):
    await message.answer("Мы находимся в Ташкенте. Скоро добавим карту. 📍")

@dp.message_handler(lambda m: m.text == "📍 Локация")
async def location_button(message: types.Message):
    await message.answer("Мы находимся в Ташкенте. Скоро добавим карту. 📍")


# /booking и кнопка "📅 Забронировать стол"
@dp.message_handler(commands=["booking"])
async def booking_command(message: types.Message):
    WAITING_BOOKING.add(message.from_user.id)
    await message.answer(
        "📅 Напишите бронь одним сообщением в формате:\n"
        "Дата, время, количество гостей, имя, телефон\n\n"
        "Пример:\n"
        "25 марта 19:00, 6 гостей, Алексей, +998901234567"
    )

@dp.message_handler(lambda m: m.text == "📅 Забронировать стол")
async def booking_button(message: types.Message):
    WAITING_BOOKING.add(message.from_user.id)
    await message.answer(
        "📅 Напишите бронь одним сообщением в формате:\n"
        "Дата, время, количество гостей, имя, телефон\n\n"
        "Пример:\n"
        "25 марта 19:00, 6 гостей, Алексей, +998901234567"
    )


# Ловим любое сообщение (и если человек в режиме брони — обрабатываем)
@dp.message_handler()
async def any_message(message: types.Message):
    if message.from_user.id not in WAITING_BOOKING:
        return

    data = parse_booking(message.text)
    if not data:
        await message.answer(
            "⚠️ Не понял формат.\n\nПожалуйста, отправьте так:\n"
            "25 марта 19:00, 6 гостей, Алексей, +998901234567"
        )
        return

    WAITING_BOOKING.discard(message.from_user.id)

    # 1) Сообщаем админу
    if ADMIN_ID != 0:
        username = f"@{message.from_user.username}" if message.from_user.username else "нет username"
        await bot.send_message(
            ADMIN_ID,
            "📅 Новая бронь!\n\n"
            f"От: {message.from_user.full_name} ({username})\n"
            f"Текст:\n{message.text}\n\n"
            f"⏰ Напоминание гостю: за 2 часа (авто)"
        )

    # 2) Подтверждение гостю
    await message.answer("✅ Спасибо! Бронь принята. Мы скоро свяжемся с вами.")

    # 3) Ставим напоминание гостю за 2 часа
    asyncio.create_task(
        schedule_reminder(
            chat_id=message.chat.id,
            booking_dt=data["dt"],
            guests=data["guests"],
            name=data["name"]
        )
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
