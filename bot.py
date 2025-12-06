import os
import json
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import requests
import sys
from datetime import datetime
import pytz
import logging
import random
import re

# ===============================
# DEBUG MODE - FORCE LOGGING
# ===============================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
print("🚀🚀🚀 BOT STARTING UP 🚀🚀🚀")
print("Initializing Oscar Library Bot...")

# ===============================
# BOT TOKEN & URL
# ===============================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4')
WEBHOOK_URL = "https://oscar-library-bot.onrender.com/" + BOT_TOKEN
PING_URL = "https://oscar-library-bot.onrender.com"

print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
print(f"🌐 Webhook URL: {WEBHOOK_URL}")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

# ===============================
# RENDER FONT FIX
# ===============================
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# ===============================
# BIRTHDAY SYSTEM CONFIGURATION
# ===============================
MYANMAR_TZ = pytz.timezone('Asia/Yangon')
def get_myanmar_time():
    return datetime.now(MYANMAR_TZ)

BIRTHDAY_IMAGE_URL = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/Happy_Birthday_Photo.jpg"
BIRTHDAY_CAPTION_TEMPLATE = """<b>Birthday Wishes 💌</b>
<b>Happy Birthday ❤️ ကမ္ဘာ❣️</b>
<b>ပျော်ရွှင်စရာမွေးနေ့လေးဖြစ်ပါစေ..🎂💗</b>

<b>{current_date}</b> မွေးနေ့လေးမှစ နောင်နှစ်ပေါင်းများစွာတိုင်အောင်... 
ကိုယ်၏ကျန်းမာခြင်း စိတ်၏ချမ်းသာခြင်းများနဲ့ပြည့်စုံပြီး လိုအပ်ချက်လိုအင်ဆန္ဒများ လည်းပြည့်ဝပါစေ...🥰

အနာဂတ်မှာ 🤍
နားလည်မှု များစွာနဲ့ 🍒
အရင်ကထက်ပိုပိုပြီး 💕
ချစ်နိုင်ကြပါစေ 💞

ချစ်ရတဲ့မိသားစုနဲ့အတူ ပျော်ရွှင်ရသောနေ့ရက်တွေကို ထာဝရပိုင်ဆိုင်နိုင်ပါစေ အမြဲဆုတောင်းပေးပါတယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊
<b>🌼 Oscar's Library 🌼</b> 

#oscaradminteam"""

# ===============================
# SYSTEM VARIABLES
# ===============================
active_groups = set()
last_birthday_post = None
post_in_progress = False

# ===============================
# KEEP ALIVE
# ===============================
def keep_alive():
    print("🌐 Keep-alive thread started")
    while True:
        try:
            response = requests.get(PING_URL, timeout=10)
            print("🌐 Keep-alive ping sent - Status:", response.status_code)
        except Exception as e:
            print(f"🌐 Keep-alive error: {e}")
        time.sleep(300)

threading.Thread(target=keep_alive, daemon=True).start()

# ===============================
# ACTIVE GROUPS TRACKING
# ===============================
def track_active_group(chat_id):
    if chat_id < 0:
        active_groups.add(chat_id)
        if len(active_groups) > 100:
            active_groups.pop()

# ===============================
# FIXED TIME CHECK SYSTEM
# ===============================
def should_send_birthday_post():
    try:
        myanmar_time = get_myanmar_time()
        current_hour = myanmar_time.strftime("%H")
        current_minute = myanmar_time.strftime("%M")
        current_date = myanmar_time.strftime("%Y-%m-%d")
        
        print(f"⏰ Time check: {current_hour}:{current_minute} (Myanmar Time) - Date: {current_date}")
        
        # Post at exactly 8:00 AM Myanmar Time
        if current_hour == "08" and current_minute == "00":
            global last_birthday_post
            if last_birthday_post != current_date:
                last_birthday_post = current_date
                print("✅✅✅ BIRTHDAY POST TRIGGERED! ✅✅✅")
                return True
        return False
    except Exception as e:
        print(f"⏰ Time check error: {e}")
        return False

