from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.core.config import settings

# Global variables, but initialized only if token is valid
bot = None
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text="Open StockUp 🛒", 
        web_app=types.WebAppInfo(url=settings.WEBAPP_URL)
    ))
    
    await message.answer(
        f"Hello, {message.from_user.first_name}! 👋\n\n"
        "Welcome to StockUp — your family shopping assistant.\n"
        "Click the button below to manage your inventory.",
        reply_markup=builder.as_markup()
    )

async def start_bot():
    global bot
    
    # Simple validation check
    if not settings.BOT_TOKEN or ":" not in settings.BOT_TOKEN:
        print("Telegram Bot: Invalid or missing token. Skipping bot startup.")
        return
    
    try:
        bot = Bot(token=settings.BOT_TOKEN)
        print("Starting Telegram Bot...")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Failed to start Telegram Bot: {e}")
