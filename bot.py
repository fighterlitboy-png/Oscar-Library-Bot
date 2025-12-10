import os
import json
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import requests
import sys
from datetime import datetime, timedelta
import pytz
import logging
import random
import re

# ===============================
# CONFIGURATION
# ===============================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
print("🚀 BOT STARTING UP")

BOT_TOKEN = os.environ.get('BOT_TOKEN', '7867668478:AAHpvrXyBri5MMbVq4n73-HdCiqpXXvyJGQ')
WEBHOOK_URL = "https://oscar-library-bot.onrender.com/webhook"
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
# BIRTHDAY IMAGES DATABASE
# ===============================
BIRTHDAY_IMAGES = [
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_2.jpg",  # ပုံ ၁
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_3.jpg",  # ပုံ ၂
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_4.jpg",  # ပုံ ၃
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_5.jpg",  # ပုံ ၄
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_6.jpg",  # ပုံ ၅
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_7.jpg"   # ပုံ ၆
]

# Track current image index for birthday
current_birthday_index = 0

def get_next_birthday_image():
    """Get next birthday image in rotation"""
    global current_birthday_index
    image_url = BIRTHDAY_IMAGES[current_birthday_index]
    current_birthday_index = (current_birthday_index + 1) % len(BIRTHDAY_IMAGES)
    print(f"🎂 Using birthday image {current_birthday_index}/{len(BIRTHDAY_IMAGES)}")
    return image_url

# ===============================
# BIRTHDAY SYSTEM CONFIGURATION
# ===============================
MYANMAR_TZ = pytz.timezone('Asia/Yangon')

def get_myanmar_time():
    return datetime.now(MYANMAR_TZ)

BIRTHDAY_CAPTION_TEMPLATE = """<b>Birthday Wishes 💌</b>
<b>Happy Birthday ❤️ ကမ္ဘာ❣️</b>
<b>ပျော်ရွှင်စရာမွေးနေ့လေးဖြစ်ပါစေ..🎂💗</b>

<b>{current_date}</b> မွေးနေ့လေးမှစ နောင်နှစ်ပေါင်းများစွာတိုင်အောင်... 
ကိုယ်၏ကျန်းမာခြင်း စိတ်၏ချမ်းသာခြင်းများနဲ့ပြည့်စုံပြီး လိုအပ်ချက်လိုအင်ဆန္ဒများ လည်းပြည့်ဝပါစေ...

အနာဂတ်မှာ 🤍
နားလည်မှု များစွာနဲ့ 🍒
အရင်ကထက်ပိုပိုပြီး 💕
ချစ်နိုင်ကြပါစေ 💞

ချစ်ရတဲ့မိသားစုနဲ့အတူ ပျော်ရွှင်ရသောနေ့ရက်တွေကို ထာဝရပိုင်ဆိုင်နိုင်ပါစေ အမြဲဆုတောင်းပေးပါတယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊
<b>🌼 Oscar's Library 🌼</b>

#oscarlibrary
#oscaradminteam"""

# ===============================
# MANUAL CHANNEL ID CONFIGURATION
# ===============================
MANUAL_CHANNEL_IDS = [-1002150199369, -1002913448959, -1002953592333, -1002970833199]
print(f"📢 Fixed Channels: {len(MANUAL_CHANNEL_IDS)} channels")

# ===============================
# SYSTEM VARIABLES
# ===============================
active_groups = set()
last_birthday_post_date = None
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
    """Check if should send birthday post at exactly 8:00 AM"""
    try:
        global last_birthday_post_date
        
        myanmar_time = get_myanmar_time()
        current_hour = myanmar_time.hour
        current_minute = myanmar_time.minute
        current_date = myanmar_time.strftime("%Y-%m-%d")
        current_time_str = myanmar_time.strftime("%H:%M")
        
        print(f"⏰ Time check: {current_time_str} (Myanmar Time) - Date: {current_date}")
        
        # Check for exactly 8:00 AM
        if current_hour == 8 and current_minute == 0:
            if last_birthday_post_date != current_date:
                last_birthday_post_date = current_date
                print("✅✅✅ BIRTHDAY POST TRIGGERED! ✅✅✅")
                return True
        
        return False
    except Exception as e:
        print(f"⏰ Time check error: {e}")
        return False