# ===============================
# GROUP DISCOVERY AND POSTING (GROUPS ONLY - NO CHANNELS)
# ===============================
def discover_all_admin_chats():
    """Find ALL chats (groups AND channels) where bot is admin"""
    admin_chats = set()
    try:
        print("🕵️ Auto-discovering ALL admin chats (Groups + Channels)...")
        for chat_id in list(active_groups):
            try:
                # Get chat info
                chat_info = bot.get_chat(chat_id)
                chat_type = chat_info.type
                chat_title = chat_info.title if hasattr(chat_info, 'title') else "Unknown"
                
                chat_member = bot.get_chat_member(chat_id, bot.get_me().id)
                if chat_member.status in ['administrator', 'creator']:
                    try:
                        bot.send_chat_action(chat_id, 'typing')
                        admin_chats.add(chat_id)
                        print(f"✅✅✅ Admin {chat_type.upper()} found: {chat_id} - '{chat_title}'")
                    except Exception as e:
                        print(f"❌ No send permission in {chat_type} {chat_id}: {e}")
                        active_groups.discard(chat_id)
            except Exception as e:
                print(f"❌ Cannot access chat {chat_id}: {e}")
                active_groups.discard(chat_id)
        print(f"🎯 Total admin chats discovered: {len(admin_chats)}")
        return list(admin_chats)
    except Exception as e:
        print(f"❌ Admin discovery error: {e}")
        return list(active_groups)

def send_to_all_chats(admin_chats):
    """Send birthday post to ALL admin chats (groups AND channels)"""
    success_count = 0
    failed_chats = []
    myanmar_time = get_myanmar_time()
    current_date = myanmar_time.strftime("%B %d")
    caption = BIRTHDAY_CAPTION_TEMPLATE.format(current_date=current_date)
    
    print(f"🎂 Starting posts to {len(admin_chats)} admin chats...")
    
    for i, chat_id in enumerate(admin_chats):
        try:
            if i > 0:
                time.sleep(1)  # Rate limiting
            
            # Get chat info for logging
            try:
                chat_info = bot.get_chat(chat_id)
                chat_title = chat_info.title if hasattr(chat_info, 'title') else "Unknown"
                chat_type = chat_info.type
            except:
                chat_title = "Unknown"
                chat_type = "chat"
            
            print(f"📤 [{i+1}/{len(admin_chats)}] Sending to {chat_type}: {chat_id} - '{chat_title}'")
            
            # Send photo to chat (works for both groups and channels)
            bot.send_photo(
                chat_id,
                BIRTHDAY_IMAGE_URL,
                caption=caption,
                parse_mode="HTML"
            )
            
            success_count += 1
            print(f"✅✅✅ [{i+1}/{len(admin_chats)}] Sent to {chat_type}: {chat_id}")
            
        except Exception as e:
            error_msg = str(e)
            chat_title = "Unknown"
            try:
                chat_info = bot.get_chat(chat_id)
                chat_title = chat_info.title if hasattr(chat_info, 'title') else "Unknown"
                chat_type = chat_info.type
            except:
                pass
                
            print(f"❌❌❌ [{i+1}/{len(admin_chats)}] Failed for {chat_type} {chat_id} ('{chat_title}'): {error_msg}")
            failed_chats.append((chat_id, error_msg))
            
            if any(x in error_msg for x in ["Forbidden", "blocked", "no rights", "kicked"]):
                active_groups.discard(chat_id)
    
    return success_count, failed_chats

