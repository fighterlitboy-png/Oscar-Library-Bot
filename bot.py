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
YOUR_CHANNEL_ID = "@bookbykosoemoe"  # သင့် channel username ထည့်ပါ

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
        # if it's exactly 08:00 (check minute-level)
        if now.hour == 8 and now.minute == 0:
            try:
                caption = create_birthday_message_text()
                bot.send_photo(chat_id=BIRTHDAY_CHANNEL_ID, photo=BIRTHDAY_PHOTO_URL, caption=caption, parse_mode='HTML')
                print(f"✅ မွေးနေ့ဆုတောင်းစာပို့ပြီး - {datetime.now()}")
            except Exception as e:
                print(f"❌ မွေးနေ့ဆုတောင်းစာပို့ရာတွင်အမှား - {e}")
            # Sleep 61 seconds to avoid double-sending within the same minute
            time.sleep(61)
        else:
            # Sleep until next minute
            time.sleep(20)

def initialize_birthday_bot():
    t = threading.Thread(target=birthday_worker, daemon=True)
    t.start()

# ===============================
# TOP FANS FUNCTIONS (as original)
# ===============================
def track_user_activity(message):
    """User activity ကိုခြေရာခံမယ်"""
    try:
        user_id = message.from_user.id
        user_message_count[user_id] = user_message_count.get(user_id, 0) + 1

        # Store username for display
        username = getattr(message.from_user, "username", None)
        first_name = message.from_user.first_name or "User"
        if username:
            user_names[user_id] = f"@{username}"
        else:
            user_names[user_id] = first_name

        # Debug print
        # print(f"📝 User {user_names[user_id]} message count: {user_message_count[user_id]}")
    except Exception as e:
        print(f"❌ Error tracking user activity: {e}")

def get_top_fans_list():
    """Top 20 fans list ထုတ်မယ်"""
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
    """Top Fans post ဖန်တီးမယ် - IMPROVED VERSION (original text preserved)"""
    try:
        top_users = get_top_fans_list()

        if not top_users:
            return "<b>🏆 အပတ်စဉ် Top Fans များ 🏆</b>\n\nဒီအပတ်အတွင်း မှတ်တမ်းရှိသူမရှိသေးပါ..."

        post = "<b>🏆 အပတ်စဉ် Top Fans များ 🏆</b>\n\n"
        post += "ဒီအပတ်အတွင်းကျွန်တော်တို့ချန်နယ်ကို အပြင်းအထန် အားပေးမှုအများဆုံး Member များကိုရွေးချယ်လိုက်ပါပြီ...!\n\n"
        post += "<b>🎖️ Official Top 20 Community Stars 🎖️</b>\n\n"

        # Gold Tier (Top 1-5) - With special titles
        gold_titles = ["👑 Channel King", "⭐ Super Star", "🔥 Fire Reactor", "💬 Chat Champion", "🎯 Most Active"]
        post += "<b>🥇 GOLD Tier (Top 1-5)</b>\n"
        for i, (user_id, score) in enumerate(top_users[:5], 1):
            username = user_names.get(user_id, f"User_{user_id}")
            title = gold_titles[i-1] if i-1 < len(gold_titles) else "⭐ Top Fan"
            post += f"{i}. {username} {title} - Score: {score}\n"

        # Silver Tier (Top 6-15) - With special titles
        silver_titles = ["✨ Rising Star", "💫 Active Member", "🌟 Community Hero", "🚀 Engagement Star", "💝 Supporter", 
                        "👍 Top Fan", "🔥 React Master", "💬 Conversation Starter", "⭐ Future Star", "🌈 Community Builder"]
        post += "\n<b>🥈 SILVER Tier (Top 6-15)</b>\n"
        for i, (user_id, score) in enumerate(top_users[5:15], 6):
            username = user_names.get(user_id, f"User_{user_id}")
            title = silver_titles[i-6] if i-6 < len(silver_titles) else "🌟 Star"
            post += f"{i}. {username} {title} - Score: {score}\n"

        # Bronze Tier (Top 16-20) - With special titles
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
        # compute next sunday at 17:59 (finalize), then post at 18:00
        # find next sunday date
        days_until_sunday = (6 - now.weekday()) % 7
        next_sunday_1759 = (now + timedelta(days=days_until_sunday)).replace(hour=17, minute=59, second=0, microsecond=0)

        # if we've already passed this week's time, move to next week
        if next_sunday_1759 <= now:
            next_sunday_1759 += timedelta(days=7)

        wait_seconds = (next_sunday_1759 - now).total_seconds()
        # wait until 17:59 on Sunday
        if wait_seconds > 0:
            # print debug
            print(f"⏰ Waiting until Sunday 17:59 -> {next_sunday_1759}")
            time.sleep(wait_seconds)

        # At 17:59 finalize (we'll wait 60 seconds then post at 18:00)
        try:
            print("🕔 Sunday 17:59 - Finalizing Top 20 List...")
            final_top_20 = get_top_fans_list()
            print(f"✅ Final Top 20: {len(final_top_20)} users")
            # wait 60 seconds to reach 18:00
            time.sleep(60)

            top_fans_post = create_top_fans_post()
            bot.send_message(chat_id=YOUR_CHANNEL_ID, text=top_fans_post, parse_mode='HTML')
            print(f"✅ Weekly Top Fans post published to channel: {YOUR_CHANNEL_ID}")

            user_message_count.clear()
            user_reaction_count.clear()
            user_names.clear()
            global tracking_start_time
            tracking_start_time = datetime.now()
            print("🔄 User tracking data reset for new week")
        except Exception as e:
            print(f"❌ Error in weekly top fans: {e}")

        # Sleep a short moment before computing next iteration
        time.sleep(5)

