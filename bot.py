import telebot
from telebot import types
import threading
import time
import requests
import sys

# ===============================
#  BOT TOKEN
# ===============================
BOT_TOKEN = "7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4"
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ===============================
#  RENDER BURMESE FONT FIX
# ===============================
sys.stdout.reconfigure(encoding='utf-8')


# ===============================
#  UPTIME KEEP-ALIVE PING (Wookhood)
# ===============================
PING_URL = "https://your-render-service.onrender.com"

def keep_alive():
    while True:
        try:
            requests.get(PING_URL, timeout=10)
        except:
            pass
        time.sleep(60)

threading.Thread(target=keep_alive, daemon=True).start()


# ===============================
#  /START MESSAGE
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
    first = message.from_user.first_name or "Friend"

    text = (
        f"မင်္ဂလာပါ **{first}** 🥰\n"
        f"🌼 **Oscar's Library** 🌼 မှ ကြိုဆိုပါတယ်\n\n"
        "စာအုပ်များရှာဖွေရန် လမ်းညွှန်ပေးမယ်...\n\n"
        "**(စာအုပ်ရှာဖို့ နှစ်ပိုင်း — ကဏ္ဍအလိုက် / စာရေးဆရာအလိုက်)**\n\n"
        "Fic၊ ကာတွန်း၊ သည်းထိပ်ရင်ဖို စသည့်ကဏ္ဍများသွားချင်ရင် **ကဏ္ဍအလိုက်** ကိုနှိပ်ပါ။\n\n"
        "စာရေးဆရာအလိုက်ရှာချင်ရင် **စာရေးဆရာ** ကိုနှိပ်ပါ။\n\n"
        "💢 **စာအုပ်ဖတ်နည်းကြည့်ပါရန်** 💢\n\n"
        "⚠️ မေးချင်တာရှိရင် ⚠️\n\n"
        **အထွေထွေမေးမြန်းရန်**\n\n"
        ကိုနှိပ်နိုင်ပါတယ်။\n\n"
        
    )

    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("📚 ကဏ္ဍအလိုက်", callback_data="category"),
        types.InlineKeyboardButton("✍️ စာရေးဆရာ", callback_data="author_menu")
    )
    kb.row(types.InlineKeyboardButton("📖 စာအုပ်ဖတ်နည်း", url="https://t.me/oscarhelpservices/17"))
    kb.row(types.InlineKeyboardButton("📺 ချန်နယ်ခွဲများ", url="https://t.me/oscarhelpservices/9"))
    kb.row(types.InlineKeyboardButton("⭐ Review ရေးရန်", url="https://t.me/sharebykosoemoe/13498"))
    kb.row(types.InlineKeyboardButton("📝 စာအုပ်ပြုပြင်ရန်", url="https://t.me/oscarhelpservices/29?single"))
    kb.row(types.InlineKeyboardButton("❓ အထွေထွေမေးမြန်းရန်", url="https://t.me/kogyisoemoe"))

    bot.send_message(message.chat.id, text, reply_markup=kb)


# ===============================
#  CATEGORY REDIRECT
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "category")
def category_redirect(call):
    bot.send_message(
        call.message.chat.id,
        "📚 **ကဏ္ဍအလိုက် စာအုပ်များ**\n"
        "https://t.me/oscarhelpservices/4\n\n"
        "🌼 Oscar's Library 🌼"
    )


# ===============================
#  AUTHORS MAIN MENU
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "author_menu")
def author_menu(call):
    text = "✍️ **စာရေးဆရာနာမည် အစစာလုံးရွေးပါ**\n\n🌼 Oscar's Library 🌼"

    rows = [
        ["က","ခ","ဂ","င"],
        ["စ","ဆ","ဇ","ည"],
        ["ဋ္ဌ","တ","ထ","ဒ"],
        ["ဓ","န","ပ","ဖ"],
        ["ဗ","ဘ","မ","ယ"],
        ["ရ","လ","ဝ","သ"],
        ["ဟ","အ","ဥ","Eng"]
    ]

    kb = types.InlineKeyboardMarkup()

    for r in rows:
        kb.row(*[types.InlineKeyboardButton(x, callback_data=f"author_{x}") for x in r])

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )


# ===============================
#  AUTHOR LINK REDIRECTS
# ===============================
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
    "ဥ": "https://t.me/oscarhelpservices/10",
    "Eng": "https://t.me/sharebykosoemoe/920"
}

@bot.callback_query_handler(func=lambda c: c.data.startswith("author_"))
def author_redirect(call):
    key = call.data.replace("author_", "")
    url = AUTHOR_LINKS.get(key)

    if url:
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"➡️ **{key} စာရေးဆရာများ**\n{url}\n\n🌼 Oscar's Library 🌼"
        )


# ===============================
#  BOT LOOP
# ===============================
print("Bot is running…")
bot.infinity_polling(skip_pending=True)