def send_birthday_to_all_chats():
    """Main function to send birthday posts to ALL admin chats"""
    global post_in_progress
    if post_in_progress:
        print("⚠️ Post already in progress, skipping...")
        return
    
    post_in_progress = True
    print(f"🔒 Lock acquired. Post in progress: {post_in_progress}")
    
    try:
        print("🎂🎂🎂 STARTING BIRTHDAY POSTS TO ALL ADMIN CHATS 🎂🎂🎂")
        
        # Discover ALL admin chats (groups + channels)
        admin_chats = discover_all_admin_chats()
        print(f"🎯 Found {len(admin_chats)} admin chats (groups + channels)")
        
        if admin_chats:
            print(f"🚀 Posting to {len(admin_chats)} chats...")
            success_count, failed_chats = send_to_all_chats(admin_chats)
            
            if failed_chats:
                print(f"📊 Failed chats:")
                for chat_id, error in failed_chats:
                    print(f"   ❌ {chat_id}: {error}")
            
            print(f"✅ Successfully posted to: {success_count}/{len(admin_chats)} chats")
            print(f"🎉🎉🎉 BIRTHDAY POSTS COMPLETED 🎉🎉🎉")
        else:
            print("ℹ️ No admin chats found to post")
        
    except Exception as e:
        print(f"💥💥💥 BIRTHDAY SYSTEM ERROR: {e}")
    finally:
        post_in_progress = False
        print(f"🔓 Lock released. Post in progress: {post_in_progress}")

# ===============================
# SCHEDULER SYSTEM
# ===============================
def birthday_scheduler():
    print("🎂 BIRTHDAY SCHEDULER STARTED!")
    print("⏰ Will post daily at exactly 8:00 AM (Myanmar Time)")
    print("📢 Target: ALL admin chats (Groups + Channels) - One time only")
    last_check = None
    while True:
        try:
            current_time = get_myanmar_time()
            current_minute = current_time.strftime("%H:%M")
            if last_check != current_minute:
                last_check = current_minute
                if should_send_birthday_post():
                    print(f"🚀🚀🚀 TRIGGERING BIRTHDAY POSTS AT {current_time.strftime('%H:%M:%S')} 🚀🚀🚀")
                    send_birthday_to_all_chats()
                else:
                    print(f"⏰ Waiting... Current time: {current_minute}")
        except Exception as e:
            print(f"🎂 Scheduler error: {e}")
        time.sleep(30)

print("🔄 Starting birthday scheduler thread...")
birthday_thread = threading.Thread(target=birthday_scheduler, daemon=True)
birthday_thread.start()
print("✅ Birthday scheduler started")

# ===============================
# LINK DETECTION SYSTEM
# ===============================
def is_link(text):
    """Link detection - @username နဲ့ လင့်မျိုးစုံကို စစ်ဆေးခြင်း"""
    if not text or not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    
    # 1. Basic URL patterns စစ်ဆေးခြင်း
    url_patterns = [
        "http://", "https://", "www.", ".com", ".org", ".net", 
        ".io", ".me", ".tk", ".ml", ".ga", ".cf", ".gq",
        "t.me/", "telegram.me/", "telegram.dog/",
        "youtube.com/", "youtu.be/", "facebook.com/", "fb.me/",
        "instagram.com/", "twitter.com/", "x.com/",
        "//", "://", ".co/", ".info", ".xyz", ".top"
    ]
    
    for pattern in url_patterns:
        if pattern in text_lower:
            return True
    
    # 2. @username pattern စစ်ဆေးခြင်း
    username_pattern = r'@[a-zA-Z0-9_]{4,}'
    if re.search(username_pattern, text):
        return True
    
    # 3. Telegram invite links စစ်ဆေးခြင်း
    telegram_patterns = [
        r't\.me/\+[\w-]+',  # t.me/+invitecode
        r't\.me/joinchat/[\w-]+',  # t.me/joinchat/invitecode
    ]
    
    for pattern in telegram_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

