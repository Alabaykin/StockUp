from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.core.config import settings

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = InlineKeyboardBuilder()
    # Replace with your actual web app URL if deployed, 
    # but for local testing it's usually set in the BotFather settings.
    # We'll use a placeholder or the one from settings if we add it.
    builder.row(types.InlineKeyboardButton(
        text="Open StockUp 🛒", 
        web_app=types.WebAppInfo(url="https://your-domain.com/") # This is just a placeholder
    ))
    
    await message.answer(
        f"Hello, {message.from_user.first_name}! 👋\n\n"
        "Welcome to StockUp — your family shopping assistant.\n"
        "Click the button below to manage your inventory.",
        reply_markup=builder.as_markup()
    )

async def start_bot():
    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        print("Bot token not set, skipping bot startup.")
        return
    
    print("Starting Telegram Bot...")
    await dp.start_polling(bot)
