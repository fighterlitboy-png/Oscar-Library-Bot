import os
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import requests
from datetime import datetime, timedelta

# ===============================
# BOT TOKEN & URL
# ===============================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4')
WEBHOOK_URL = "https://oscar-library-bot.onrender.com/" + BOT_TOKEN
PING_URL = "https://oscar-library-bot.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ===============================
# CHANNEL CONFIGURATION
# ===============================
YOUR_CHANNEL_ID = "@bookbykosoemoe"  # သင့် channel username

# ===============================
# BIRTHDAY CONFIGURATION
# ===============================
BIRTHDAY_CHANNEL_ID = "1002150199369"
BIRTHDAY_PHOTO_URL = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/Happy_Birthday_Photo.jpg"
WELCOME_PHOTO_URL = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/welcome_photo.jpg"

# ===============================
# TOP FANS STORAGE
# ===============================
user_message_count = {}
user_reaction_count = {}
user_names = {}
tracking_start_time = datetime.now()

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

# ===============================
# BIRTHDAY POST
# ===============================
def get_current_date_str():
    now = datetime.now()
    month = now.strftime("%B")
    day = now.day
    return f"{month}, {day}"

def create_birthday_message_text():
    current_date = get_current_date_str()
    message = f"""<b>Birthday Wishes 💌🎈</b>

<b>Happy Birthday ❤️ ကမ္ဘာ❣️
ပျော်ရွှင်စရာမွေးနေ့လေးဖြစ်ပါစေ..🎂</b>

<b>{current_date} မွေးနေ့ရှင်လေးများ 
နောင်နှစ်ပေါင်းများစွာတိုင်အောင်...💙</b>

ကိုယ်၏ကျန်းမာခြင်း စိတ်၏ချမ်းသာခြင်းများနဲ့ပြည့်စုံပြီး လိုအင်ဆန္ဒများလည်းပြည့်ဝပါစေ...🥰

ဘ၀ခရီးကို မပူမပင်မကြောင့်ကြစေရပဲ အေးအေးချမ်းချမ်း ဖြတ်သန်းသွားနိုင်ပါစေ...💞

ချစ်ရတဲ့ မိသားစုနဲ့အတူပျော်ရွှင်ရောနေ့ရက်တွေကို ထာဝရ ပိုင်ဆိုင်နိုင်ပါစေ 
လို့ ဆုတောင်းပေးပါတယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊

<b>🌼 Oscar's Library 🌼</b>

#adminteam"""
    return message

def birthday_worker():
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:
            try:
                caption = create_birthday_message_text()
                bot.send_photo(chat_id=BIRTHDAY_CHANNEL_ID, photo=BIRTHDAY_PHOTO_URL, caption=caption)
                print(f"✅ Birthday sent - {datetime.now()}")
            except Exception as e:
                print(f"❌ Birthday error - {e}")
            time.sleep(61)
        else:
            time.sleep(20)

threading.Thread(target=birthday_worker, daemon=True).start()

# ===============================
# TOP FANS SYSTEM
# ===============================
def track_user_activity(message):
    try:
        user_id = message.from_user.id
        user_message_count[user_id] = user_message_count.get(user_id, 0) + 1
        username = getattr(message.from_user, "username", None)
        first_name = message.from_user.first_name or "User"
        user_names[user_id] = f"@{username}" if username else first_name
    except Exception as e:
        print(f"❌ Tracking error: {e}")

def get_top_fans_list():
    try:
        user_scores = {}
        for user_id in set(list(user_message_count.keys()) + list(user_reaction_count.keys())):
            message_score = user_message_count.get(user_id, 0)
            reaction_score = user_reaction_count.get(user_id, 0)
            user_scores[user_id] = message_score + (reaction_score * 2)
        all_top_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        final_top_20 = all_top_users[:20]
        return final_top_20
    except Exception as e:
        print(f"❌ Error getting top fans: {e}")
        return []

def create_top_fans_post():
    try:
        top_users = get_top_fans_list()
        if not top_users:
            return "<b>🏆 အပတ်စဉ် Top Fans များ 🏆</b>\n\nဒီအပတ်အတွင်း မှတ်တမ်းရှိသူမရှိသေးပါ..."
        post = "<b>🏆 အပတ်စဉ် Top Fans 🏆</b>\n\n"
        post += "ဒီအပတ်အတွင်းကျွန်တော်တို့ချန်နယ်ကို အပြင်းအထန် အားပေးမှုအများဆုံး Member များကိုရွေးချယ်လိုက်ပါပြီ...!\n\n"
        gold_titles = ["👑 Channel King", "⭐ Super Star", "🔥 Fire Reactor", "💬 Chat Champion", "🎯 Most Active"]
        post += "<b>🥇 GOLD Tier (Top 1-5)</b>\n"
        for i, (user_id, score) in enumerate(top_users[:5], 1):
            username = user_names.get(user_id, f"User_{user_id}")
            title = gold_titles[i-1] if i-1 < len(gold_titles) else "⭐ Top Fan"
            post += f"{i}. {username} {title} - Score: {score}\n"
        post += "\n<b>🥈 SILVER Tier (Top 6-15)</b>\n"
        silver_titles = ["✨ Rising Star", "💫 Active Member", "🌟 Community Hero", "🚀 Engagement Star", "💝 Supporter", 
                        "👍 Top Fan", "🔥 React Master", "💬 Conversation Starter", "⭐ Future Star", "🌈 Community Builder"]
        for i, (user_id, score) in enumerate(top_users[5:15], 6):
            username = user_names.get(user_id, f"User_{user_id}")
            title = silver_titles[i-6] if i-6 < len(silver_titles) else "🌟 Star"
            post += f"{i}. {username} {title} - Score: {score}\n"
        post += "\n<b>🥉 BRONZE Tier (Top 16-20)</b>\n"
        bronze_titles = ["🎉 Celebration Star", "💎 Diamond Member", "🌟 Shining Star", "🚀 Rocket Booster", "💖 Heart Giver"]
        for i, (user_id, score) in enumerate(top_users[15:20], 16):
            username = user_names.get(user_id, f"User_{user_id}")
            title = bronze_titles[i-16] if i-16 < len(bronze_titles) else "🌟 Member"
            post += f"{i}. {username} {title} - Score: {score}\n"
        post += "\n💫 နောက်အပတ်မှာ Top Fan ဘယ်သူတွေဖြစ်မလဲ...\nဒီအပတ် ပါဝင်သူတစ်ယောက်စီကို အထူးကျေးဇူးတင်ရှိပါတယ်!"
        return post
    except Exception as e:
        print(f"❌ Error creating top fans post: {e}")
        return "<b>❌ Top Fans list error</b>"