# ======================================================
# ADMIN STATUS CHECK (NO ID CHECKING)
# ======================================================
def is_user_admin(message):
    """User က admin ဟုတ်မဟုတ် status နဲ့ပဲစစ်ခြင်း"""
    
    chat_id = message.chat.id
    chat_type = message.chat.type
    
    # Private chat ဆိုရင် စစ်စရာမလိုဘူး
    if chat_type == "private":
        return True
    
    # User ID ရှာပါ
    user_id = None
    if message.forward_from:
        user_id = message.forward_from.id
        print(f"📩 Forwarded from user: {user_id}")
    elif message.from_user:
        user_id = message.from_user.id
        print(f"👤 Direct from user: {user_id}")
    
    if not user_id:
        print(f"⚠️ No user ID found")
        return True  # မသိရင် မဖျက်ဘူး (safety)
    
    # Anonymous admin bot check
    if user_id == 1087968824:
        print(f"✅ Anonymous admin bot detected - treating as admin")
        return True
    
    # Check admin status in group
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        status = chat_member.status
        
        print(f"👑 User status in group: {status}")
        
        if status in ['administrator', 'creator']:
            print(f"✅✅✅ ADMIN DETECTED (status: {status})")
            return True
        else:
            print(f"❌ User is NOT admin (status: {status})")
            return False
            
    except Exception as e:
        print(f"⚠️ Error checking admin status: {e}")
        return True  # Error ဖြစ်ရင် မဖျက်ဘူး

# ======================================================
# RANDOM REPLIES FOR "စာအုပ်" KEYWORD
# ======================================================
def get_random_book_reply():
    """Random book replies with bold "စာရေးဆရာ" """
    replies = [
        "စာအုပ်တွေဖတ်ချင်တယ်ဆိုရင် <b>စာရေးဆရာ</b>အမည်လေးပြောပြပါလား စာဖတ်ချစ်သူလေးရေ...🥰",
        "စာအုပ်လေးတွေ ရှာဖွေဖတ်ရှုချင်တယ်ဆိုရင် <b>စာရေးဆရာ</b>အမည်လေးကို ပြောပြပါဦး...📚",
        "စာအုပ်လေးတွေ ဖတ်ချင်တယ်လား? <b>စာရေးဆရာ</b>အမည်လေး ပြောပြပါအုံး...🤓",
        "စာဖတ်ချစ်သူလေး ဘယ်<b>စာရေးဆရာ</b>ရဲ့စာအုပ်စဉ်ကို ဖတ်ချင်လဲ? ပြောပြပါ...✨",
        "ကြိုက်နှစ်သက်ရာ <b>စာရေးဆရာ</b>အမည်လေး ပြောပြပါ...စာအုပ်ရှာပေးပါရစေ...📖",
        "<b>စာရေးဆရာ</b>အမည်လေး ပြောပြပါလား စာအုပ်လေးတွေ ရှာပေးပါမယ်...🥰",
        "စာဖတ်ချစ်သူလေး ဘယ်လိုအကြိုက်စာအုပ်မျိုးဖတ်ချင်လဲ? <b>စာရေးဆရာ</b>အမည်လေးပြောပြပါ...🌸",
        "စာအုပ်ရှာဖွေဖို့ <b>စာရေးဆရာ</b>အမည်လေးကို ပြောပြပေးပါ ကူညီ�ှာပေးပါ့မယ်...💕"
    ]
    return random.choice(replies)

# ======================================================
# GROUP WELCOME SYSTEM
# ======================================================
WELCOME_IMAGE_URL = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/welcome_photo.jpg"

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    print(f"👋 Welcome message for new member in chat: {message.chat.id}")
    track_active_group(message.chat.id)
    
    for user in message.new_chat_members:
        caption = f"""<b>နွေးထွေးစွာကြိုဆိုပါတယ်...🧸</b>

<b>{user.first_name} ...🥰</b>

<b>📚 Oscar's Library မှ</b>
မင်းရဲ့စာဖတ်ခြင်းအတွက် 
အမြဲအသင့်ရှိပါတယ်...🤓 

✨📚 မင်းကြိုက်တဲ့စာအုပ်တွေ 
🗃️ ရွေးဖတ်ဖို့ <b>Button</b> ကိုနှိပ်ပါ ✨"""
        
        welcome_kb = types.InlineKeyboardMarkup()
        welcome_kb.row(
            types.InlineKeyboardButton(
                "စာပေချစ်သူများအတွက်", 
                url="https://t.me/oscar_libray_bot"
            )
        )
        
        try:
            print(f"🖼️ Sending welcome image...")
            bot.send_photo(
                message.chat.id, 
                WELCOME_IMAGE_URL, 
                caption=caption,
                reply_markup=welcome_kb,
                parse_mode="HTML"
            )
            print(f"✅ Welcome message sent")
        except Exception as e:
            print(f"❌ Welcome image error: {e}")
            try:
                bot.send_message(
                    message.chat.id,
                    caption,
                    reply_markup=welcome_kb,
                    parse_mode="HTML"
                )
                print(f"✅ Sent text-only welcome")
            except Exception as e2:
                print(f"❌ Failed to send welcome: {e2}")

