import os
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import requests
import sys
from datetime import datetime, timedelta
import asyncio

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
# TOP FANS TRACKING SYSTEM
# ===============================
user_message_count = {}
user_reaction_count = {}
tracking_start_time = datetime.now()

class BirthdayWishBot:
    def __init__(self):
        self.channel_id = BIRTHDAY_CHANNEL_ID
        self.photo_url = BIRTHDAY_PHOTO_URL
    
    def get_current_date(self):
        """လက်ရှိလနဲ့ရက်ကိုရယူ"""
        now = datetime.now()
        month = now.strftime("%B")
        day = now.day
        return f"{month}, {day}"
    
    def create_birthday_message(self):
        """မွေးနေ့ဆုတောင်းစာဖန်တီး"""
        current_date = self.get_current_date()
        
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

ချစ်ရတဲ့ မိသားစုနဲ့အတူပျော်ရွှင်ရသော
နေ့ရက်တွေကို ထာဝရ ပိုင်ဆိုင်နိုင်ပါစေ 
လို့ ဆုတောင်းပေးပါတယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊

<b>🌼 Oscar's Library 🌼</b>
 
#adminteam"""
        
        return message
    
    async def send_birthday_wish(self):
        """မွေးနေ့ဆုတောင်းစာပို့ရန်"""
        try:
            message = self.create_birthday_message()
            
            await bot.send_photo(
                chat_id=self.channel_id,
                photo=self.photo_url,
                caption=message
            )
            
            print(f"✅ မွေးနေ့ဆုတောင်းစာပို့ပြီး - {datetime.now()}")
            
        except Exception as e:
            print(f"❌ မွေးနေ့ဆုတောင်းစာပို့ရာတွင်အမှား - {e}")
    
    async def schedule_daily_message(self):
        """နေ့စဉ်ပို့ရန် စီစဉ်ခြင်း"""
        while True:
            now = datetime.now()
            
            if now.hour == 8 and now.minute == 0:
                await self.send_birthday_wish()
                await asyncio.sleep(3600)
            else:
                await asyncio.sleep(60)

# ===============================
# BIRTHDAY BOT INITIALIZATION
# ===============================
birthday_bot = BirthdayWishBot()

async def start_birthday_bot():
    """Birthday bot ကို start လုပ်မယ်"""
    print("🤖 Birthday Wish Bot စတင်ပါပြီ...")
    print("⏰ နေ့စဉ် နံနက် ၈ နာရီတွင် ပို့ပေးသွားမည်")
    await birthday_bot.schedule_daily_message()

def initialize_birthday_bot():
    """Birthday bot ကို background တွင် start လုပ်မယ်"""
    def run_birthday_bot():
        asyncio.run(start_birthday_bot())
    
    birthday_thread = threading.Thread(target=run_birthday_bot, daemon=True)
    birthday_thread.start()

# ===============================
# BIRTHDAY PREVIEW COMMAND
# ===============================
@bot.message_handler(commands=['showbirthday'])
def show_birthday_post(message):
    """Show the current birthday post with image preview"""
    try:
        current_date = birthday_bot.get_current_date()
        preview_text = birthday_bot.create_birthday_message()
        
        bot.send_photo(
            message.chat.id,
            photo=BIRTHDAY_PHOTO_URL,
            caption=preview_text
        )
        
    except Exception as e:
        bot.send_message(message.chat.id, preview_text)
        print(f"❌ ပုံမတင်နိုင်: {e}")