def top_fans_worker():
    while True:
        now = datetime.now()
        days_until_sunday = (6 - now.weekday()) % 7
        next_sunday_1759 = (now + timedelta(days=days_until_sunday)).replace(hour=17, minute=59, second=0, microsecond=0)
        if next_sunday_1759 <= now:
            next_sunday_1759 += timedelta(days=7)
        wait_seconds = (next_sunday_1759 - now).total_seconds()
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        try:
            time.sleep(61)
            top_fans_post = create_top_fans_post()
            bot.send_message(chat_id=YOUR_CHANNEL_ID, text=top_fans_post)
            user_message_count.clear()
            user_reaction_count.clear()
            user_names.clear()
            global tracking_start_time
            tracking_start_time = datetime.now()
        except Exception as e:
            print(f"❌ Weekly top fans error: {e}")
        time.sleep(5)

threading.Thread(target=top_fans_worker, daemon=True).start()

# ===============================
# WELCOME SYSTEM
# ===============================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for user in message.new_chat_members:
        caption = f"နွေးထွေးစွာကြိုဆိုပါတယ်...🧸 {user.first_name} ...🥰"
        kb = types.InlineKeyboardMarkup()
        kb.row(types.InlineKeyboardButton("စာပေချစ်သူများအတြက္", url="https://t.me/oscar_libray_bot"))
        try:
            bot.send_photo(message.chat.id, photo=WELCOME_PHOTO_URL, caption=caption, reply_markup=kb)
        except Exception:
            bot.send_message(message.chat.id, caption, reply_markup=kb)

# ===============================
# LINK BLOCKER
# ===============================
def is_link(text):
    if not text:
        return False
    return any(x in text.lower() for x in ["http://", "https://", "www.", "t.me/", "telegram.me/"])

def has_link_api(message):
    if getattr(message, "text", None) and is_link(message.text):
        return True
    if getattr(message, "caption", None) and is_link(message.caption):
        return True
    return False

def is_admin(chat_id, user_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        return user_id in [admin.user.id for admin in admins]
    except:
        return False

@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"], content_types=['text', 'photo', 'video', 'document'])
def handle_group_messages(message):
    if has_link_api(message) and not is_admin(message.chat.id, message.from_user.id):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            user_first_name = message.from_user.first_name
            user_id = message.from_user.id
            warning_msg = f'⚠️ <a href="tg://user?id={user_id}">{user_first_name}</a> 💢 Link🔗 ပိတ်ထားပါတယ် 🙅🏻'
            bot.send_message(message.chat.id, warning_msg, parse_mode='HTML')
        except Exception as e:
            print(f"Link blocker error: {e}")

# ===============================
# /START COMMAND
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
    first = message.from_user.first_name or "Friend"
    text = f"သာယာသောနေ့လေးဖြစ်ပါစေ...🌸 {first} ...🥰"
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton("📚 ကဏ္ဍအလိုက်", callback_data="category"),
           types.InlineKeyboardButton("✍️ စာရေးဆရာ", callback_data="author_menu"))
    bot.send_message(message.chat.id, text, reply_markup=kb)

# ===============================
# CATEGORY & AUTHOR CALLBACKS
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "category")
def category_redirect(call):
    bot.send_message(call.message.chat.id, "📚 ကဏ္ဍအလိုက် စာအုပ်များ\nhttps://t.me/oscarhelpservices/4")

@bot.callback_query_handler(func=lambda c: c.data == "author_menu")
def author_menu(call):
    text = "✍️ စာရေးဆရာနာမည် 'အစ' စာလုံးရွေးပါ"
    rows = [["က","ခ","ဂ","င"], ["စ","ဆ","ဇ","ည"], ["ဋ္ဌ","တ","ထ","ဒ"], ["ဓ","န","ပ","ဖ"], ["ဗ","ဘ","မ","ယ"], ["ရ","လ","ဝ","သ"], ["ဟ","အ","ဥ","Eng"]]
    kb = types.InlineKeyboardMarkup()
    for r in rows:
        kb.row(*[types.InlineKeyboardButton(x, callback_data=f"author_{x}") for x in r])
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)
    except Exception:
        bot.send_message(call.message.chat.id, text, reply_markup=kb)

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
        bot.send_message(call.message.chat.id, f"➡️ {key} ဖြင့်စသောစာရေးဆရာများ\n{url}")

# ===============================
# RUN FLASK WEBHOOK
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