# ======================================================
# MAIN GROUP MESSAGE HANDLER
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"], content_types=['text', 'photo', 'video', 'document', 'audio'])
def handle_group_messages(message):
    """Group messages handler"""
    
    # Skip commands and new members
    if message.text and message.text.startswith('/'):
        return
    if message.new_chat_members:
        return
    
    track_active_group(message.chat.id)
    
    print(f"\n" + "="*50)
    print(f"📨 GROUP MESSAGE")
    print(f"👤 From: {message.from_user.first_name if message.from_user else 'Unknown'}")
    print(f"💬 Chat: {message.chat.title if hasattr(message.chat, 'title') else 'Group'}")
    print(f"📝 Text: {message.text[:100] if message.text else 'Media'}")
    
    # "စာအုပ်" keyword စစ်ပါ
    if message.text and 'စာအုပ်' in message.text:
        print(f"📚 'စာအုပ်' keyword - replying")
        try:
            bot.reply_to(message, get_random_book_reply(), parse_mode="HTML")
        except Exception as e:
            print(f"❌ Reply error: {e}")
        return
    
    # Admin check - STATUS နဲ့ပဲစစ်
    if is_user_admin(message):
        print(f"✅ ADMIN USER - NO ACTION")
        return
    
    # Non-admin user - check for links
    text_to_check = message.text or message.caption or ""
    
    # ALLOWED LINKS (မဖျက်တဲ့ link တွေ)
    allowed_patterns = [
        r'tg://user\?id=\d+',  # User links
        r't\.me/\d+',  # t.me user links
        r'telegram\.me/\d+',  # telegram.me user links
        r'@oscar_libray_bot',  # Bot username
        r'@oscarhelpservices',  # Channel username
    ]
    
    # Check if it's an allowed link
    is_allowed = False
    for pattern in allowed_patterns:
        if re.search(pattern, text_to_check, re.IGNORECASE):
            print(f"✅ Allowed link: {pattern}")
            is_allowed = True
            break
    
    # If not allowed, check for blocked links
    if not is_allowed and is_link(text_to_check):
        print(f"🚫 BLOCKED LINK DETECTED - DELETING")
        try:
            bot.delete_message(message.chat.id, message.message_id)
            
            # Send warning
            user_name = message.from_user.first_name if message.from_user else "User"
            user_id = message.from_user.id if message.from_user else None
            
            if user_id:
                warning_msg = f'⚠️ [{user_name}](tg://user?id={user_id}) 💢\n\n**Link🔗 များကို ပိတ်ထားပါတယ်** 🙅🏻\n\n✅ User link များကိုသာ သုံးပါ\n❗လိုအပ်ချက်ရှိရင် **Admin** ကို ဆက်သွယ်ပါနော်...'
            else:
                warning_msg = f'⚠️ {user_name} 💢\n\n**Link🔗 များကို ပိတ်ထားပါတယ်** 🙅🏻\n\n✅ User link များကိုသာ သုံးပါ\n❗လိုအပ်ချက်ရှိရင် **Admin** ကို ဆက်သွယ်ပါနော်...'
            
            bot.send_message(message.chat.id, warning_msg, parse_mode="Markdown")
            print(f"✅ Message deleted + warning sent")
            
        except Exception as e:
            print(f"❌ Delete error: {e}")
    else:
        print(f"✅ No blocked links - NO ACTION")
    
    print(f"="*50)