# ===============================
# TOP FANS TRACKING FUNCTIONS
# ===============================
def track_user_activity(message):
    """User activity ကိုခြေရာခံမယ်"""
    try:
        user_id = message.from_user.id
        user_message_count[user_id] = user_message_count.get(user_id, 0) + 1
        print(f"📝 User {user_id} message count: {user_message_count[user_id]}")
        
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
    """Top Fans post ဖန်တီးမယ်"""
    try:
        top_users = get_top_fans_list()
        
        if not top_users:
            return "<b>🏆 အပတ်စဉ် Top Fans များ 🏆</b>\n\nဒီအပတ်အတွင်း မှတ်တမ်းရှိသူမရှိသေးပါ..."
        
        post = "<b>🏆 အပတ်စဉ် Top Fans များ 🏆</b>\n\n"
        post += "ဒီအပတ်အတွင်းကျွန်တော်တို့ချန်နယ်ကို အပြင်းအထန် အားပေးမှုအများဆုံး Member များကိုရွေးချယ်လိုက်ပါပြီ...!\n\n"
        post += "<b>🎖️ Official Top 20 Community Stars 🎖️</b>\n\n"
        
        # Gold Tier (Top 1-5)
        post += "<b>🥇 GOLD Tier (Top 1-5)</b>\n"
        for i, (user_id, score) in enumerate(top_users[:5], 1):
            post += f"{i}. User_{user_id} ⭐ Score: {score}\n"
        
        # Silver Tier (Top 6-15)
        post += "\n<b>🥈 SILVER Tier (Top 6-15)</b>\n"
        for i, (user_id, score) in enumerate(top_users[5:15], 6):
            post += f"{i}. User_{user_id} ✨ Score: {score}\n"
        
        # Bronze Tier (Top 16-20)
        post += "\n<b>🥉 BRONZE Tier (Top 16-20)</b>\n"
        for i, (user_id, score) in enumerate(top_users[15:20], 16):
            post += f"{i}. User_{user_id} 🌟 Score: {score}\n"
        
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
# TOP FANS AUTO POST SYSTEM
# ===============================
async def schedule_weekly_top_fans():
    """တနင်္ဂနွေ ည ၅:၅၉ မှာ Final Top 20 ထုတ်ပြီး ၆:၀၀ မှာ Post တင်မယ်"""
    while True:
        now = datetime.now()
        
        # တနင်္ဂနွေ ည ၅:၅၉ စစ်ဆေးခြင်း
        next_sunday = now.replace(hour=17, minute=59, second=0, microsecond=0)
        days_until_sunday = (6 - now.weekday()) % 7
        next_sunday += timedelta(days=days_until_sunday)
        
        wait_seconds = (next_sunday - now).total_seconds()
        if wait_seconds > 0:
            print(f"⏰ Waiting until Sunday 5:59PM: {next_sunday}")
            await asyncio.sleep(wait_seconds)
        
        try:
            print("🕔 Sunday 5:59PM - Finalizing Top 20 List...")
            
            final_top_20 = get_top_fans_list()
            print(f"✅ Final Top 20: {len(final_top_20)} users")
            
            await asyncio.sleep(60)
            
            top_fans_post = create_top_fans_post()
            
            # ✅ CHANNEL ကို POST တင်မယ်
            await bot.send_message(
                chat_id=YOUR_CHANNEL_ID, 
                text=top_fans_post, 
                parse_mode='HTML'
            )
            
            print(f"✅ Weekly Top Fans post published to channel: {YOUR_CHANNEL_ID}")
            
            user_message_count.clear()
            user_reaction_count.clear()
            tracking_start_time = datetime.now()
            print("🔄 User tracking data reset for new week")
            
        except Exception as e:
            print(f"❌ Error in weekly top fans: {e}")
        
        await asyncio.sleep(604800)

# ===============================
# SHOW TOP FANS POST COMMAND
# ===============================
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
# MESSAGE TRACKING HANDLER
# ===============================
@bot.message_handler(func=lambda m: True)
def track_all_messages(message):
    """အရာအားလုံးကိုခြေရာခံမယ်"""
    try:
        if message.text and message.text.startswith('/'):
            return
        track_user_activity(message)
    except Exception as e:
        print(f"❌ Error tracking message: {e}")

# ===============================
# INITIALIZE TOP FANS SYSTEM
# ===============================
async def start_top_fans_bot():
    """Top Fans bot ကို start လုပ်မယ်"""
    print("🤖 Top Fans Tracking System စတင်ပါပြီ...")
    print("⏰ တနင်္ဂနွေ ည ၅:၅၉ မှာ Final List ထုတ်ပြီး ၆:၀၀ မှာ Post တင်မည်")
    await schedule_weekly_top_fans()

def initialize_top_fans_bot():
    """Top Fans bot ကို background တွင် start လုပ်မယ်"""
    def run_top_fans_bot():
        asyncio.run(start_top_fans_bot())
    top_fans_thread = threading.Thread(target=run_top_fans_bot, daemon=True)
    top_fans_thread.start()

# ===============================
# RENDER FONT FIX & KEEP ALIVE
# ===============================
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

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
                "စာပေချစ်သူများအတွက်", 
                url="https://t.me/oscar_libray_bot"
            )
        )
        
        try:
            bot.send_photo(
                message.chat.id, 
                photo=WELCOME_PHOTO_URL, 
                caption=caption,
                reply_markup=welcome_kb
            )
        except Exception as e:
            print(f"Welcome image error: {e}")
            bot.send_message(
                message.chat.id,
                caption,
                reply_markup=welcome_kb,
                parse_mode='HTML'
            )

