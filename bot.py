import os
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import requests
import sys
from datetime import datetime, timedelta

# ===============================
# BOT TOKEN & URL (Environment Variables)
# ===============================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4')
WEBHOOK_URL = "https://oscar-library-bot.onrender.com/" + BOT_TOKEN
PING_URL = "https://oscar-library-bot.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ===============================
# CHANNEL CONFIGURATION
# ===============================
YOUR_CHANNEL_ID = "1002150199369"  # သင့် channel username ထည့်ပါ

# ===============================
# BIRTHDAY WISH BOT CONFIGURATION
# ===============================
BIRTHDAY_CHANNEL_ID = "1002150199369"
BIRTHDAY_PHOTO_URL = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/Happy_Birthday_Photo.jpg"
WELCOME_PHOTO_URL = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/welcome_photo.jpg"

# ===============================
# TOP FANS TRACKING SYSTEM - STORAGE
# ===============================
user_message_count = {}
user_reaction_count = {}
user_names = {}  # Store usernames for display
tracking_start_time = datetime.now()

# ===============================
# RENDER FONT FIX
# ===============================
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# ===============================
# KEEP ALIVE (ping)
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
# BIRTHDAY MESSAGE CREATION (uses original text)
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

အနာဂတ်မှာ 🤍
နားလည်မှု များစွာနဲ့ 🍒
အရင်ကထက်ပိုပိုပြီး  💕
ဆထက်တပိုး ပိုပြီး ချစ်နိုင်ပါစေ 🤍💞

ချစ်ရတဲ့ မိသားစုနဲ့အတူပျော်ရွှင်ရောနေ့ရက်တွေကို ထာဝရ ပိုင်ဆိုင်နိုင်ပါစေ 
လို့ ဆုတောင်းပေးပါတယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊

<b>🌼 Oscar's Library 🌼</b>
 
#adminteam"""
    return message

# ===============================
# Birthday sender worker (thread)
# ===============================
def birthday_worker():
    print("🤖 Birthday worker started (daily 08:00)")
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:
            try:
                caption = create_birthday_message_text()
                bot.send_photo(chat_id=BIRTHDAY_CHANNEL_ID, photo=BIRTHDAY_PHOTO_URL, caption=caption, parse_mode='HTML')
                print(f"✅ မွေးနေ့ဆုတောင်းစာပို့ပြီး - {datetime.now()}")
            except Exception as e:
                print(f"❌ မွေးနေ့ဆုတောင်းစာပို့ရာတွင်အမှား - {e}")
            time.sleep(61)
        else:
            time.sleep(20)

def initialize_birthday_bot():
    t = threading.Thread(target=birthday_worker, daemon=True)
    t.start()