# ===============================
# /START MESSAGE
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
    print(f"🔄 /start command from user: {message.from_user.id}")
    first = message.from_user.first_name or "Friend"
    text = f"""<b>သာယာသောနေ့လေးဖြစ်ပါစေ...🌸</b>
<b>{first}</b> ...🥰
<b>🌼 Oscar's Library 🌼</b> မှကြိုဆိုပါတယ်။
စာအုပ်များရှာဖွေရန် လမ်းညွှန်ပေးမယ်...

<b>စာအုပ်ရှာဖို့ နှစ်ပေါင်းခွဲထားတယ်</b>
<b>📚ကဏ္ဍအလိုက် 💠 ✍️စာရေးဆရာ</b>

Fic၊ ကာတွန်း၊ သည်းထိပ်ရင်ဖို 
စသည့်ကဏ္ဍများရှာဖတ်ချင်ရင် 
<b>📚ကဏ္ဍအလိုက်</b> ကိုနှိပ်ပါ။

စာရေးဆရာအအလိုက်ရှာဖတ်ချင်ရင် 
<b>✍️စာရေးဆရာ</b> ကိုနှိပ်ပါ။

<b>💢 📖စာအုပ်ဖတ်နည်းကြည့်ပါရန် 💢</b>

⚠️ အဆင်မပြေတာရှိရင် ⚠️
<b>❓အထွေထွေမေးမြန်းရန်</b> ကိုနှိပ်ပါ။"""
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("📚 ကဏ္ဍအလိုက်", callback_data="category"),
        types.InlineKeyboardButton("✍️ စာရေးဆရာ", callback_data="author_menu")
    )
    kb.row(
        types.InlineKeyboardButton("📖 စာအုပ်ဖတ်နည်း", url="https://t.me/oscarhelpservices/17"),
        types.InlineKeyboardButton("📝 စာအုပ်ပြုပြင်ရန်", url="https://t.me/oscarhelpservices/29?single")
    )
    kb.row(
        types.InlineKeyboardButton("🌼 ချန်နယ်ခွဲများ", url="https://t.me/oscarhelpservices/9"),
        types.InlineKeyboardButton("⭐ Review ရေးရန်", url="https://t.me/sharebykosoemoe/13498")
    )
    kb.row(types.InlineKeyboardButton("❓ အထွေထွေမေးမြန်းရန်", url="https://t.me/kogyisoemoe"))
    bot.send_message(message.chat.id, text, reply_markup=kb, parse_mode="HTML")

# ======================================================
# DEBUG COMMANDS
# ======================================================
@bot.message_handler(commands=['myid'])
def show_my_id(message):
    """Show my user ID"""
    user_id = message.from_user.id if message.from_user else None
    
    response = f"""
<b>🔍 YOUR ID INFORMATION:</b>

<b>User ID:</b> <code>{user_id}</code>
<b>Chat ID:</b> <code>{message.chat.id}</code>
<b>Chat Type:</b> {message.chat.type}

<b>Bot will check your ADMIN STATUS, not your ID.</b>
✅ Admin users can post links
❌ Non-admin users cannot post links
"""
    
    bot.reply_to(message, response, parse_mode="HTML")
    print(f"📊 User {user_id} checked their ID")

