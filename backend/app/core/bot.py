from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from app.core.config import settings

# Global variables, but initialized only if token is valid
bot = None
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Reply Keyboard (always visible at the bottom)
    reply_builder = ReplyKeyboardBuilder()
    reply_builder.add(types.KeyboardButton(
        text="🛒 Open StockUp", 
        web_app=types.WebAppInfo(url=settings.WEBAPP_URL)
    ))
    
    # Inline Keyboard (attached to the message)
    inline_builder = InlineKeyboardBuilder()
    inline_builder.row(types.InlineKeyboardButton(
        text="Open StockUp 🛒", 
        web_app=types.WebAppInfo(url=settings.WEBAPP_URL)
    ))
    
    await message.answer(
        f"Hello, {message.from_user.first_name}! 👋\n\n"
        "Welcome to StockUp — your family shopping assistant.",
        reply_markup=reply_builder.as_markup(resize_keyboard=True)
    )
    
    await message.answer(
        "Click the button below or in the menu to manage your inventory:",
        reply_markup=inline_builder.as_markup()
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
        
        # Set the global Menu Button
        try:
            await bot.set_chat_menu_button(
                menu_button=types.MenuButtonWebApp(
                    type="web_app",
                    text="Open App",
                    web_app=types.WebAppInfo(url=settings.WEBAPP_URL)
                )
            )
            print("Successfully set Menu Button Web App")
        except Exception as e:
            print(f"Failed to set Menu Button: {e}")
            
        await dp.start_polling(bot, handle_signals=False)
    except Exception as e:
        print(f"Failed to start Telegram Bot: {e}")
