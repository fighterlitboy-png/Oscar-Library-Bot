from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Bot Token - Render environment variable မှသတ်မှတ်မည်
BOT_TOKEN = os.getenv('BOT_TOKEN', '7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    welcome_text = f"""
မင်္ဂလာပါ {user.first_name} 🥰
<b>🌼 Oscar's Library 🌼 မှကြိုဆိုပါတယ်</b>
စာအုပ်များရှာဖွေရန်လမ်းညွှန်ပေးမယ်...

<b>စာအုပ်ရှာဖို့ နှစ်ပိုင်းခွဲထားတယ်</b>
<b>ကဏ္ဍအလိုက် နှင့် စာရေးဆရာ ဖြစ်ပါတယ်</b>
<b>Fic၊ ကာတွန်း၊ သည်းထိပ်ရင်ဖို စသည့်ကဏ္ဍများဖြင့်သွားရန် ကဏ္ဍအလိုက်ကိုရွေးပါ။ စာရေးဆရာဖြင့်ရှာချင်ရင် စာရေးဆရာ ကိုရွေးပေးပါ။</b>

💢စာအုပ်ဖတ်နည်းကိုအရင်ကြည့်ပါရန်
⚠️ အဆင်မပြေမှုများရှိပါက အထွေထွေမေးမြန်းရန်ကိုနှိပ်ပြီးမေးမြန်းနိုင်ပါသည်။
    """
    
    # Main Menu Keyboard
    keyboard = [
        [
            InlineKeyboardButton("ကဏ္ဍအလိုက်", url="https://t.me/oscarhelpservices/4"),
            InlineKeyboardButton("စာရေးဆရာ", callback_data="author_menu"),
            InlineKeyboardButton("စာအုပ်ဖတ်နည်း", url="https://t.me/oscarhelpservices/17")
        ],
        [
            InlineKeyboardButton("ချန်နယ်ခွဲများ", url="https://t.me/oscarhelpservices/9"),
            InlineKeyboardButton("Review ရေးရန်", url="https://t.me/sharebykosoemoe/13498"),
            InlineKeyboardButton("စာအုပ်ပြုပြင်ရန်", url="https://t.me/oscarhelpservices/29?single"),
            InlineKeyboardButton("အထွေထွေမေးမြန်ရန်", url="https://t.me/kogyisoemoe")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='HTML')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks"""
    query = update.callback_query
    await query.answer()
    
    # Author buttons URL mapping
    author_urls = {
        "author_က": "https://t.me/oscarhelpservices/5",
        "author_ခ": "https://t.me/oscarhelpservices/7", 
        "author_ဂ": "https://t.me/oscarhelpservices/12",
        "author_င": "https://t.me/oscarhelpservices/14",
        "author_စ": "https://t.me/oscarhelpservices/16",
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
    
    if query.data in author_urls:
        # Direct URL opening for author buttons
        url = author_urls[query.data]
        await query.edit_message_text(
            "လင့်ခ်သို့ ခေါ်ဆောင်သွားပါမည်...",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("လင့်ခ်ကိုဖွင့်ရန် ဤနေရာကိုနှိပ်ပါ", url=url)
            ]])
        )
    
    elif query.data == "author_menu":
        # Author selection menu
        author_keyboard = [
            [
                InlineKeyboardButton("က", callback_data="author_က"),
                InlineKeyboardButton("ခ", callback_data="author_ခ"), 
                InlineKeyboardButton("ဂ", callback_data="author_ဂ"),
                InlineKeyboardButton("င", callback_data="author_င"),
                InlineKeyboardButton("စ", callback_data="author_စ")
            ],
            [
                InlineKeyboardButton("ဆ", callback_data="author_ဆ"),
                InlineKeyboardButton("ဇ", callback_data="author_ဇ"),
                InlineKeyboardButton("ည", callback_data="author_ည"),
                InlineKeyboardButton("ဋ္ဌ", callback_data="author_ဋ္ဌ"),
                InlineKeyboardButton("တ", callback_data="author_တ")
            ],
            [
                InlineKeyboardButton("ထ", callback_data="author_ထ"),
                InlineKeyboardButton("ဒ", callback_data="author_ဒ"),
                InlineKeyboardButton("ဓ", callback_data="author_ဓ"),
                InlineKeyboardButton("န", callback_data="author_န"),
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