@bot.message_handler(commands=['admincheck'])
def check_admin_status(message):
    """Check admin status"""
    user_id = message.from_user.id if message.from_user else None
    
    if not user_id:
        bot.reply_to(message, "❌ Cannot get user ID")
        return
    
    try:
        chat_member = bot.get_chat_member(message.chat.id, user_id)
        status = chat_member.status
        
        response = f"""
<b>🔍 ADMIN STATUS CHECK:</b>

<b>User ID:</b> <code>{user_id}</code>
<b>Status:</b> <b>{status}</b>

<b>Result:</b>
"""
        
        if status in ['administrator', 'creator']:
            response += "✅ <b>YOU ARE ADMIN - Can post links</b>"
        else:
            response += "❌ <b>YOU ARE NOT ADMIN - Cannot post links</b>"
        
        bot.reply_to(message, response, parse_mode="HTML")
        print(f"🔍 Admin check for {user_id}: {status}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# ======================================================
# PRIVATE CHAT HANDLER
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_private_messages(message):
    if message.text and message.text.startswith('/'):
        return
    
    # "စာအုပ်" keyword စစ်ပါ
    if message.text and 'စာအုပ်' in message.text:
        print(f"📚 Private chat 'စာအုပ်' keyword")
        try:
            bot.send_message(message.chat.id, get_random_book_reply(), parse_mode="HTML")
        except Exception as e:
            print(f"❌ Reply error: {e}")
        return

# ======================================================
# FORCE POST COMMAND
# ======================================================
@bot.message_handler(commands=['forcepost'])
def force_birthday_post(message):
    try:
        print(f"🔧 Forcepost command from: {message.from_user.id}")
        bot.reply_to(message, "🚀 Force sending birthday posts...")
        send_birthday_to_all_chats()
        bot.reply_to(message, "✅ Force post completed!")
    except Exception as e:
        error_msg = f"❌ Force post error: {e}"
        print(error_msg)
        bot.reply_to(message, error_msg)

# ===============================
# CALLBACK HANDLERS
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "category")
def category_redirect(call):
    bot.send_message(
        call.message.chat.id,
        "<b>📚 ကဏ္ဍအလိုက် စာအုပ်များ</b>\nhttps://t.me/oscarhelpservices/4\n\n<b>🌼 Oscar's Library 🌼</b>",
        parse_mode="HTML"
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
    kb.row(types.InlineKeyboardButton("⬅ Back", callback_data="back_to_main"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data == "back_to_main")
def back_to_main(call):
    first = call.from_user.first_name or "Friend"
    text = f"""<b>သာယာသောနေ့လေးဖြစ်ပါစေ...🌸</b>
<b>{first}</b> ...🥰
<b>🌼 Oscar's Library 🌼</b> မှကြိုဆိုပါတယ်။
စာအုပ်များရှာဖွေရန် လမ်းညွှန်ပေးမယ်...

<b>စာအုပ်ရှာဖို့ နှစ်ပေါင်းခွဲထားတယ်</b>
<b>📚ကဏ္ဍအလိုက် 💠 ✍️စာရေးဆရာ</b>

Fic၊ ကာတွန်း၊ သည်းထိပ်ရင်ဖို 
စသည့်ကဏ္ဍများရှာဖတ်ချင်ရင် 
<b>📚ကဏ္ဍအလိုက်</b> ကိုနှိပ်ပါ။

စာရေးဆရာအအလိုက်ရှာဖတ်ချင်ရင် 
<b>✍️စာရေးဆရာ</b> ကိုနှိပ်ပါ။

<b>💢 📖စာအုပ်ဖတ်နည်းကြည့်ပါရန် 💢</b>

⚠️ အဆင်မပြေတာရှိရင် ⚠️
<b>❓အထွေထွေမေးမြန်းရန်</b> ကိုနှိပ်ပါ။"""
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("📚 ကဏ္ဍအလိုက်", callback_data="category"),
        types.InlineKeyboardButton("✍️ စာရေးဆရာ", callback_data="author_menu")
    )
    kb.row(
        types.InlineKeyboardButton("📖 စာအုပ်ဖတ်နည်း", url="https://t.me/oscarhelpservices/17"),
        types.InlineKeyboardButton("📝 စာအုပ်ပြုပြင်ရန်", url="https://t.me/oscarhelpservices/29?single")
    )
    kb.row(
        types.InlineKeyboardButton("🌼 ချန်နယ်ခွဲများ", url="https://t.me/oscarhelpservices/9"),
        types.InlineKeyboardButton("⭐ Review ရေးရန်", url="https://t.me/sharebykosoemoe/13498")
    )
    kb.row(types.InlineKeyboardButton("❓ အထွေထွေမေးမြန်းရန်", url="https://t.me/kogyisoemoe"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb, parse_mode="HTML")

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
            f"<b>➡️ {key} ဖြင့်စသောစာရေးဆရာများ</b>\n{url}\n\n<b>🌼 Oscar's Library 🌼</b>",
            parse_mode="HTML"
        )

# ===============================
# WEBHOOK HANDLERS
# ===============================
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    print(f"📨 WEBHOOK RECEIVED - {datetime.now()}")
    
    try:
        if request.method == 'POST':
            raw_data = request.get_data(as_text=True)
            
            if raw_data:
                try:
                    json_data = json.loads(raw_data)
                    print(f"✅ JSON PARSED")
                    
                    update = telebot.types.Update.de_json(json_data)
                    
                    def process_update():
                        try:
                            bot.process_new_updates([update])
                            print(f"✅ UPDATE PROCESSED")
                        except Exception as e:
                            print(f"❌ Error in bot.process_new_updates: {e}")
                    
                    import threading
                    thread = threading.Thread(target=process_update)
                    thread.daemon = True
                    thread.start()
                    
                except json.JSONDecodeError as e:
                    print(f"❌ JSON DECODE ERROR: {e}")
                except Exception as e:
                    print(f"❌ GENERAL ERROR: {e}")
        else:
            print(f"⚠️ Not a POST request")
            
        return "OK", 200
        
    except Exception as e:
        print(f"💥 CRITICAL ERROR: {e}")
        return "OK", 200

@app.route("/", methods=['GET', 'POST'])  
def index():
    print("🌐 Health check received")
    return "✅ Bot is running...", 200

# ===============================
# WEBHOOK SETUP
# ===============================
print("🔄 SETTING UP WEBHOOK...")
try:
    print("🗑️ Removing existing webhook...")
    bot.remove_webhook()
    time.sleep(2)
    
    print(f"🔧 Setting webhook to: {WEBHOOK_URL}")
    success = bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=None,
        max_connections=100,
        allowed_updates=["message", "callback_query", "chat_member"],
        timeout=60
    )
    
    if success:
        print(f"✅✅✅ WEBHOOK SET SUCCESSFULLY")
        
        time.sleep(1)
        try:
            webhook_info = bot.get_webhook_info()
            print(f"🎯 Webhook URL: {webhook_info.url}")
            print(f"🎯 Pending updates: {webhook_info.pending_update_count}")
        except Exception as e:
            print(f"🎯⚠️ Cannot verify webhook: {e}")
            
    else:
        print("❌❌❌ WEBHOOK SET FAILED")
        