# ======================================================
# 2️⃣ LINK BLOCKER (GROUP ONLY)
# ======================================================

def is_link(text):
    """Basic raw-text link patterns"""
    if not text:
        return False
    return any(x in text.lower() for x in ["http://", "https://", "www.", "t.me/", "telegram.me/", ".com", ".org", ".net"])

def has_link_api(message):
    """Detect links in all message locations including forwarded text/captions"""

    # 1) Normal text
    try:
        if message.text and is_link(message.text):
            return True
    except:
        pass

    # 2) Caption
    try:
        if message.caption and is_link(message.caption):
            return True
    except:
        pass

    # 3) Entities (normal message)
    try:
        ents = getattr(message, "entities", None)
        if ents:
            for e in ents:
                if e.type in ["url", "text_link"]:
                    return True
    except:
        pass

    # 4) Caption entities
    try:
        cent = getattr(message, "caption_entities", None)
        if cent:
            for e in cent:
                if e.type in ["url", "text_link"]:
                    return True
    except:
        pass

    # 5) Forwarded message (Telegram does NOT send entities in forward text)
    #    So we must check raw text/caption again manually
    if message.forward_from or message.forward_from_chat:
        # Forwarded text
        try:
            if message.text and is_link(message.text):
                return True
        except:
            pass

        # Forwarded caption
        try:
            if message.caption and is_link(message.caption):
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
    
    if message.text and message.text.startswith('/'):
        return
    if message.new_chat_members:
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
# /START MESSAGE - FIXED
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
    first = message.from_user.first_name or "Friend"
    text = f"""<b>သာယာသောနေ့လေးဖြစ်ပါစေ...🌸
    {first} ...🥰</b>
    
<b>🌼 Oscar's Library 🌼 မှ ကြိုဆိုပါတယ်</b>

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

# ======================================================
# 3️⃣ PRIVATE CHAT MESSAGE HANDLER - FIXED
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_private_messages(message):
    """Handle private messages including forwarded links"""
    
    if message.text and message.text.startswith('/'):
        return
    
    user_first_name = message.from_user.first_name
    user_id = message.from_user.id
    
    if message.forward_from_chat or message.forward_from:
        if message.text and is_link(message.text):
            bot.send_message(
                message.chat.id, 
                f'🔗 <a href="tg://user?id={user_id}">{user_first_name}</a> 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်...',
                parse_mode='HTML'
            )
        elif message.caption and is_link(message.caption):
            bot.send_message(
                message.chat.id, 
                f'🔗 <a href="tg://user?id={user_id}">{user_first_name}</a> 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်...',
                parse_mode='HTML'
            )
        else:
            bot.send_message(
                message.chat.id, 
                f'📩 <a href="tg://user?id={user_id}">{user_first_name}</a> ရဲ့ Forwarded message received!\n\nNote: I can process links from forwarded messages in private chats.',
                parse_mode='HTML'
            )
    elif message.text and not message.text.startswith('/'):
        if is_link(message.text):
            bot.send_message(
                message.chat.id, 
                f'🔗 <a href="tg://user?id={user_id}">{user_first_name}</a> 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်...',
                parse_mode='HTML'
            )
        else:
            bot.send_message(
                message.chat.id, 
                f'🤖 <a href="tg://user?id={user_id}">{user_first_name}</a> ရဲ့ Message:\n{message.text}',
                parse_mode='HTML'
            )

# ===============================
# CATEGORY & AUTHOR HANDLERS
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "category")
def category_redirect(call):
    bot.send_message(
        call.message.chat.id,
        "<b>📚 ကဏ္ဍအလိုက် စာအုပ်များ</b>\nhttps://t.me/oscarhelpservices/4\n\n<b>🌼 Oscar's Library 🌼</b>",
        parse_mode='HTML'
    )

@bot.callback_query_handler(func=lambda c: c.data == "author_menu")
def author_menu(call):
    text = "<b>✍️ စာရေးဆရာနာမည် 'အစ' စာလုံးရွေးပါ</b>\n\n<b>🌼 Oscar's Library 🌼</b>"
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
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb, parse_mode='HTML')

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
            f'<b>➡️ {key} ဖြင့်စသောစာရေးဆရာများ</b>\n{url}\n\n<b>🌼 Oscar\'s Library 🌼</b>',
            parse_mode='HTML'
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
    initialize_birthday_bot()
    initialize_top_fans_bot()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
