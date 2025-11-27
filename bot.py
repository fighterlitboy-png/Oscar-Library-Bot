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
# CHANNEL & IMAGE CONFIG
# ===============================
YOUR_CHANNEL_ID = "@bookbykosoemoe"
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
    return f"{now.strftime('%B')}, {now.day}"

def create_birthday_message_text():
    current_date = get_current_date_str()
    return f"<b>Birthday Wishes 💌🎈</b>\n\n<b>Happy Birthday ❤️</b>\n<b>{current_date} မွေးနေ့ရှင်များ💙</b>"

def birthday_worker():
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:
            try:
                bot.send_photo(BIRTHDAY_CHANNEL_ID, BIRTHDAY_PHOTO_URL, caption=create_birthday_message_text(), parse_mode='HTML')
            except Exception as e:
                print(f"Birthday send error: {e}")
            time.sleep(61)
        else:
            time.sleep(20)

threading.Thread(target=birthday_worker, daemon=True).start()

# ===============================
# TOP FANS LOGIC
# ===============================
def track_user_activity(message):
    try:
        user_id = message.from_user.id
        user_message_count[user_id] = user_message_count.get(user_id, 0) + 1
        username = getattr(message.from_user, "username", None)
        user_names[user_id] = f"@{username}" if username else message.from_user.first_name
    except:
        pass

def get_top_fans_list():
    try:
        # Auto remove users who left channel
        for user_id in list(user_message_count.keys()):
            try:
                status = bot.get_chat_member(YOUR_CHANNEL_ID, user_id).status
                if status in ["left", "kicked"]:
                    user_message_count.pop(user_id, None)
                    user_reaction_count.pop(user_id, None)
                    user_names.pop(user_id, None)
            except:
                pass
        user_scores = {}
        for user_id in set(list(user_message_count.keys()) + list(user_reaction_count.keys())):
            message_score = user_message_count.get(user_id, 0)
            reaction_score = user_reaction_count.get(user_id, 0)
            user_scores[user_id] = message_score + (reaction_score * 2)
        top_20 = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:20]
        return top_20
    except:
        return []

def create_top_fans_post():
    top_users = get_top_fans_list()
    if not top_users:
        return "<b>🏆 Top Fans မရှိသေးပါ</b>"
    post = "<b>🏆 အပတ်စဉ် Top Fans 🏆</b>\n\n"
    for i, (user_id, score) in enumerate(top_users, 1):
        username = user_names.get(user_id, f"User_{user_id}")
        post += f"{i}. <b>{username}</b> - <i>Score:</i> {score}\n"
    return post

def top_fans_worker():
    while True:
        now = datetime.now()
        days_until_sunday = (6 - now.weekday()) % 7
        next_sunday_1759 = (now + timedelta(days=days_until_sunday)).replace(hour=17, minute=59, second=0, microsecond=0)
        if next_sunday_1759 <= now:
            next_sunday_1759 += timedelta(days=7)
        wait_seconds = (next_sunday_1759 - now).total_seconds()
        time.sleep(max(wait_seconds, 0))
        try:
            time.sleep(60)  # wait until 18:00
            bot.send_message(YOUR_CHANNEL_ID, create_top_fans_post(), parse_mode='HTML')
            user_message_count.clear()
            user_reaction_count.clear()
            user_names.clear()
        except Exception as e:
            print(f"TopFans weekly error: {e}")
        time.sleep(5)

threading.Thread(target=top_fans_worker, daemon=True).start()

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
    try:
        for e in getattr(message, "entities", []):
            if getattr(e, "type", "") in ["url", "text_link"]:
                return True
        for e in getattr(message, "caption_entities", []):
            if getattr(e, "type", "") in ["url", "text_link"]:
                return True
    except:
        pass
    return False

def is_admin(chat_id, user_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        return user_id in [a.user.id for a in admins]
    except:
        return False

@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"], content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def handle_group_messages(message):
    if has_link_api(message) and not is_admin(message.chat.id, message.from_user.id):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            user_id = message.from_user.id
            first_name = message.from_user.first_name
            bot.send_message(message.chat.id, f'⚠️ <a href="tg://user?id={user_id}">{first_name}</a> 💢 Link မရနိုင်ပါ 🙅🏻', parse_mode='HTML')
        except:
            pass
    else:
        track_user_activity(message)

# ===============================
# WELCOME SYSTEM
# ===============================
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for user in message.new_chat_members:
        caption = f"<b>နွေးထွေးစွာကြိုဆိုပါတယ်🧸</b>\n<b>{user.first_name}</b>\n📚 Oscar's Library မှ အမြဲအသင့်ရှိပါတယ်!"
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("စာပေချစ်သူများအတွက်", url="https://t.me/oscar_libray_bot"))
        try:
            bot.send_photo(message.chat.id, WELCOME_PHOTO_URL, caption=caption, reply_markup=kb, parse_mode='HTML')
        except:
            bot.send_message(message.chat.id, caption, reply_markup=kb, parse_mode='HTML')

# ===============================
# /START COMMAND
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
    first = message.from_user.first_name
    text = f"<b>သာယာသောနေ့လေးဖြစ်ပါစေ 🌸</b>\n<b>{first}</b>, Oscar's Library မှ ကြိုဆိုပါတယ်!"
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton("📚 ကဏ္ဍအလိုက်", callback_data="category"),
           types.InlineKeyboardButton("✍️ စာရေးဆရာ", callback_data="author_menu"))
    bot.send_message(message.chat.id, text, reply_markup=kb, parse_mode='HTML')

# ===============================
# CATEGORY & AUTHOR MENU
# ===============================
AUTHOR_LINKS = {"က": "https://t.me/oscarhelpservices/5", "Eng": "https://t.me/sharebykosoemoe/920"}  # simplified

@bot.callback_query_handler(func=lambda c: c.data.startswith("author_"))
def author_redirect(call):
    key = call.data.replace("author_", "")
    url = AUTHOR_LINKS.get(key)
    if url:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"➡️ <b>{key}</b> စာရေးဆရာများ\n{url}", parse_mode='HTML')

# ===============================
# SHOW COMMANDS
# ===============================
@bot.message_handler(commands=['showbirthday'])
def show_birthday_post(message):
    bot.send_photo(message.chat.id, BIRTHDAY_PHOTO_URL, caption=create_birthday_message_text(), parse_mode='HTML')

@bot.message_handler(commands=['showtopfan'])
def show_top_post(message):
    bot.send_message(message.chat.id, create_top_fans_post(), parse_mode='HTML')

@bot.message_handler(commands=['mystats'])
def show_my_stats(message):
    user_id = message.from_user.id
    message_count = user_message_count.get(user_id, 0)
    reaction_count = user_reaction_count.get(user_id, 0)
    total_score = message_count + (reaction_count * 2)
    bot.send_message(message.chat.id, f"<b>📊 သင့် Stats</b>\n💬 Messages: {message_count}\n❤️ Reactions: {reaction_count}\n⭐ Total Score: {total_score}", parse_mode='HTML')

# ===============================
# TRACK ALL MESSAGES
# ===============================
@bot.message_handler(func=lambda m: True)
def track_all_messages(message):
    if message.text and message.text.startswith('/'):
        return
    track_user_activity(message)

# ===============================
# FLASK WEBHOOK
# ===============================
app = Flask(__name__)
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_json(force=True))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/", methods=['GET'])
def index():
    return "Bot is running…", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