def initialize_top_fans_bot():
    t = threading.Thread(target=top_fans_worker, daemon=True)
    t.start()

# ===============================
# WELCOME SYSTEM (original text preserved)
# ===============================
WELCOME_IMAGE = "welcome_photo.jpg"

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
            # try sending hosted image URL first
            bot.send_photo(
                message.chat.id, 
                photo=WELCOME_PHOTO_URL, 
                caption=caption,
                reply_markup=welcome_kb,
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Welcome image error: {e}")
            bot.send_message(
                message.chat.id,
                caption,
                reply_markup=welcome_kb,
                parse_mode='HTML'
            )

# ===============================
# LINK BLOCKER (GROUP ONLY) - FULL (original logic kept, with minor robustness)
# ===============================
def is_link(text):
    """Basic raw-text link patterns"""
    if not text:
        return False
    return any(x in text.lower() for x in ["http://", "https://", "www.", "t.me/", "telegram.me/", ".com", ".org", ".net"])

def has_link_api(message):
    """Detect links in all message locations including forwarded text/captions"""
    # 1) Normal text
    try:
        if getattr(message, "text", None) and is_link(message.text):
            return True
    except:
        pass

    # 2) Caption
    try:
        if getattr(message, "caption", None) and is_link(message.caption):
            return True
    except:
        pass

    # 3) Entities (normal message)
    try:
        ents = getattr(message, "entities", None)
        if ents:
            for e in ents:
                if getattr(e, "type", "") in ["url", "text_link"]:
                    return True
    except:
        pass

    # 4) Caption entities
    try:
        cent = getattr(message, "caption_entities", None)
        if cent:
            for e in cent:
                if getattr(e, "type", "") in ["url", "text_link"]:
                    return True
    except:
        pass

    # 5) Forwarded message (Telegram does NOT send entities in forward text)
    if getattr(message, "forward_from", None) or getattr(message, "forward_from_chat", None):
        # Forwarded text
        try:
            if getattr(message, "text", None) and is_link(message.text):
                return True
        except:
            pass

        # Forwarded caption
        try:
            if getattr(message, "caption", None) and is_link(message.caption):
                return True
        except:
            pass

    return False

def is_admin(chat_id, user_id):
    """Check if user is admin in the group"""
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in admins]
        return user_id in admin_ids
    except Exception as e:
        print(f"Admin check error: {e}")
        return False

@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"], content_types=['text', 'photo', 'video', 'document', 'audio', 'voice'])
def handle_group_messages(message):
    """Handle all group messages including forwarded ones"""
    # Skip commands and new member messages
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
                print(f"🔗 Link blocked from user {user_first_name} in group {message.chat.id}")
            except Exception as e:
                print(f"Link blocker error: {e}")

# ===============================
# /START MESSAGE (original text preserved)
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
# CATEGORY & AUTHOR CALLBACKS (original)
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "category")
def category_redirect(call):
    bot.send_message(
        call.message.chat.id,
        "📚 **ကဏ္ဍအလိုက် စာအုပ်များ**\nhttps://t.me/oscarhelpservices/4\n\n🌼 Oscar's Library 🌼"
    )

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
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)
    except Exception:
        # fallback: send new message with keyboard
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
        bot.send_message(
            call.message.chat.id,
            f"➡️ **{key} ဖြင့်စသောစာရေးဆရာများ**\n{url}\n\n🌼 Oscar's Library 🌼"
        )

