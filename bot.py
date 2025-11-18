import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4")

# URLs
MAIN_LINKS = {
    "category": "https://t.me/oscarhelpservices/4",
    "how_to_read": "https://t.me/oscarhelpservices/17",
    "channels": "https://t.me/oscarhelpservices/9",
    "review": "https://t.me/sharebykosoemoe/13498",
    "edit_book": "https://t.me/oscarhelpservices/29?single",
    "general_qa": "https://t.me/kogyisoemoe",
}

AUTHOR_LINKS = {
    "က": "https://t.me/oscarhelpservices/5",
    "ခ": "https://t.me/oscarhelpservices/7",
    "ဂ": "https://t.me/oscarhelpservices/12",
    "င": "https://t.me/oscarhelpservices/14",
    "စ": "https://t.me/oscarhelpservices/16",
    "ဆ": "https://t.me/oscarhelpservices/18",
    "ဇ": "https://t.me/oscarhelpservices/20",
    "ည": "https://t.me/oscarhelpservices/23",
    "ဋ္ဌ": "https://t.me/oscarhelpservices/25",
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = user.full_name or user.username or "မိတ်ဆွေ"

    welcome_message = (
        f"မင်္ဂလာပါ {username} 🥰\n"
        "🌼 *Oscar's Library* 🌼 မှကြိုဆိုပါတယ်\n"
        "*စာအုပ်များရှာဖွေရန်လမ်းညွှန်ပေးမယ်...*\n"
        "( *စာအုပ်ရှာဖို့ နှစ်ပိုင်းခွဲထားတယ် —*\n"
        "*ကဏ္ဍအလိုက်* နှင့် *စာရေးဆရာ* ဖြစ်ပါတယ် )📚\n"
        "💢 *စာအုပ်ဖတ်နည်းကိုအရင်ကြည့်ပါရန်*\n"
        "⚠️ *အဆင်မပြေမှုများရှိပါက အထွေထွေမေးမြန်းရန်ကိုနှိပ်ပြီးမေးမြန်းနိုင်ပါသည်။*\n"
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
        welcome_message,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "category":
        await query.edit_message_text("📂 ကဏ္ဍအလိုက် ရှာဖွေခြင်း...", reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("သွားရန် 👉", url=MAIN_LINKS["category"])]]
        ))

    elif query.data == "authors":
        # Show author categories
        keyboard = []
        row = []
        for i, (key, _) in enumerate(AUTHOR_LINKS.items(), start=1):
            row.append(InlineKeyboardButton(key, callback_data=f"author_{key}"))
            if i % 4 == 0:  # 4 per row
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        await query.edit_message_text(
            "✍ *စာရေးဆရာ အစ စလုံးဖြင့်ရွေးရှာပေးပါ*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    elif query.data.startswith("author_"):
        key = query.data.replace("author_", "")
        link = AUTHOR_LINKS.get(key)
        if link:
            await query.edit_message_text(f"✍ {key} စာရေးဆရာများအတွက် ➡️", reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("သွားရန် 👉", url=link)]]
            ))
        else:
            await query.edit_message_text("မရှိသေးပါ။")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("Bot is running...")
    app.run_polling()
