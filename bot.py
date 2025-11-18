import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# =========================
# MAIN LINK BUTTON TARGETS
# =========================
MAIN_LINKS = {
    "category": "https://t.me/oscarhelpservices/4",
    "how_to_read": "https://t.me/oscarhelpservices/17",
    "channels": "https://t.me/oscarhelpservices/9",
    "review": "https://t.me/sharebykosoemoe/13498",
    "edit_book": "https://t.me/oscarhelpservices/29?single",
    "general_qa": "https://t.me/kogyisoemoe",
}

# =========================
# AUTHOR LETTER ROUTES
# =========================
AUTHOR_LINKS = {
    "က": "https://t.me/oscarhelpservices/5",
    "ခ": "https://t.me/oscarhelpservices/7",
    "ဂ": "https://t.me/oscarhelpservices/12",
    "င": "https://t.me/oscarhelpservices/14",
    "စ": "https://t.me/oscarhelpservices/16",
    "ဆ": "https://t.me/oscarhelpservices/18",
    "ဇ": "https://t.me/oscarhelpservices/20",
    "ည": "https://t.me/oscarhelpservices/23",
    "ဌ": "https://t.me/oscarhelpservices/25",   # << FIXED HERE
    "တ": "https://t.me/oscarhelpservices/27",
    "ထ": "https://t.me/oscarhelpservices/33",
    "ဒ": "https://t.me/oscarhelpservices/35",
    "ဓ": "https://t.me/oscarhelpservices/37",
    "န": "https://t.me/oscarhelpservices/39",
    "ပ": "https://t.me/oscarhelpservices/41",
    "ဖ": "https://t.me/oscarhelpservices/43",
    "ဗ": "https://t.me/oscarhelpservices/45",
    "ဘ": "https://t.me/oscarhelpservices/47",
    "မ": "https://t.me/oscarhelpservices/49",
    "ယ": "https://t.me/oscarhelpservices/51",
    "ရ": "https://t.me/oscarhelpservices/53",
    "လ": "https://t.me/oscarhelpservices/55",
    "ဝ": "https://t.me/oscarhelpservices/57",
    "သ": "https://t.me/oscarhelpservices/59",
    "ဟ": "https://t.me/oscarhelpservices/61",
    "အ": "https://t.me/oscarhelpservices/30",
    "ဥ၊ဩ၊ဧ": "https://t.me/oscarhelpservices/10",
    "Eng": "https://t.me/sharebykosoemoe/920",
}

# =========================
# /START HANDLER
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.full_name or user.username or "မိတ်ဆွေ"

    welcome_text = (
        f"မင်္ဂလာပါ {username} 🥰\n"
        "🌼 *Oscar's Library* 🌼 မှကြိုဆိုပါတယ်\n"
        "*စာအုပ်များရှာဖွေရန်လမ်းညွှန်ပေးမယ်...*\n"
        "( *စာအုပ်ရှာဖို့ နှစ်ပိုင်းခွဲထားတယ် —*\n"
        "*ကဏ္ဍအလိုက်* နှင့် *စာရေးဆရာ* ဖြစ်ပါတယ် )📚\n"
        "💢 *စာအုပ်ဖတ်နည်းကိုအရင်ကြည့်ပါရန်*\n"
        "⚠️ *အဆင်မပြေမှုများရှိရင် အထွေထွေမေးမြန်းရန် ကိုနှိပ်ပြီးမေးပါ*\n"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📂 ကဏ္ဍအလိုက်", callback_data="category")],
        [InlineKeyboardButton("✍ စာရေးဆရာ", callback_data="authors")],
        [InlineKeyboardButton("📖 စာအုပ်ဖတ်နည်း", url=MAIN_LINKS["how_to_read"])],
        [InlineKeyboardButton("📺 ချန်နယ်ခွဲများ", url=MAIN_LINKS["channels"])],
        [InlineKeyboardButton("📝 Review ရေးရန်", url=MAIN_LINKS["review"])],
        [InlineKeyboardButton("🛠 စာအုပ်ပြုပြင်ရန်", url=MAIN_LINKS["edit_book"])],
        [InlineKeyboardButton("❓ အထွေထွေမေးမြန်ရန်", url=MAIN_LINKS["general_qa"])],
    ])

    await update.message.reply_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# =========================
# BUTTON HANDLER
# =========================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # CATEGORY BUTTON
    if query.data == "category":
        await query.edit_message_text(
            "📂 ကဏ္ဍအလိုက် ရှာဖွေနေပါသည်...",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("သွားရန် 👉", url=MAIN_LINKS["category"])]
            ])
        )

    # AUTHOR BUTTON ROOT
    elif query.data == "authors":
        kb = []
        row = []
        for i, key in enumerate(AUTHOR_LINKS.keys(), start=1):
            row.append(InlineKeyboardButton(key, callback_data=f"author_{key}"))
            if i % 4 == 0:
                kb.append(row)
                row = []
        if row:
            kb.append(row)

        await query.edit_message_text(
            "✍ *စာရေးဆရာ အစ စလုံးဖြင့်ရွေးပါ*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    # AUTHOR LETTER PRESSED
    elif query.data.startswith("author_"):
        letter = query.data.replace("author_", "")
        url = AUTHOR_LINKS.get(letter)
        await query.edit_message_text(
            f"✍ *{letter} စာရေးဆရာများအတွက်*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("သွားရန် 👉", url=url)]
            ])
        )

# =========================
# BOT LAUNCH
# =========================
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("🚀 BOT IS RUNNING...")
    app.run_polling()
allback_data="author_မ"),
                InlineKeyboardButton("ယ", callback_data="author_ယ")
            ],
            # Row 5: 5 buttons
            [
                InlineKeyboardButton("ရ", callback_data="author_ရ"),
                InlineKeyboardButton("လ", callback_data="author_လ"),
                InlineKeyboardButton("ဝ", callback_data="author_ဝ"),
                InlineKeyboardButton("သ", callback_data="author_သ"),
                InlineKeyboardButton("ဟ", callback_data="author_ဟ")
            ],
            # Row 6: 3 buttons
            [
                InlineKeyboardButton("အ", callback_data="author_အ"),
                InlineKeyboardButton("ဥ၊ဩ၊ဧ", callback_data="author_ဥသြဧ"),
                InlineKeyboardButton("Eng", callback_data="author_Eng")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(author_keyboard)
        await query.edit_message_text(
            "စာရေးဆရာနာမည်\nအစ စလုံးဖြင့်ရွေးရှာပေးပါ",
            reply_markup=reply_markup
        )

def main():
    # Create Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Start bot
    print("🤖 Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