# ===============================
# POST SENDING FUNCTIONS
# ===============================
def send_post_to_channels(image_url, caption):
    """Send post to fixed channels"""
    results = []
    if not MANUAL_CHANNEL_IDS:
        print("❌ No channels configured")
        return results
    
    print(f"📤 Sending post to {len(MANUAL_CHANNEL_IDS)} fixed channels...")
    print(f"🖼️ Image: {image_url}")
    
    for channel_id in MANUAL_CHANNEL_IDS:
        try:
            print(f"📡 Attempting to send to channel: {channel_id}")
            
            # Check if bot is admin
            chat_member = bot.get_chat_member(channel_id, bot.get_me().id)
            if chat_member.status not in ['administrator', 'creator']:
                error_msg = "Bot is not admin in channel"
                print(f"❌ {error_msg}")
                results.append((channel_id, False, error_msg))
                continue
            
            print(f"🖼️ Sending photo to channel {channel_id}...")
            bot.send_photo(
                channel_id,
                image_url,
                caption=caption,
                parse_mode="HTML"
            )
            print(f"✅✅✅ Successfully posted to channel: {channel_id}")
            results.append((channel_id, True, "Success"))
        except Exception as e:
            error_msg = str(e)
            print(f"❌❌❌ Channel post failed for {channel_id}: {error_msg}")
            results.append((channel_id, False, error_msg))
    
    return results

# ===============================
# DISCOVER AND SEND TO ALL ADMIN GROUPS
# ===============================
def discover_all_admin_groups():
    """Find all groups where bot is admin"""
    admin_groups = []
    print("🔍 Discovering admin groups...")
    
    # Check active groups first
    for chat_id in list(active_groups):
        try:
            chat_member = bot.get_chat_member(chat_id, bot.get_me().id)
            if chat_member.status in ['administrator', 'creator']:
                # Try to send a test action to check permissions
                try:
                    bot.send_chat_action(chat_id, 'typing')
                    admin_groups.append(chat_id)
                    print(f"✅ Admin group found: {chat_id}")
                except:
                    print(f"❌ No permission in group {chat_id}")
                    active_groups.discard(chat_id)
        except Exception as e:
            print(f"❌ Cannot access chat {chat_id}: {e}")
            active_groups.discard(chat_id)
    
    print(f"👥 Found {len(admin_groups)} admin groups")
    return admin_groups

def send_to_admin_groups(admin_groups, image_url, caption):
    """Send post to all admin groups"""
    success_count = 0
    failed_groups = []
    
    if not admin_groups:
        print("ℹ️ No admin groups found")
        return 0, []
    
    print(f"👥 Sending to {len(admin_groups)} admin groups...")
    
    for i, chat_id in enumerate(admin_groups):
        try:
            # Small delay to avoid flood limit
            if i > 0:
                time.sleep(1)
            
            print(f"📤 Sending to group {i+1}/{len(admin_groups)}: {chat_id}")
            bot.send_photo(
                chat_id,
                image_url,
                caption=caption,
                parse_mode="HTML"
            )
            success_count += 1
            print(f"✅ [{i+1}/{len(admin_groups)}] Sent to group: {chat_id}")
        except Exception as e:
            error_msg = str(e)
            print(f"❌ [{i+1}/{len(admin_groups)}] Failed for group {chat_id}: {error_msg}")
            failed_groups.append((chat_id, error_msg))
            
            # Remove from active groups if blocked/kicked
            if any(x in error_msg for x in ["Forbidden", "blocked", "no rights", "kicked"]):
                active_groups.discard(chat_id)
    
    return success_count, failed_groups