data="author_န"),
                InlineKeyboardButton("ပ", callback_data="author_ပ")
            ],
            [
                InlineKeyboardButton("ဖ", callback_data="author_ဖ"),
                InlineKeyboardButton("ဗ", callback_data="author_ဗ"),
                InlineKeyboardButton("ဘ", callback_data="author_ဘ"),
                InlineKeyboardButton("မ", callback_data="author_မ"), 
                InlineKeyboardButton("ယ", callback_data="author_ယ")
            ],
            [
                InlineKeyboardButton("ရ", callback_data="author_ရ"),
                InlineKeyboardButton("လ", callback_data="author_လ"),
                InlineKeyboardButton("ဝ", callback_data="author_ဝ"),
                InlineKeyboardButton("သ", callback_data="author_သ"),
                InlineKeyboardButton("ဟ", callback_data="author_ဟ")
            ],
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
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Start polling
    print("🚀 Oscar's Library Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()        "author_စ": "https://t.me/oscarhelpservices/16",
        "author_ဆ": "https://t.me/oscarhelpservices/18",
        "author_ဇ": "https://t.me/oscarhelpservices/20",
        "author_ည": "https://t.me/oscarhelpservices/23",
        "author_ဋ္ဌ": "https://t.me/oscarhelpservices/25",
        "author_တ": "https://t.me/oscarhelpservices/27",
        "author_ထ": "https://t.me/oscarhelpservices/33",
        "author_ဒ": "https://t.me/oscarhelpservices/35",
        "author_ဓ": "https://t.me/oscarhelpservices/37",
        "author_န": "https://t.me/oscarhelpservices/39",
        "author_ပ": "https://t.me/oscarhelpservices/41",
        "author_ဖ": "https://t.me/oscarhelpservices/43",
        "author_ဗ": "https://t.me/oscarhelpservices/45",
        "author_ဘ": "https://t.me/oscarhelpservices/47",
        "author_မ": "https://t.me/oscarhelpservices/49",
        "author_ယ": "https://t.me/oscarhelpservices/51",
        "author_ရ": "https://t.me/oscarhelpservices/53",
        "author_လ": "https://t.me/oscarhelpservices/55",
        "author_ဝ": "https://t.me/oscarhelpservices/57",
        "author_သ": "https://t.me/oscarhelpservices/59",
        "author_ဟ": "https://t.me/oscarhelpservices/61",
        "author_အ": "https://t.me/oscarhelpservices/30",
        "author_ဥသြဧ": "https://t.me/oscarhelpservices/10",
        "author_Eng": "https://t.me/sharebykosoemoe/920"
    }
    
    if callback_data in author_url_mappings:
        url = author_url_mappings[callback_data]
        # Directly open the URL without showing message
        await query.edit_message_text(
            "လင့်ခ်သို့ ခေါ်ဆောင်သွားပါမည်...",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("လင့်ခ်ကိုဖွင့်ရန် ဤနေရာကိုနှိပ်ပါ", url=url)
            ]])
        )
    
    elif callback_data == "author_menu":
        # Author menu with your specified layout - 6 rows
        author_keyboard = [
            # Row 1: 5 buttons
            [
                InlineKeyboardButton("က", callback_data="author_က"),
                InlineKeyboardButton("ခ", callback_data="author_ခ"),
                InlineKeyboardButton("ဂ", callback_data="author_ဂ"),
                InlineKeyboardButton("င", callback_data="author_င"),
                InlineKeyboardButton("စ", callback_data="author_စ")
            ],
            # Row 2: 5 buttons
            [
                InlineKeyboardButton("ဆ", callback_data="author_ဆ"),
                InlineKeyboardButton("ဇ", callback_data="author_ဇ"),
                InlineKeyboardButton("ည", callback_data="author_ည"),
                InlineKeyboardButton("ဋ္ဌ", callback_data="author_ဋ္ဌ"),
                InlineKeyboardButton("တ", callback_data="author_တ")
            ],
            # Row 3: 5 buttons
            [
                InlineKeyboardButton("ထ", callback_data="author_ထ"),
                InlineKeyboardButton("ဒ", callback_data="author_ဒ"),
                InlineKeyboardButton("ဓ", callback_data="author_ဓ"),
                InlineKeyboardButton("န", callback_data="author_န"),
                InlineKeyboardButton("ပ", callback_data="author_ပ")
            ],
            # Row 4: 5 buttons
            [
                InlineKeyboardButton("ဖ", callback_data="author_ဖ"),
                InlineKeyboardButton("ဗ", callback_data="author_ဗ"),
                InlineKeyboardButton("ဘ", callback_data="author_ဘ"),
                InlineKeyboardButton("မ", callback_data="author_မ"),
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
