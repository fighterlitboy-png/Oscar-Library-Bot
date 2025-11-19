import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# =============================
# BOT TOKEN
# =============================
TOKEN = "7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4"

# =============================
# Logging
# =============================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# =============================
# /start Handler
# =============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.first_name

    keyboard = [
        [InlineKeyboardButton("📚 ကဏ္ဍအလိုက်", callback_data="category")],
        [InlineKeyboardButton("✍️ စာရေးဆရာ", callback_data="author")],
        [InlineKeyboardButton("📖 စာအုပ်ဖတ်နည်း", callback_data="read_guide")],
        [InlineKeyboardButton("📺 ချန်နယ်ခွဲများ", callback_data="channels")],
        [InlineKeyboardButton("⭐ Review ရေးရန်", callback_data="review")],
        [InlineKeyboardButton("🛠 စာအုပ်ပြုပြင်ရန်", callback_data="edit_book")],
        [InlineKeyboardButton("❓ အထွေထွေမေးမြန်းရန်", callback_data="general_ask")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    text = f"မင်္ဂလာပါ {user} 🥰\nOscar Help Service Bot မှ ကြိုဆိုပါတယ် ❤️"

    await update.message.reply_text(text, reply_markup=reply_markup)

# =============================
# CALLBACK HANDLER
# =============================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    # CATEGORY
    if data == "category":
        await query.edit_message_text("📚 ကဏ္ဍများကို ဒီမှာကြည့်ပါ👇\nhttps://t.me/oscarhelpservices/4")

    # AUTHOR
    elif data == "author":
        await query.edit_message_text("✍️ စာရေးဆရာများ👇\nhttps://t.me/oscarhelpservices/6")

    # READ GUIDE
    elif data == "read_guide":
        await query.edit_message_text("📖 စာအုပ်ဖတ်နည်း👇\nhttps://t.me/oscarhelpservices/17")

    # CHANNELS
    elif data == "channels":
        await query.edit_message_text("📺 ချန်နယ်ခွဲများ👇\nhttps://t.me/oscarhelpservices/9")

    # REVIEW
    elif data == "review":
        await query.edit_message_text("⭐ Review ပေးရန်👇\nhttps://t.me/sharebykosoemoe/13498")

    # EDIT BOOK
    elif data == "edit_book":
        await query.edit_message_text("🛠 စာအုပ်ပြုပြင်ရန်👇\nhttps://t.me/oscarhelpservices/29?single")

    # GENERAL ASK
    elif data == "general_ask":
        await query.edit_message_text("❓ မေးမြန်းရန်👇\nhttps://t.me/kogyisoemoe")


# =============================
# MAIN
# =============================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()
