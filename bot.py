import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Telegram Bot Token
TOKEN = "7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4"

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===========================
# MAIN MENU
# ===========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name or "Friend"

    text = (
        f"မင်္ဂလာပါ **{user}** 🥰\n"
        "🌼 **Oscar's Library** 🌼 မှ ကြိုဆိုပါတယ်\n\n"
        "စာအုပ်များရှာဖွေရန် လမ်းညွှန်ပေးမယ်...\n\n"
        "(**စာအုပ်ရှာဖို့ နှစ်ပိုင်းခွဲထားတယ် — "
        "ကဏ္ဍအလိုက် နှင့် စာရေးဆရာ ဖြစ်ပါတယ်**\n\n"
        "**Fic၊ ကာတွန်း၊ သည်းထိပ်ရင်ဖို စသည့် ကဏ္ဍများဖြင့်သွားရန်** "
        "→ *ကဏ္ဍအလိုက်* ကိုရွေးပါ\n\n"
        "**စာရေးဆရာနာမည်ဖြင့်ရှာချင်ရင်** → *စာရေးဆရာ* ကိုရွေးပေးပါ)\n\n"
        "💢 စာအုပ်ဖတ်နည်းကို အရင်ကြည့်ပါရန်\n\n"
        "⚠️ အဆင်မပြေမှုရှိပါက ‘အထွေထွေမေးမြန်းရန်’ ကိုနှိပ်ပြီး မေးမြန်းနိုင်ပါတယ်။"
    )

    keyboard = [
        [
            InlineKeyboardButton("📚 ကဏ္ဍအလိုက်", callback_data="cat"),
            InlineKeyboardButton("✍️ စာရေးဆရာ", callback_data="author_menu"),
        ],
        [
            InlineKeyboardButton("📖 စာအုပ်ဖတ်နည်း", callback_data="read_guide"),
            InlineKeyboardButton("📂 ချန်နယ်ခွဲများ", callback_data="channels"),
        ],
        [
            InlineKeyboardButton("⭐ Review ရေးရန်", callback_data="review"),
            InlineKeyboardButton("🛠 စာအုပ်ပြုပြင်ရန်", callback_data="edit_book"),
        ],
        [
            InlineKeyboardButton("❓ အထွေထွေမေးမြန်းရန်", callback_data="qa"),
        ]
    ]

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ===========================
# REDIRECT FUNCTIONS
# ===========================
async def redirect(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text(f"👇 အောက်က Link ကိုနှိပ်ပါ\n{url}")


# ===========================
# MAIN MENU CALLBACKS
# ===========================
async def handle_main_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "cat":
        await redirect(update, context, "https://t.me/oscarhelpservices/4")

    elif data == "read_guide":
        await redirect(update, context, "https://t.me/oscarhelpservices/17")

    elif data == "channels":
        await redirect(update, context, "https://t.me/oscarhelpservices/9")

    elif data == "review":
        await redirect(update, context, "https://t.me/sharebykosoemoe/13498")

    elif data == "edit_book":
        await redirect(update, context, "https://t.me/oscarhelpservices/29?single")

    elif data == "qa":
        await redirect(update, context, "https://t.me/kogyisoemoe")

    elif data == "author_menu":
        await show_author_menu(update, context)


# ===========================
# AUTHOR MENU
# ===========================
author_links = {
    "က": "5",
    "ခ": "7",
    "ဂ": "12",
    "င": "14",
    "စ": "16",
    "ဆ": "18",
    "ဇ": "20",
    "ည": "23",
    "ဋ္ဌ": "25",
    "တ": "27",
    "ထ": "33",
    "ဒ": "35",
    "ဓ": "37",
    "န": "39",
    "ပ": "41",
    "ဖ": "43",
    "ဗ": "45",
    "ဘ": "47",
    "မ": "49",
    "ယ": "51",
    "ရ": "53",
    "လ": "55",
    "ဝ": "57",
    "သ": "59",
    "ဟ": "61",
    "အ": "30",
    "ဥ": "10",
    "Eng": "920",
}

async def show_author_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = []
    row = []

    for key in author_links.keys():
        row.append(InlineKeyboardButton(key, callback_data=f"author_{key}"))
        if len(row) == 4:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    await query.message.reply_text(
        "စာရေးဆရာနာမည် **အစ စလုံးဖြင့်** ရွေးပါ👇",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ===========================
# AUTHOR BUTTON CLICK
# ===========================
async def handle_author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    key = query.data.replace("author_", "")
    link_id = author_links.get(key)

    if link_id:
        await redirect(update, context, f"https://t.me/oscarhelpservices/{link_id}")


# ===========================
# MAIN APP
# ===========================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_main_buttons, pattern="^(cat|read_guide|channels|review|edit_book|qa|author_menu)$"))
    app.add_handler(CallbackQueryHandler(handle_author, pattern="^author_"))

    app.run_polling()


if __name__ == "__main__":
    main()
