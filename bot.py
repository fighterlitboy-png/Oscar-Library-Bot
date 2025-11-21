import os
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import requests
import sys


# ===============================
#  BOT TOKEN & URL
# ===============================
BOT_TOKEN = "7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4"
WEBHOOK_URL = "https://oscar-library-bot.onrender.com/" + BOT_TOKEN
PING_URL = "https://oscar-library-bot.onrender.com"  # Render free plan idle timeout မဖြစ်အောင် ping

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ===============================
#  RENDER BURMESE FONT FIX
# ===============================
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# ===============================
#  KEEP-ALIVE PING THREAD
# ===============================
def keep_alive():
    while True:
        try:
            requests.get(PING_URL, timeout=10)
        except:
            pass
        time.sleep(60)

threading.Thread(target=keep_alive, daemon=True).start()


# =====================================================
#  GROUP WELCOME MESSAGE + LOGO + AUTO MENTION
# =====================================================
WELCOME_LOGO = "/mnt/data/photo_2025-10-13_19-11-04.jpg"

WELCOME_TEXT = """
<b>🎉 Oscar's Library Group မှ နွေးထွေးစွာကြိုဆိုပါတယ် ❤️</b>

<b>{username} 🥰</b>

စာအုပ်များက မင်းရဲ့စာဖတ်ခရီးကို
အတူလိုက်ပြီး ကြင်နာစွာနဲ့ 
လမ်းညွှန်ပေးဖို့ အမြဲရှိနေတယ်…🥰

မင်းစိတ်ကူးထဲက စာအုပ်တွေ၊ 
မင်းဖတ်ချင်တဲ့ ဝတ္ထုတွေကို 
အတူရှာကြမယ်…📚🤓

မင်းစာဖတ်သံ ကြားရဖို့…🫠
မင်းစာသားတွေဖတ်ရင် ပြုံးလာမယ့် 
မျက်နှာလေး မြင်ရဖို့…😍

✨📚 စာအုပ်ရွေးဖို့ ဒီကိုနှိပ်ပါ👇📚✨
<a href="https://t.me/oscar_libray_bot">📚 Oscar Library Bot</a>
"""


@bot.message_handler(content_types=['new_chat_members'])
def welcome_group_member(message):
    for user in message.new_chat_members:
        username = user.first_name or "Friend"
        text = WELCOME_TEXT.format(username=username)

        with open(WELCOME_LOGO, "rb") as img:
            bot.send_photo(message.chat.id, img, caption=text)



# =====================================================
#  LINK BLOCKER (GROUP ONLY)
# =====================================================
FORBIDDEN = ["http://", "https://", "t.me/", ".com", ".org"]

BLOCK_WARNING = """
⚠️ Username ရေ Link 🔗 ပို့တာကို ပိတ်ထားပါတယ် 🙅🏻

အရေးကြီးတာ ဆိုရင် Owner ကို ဆက်သွယ်ပါနော်…
"""


@bot.message_handler(content_types=['text'])
def block_links(message):
    # Private chat မပိတ်
    if message.chat.type not in ["group", "supergroup"]:
        return

    txt = message.text.lower()

    if any(x in txt for x in FORBIDDEN):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, BLOCK_WARNING)
        except:
            pass



# =====================================================
#  /START MESSAGE (PRIVATE FEATURE)
# =====================================================
@bot.message_handler(commands=['start'])
def start_message(message):
    first = message.from_user.first_name or "Friend"

    text = f"""သာယာသောနေလေးဖြစ်ပါစေ... 
    <b>{first}</b> 🥰
    
🌼 <b>Oscar's Library</b> 🌼 မှ ကြိုဆိုပါတယ်

စာအုပ်များရှာဖွေရန် လမ်းညွှန်ပေးမယ်...

<b>📚 ကဏ္ဍအလိုက် / ✍️ စာရေးဆရာအလိုက်</b> ရွေးနိုင်ပါတယ်။

⚠️ အဆင်မပြေတာရှိရင် ‘အထွေထွေမေးမြန်းရန်’ ကိုနှိပ်ပါ။
"""

    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("📚 ကဏ္ဍအလိုက်", callback_data="category"),
        types.InlineKeyboardButton("✍️ စာရေးဆရာ", callback_data="author_menu")
    )
    kb.row(types.InlineKeyboardButton("📖 စာအုပ်ဖတ်နည်း", url="https://t.me/oscarhelpservices/17"))
    kb.row(types.InlineKeyboardButton("🌼 ချန်နယ်ခွဲများ", url="https://t.me/oscarhelpservices/9"))
    kb.row(types.InlineKeyboardButton("⭐ Review ရေးရန်", url="https://t.me/sharebykosoemoe/13498"))
    kb.row(types.InlineKeyboardButton("📝 စာအုပ်ပြုပြင်ရန်", url="https://t.me/oscarhelpservices/29?single"))
    kb.row(types.InlineKeyboardButton("❓ အထွေထွေမေးမြန်းရန်", url="https://t.me/kogyisoemoe"))

    bot.send_message(message.chat.id, text, reply_markup=kb)



# =====================================================
# CATEGORY REDIRECT
# =====================================================
@bot.callback_query_handler(func=lambda c: c.data == "category")
def category_redirect(call):
    bot.send_message(
        call.message.chat.id,
        "📚 <b>ကဏ္ဍအလိုက် စာအုပ်များ</b>\n"
        "https://t.me/oscarhelpservices/4\n\n"
        "🌼 Oscar's Library 🌼"
    )



# =====================================================
# AUTHORS MAIN MENU
# =====================================================
@bot.callback_query_handler(func=lambda c: c.data == "author_menu")
def author_menu(call):
    text = "✍️ <b>စာရေးဆရာနာမည် 'အစ' စာလုံးရွေးပါ</b>\n\n🌼 Oscar's Library 🌼"

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

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)



# =====================================================
# AUTHOR LINK REDIRECTS
# =====================================================
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
    "မ": "https://t.me/oscarhelpservices/58",
    "ယ": "https://t.me/oscarhelpservices/59",
    "ရ": "https://t.me/oscarhelpservices/61",
    "လ": "https://t.me/oscarhelpservices/63",
    "ဝ": "https://t.me/oscarhelpservices/65",
    "သ": "https://t.me/oscarhelpservices/67",
    "ဟ": "https://t.me/oscarhelpservices/69",
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
            f"➡️ <b>{key}</b> ဖြင့်စသောစာရေးဆရာများ\n{url}\n\n🌼 Oscar's Library 🌼"
        )



# =====================================================
#  FLASK WEBHOOK SERVER
# =====================================================
app = Flask(__name__)

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)


@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    json_data = request.get_json(force=True)
    if json_data:
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
    return "OK", 200


@app.route("/", methods=['GET'])
def index():
    return "Bot is running…", 200


# =====================================================
#  RUN FLASK SERVER
# =====================================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