# ===============================
# BIRTHDAY POSTING FUNCTION
# ===============================
def send_birthday_to_all_chats():
    global post_in_progress
    if post_in_progress:
        print("⚠️ Post already in progress, skipping...")
        return
    
    post_in_progress = True
    try:
        print("🎂🎂🎂 STARTING BIRTHDAY POSTS 🎂🎂🎂")
        
        myanmar_time = get_myanmar_time()
        current_time = myanmar_time.strftime("%H:%M:%S")
        current_date = myanmar_time.strftime("%B %d")
        print(f"🕐 Posting time: {current_time}")
        
        # Prepare birthday post
        caption = BIRTHDAY_CAPTION_TEMPLATE.format(current_date=current_date)
        birthday_image = get_next_birthday_image()
        
        total_success = 0
        
        # 1. Send to fixed channels
        if MANUAL_CHANNEL_IDS:
            print("📢 Posting to fixed channels...")
            channel_results = send_post_to_channels(birthday_image, caption)
            for channel_id, success, error in channel_results:
                if success:
                    total_success += 1
                    print(f"✅ Channel {channel_id}: SUCCESS")
                else:
                    print(f"❌ Channel {channel_id}: FAILED - {error}")
        
        # 2. Send to all admin groups
        print("👥 Discovering admin groups...")
        admin_groups = discover_all_admin_groups()
        
        if admin_groups:
            print(f"👥 Posting to {len(admin_groups)} admin groups...")
            groups_success, groups_failed = send_to_admin_groups(admin_groups, birthday_image, caption)
            total_success += groups_success
            print(f"👥 Groups: {groups_success} successful, {len(groups_failed)} failed")
        else:
            print("ℹ️ No admin groups found")
        
        total_targets = len(MANUAL_CHANNEL_IDS) + len(admin_groups)
        print(f"🎉🎉🎉 BIRTHDAY POSTS COMPLETED: {total_success}/{total_targets} chats 🎉🎉🎉")
        
    except Exception as e:
        print(f"💥💥💥 BIRTHDAY SYSTEM ERROR: {e}")
    finally:
        post_in_progress = False

# ===============================
# FIXED SCHEDULER SYSTEM
# ===============================
def birthday_scheduler():
    print("🎂 BIRTHDAY SCHEDULER STARTED!")
    print("⏰ Will post daily at 8:00 AM (Myanmar Time)")
    print(f"📢 Fixed Channels: {len(MANUAL_CHANNEL_IDS)}")
    print("👥 Will also post to ALL admin groups")
    
    last_minute = None
    
    while True:
        try:
            current_time = get_myanmar_time()
            current_minute = current_time.strftime("%H:%M")
            
            # Only check once per minute
            if last_minute != current_minute:
                last_minute = current_minute
                print(f"⏰ Scheduler checking: {current_minute}")
                
                if should_send_birthday_post():
                    print(f"🚀🚀🚀 TRIGGERING BIRTHDAY POSTS AT {current_time.strftime('%H:%M:%S')} 🚀🚀🚀")
                    send_birthday_to_all_chats()
            
            # Sleep for 30 seconds
            time.sleep(30)
            
        except Exception as e:
            print(f"🎂 Scheduler error: {e}")
            time.sleep(30)

# Start the scheduler thread
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
    
    username_pattern = r'@[a-zA-Z0-9_]{4,}'
    if re.search(username_pattern, text):
        return True
    
    telegram_patterns = [
        r't\.me/\+[\w-]+',
        r't\.me/joinchat/[\w-]+',
    ]
    
    for pattern in telegram_patterns:
        if re.search(pattern, text_lower):
            return True
    
    return False

# ======================================================
# ADMIN STATUS CHECK
# ======================================================
def is_user_admin(message):
    """User က admin ဟုတ်မဟုတ် status နဲ့ပဲစစ်ခြင်း"""
    
    chat_id = message.chat.id
    chat_type = message.chat.type
    
    if chat_type == "private":
        return True
    
    user_id = None
    if message.forward_from:
        user_id = message.forward_from.id
        print(f"📩 Forwarded from user: {user_id}")
    elif message.from_user:
        user_id = message.from_user.id
        print(f"👤 Direct from user: {user_id}")
    
    if not user_id:
        print(f"⚠️ No user ID found")
        return True
    
    if user_id == 1087968824:
        print(f"✅ Anonymous admin bot detected - treating as admin")
        return True
    
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
        return True

# ======================================================
# PRE-DEFINED AUTHORS WITH LINKS
# ======================================================
AUTHOR_LINKS = {
    "ကလျာ(ဝိဇ္ဇာ၊သိပ္ပံ)": "https://t.me/sharebykosoemoe/9650",
    "ကံချွန်": "https://t.me/sharebykosoemoe/9891",
}

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
        "စာအုပ်ရှာဖွေဖို့ <b>စာရေးဆရာ</b>အမည်လေးကို ပြောပြပေးပါ ကူညီရှာပေးပါ့မယ်...💕"
    ]
    return random.choice(replies)

# ======================================================
# AUTHOR DETECTION SYSTEM
# ======================================================
def detect_author(text):
    """စာသားထဲက သတ်မှတ်ထားတဲ့ စာရေးဆရာကို ရှာဖွေခြင်း"""
    if not text:
        return None
    
    for author_name in AUTHOR_LINKS.keys():
        if author_name in text:
            return {
                "name": author_name,
                "link": AUTHOR_LINKS[author_name]
            }
    
    return None

