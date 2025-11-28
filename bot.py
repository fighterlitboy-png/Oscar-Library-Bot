import os
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import requests
import sys
from datetime import datetime
import pytz
import io

# ===============================
# BOT TOKEN & URL
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
# 2️⃣ LINK BLOCKER (GROUP ONLY)
# ======================================================
def is_link(text):
    if not text:
        return False
    return any(x in text.lower() for x in ["http://", "https://", "www.", "t.me/", "telegram.me/", ".com"])

def has_link_api(message):
    try:
        if message.text and is_link(message.text):
            return True
    except:
        pass
    try:
        if message.caption and is_link(message.caption):
            return True
    except:
        pass
    try:
        ents = getattr(message, "entities", None)
        if ents:
            for e in ents:
                if e.type in ["url", "text_link"]:
                    return True
    except:
        pass
    try:
        cent = getattr(message, "caption_entities", None)
        if cent:
            for e in cent:
                if e.type in ["url", "text_link"]:
                    return True
    except:
        pass
    if message.forward_from or message.forward_from_chat:
        try:
            if message.text and is_link(message.text):
                return True
        except:
            pass
        try:
            if message.caption and is_link(message.caption):
                return True
        except:
            pass
    return False

def is_admin(chat_id, user_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in admins]
        return user_id in admin_ids
    except Exception as e:
        print(f"Admin check error: {e}")
        return False

@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
def handle_group_messages(message):
    if message.text and message.text.startswith('/'):
        return
    if message.new_chat_members:
        return
    if has_link_api(message):
        if not is_admin(message.chat.id, message.from_user.id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
                warning_msg = f"⚠️ {message.from_user.first_name} 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်..."
                bot.send_message(message.chat.id, warning_msg)
            except Exception as e:
                print(f"Link blocker error: {e}")

# ===============================
# /START MESSAGE
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
❓အထွေထွေမေးမြန်းရန်** ကိုနှိပ်ပါ။"""
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

# ===============================
# CATEGORY & AUTHOR MENU (unchanged)
# ===============================
# ... (ထည့်ထားတဲ့ code အားလုံးကို 그대로 အလုပ်လုပ်အောင်ထားပါ)

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
    # Webhook retry loop
    while True:
        try:
            bot.remove_webhook()
            bot.set_webhook(url=WEBHOOK_URL)
            print("Webhook set successfully!")
            break
        except telebot.apihelper.ApiTelegramException as e:
            if "429" in str(e):
                print("Too many requests, retrying in 2 seconds...")
                time.sleep(2)
            else:
                raise e

    # ===============================
    # Birthday Post /showbirthday
    # ===============================
    BIRTHDAY_CHANNEL = -1002150199369
    BIRTHDAY_PHOTO_RAW = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/Happy_Birthday_Photo.jpg"
    yangon_tz = pytz.timezone("Asia/Yangon")

    def get_today_date():
        now = datetime.now(yangon_tz)
        return now.strftime("%B %d").replace(" 0", " ")

    def generate_birthday_text():
        today = get_today_date()
        return f"""* Birthday Wishes 💌  
...
🌼 Oscar's Library 🌼 *"""

    def fetch_image_bytes(url):
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            return io.BytesIO(r.content)
        except Exception as e:
            print(f"Image download error: {e}")
            return None

    def post_birthday_to_channel():
        try:
            img = fetch_image_bytes(BIRTHDAY_PHOTO_RAW)
            if img:
                img.name = "birthday.jpg"
                bot.send_photo(
                    BIRTHDAY_CHANNEL,
                    img,
                    caption=generate_birthday_text(),
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(
                    BIRTHDAY_CHANNEL,
                    generate_birthday_text(),
                    parse_mode="Markdown"
                )
            print("Birthday posted.")
        except Exception as e:
            print("Birthday post error:", e)

    def schedule_daily_birthday(hour=8, minute=0):
        last_post_date = None
        while True:
            now = datetime.now(yangon_tz)
            today = now.date()
            if now.hour == hour and now.minute == minute:
                if last_post_date != today:
                    post_birthday_to_channel()
                    last_post_date = today
                    time.sleep(61)
            time.sleep(5)

    threading.Thread(target=schedule_daily_birthday, daemon=True).start()

    @bot.message_handler(commands=['showbirthday'])
    def cmd_showbirthday(message):
        try:
            img = fetch_image_bytes(BIRTHDAY_PHOTO_RAW)
            if img:
                img.name = "birthday.jpg"
                bot.send_photo(
                    message.chat.id,
                    img,
                    caption=generate_birthday_text(),
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(message.chat.id, generate_birthday_text(), parse_mode="Markdown")

            try:
                bot.reply_to(message, "🎉 Birthday post sent!")
            except:
                pass
        except Exception as e:
            bot.send_message(message.chat.id, f"Error: {e}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
