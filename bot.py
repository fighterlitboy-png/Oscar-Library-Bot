import os
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import requests
import sys

# ===============================
# BOT TOKEN & URL (Environment Variables)
# ===============================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4')
WEBHOOK_URL = "https://oscar-library-bot.onrender.com/" + BOT_TOKEN
PING_URL = "https://oscar-library-bot.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ===============================
# RENDER FONT FIX
# ===============================
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# ===============================
# KEEP ALIVE
# ===============================
def keep_alive():
    while True:
        try:
            requests.get(PING_URL, timeout=10)
        except:
            pass
        time.sleep(60)

threading.Thread(target=keep_alive, daemon=True).start()

# ======================================================
# 1️⃣ GROUP WELCOME SYSTEM
# ======================================================
WELCOME_IMAGE = "welcome_photo.jpg"

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for user in message.new_chat_members:
        caption = f"""နွေးထွေးစွာကြိုဆိုပါတယ်...🧸
{user.first_name} ...🥰

📚 Oscar's Library မှ
မင်းရဲ့စာဖတ်ခြင်းအတွက် 
အမြဲအသင့်ရှိပါတယ်...🤓

✨📚 မင်းကြိုက်တဲ့စာအုပ်တွေ 
🗃️ ရွေးဖတ်ဖို့ Button ကိုနှိပ်ပါ ✨"""
        
        # Button ထည့်ရန်
        welcome_kb = types.InlineKeyboardMarkup()
        welcome_kb.row(
            types.InlineKeyboardButton(
                "စာပေချစ်သူများအတွက်", 
                url="https://t.me/oscar_libray_bot"
            )
        )
        
        try:
            with open(WELCOME_IMAGE, "rb") as img:
                bot.send_photo(
                    message.chat.id, 
                    img, 
                    caption=caption,
                    reply_markup=welcome_kb
                )
        except Exception as e:
            print(f"Welcome image error: {e}")
            bot.send_message(
                message.chat.id,
                caption,
                reply_markup=welcome_kb
            )

# ======================================================
# 2️⃣ LINK BLOCKER (GROUP ONLY) - FIXED ADMIN CHECK
# ======================================================
def is_link(text):
    if not text:
        return False
    return any(x in text.lower() for x in ["http://", "https://", "www.", "t.me/", "telegram.me/", ".com"])

def is_admin(chat_id, user_id):
    """Check if user is admin in the group"""
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in admins]
        return user_id in admin_ids
    except Exception as e:
        print(f"Admin check error: {e}")
        return False

@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
def handle_group_messages(message):
    """Handle all group messages including forwarded ones"""
    
    # Skip if it's a command or new chat members
    if message.text and message.text.startswith('/'):
        return
    if message.new_chat_members:
        return
    
    # Check if message contains text (original or forwarded)
    message_text = ""
    
    # Get text from original message
    if message.text:
        message_text = message.text
    # Get text from forwarded message
    elif message.forward_from_chat or message.forward_from:
        if message.caption:  # For media messages with caption
            message_text = message.caption
    
    # If message contains links and user is not admin, block it
    if message_text and is_link(message_text):
        if not is_admin(message.chat.id, message.from_user.id):
            try:
                # Delete the message with link
                bot.delete_message(message.chat.id, message.message_id)
                
                # Send warning message
                warning_msg = f"⚠️ {message.from_user.first_name} 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်..."
                bot.send_message(message.chat.id, warning_msg)
                
            except Exception as e:
                print(f"Link blocker error: {e}")

# ===============================
# /START MESSAGE - FIXED
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
    first = message.from_user.first_name or "Friend"
    text = f"""သာယာသောနေ့လေးဖြစ်ပါစေ...🌸 **
    {first}** ...🥰
    
🌼 **Oscar's Library** 🌼 မှ ကြိုဆိုပါတယ်

စာအုပ်များရှာဖွေရန် လမ်းညွှန်ပေးမယ်...

**စာအုပ်ရှာဖို့ နှစ်ပိုင်းခွဲထားတယ် 
📚ကဏ္ဍအလိုက် 💠 ✍️စာရေးဆရာ**

Fic၊ ကာတွန်း၊ သည်းထိပ်ရင်ဖို 
စသည့်ကဏ္ဍများရှာဖတ်ချင်ရင် 
**📚ကဏ္ဍအလိုက်** ကိုနှိပ်ပါ။

စာရေးဆရာအလိုက်ရှာဖတ်ချင်ရင် 
**✍️စာရေးဆရာ** ကိုနှိပ်ပါ။

💢 **📖စာအုပ်ဖတ်နည်းကြည့်ပါရန်** 💢

⚠️ အဆင်မပြေတာရှိရင် ⚠️ **
❓အထွေထွေမေးမြန်းရန်** ကိုနှိပ်နိုင်ပါ။"""

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

# ======================================================
# 3️⃣ PRIVATE CHAT MESSAGE HANDLER - FIXED
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_private_messages(message):
    """Handle private messages including forwarded links"""
    
    # Skip if it's a command (already handled by start handler)
    if message.text and message.text.startswith('/'):
        return
    
    # Check for forwarded messages containing links
    if message.forward_from_chat or message.forward_from:
        # For forwarded messages with text
        if message.text and is_link(message.text):
            bot.send_message(
                message.chat.id, 
                f"🔗 Forwarded link detected:\n{message.text}\n\nI can see the forwarded link! ✅"
            )
        # For forwarded media messages with captions containing links
        elif message.caption and is_link(message.caption):
            bot.send_message(
                message.chat.id, 
                f"🔗 Forwarded media with link:\n{message.caption}\n\nI can see the forwarded link! ✅"
            )
        else:
            # Regular forwarded message without links
            bot.send_message(
                message.chat.id, 
                "📩 Forwarded message received!\n\n" +
                "Note: I can process links from forwarded messages in private chats."
            )
    # Regular text messages (not commands)
    elif message.text and not message.text.startswith('/'):
        if is_link(message.text):
            bot.send_message(
                message.chat.id, 
                f"🔗 Link detected:\n{message.text}\n\nThis is a direct link message! ✅"
            )
        else:
            bot.send_message(message.chat.id, f"🤖 Auto Reply:\n{message.text}")

# ===============================
# CATEGORY REDIRECT
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "category")
def category_redirect(call):
    bot.send_message(
        call.message.chat.id,
        "📚 **ကဏ္ဍအလိုက် စာအုပ်များ**\nhttps://t.me/oscarhelpservices/4\n\n🌼 Oscar's Library 🌼"
    )

# ===============================
# AUTHORS MENU
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "author_menu")
def author_menu(call):
    text = "✍️ **စာရေးဆရာနာမည် 'အစ' စာလုံးရွေးပါ**\n\n🌼 Oscar's Library 🌼"
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

# ===============================
# AUTHOR LINKS
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

# ===============================
# AUTHOR REDIRECT
# ===============================
@bot.callback_query_handler(func=lambda c: c.data.startswith("author_"))
def author_redirect(call):
    key = call.data.replace("author_", "")
    url = AUTHOR_LINKS.get(key)
    if url:
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"➡️ **{key} ဖြင့်စသောစာရေးဆရာများ**\n{url}\n\n🌼 Oscar's Library 🌼"
        )

# ===============================
# FLASK SERVER
# ===============================
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

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