except Exception as e:
    print(f"💥 WEBHOOK SETUP ERROR: {e}")

print("\n" + "="*60)
print("🎂 BIRTHDAY SYSTEM STATUS")
print("="*60)
print("✅ Time check: 08:00 AM exactly (Myanmar Time)")
print("✅ All-chat mode: ACTIVE (Groups + Channels)")
print("✅ Single post system: ACTIVE (No duplicate)")
print("✅ Post lock: ACTIVE (prevents duplicate runs)")
print("="*60)

print("\n" + "="*60)
print("📚 OTHER FEATURES")
print("="*60)
print("✅ 'စာအုပ်' Auto Reply: ENABLED")
print("✅ Link Blocker: ADMIN STATUS CHECK ONLY")
print("✅ Welcome System: ENABLED")
print("✅ Admin Check: By STATUS (not ID)")
print("="*60)

print("\n🚀 Bot is now LIVE!")
print("💡 Commands: /start, /forcepost, /myid, /admincheck")
print("🔒 Admin users can post links automatically")
print("🎯 Bot will post to ALL admin chats (Groups + Channels) daily at 8:00 AM")
print("⚠️ Note: Manual Channel ID system is REMOVED - uses auto-discovery only")

# ===============================
# RUN WITH FLASK
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    
    print("\n" + "="*60)
    print("🚀 STARTING FLASK SERVER")
    print("="*60)
    print(f"📡 Port: {port}")
    print(f"🌐 Webhook URL: {WEBHOOK_URL}")
    print(f"🤖 Bot: @oscar_libray_bot")
    print("="*60 + "\n")
    
    import sys
    sys.stdout.flush()
    
    app.run(host="0.0.0.0", port=port, debug=True)