# ===============================
# PRIVATE CHAT HANDLER - preserved behavior
# ===============================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_private_messages(message):
    """Handle private messages including forwarded links - FIXED VERSION"""
    # Ignore commands - let them be handled by their specific handlers
    if message.text and message.text.startswith('/'):
        return

    user_first_name = message.from_user.first_name
    user_id = message.from_user.id

    # Check for links in any type of message
    if has_link_api(message):
        warning_msg = f'🔗 <a href="tg://user?id={user_id}">{user_first_name}</a> 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်...'
        bot.send_message(message.chat.id, warning_msg, parse_mode='HTML')
        print(f"🔗 Link blocked in private chat from user {user_first_name}")
    else:
        # If no links, track the message for Top Fans system
        track_user_activity(message)
        print(f"📝 Message tracked from {user_first_name} in private chat")

# ===============================
# SHOW COMMANDS: /showbirthday, /showtopfan, /mystats
# ===============================
@bot.message_handler(commands=['showbirthday'])
def show_birthday_post(message):
    """Show the current birthday post with image preview"""
    try:
        preview_text = create_birthday_message_text()
        bot.send_photo(
            message.chat.id,
            photo=BIRTHDAY_PHOTO_URL,
            caption=preview_text,
            parse_mode='HTML'
        )
    except Exception as e:
        bot.send_message(message.chat.id, preview_text, parse_mode='HTML')
        print(f"❌ ပုံမတင်နိုင်: {e}")

@bot.message_handler(commands=['showtopfan'])
def show_top_post(message):
    """Show the current top fans post"""
    try:
        top_fans_post = create_top_fans_post()
        bot.send_message(message.chat.id, top_fans_post, parse_mode='HTML')
        print(f"✅ /showtopfan command processed for user: {message.from_user.id}")
    except Exception as e:
        print(f"❌ Error in /showtopfan: {e}")
        bot.send_message(message.chat.id, "❌ Top Fans post ပြရာတွင် အမှားတစ်ခုဖြစ်နေသည်။")

@bot.message_handler(commands=['mystats'])
def show_my_stats(message):
    """User ရဲ့ stats ကိုပြမယ်"""
    try:
        user_id = message.from_user.id
        message_count = user_message_count.get(user_id, 0)
        reaction_count = user_reaction_count.get(user_id, 0)
        total_score = message_count + (reaction_count * 2)

        stats_text = f"""<b>📊 သင့်ရဲ့ Stats</b>

💬 Messages: {message_count}
❤️ Reactions: {reaction_count} 
⭐ Total Score: {total_score}

<b>နောက်တစ်ပါတ်အတွက် Top 20 ဝင်ရန်:</b>
✅ မက်ဆေ့များများပို့ပါ
✅ React များများပေးပါ
✅ Active ဖြစ်အောင်နေပါ

<b>တနင်္ဂနွေ ည ၆ နာရီတွင် Top Fans list အသစ်ထွက်မည်!</b>"""

        bot.send_message(message.chat.id, stats_text, parse_mode='HTML')

    except Exception as e:
        print(f"❌ Error in /mystats: {e}")

# ===============================
# MESSAGE TRACKING HANDLER (for all messages)
# ===============================
@bot.message_handler(func=lambda m: True)
def track_all_messages(message):
    """အရာအားလုံးကိုခြေရာခံမယ်"""
    try:
        # Do not track commands
        if message.text and message.text.startswith('/'):
            return
        # Track activity
        track_user_activity(message)
    except Exception as e:
        print(f"❌ Error tracking message: {e}")

# ===============================
# INITIALIZE BACKGROUND SYSTEMS
# ===============================
def initialize_all_systems():
    """Initialize all background systems"""
    print("🚀 Starting all background systems...")
    initialize_birthday_bot()
    initialize_top_fans_bot()
    print("✅ All systems initialized!")

initialize_all_systems()

# ======================================================
# FLASK WEBHOOK SETUP (for Render)
# ======================================================
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
# RUN (Flask)
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("🤖 Oscar Library Bot is running...")
    print("✅ /start command: ACTIVE")
    print("✅ Link Blocker: ACTIVE")
    print("✅ Top Fans System: ACTIVE")
    print("✅ Birthday Bot: ACTIVE")
    app.run(host="0.0.0.0", port=port)