# ===============================
# TOP FANS FUNCTIONS
# ===============================
def track_user_activity(message):
    try:
        user_id = message.from_user.id
        user_message_count[user_id] = user_message_count.get(user_id, 0) + 1

        username = getattr(message.from_user, "username", None)
        first_name = message.from_user.first_name or "User"
        if username:
            user_names[user_id] = f"@{username}"
        else:
            user_names[user_id] = first_name
    except Exception as e:
        print(f"❌ Error tracking user activity: {e}")

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
        post = "<b>🏆 အပတ်စဉ် Top Fans များ 🏆</b>\n\n"
        post += "ဒီအပတ်အတွင်းကျွန်တော်တို့ချန်နယ်ကို အပြင်းအထန် အားပေးမှုအများဆုံး Member များကိုရွေးချယ်လိုက်ပါပြီ...!\n\n"
        post += "<b>🎖️ Official Top 20 Community Stars 🎖️</b>\n\n"
        gold_titles = ["👑 Channel King", "⭐ Super Star", "🔥 Fire Reactor", "💬 Chat Champion", "🎯 Most Active"]
        post += "<b>🥇 GOLD Tier (Top 1-5)</b>\n"
        for i, (user_id, score) in enumerate(top_users[:5], 1):
            username = user_names.get(user_id, f"User_{user_id}")
            title = gold_titles[i-1] if i-1 < len(gold_titles) else "⭐ Top Fan"
            post += f"{i}. {username} {title} - Score: {score}\n"
        silver_titles = ["✨ Rising Star", "💫 Active Member", "🌟 Community Hero", "🚀 Engagement Star", "💝 Supporter", 
                        "👍 Top Fan", "🔥 React Master", "💬 Conversation Starter", "⭐ Future Star", "🌈 Community Builder"]
        post += "\n<b>🥈 SILVER Tier (Top 6-15)</b>\n"
        for i, (user_id, score) in enumerate(top_users[5:15], 6):
            username = user_names.get(user_id, f"User_{user_id}")
            title = silver_titles[i-6] if i-6 < len(silver_titles) else "🌟 Star"
            post += f"{i}. {username} {title} - Score: {score}\n"
        bronze_titles = ["🎉 Celebration Star", "💎 Diamond Member", "🌟 Shining Star", "🚀 Rocket Booster", "💖 Heart Giver"]
        post += "\n<b>🥉 BRONZE Tier (Top 16-20)</b>\n"
        for i, (user_id, score) in enumerate(top_users[15:20], 16):
            username = user_names.get(user_id, f"User_{user_id}")
            title = bronze_titles[i-16] if i-16 < len(bronze_titles) else "🌟 Member"
            post += f"{i}. {username} {title} - Score: {score}\n"
        post += "\n<b>💫 နောက်အပတ်မှာ Top Fan ဘယ်သူတွေဖြစ်မလဲ...</b>\n\n"
        post += "ဒီအပတ် ပါဝင်သူတစ်ယောက်စီတိုင်းကို အထူးကျေးဇူးတင်ရှိပါတယ်!\n"
        post += "နောက်အပတ်မှာတော့ သင့်နာမည် ဒီစာရင်းမှာပါအောင်...🥰\n\n"
        post += "✅ React လေးတွေ ပိုပေးပါ...\n"
        post += "✅ စကားဝိုင်းမှာ ပါဝင်ပါ...\n"
        post += "✅ ချန်နယ်ကို အားပေးပါ...\n\n"
        post += "သင့်ရဲ့တစ်ခုတည်းသော Reactကလေးက ကျွန်တော်တို့အတွက် များစွာအဓိပ္ပာယ်ရှိပါတယ်! 💝\n\n"
        post += "<b>🌟 ကျွန်တော်တို့ရဲ့ချန်နယ်ကို အသက်သွင်းပေးထားတဲ့ အချစ်တော်လေးများကျေးဇူးကမ္ဘာပါ...🤞</b>\n"
        post += "သင့်ရဲ့ ပါဝင်မှုတိုင်းက ကျွန်တော်တို့အတွက် ဆက်လက်လုပ်ဆောင်နိုင်တဲ့ စွမ်းအားပါ...✨\n\n"
        post += "<b>📅 နောက်တစ်ကြိမ် - တနင်္ဂနွေ ည ၆ နာရီ</b>\n"
        post += "ဘယ်သူတွေ Top 20 ထဲဝင်မလဲ စောင့်ကြည့်လိုက်ကြရအောင်...! 🎊"
        return post
    except Exception as e:
        print(f"❌ Error creating top fans post: {e}")
        return "<b>❌ Top Fans list ထုတ်ရာတွင် အမှားတစ်ခုဖြစ်နေသည်</b>"

# ===============================
# TOP FANS WEEKLY WORKER (thread)
# ===============================
def top_fans_worker():
    print("🤖 TopFans worker started (weekly Sunday 18:00)")
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
            final_top_20 = get_top_fans_list()
            time.sleep(60)
            top_fans_post = create_top_fans_post()
            bot.send_message(chat_id=YOUR_CHANNEL_ID, text=top_fans_post, parse_mode='HTML')
            user_message_count.clear()
            user_reaction_count.clear()
            user_names.clear()
            global tracking_start_time
            tracking_start_time = datetime.now()
        except Exception as e:
            print(f"❌ Error in weekly top fans: {e}")
        time.sleep(5)

def initialize_top_fans_bot():
    t = threading.Thread(target=top_fans_worker, daemon=True)
    t.start()