# ======================================================
# AUTHOR REPLY TEMPLATE
# ======================================================
def get_author_reply(author_info):
    """စာရေးဆရာအတွက် ပုံသေစာပြန်ခြင်း"""
    
    author_name = author_info["name"]
    author_link = author_info["link"]
    
    reply = f"""
📚 <b>{author_name} 📚</b>

<code>စာရေးဆရာ {author_name}</code> ၏ စာအုပ်များဖတ်ရှုရန် ✨

🔗 {author_link}

🌸 စာဖတ်ချစ်သူလေးရေ... 
ပျော်ရွှင်စရာဖတ်ရှုချိန်လေးဖြစ်ပါစေ... 🥰
"""
    
    return reply

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
    
    user_message = message.text or message.caption or ""
    
    author_info = detect_author(user_message)
    
    if author_info:
        print(f"📚 Author detected: {author_info['name']}")
        try:
            reply_text = get_author_reply(author_info)
            bot.reply_to(
                message, 
                reply_text, 
                parse_mode="HTML",
                disable_web_page_preview=False
            )
            print(f"✅ Sent author-specific reply")
            return
        except Exception as e:
            print(f"❌ Author reply error: {e}")
    
    if 'စာအုပ်' in user_message:
        print(f"📚 'စာအုပ်' keyword detected")
        try:
            bot.reply_to(message, get_random_book_reply(), parse_mode="HTML")
            print(f"✅ Replied with random book suggestion")
            return
        except Exception as e:
            print(f"❌ Reply error: {e}")
    
    if is_user_admin(message):
        print(f"✅ ADMIN USER - NO ACTION")
        return
    
    allowed_patterns = [
        r'tg://user\?id=\d+',
        r't\.me/\d+',
        r'telegram\.me/\d+',
        r'@oscar_libray_bot',
        r'@oscarhelpservices',
    ]
    
    is_allowed = False
    for pattern in allowed_patterns:
        if re.search(pattern, user_message, re.IGNORECASE):
            print(f"✅ Allowed link: {pattern}")
            is_allowed = True
            break
    
    if not is_allowed and is_link(user_message):
        print(f"🚫 BLOCKED LINK DETECTED - DELETING")
        try:
            bot.delete_message(message.chat.id, message.message_id)
            
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
# /SHOWPOST COMMAND - NEW
# ======================================================
@bot.message_handler(commands=['showpost'])
def show_post_preview(message):
    """Show preview of birthday post"""
    print(f"📊 /showpost command from user: {message.from_user.id}")
    
    try:
        print("🎨 Preparing birthday post preview...")
        
        # Get Myanmar time
        myanmar_time = get_myanmar_time()
        current_date = myanmar_time.strftime("%B %d")
        
        # Prepare the post
        caption = BIRTHDAY_CAPTION_TEMPLATE.format(current_date=current_date)
        birthday_image = get_next_birthday_image()
        
        # Show stats
        stats_text = f"""
📊 <b>BIRTHDAY POST PREVIEW</b>
📅 Date: {current_date}
🕐 Time: {myanmar_time.strftime("%H:%M:%S")} (Myanmar Time)

📢 <b>Target Channels:</b> {len(MANUAL_CHANNEL_IDS)}
👥 <b>Active Groups:</b> {len(active_groups)}
🖼️ <b>Image:</b> {current_birthday_index}/{len(BIRTHDAY_IMAGES)}

<b>Will post to:</b>
1️⃣ Fixed Channels (4 channels)
2️⃣ All Admin Groups ({len(active_groups)} groups found)

<b>Auto-post schedule:</b>
✅ Daily at 8:00 AM Myanmar Time
✅ Next post: Tomorrow 8:00 AM

<b>Caption Preview:</b>
{caption[:200]}...
        """
        
        # Send preview to user
        bot.send_message(message.chat.id, stats_text, parse_mode="HTML")
        
        # Send the actual image with caption
        print("🖼️ Sending preview image...")
        bot.send_photo(
            message.chat.id,
            birthday_image,
            caption=caption,
            parse_mode="HTML"
        )
        
        print("✅ Post preview sent successfully")
        
    except Exception as e:
        error_msg = f"❌ Error showing post preview: {e}"
        print(error_msg)
        bot.reply_to(message, error_msg)