# ===============================
# WELCOME SYSTEM
# ===============================
WELCOME_IMAGE = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/welcome_photo.jpg"

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for user in message.new_chat_members:
        caption = f"""<b>နွေးထွေးစွာကြိုဆိုပါတယ်...🧸</b>
{user.first_name} ...🥰

<b>📚 Oscar's Library မှ
မင်းရဲ့စာဖတ်ခြင်းအတွက် 
အမြဲအသင့်ရှိပါတယ်...🤓</b>

✨📚 မင်းကြိုက်တဲ့စာအုပ်တွေ 
🗃️ ရွေးဖတ်ဖို့ Button ကိုနှိပ်ပါ ✨"""
        welcome_kb = types.InlineKeyboardMarkup()
        welcome_kb.row(
            types.InlineKeyboardButton(
                "စာပေချစ်သူများအတြက္", 
                url="https://t.me/oscar_libray_bot"
            )
        )
        try:
            bot.send_photo(
                message.chat.id, 
                photo=WELCOME_PHOTO_URL, 
                caption=caption,
                reply_markup=welcome_kb,
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Welcome image error: {e}")
            bot.send_message(message.chat.id, caption, reply_markup=welcome_kb, parse_mode='HTML')

# ===============================
# LINK BLOCKER
# ===============================
def is_link(text):
    if not text:
        return False
    return any(x in text.lower() for x in ["http://", "https://", "www.", "t.me/", "telegram.me/", ".com", ".org", ".net"])

def has_link_api(message):
    try:
        if getattr(message, "text", None) and is_link(message.text):
            return True
    except: pass
    try:
        if getattr(message, "caption", None) and is_link(message.caption):
            return True
    except: pass
    try:
        ents = getattr(message, "entities", None)
        if ents:
            for e in ents:
                if getattr(e, "type", "") in ["url", "text_link"]:
                    return True
    except: pass
    try:
        cent = getattr(message, "caption_entities", None)
        if cent:
            for e in cent:
                if getattr(e, "type", "") in ["url", "text_link"]:
                    return True
    except: pass
    if getattr(message, "forward_from", None) or getattr(message, "forward_from_chat", None):
        try:
            if getattr(message, "text", None) and is_link(message.text):
                return True
        except: pass
        try:
            if getattr(message, "caption", None) and is_link(message.caption):
                return True
        except: pass
    return False

def is_admin(chat_id, user_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in admins]
        return user_id in admin_ids
    except Exception as e:
        print(f"Admin check error: {e}")
        return False

@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"], content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def handle_group_messages(message):
    if getattr(message, "text", None) and message.text.startswith('/'):
        return
    if getattr(message, "new_chat_members", None):
        return
    if has_link_api(message):
        if not is_admin(message.chat.id, message.from_user.id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
                user_first_name = message.from_user.first_name
                user_id = message.from_user.id
                warning_msg = f'⚠️ <a href="tg://user?id={user_id}">{user_first_name}</a> 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်...'
                bot.send_message(message.chat.id, warning_msg, parse_mode='HTML')
            except Exception as e:
                print(f"Link blocker error: {e}")

# ===============================
# /START MESSAGE
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
    first = message.from_user.first_name or "Friend"
    text = f"""သာယာသောနေ့လေးဖြစ်ပါစေ...🌸
{first} ...🥰

🌼 <b>Oscar's Library</b> မှ ကြိုဆိုပါတယ်

စာအုပ်များရှာဖွေရန် လမ်းညွှန်ပေးမယ်...

<b>စာအုပ်ရှာဖို့ နှစ်ပိုင်းခွဲထားတယ် 
📚ကဏ္ဍအလိုက် 💠 ✍️စာရေးဆရာ</b>

Fic၊ ကာတွန်း၊ သည်းထိပ်ရင်ဖို 
စသည့်ကဏ္ဍများရှာဖတ်ချင်ရင် 
<b>📚ကဏ္ဍအလိုက်</b> ကိုနှိပ်ပါ။

စာရေးဆရာအလိုက်ရှာဖတ်ချင်ရင် 
<b>✍️စာရေးဆရာ</b> ကိုနှိပ်ပါ။

<b>💢 📖စာအုပ်ဖတ်နည်းကြည့်ပါရန် 💢</b>

<b>⚠️ အဆင်မပြေတာရှိရင် ⚠️
❓အထွေထွေမေးမြန်းရန်</b> ကိုနှိပ်ပါ။"""
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
    bot.send_message(message.chat.id, text, reply_markup=kb, parse_mode='HTML')

# ===============================
# FLASK WEBHOOK SETUP (for Render)
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
    initialize_birthday_bot()
    initialize_top_fans_bot()
    app.run(host="0.0.0.0", port=port)