# ======================================================
# /TESTBIRTHDAY COMMAND - FOR TESTING
# ======================================================
@bot.message_handler(commands=['testbirthday'])
def test_birthday_command(message):
    """Manual test for birthday post"""
    print(f"🧪 /testbirthday command from user: {message.from_user.id}")
    
    try:
        print("🧪 MANUAL BIRTHDAY TEST TRIGGERED!")
        
        # Send test message
        test_msg = bot.reply_to(message, "🧪 Testing birthday post system...")
        
        # Trigger the birthday post
        send_birthday_to_all_chats()
        
        # Update message
        bot.edit_message_text(
            "✅ Birthday post test completed!\nCheck channels and groups for posts.",
            message.chat.id,
            test_msg.message_id
        )
        
        print("✅ Manual birthday test completed")
        
    except Exception as e:
        error_msg = f"❌ Test failed: {e}"
        print(error_msg)
        bot.reply_to(message, error_msg)

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
# /STATUS COMMAND - NEW
# ======================================================
@bot.message_handler(commands=['status'])
def bot_status(message):
    """Show bot status and next post time"""
    
    try:
        myanmar_time = get_myanmar_time()
        current_time = myanmar_time.strftime("%H:%M:%S")
        current_date = myanmar_time.strftime("%Y-%m-%d")
        
        # Calculate next post time
        now = myanmar_time
        target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)
        
        if now > target_time:
            target_time += timedelta(days=1)
        
        time_until = target_time - now
        hours = int(time_until.total_seconds() // 3600)
        minutes = int((time_until.total_seconds() % 3600) // 60)
        
        status_text = f"""
<b>🤖 BOT STATUS REPORT</b>

<b>⏰ Current Myanmar Time:</b> {current_time}
<b>📅 Current Date:</b> {current_date}
<b>📍 Timezone:</b> Asia/Yangon

<b>🎂 BIRTHDAY POST SYSTEM:</b>
<b>Last Post Date:</b> {last_birthday_post_date or "Never"}
<b>Next Post:</b> Tomorrow at 8:00 AM
<b>Time Until Next Post:</b> {hours}h {minutes}m

<b>📊 STATISTICS:</b>
<b>Fixed Channels:</b> {len(MANUAL_CHANNEL_IDS)}
<b>Active Groups:</b> {len(active_groups)}
<b>Birthday Images:</b> {len(BIRTHDAY_IMAGES)}
<b>Current Image Index:</b> {current_birthday_index}

<b>🔧 COMMANDS:</b>
• /showpost - Preview birthday post
• /testbirthday - Test post immediately
• /status - This status report
• /myid - Show your Telegram ID
"""
        
        bot.reply_to(message, status_text, parse_mode="HTML")
        print(f"📊 Status report sent to {message.from_user.id}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error getting status: {e}")

# ======================================================
# PRIVATE CHAT HANDLER
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_private_messages(message):
    if message.text and message.text.startswith('/'):
        return
    
    user_message = message.text or ""
    
    print(f"\n📱 PRIVATE MESSAGE")
    print(f"👤 From: {message.from_user.first_name}")
    print(f"💬 Text: {user_message}")
    
    author_info = detect_author(user_message)
    
    if author_info:
        print(f"📚 Author detected in private: {author_info['name']}")
        try:
            reply_text = get_author_reply(author_info)
            bot.send_message(
                message.chat.id, 
                reply_text, 
                parse_mode="HTML",
                disable_web_page_preview=False
            )
            print(f"✅ Sent author reply in private chat")
            return
        except Exception as e:
            print(f"❌ Private author reply error: {e}")
    
    if 'စာအုပ်' in user_message:
        print(f"📚 'စာအုပ်' keyword detected in private")
        try:
            bot.send_message(message.chat.id, get_random_book_reply(), parse_mode="HTML")
            print(f"✅ Sent book reply in private")
            return
        except Exception as e:
            print(f"❌ Private book reply error: {e}")

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

Fic၊ ကာတွန်း၊ သည�ထိပ်ရင်ဖို 
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

AUTHOR_LINKS_MENU = {
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
    url = AUTHOR_LINKS_MENU.get(key)
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
@app.route("/webhook", methods=['POST'])
def webhook():
    print(f"📨 WEBHOOK RECEIVED - {datetime.now()}")
    
    try:
        if request.method == 'POST':
            json_data = request.get_json()
            if json_data:
                update = telebot.types.Update.de_json(json_data)
                
                def process_update():
                    try:
                        bot.process_new_updates([update])
                        print(f"✅ UPDATE PROCESSED")
                    except Exception as e:
                        print(f"❌ Error in bot.process_new_updates: {e}")
                
                thread = threading.Thread(target=process_update)
                thread.daemon = True
                thread.start()
                
        return "OK", 200
        
    except Exception as e:
        print(f"💥 WEBHOOK ERROR: {e}")
        return "OK", 200

@app.route("/", methods=['GET', 'POST'])  
def index():
    print("🌐 Health check received")
    return "✅ Bot is running...", 200

# ===============================
# WEBHOOK SETUP
# ===============================
print("\n🔄 SETTING UP WEBHOOK...")
try:
    print("🗑️ Removing existing webhook...")
    bot.remove_webhook()
    time.sleep(2)
    
    print(f"🔧 Setting webhook to: {WEBHOOK_URL}")
    bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=None,
        max_connections=100,
        allowed_updates=["message", "callback_query", "chat_member", "my_chat_member"],
        timeout=60
    )
    
    time.sleep(1)
    webhook_info = bot.get_webhook_info()
    print(f"✅ WEBHOOK SET SUCCESSFULLY")
    print(f"🎯 Webhook URL: {webhook_info.url}")
    print(f"🎯 Pending updates: {webhook_info.pending_update_count}")
        
except Exception as e:
    print(f"💥 WEBHOOK SETUP ERROR: {e}")

# ===============================
# BOT STATUS
# ===============================
print("\n" + "="*60)
print("🎂 BOT STATUS SUMMARY")
print("="*60)
myanmar_time = get_myanmar_time()
print(f"⏰ Current Myanmar Time: {myanmar_time.strftime('%H:%M:%S')}")
print(f"📅 Current Date: {myanmar_time.strftime('%Y-%m-%d')}")
print(f"📢 Fixed Channels: {len(MANUAL_CHANNEL_IDS)} channels")
print(f"🖼️ Birthday Images: {len(BIRTHDAY_IMAGES)} images")
print(f"📚 'စာအုပ်' Auto Reply: ENABLED")
print(f"👑 Admin Check: By STATUS (not ID)")
print(f"🔗 Link Blocker: ENABLED for non-admins")

print("\n📖 AUTHOR AUTO-REPLY SYSTEM")
print("="*60)
print("✅ 'စာအုပ်' keyword: Random book reply")
print("✅ 'ကလျာ(ဝိဇ္ဇာ၊သိပ္ပံ)': Link reply")
print("✅ 'ကံချွန်': Link reply")

print("\n🎂 BIRTHDAY POST SYSTEM")
print("="*60)
print("✅ Daily at 8:00 AM (Myanmar Time)")
print(f"✅ {len(BIRTHDAY_IMAGES)} rotating images")
print(f"✅ Sending to {len(MANUAL_CHANNEL_IDS)} fixed channels")
print("✅ AUTO DISCOVERY: Will send to ALL admin groups")
print("✅ Active groups tracking: Yes")
print("✅ Admin check before posting: Yes")

print("\n🔧 NEW COMMANDS ADDED:")
print("="*60)
print("✅ /showpost - Birthday post preview")
print("✅ /testbirthday - Test post immediately")
print("✅ /status - Bot status report")
print("✅ /myid - Show your Telegram ID")
print("✅ /admincheck - Check admin status")

print("\n📊 BIRTHDAY POST STRATEGY:")
print("="*60)
print("1. Fixed Channels 4ခုကို တင်မယ်")
print("2. Bot admin ဖြစ်တဲ့ group/supergroup အားလုံးကို တင်မယ်")
print("3. Auto-discover လုပ်ပြီး တင်မယ်")
print("4. Bot ရောက်တဲ့နေရာတိုင်း track လုပ်မယ်")
print("5. Admin မဟုတ်ရင် group မှာ link တွေ block လုပ်မယ်")

print("\n🚀 Bot is now LIVE and READY!")
print("="*60)

# ===============================
# RUN WITH FLASK
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🌐 Starting Flask server on port {port}")
    
    import sys
    sys.stdout.flush()
    
    app.run(host="0.0.0.0", port=port, debug=False)
