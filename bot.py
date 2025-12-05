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
OWNER_ID = 6272937931  
ADMIN_IDS = [6904606472, 6272937931]   # Admin ID list

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
ကိုယ်၏ကျန်းမာခြင်း စိတ်၏ချမ်းသာခြင်းများနဲ့ပြည့်စုံပြီး လိုအပ်ချက်လိုအင်ဆန္ဒများ လည်းပြည့်ဝပါစေ...

အနာဂတ်မှာ 🤍
နားလည်မှု များစွာနဲ့ 🍒
အရင်ကထက်ပိုပိုပြီး 💕
ချစ်နိုင်ကြပါစေ 💞

ချစ်ရတဲ့မိသားစုနဲ့အတူ ပျော်ရွှင်ရသောနေ့ရက်တွေကို ထာဝရပိုင်ဆိုင်နိုင်ပါစေ အမြဲဆုတောင်းပေးပါတယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊
<b>🌼 Oscar's Library 🌼</b> 
#oscaradminteam"""

# ===============================
# MANUAL CHANNEL ID CONFIGURATION
# ===============================
MANUAL_CHANNEL_IDS = [-1002150199369]
print(f"📢 Target Channels: {MANUAL_CHANNEL_IDS}")

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
# IMPROVED TIME CHECK SYSTEM
# ===============================
def should_send_birthday_post():
    try:
        myanmar_time = get_myanmar_time()
        current_time = myanmar_time.strftime("%H:%M")
        current_date = myanmar_time.strftime("%Y-%m-%d")
        print(f"⏰ Time check: {current_time} (Myanmar Time) - Date: {current_date}")
        if current_time.startswith("08:"):
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
# IMPROVED CHANNEL POSTING SYSTEM
# ===============================
def send_to_target_channels():
    results = []
    if not MANUAL_CHANNEL_IDS:
        print("❌ No channels configured")
        return results
    myanmar_time = get_myanmar_time()
    current_date = myanmar_time.strftime("%B %d")
    caption = BIRTHDAY_CAPTION_TEMPLATE.format(current_date=current_date)
    print(f"🎂 Sending to {len(MANUAL_CHANNEL_IDS)} channels...")
    for channel_id in MANUAL_CHANNEL_IDS:
        try:
            print(f"📡 Attempting to send to channel: {channel_id}")
            chat = bot.get_chat(channel_id)
            print(f"📢 Channel info: {chat.title}")
            chat_member = bot.get_chat_member(channel_id, bot.get_me().id)
            print(f"👑 Bot role in channel: {chat_member.status}")
            if chat_member.status not in ['administrator', 'creator']:
                error_msg = "Bot is not admin in channel"
                print(f"❌ {error_msg}")
                results.append((channel_id, False, error_msg))
                continue
            print(f"🖼️ Sending photo to channel {channel_id}...")
            bot.send_photo(
                channel_id,
                BIRTHDAY_IMAGE_URL,
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
# GROUP DISCOVERY AND POSTING
# ===============================
def discover_all_admin_chats():
    admin_chats = set()
    try:
        print("🕵️ Auto-discovering admin chats...")
        for chat_id in list(active_groups):
            try:
                chat_member = bot.get_chat_member(chat_id, bot.get_me().id)
                if chat_member.status in ['administrator', 'creator']:
                    try:
                        bot.send_chat_action(chat_id, 'typing')
                        admin_chats.add(chat_id)
                        print(f"✅ Admin chat found: {chat_id}")
                    except Exception as e:
                        print(f"❌ No send permission in {chat_id}: {e}")
                        active_groups.discard(chat_id)
            except Exception as e:
                print(f"❌ Cannot access chat {chat_id}: {e}")
                active_groups.discard(chat_id)
        print(f"🎯 Total admin groups discovered: {len(admin_chats)}")
        return list(admin_chats)
    except Exception as e:
        print(f"❌ Admin discovery error: {e}")
        return list(active_groups)

def send_to_groups(admin_groups):
    success_count = 0
    failed_groups = []
    myanmar_time = get_myanmar_time()
    current_date = myanmar_time.strftime("%B %d")
    caption = BIRTHDAY_CAPTION_TEMPLATE.format(current_date=current_date)
    print(f"🎂 Starting group posts to {len(admin_groups)} groups...")
    for i, chat_id in enumerate(admin_groups):
        try:
            if i > 0:
                time.sleep(1)
            print(f"📤 Sending to group {i+1}/{len(admin_groups)}: {chat_id}")
            bot.send_photo(
                chat_id,
                BIRTHDAY_IMAGE_URL,
                caption=caption,
                parse_mode="HTML"
            )
            success_count += 1
            print(f"✅✅✅ [{i+1}/{len(admin_groups)}] Sent to group: {chat_id}")
        except Exception as e:
            error_msg = str(e)
            print(f"❌❌❌ [{i+1}/{len(admin_groups)}] Failed for group {chat_id}: {error_msg}")
            failed_groups.append((chat_id, error_msg))
            if any(x in error_msg for x in ["Forbidden", "blocked", "no rights", "kicked"]):
                active_groups.discard(chat_id)
    return success_count, failed_groups

def send_birthday_to_all_chats():
    global post_in_progress
    if post_in_progress:
        print("⚠️ Post already in progress, skipping...")
        return
    post_in_progress = True
    try:
        print("🎂🎂🎂 STARTING BIRTHDAY POSTS 🎂🎂🎂")
        total_success = 0
        if MANUAL_CHANNEL_IDS:
            print("📢 Posting to channels...")
            channel_results = send_to_target_channels()
            for channel_id, success, error in channel_results:
                if success:
                    total_success += 1
                    print(f"✅ Channel {channel_id}: SUCCESS")
                else:
                    print(f"❌ Channel {channel_id}: FAILED - {error}")
        admin_groups = discover_all_admin_chats()
        print(f"👥 Found {len(admin_groups)} admin groups")
        if admin_groups:
            print(f"👥 Posting to {len(admin_groups)} groups...")
            groups_success, groups_failed = send_to_groups(admin_groups)
            total_success += groups_success
            print(f"✅ Groups: {groups_success} successful, {len(groups_failed)} failed")
        else:
            print("ℹ️ No admin groups found to post")
        total_targets = len(MANUAL_CHANNEL_IDS) + len(admin_groups)
        print(f"🎉🎉🎉 BIRTHDAY POSTS COMPLETED: {total_success}/{total_targets} chats 🎉🎉🎉")
    except Exception as e:
        print(f"💥💥💥 BIRTHDAY SYSTEM ERROR: {e}")
    finally:
        post_in_progress = False

# ===============================
# SCHEDULER SYSTEM
# ===============================
def birthday_scheduler():
    print("🎂 BIRTHDAY SCHEDULER STARTED!")
    print("⏰ Will post daily throughout 8:00 AM hour (Myanmar Time)")
    print(f"📢 Target Channels: {len(MANUAL_CHANNEL_IDS)}")
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
# UPDATED LINK DETECTION SYSTEM
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
    # @ နဲ့စပြီး စာလုံး၊ ဂဏန်း၊ underscore တွေပါတဲ့ username
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

def has_link_api(message):
    """Message ထဲက link/username အားလုံးကို စစ်ဆေးခြင်း - Forwarded messages အပါအဝင်"""
    
    # Debug logging
    print(f"🔍 Checking message from {message.from_user.id if message.from_user else 'unknown'}")
    
    # 1. Direct text ထဲက link စစ်ဆေးခြင်း
    if message.text and is_link(message.text):
        print(f"✅ Direct text link found: {message.text[:50]}")
        return True
    
    # 2. Caption ထဲက link စစ်ဆေးခြင်း
    if message.caption and is_link(message.caption):
        print(f"✅ Caption link found: {message.caption[:50]}")
        return True
    
    # 3. Message entities စစ်ဆေးခြင်း (ဒါက forwarded messages အတွက် အရေးကြီးပါတယ်)
    try:
        if message.entities:
            for entity in message.entities:
                if entity.type in ["url", "text_link"]:
                    print(f"✅ Entity link found: {entity.type}")
                    return True
    except Exception as e:
        print(f"⚠️ Error checking entities: {e}")
        pass
    
    # 4. Caption entities စစ်ဆေးခြင်း
    try:
        if message.caption_entities:
            for entity in message.caption_entities:
                if entity.type in ["url", "text_link"]:
                    print(f"✅ Caption entity link found: {entity.type}")
                    return True
    except Exception as e:
        print(f"⚠️ Error checking caption entities: {e}")
        pass
    
    # 5. Forwarded messages အတွက် အထူးစစ်ဆေးခြင်း
    if message.forward_from_chat or message.forward_from:
        print(f"📩 Forwarded message detected")
        
        # Forwarded message ရဲ့ text ကို ရယူကြိုးစားခြင်း
        forwarded_text = ""
        
        if message.text:
            forwarded_text = message.text
            print(f"📩 Forwarded text: {forwarded_text[:100]}")
        elif message.caption:
            forwarded_text = message.caption
            print(f"📩 Forwarded caption: {forwarded_text[:100]}")
        
        # Forwarded chat info ရှိရင် log ထုတ်ခြင်း
        if message.forward_from_chat:
            print(f"📩 Forwarded from: {message.forward_from_chat.title} (ID: {message.forward_from_chat.id})")
        
        if message.forward_from:
            print(f"📩 Forwarded from user: {message.forward_from.first_name}")
        
        # Forwarded text ထဲမှာ link ရှိမရှိစစ်ဆေးခြင်း
        if forwarded_text and is_link(forwarded_text):
            print(f"✅ Forwarded link found: {forwarded_text[:50]}")
            return True
    
    # 6. Additional check: Message ထဲက text အားလုံးကို ပေါင်းပြီး @username ရှာခြင်း
    all_text = ""
    if message.text:
        all_text += message.text + " "
    if message.caption:
        all_text += message.caption + " "
    
    if all_text:
        # @username pattern အတွက် ထပ်စစ်ဆေးခြင်း
        usernames = re.findall(r'@[a-zA-Z0-9_]{4,}', all_text)
        if usernames:
            print(f"✅ Usernames found in text: {usernames}")
            return True
    
    print(f"❌ No links found in message")
    return False

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
# 1️⃣ GROUP WELCOME SYSTEM (FIXED VERSION)
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
            # Use URL instead of local file
            print(f"🖼️ Sending welcome image from URL...")
            bot.send_photo(
                message.chat.id, 
                WELCOME_IMAGE_URL, 
                caption=caption,
                reply_markup=welcome_kb,
                parse_mode="HTML"
            )
            print(f"✅ Welcome message sent successfully")
        except Exception as e:
            print(f"❌ Welcome image error: {e}")
            # Fallback: Send text-only welcome message
            try:
                bot.send_message(
                    message.chat.id,
                    caption,
                    reply_markup=welcome_kb,
                    parse_mode="HTML"
                )
                print(f"✅ Sent text-only welcome message")
            except Exception as e2:
                print(f"❌ Failed to send welcome message: {e2}")

# ======================================================
# 🌟🌟🌟 UNIFIED GROUP HANDLER (FINAL FIXED VERSION) 🌟🌟🌟
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"], content_types=['text', 'photo', 'video', 'document', 'audio'])
def handle_all_group_activity(message):
    """Group အတွင်းက ဖြစ်တဲ့ အရာအားလုံးကို စီမံတဲ့ စုပေါင်းထားတဲ့ Handler"""
    
    # Command နဲ့ new members ကို ကျော်ပါ
    if message.text and message.text.startswith('/'):
        return
    if message.new_chat_members:
        return

    track_active_group(message.chat.id)
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_name = message.from_user.first_name

    print(f"🔍 Processing message from {user_name} ({user_id}) in chat {chat_id}")

    # 1️⃣ GLOBAL ADMIN CHECK (ပထမဆုံးစစ်ပါ) - BYPASS ALL CHECKS
    if user_id == OWNER_ID or user_id in ADMIN_IDS:
        print(f"✅✅✅ GLOBAL ADMIN BYPASS: User {user_name} ({user_id}) is GLOBAL ADMIN. NO ACTION.")
        return

    # 2️⃣ LOCAL ADMIN CHECK (ဒုတိယအနေဲ့ စစ်ပါ) - BYPASS ALL CHECKS
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            print(f"✅✅✅ LOCAL ADMIN BYPASS: User {user_name} ({user_id}) is LOCAL ADMIN (status: {chat_member.status}). NO ACTION.")
            return
        else:
            print(f"❌ User {user_name} ({user_id}) is NOT an admin (status: {chat_member.status})")
            # ဒီနေရာမှာ non-admin ဖြစ်လို့ ဆက်စစ်မယ်
    except Exception as e:
        print(f"⚠️ Admin check error: {e}")
        # Admin check မအောင်မြင်ရင် non-admin လို့မှတ်ယူပြီး ဆက်စစ်မယ်

    # --- ဒီအောက်ကကုဒ်တွေက NON-ADMIN တွေအတွက်ပဲ run မယ် ---

    # 1️⃣ "စာအုပ်" keyword စစ်ပါ (RANDOM REPLY)
    if message.text and 'စာအုပ်' in message.text:
        print(f"📚 Non-admin {user_name} ({user_id}) typed 'စာအုပ်'. Sending reply.")
        try:
            reply_text = get_random_book_reply()
            bot.reply_to(message, reply_text, parse_mode="HTML")
            print(f"✅ Replied to {user_name} ({user_id}).")
        except Exception as e:
            print(f"❌ Failed to reply to {user_name} ({user_id}): {e}")
        return

    # 2️⃣ Link ရှိမရှိစစ်ပါ (Forwarded လည်း အပါအဝင်)
    if has_link_api(message):
        print(f"🚫🚫🚫 Non-admin {user_name} ({user_id}) posted a link. DELETING MESSAGE.")
        try:
            bot.delete_message(chat_id, message.message_id)
            warning_msg = f'⚠️ [{message.from_user.first_name}](tg://user?id={user_id}) 💢\n\n**Link🔗 များကို ပိတ်ထားပါတယ်** 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် **Admin** ကို ဆက်သွယ်ပါနော်...'
            bot.send_message(chat_id, warning_msg, parse_mode="Markdown")
            print(f"✅ Deleted message from non-admin {user_name} ({user_id})")
        except Exception as e:
            print(f"❌ Error deleting non-admin's link: {e}")
        return

    # 3️⃣ Normal Message - No action
    print(f"--- Message from {user_name} ({user_id}) was normal. No action taken. ---")

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
# PRIVATE CHAT MESSAGE HANDLER (FIXED VERSION)
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_private_messages(message):
    # GLOBAL ADMIN BYPASS - PRIVATE CHAT
    if message.from_user.id == OWNER_ID or message.from_user.id in ADMIN_IDS:
        print(f"✅ Private chat: Global admin {message.from_user.id} bypassed")
        return
    
    if message.text and message.text.startswith('/'):
        return
    
    # Private chat တွင် "စာအုပ်" keyword အတွက် RANDOM REPLY
    if message.text and 'စာအုပ်' in message.text:
        print(f"📚 Private chat မှာ 'စာအုပ်' keyword ရှာတွေ့: {message.from_user.id}")
        try:
            reply_text = get_random_book_reply()
            bot.send_message(message.chat.id, reply_text, parse_mode="HTML")
            print(f"✅ Private chat မှာ RANDOM book reply ပြန်လိုက်ပြီ")
        except Exception as e:
            print(f"❌ Private chat မှာ reply မပြန်နိုင်: {e}")
        return
    
    # Private chat တွင် link စစ်ဆေးခြင်း (NON-ADMIN များအတွက်သာ)
    if message.text and is_link(message.text):
        print(f"🔗 Private chat: Non-admin {message.from_user.id} tried to send link")
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "⚠️ Link မပို့နိုင်ပါဘူး…")
        except Exception as e:
            print(f"❌ Private chat delete error: {e}")
        return
    
    if message.forward_from_chat or message.forward_from:
        if message.text and is_link(message.text):
            bot.send_message(
                message.chat.id, 
                f"<b>🔗 Forwarded link detected:</b>\n{message.text}\n\n<b>I can see the forwarded link! ✅</b>",
                parse_mode="HTML"
            )
        elif message.caption and is_link(message.caption):
            bot.send_message(
                message.chat.id, 
                f"<b>🔗 Forwarded media with link:</b>\n{message.caption}\n\n<b>I can see the forwarded link! ✅</b>",
                parse_mode="HTML"
            )
        else:
            bot.send_message(
                message.chat.id, 
                "<b>📩 Forwarded message received!</b>\n\nNote: I can process links from forwarded messages in private chats.",
                parse_mode="HTML"
            )
    elif message.text and not message.text.startswith('/'):
        if is_link(message.text):
            bot.send_message(
                message.chat.id, 
                f"<b>🔗 Link detected:</b>\n{message.text}\n\n<b>This is a direct link message! ✅</b>",
                parse_mode="HTML"
            )
        else:
            bot.send_message(message.chat.id, f"<b>🤖 Auto Reply:</b>\n{message.text}", parse_mode="HTML")

# ======================================================
# FORCE POST COMMAND ONLY
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
# WEBHOOK HANDLERS WITH DEBUG
# ===============================
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    print(f"📨📨📨 WEBHOOK RECEIVED - {datetime.now()} 📨📨📨")
    print(f"📦 Method: {request.method}")
    print(f"📦 Content-Type: {request.headers.get('Content-Type')}")
    print(f"📦 Content-Length: {request.headers.get('Content-Length')}")
    
    try:
        if request.method == 'POST':
            # Get raw data first
            raw_data = request.get_data(as_text=True)
            print(f"📦 Raw data received: {len(raw_data)} chars")
            
            if raw_data:
                # Try to parse JSON
                try:
                    json_data = json.loads(raw_data)
                    print(f"✅✅✅ JSON PARSED SUCCESSFULLY!")
                    print(f"📦 Update ID: {json_data.get('update_id')}")
                    
                    # Check what type of update
                    if 'message' in json_data:
                        msg = json_data['message']
                        chat_id = msg.get('chat', {}).get('id')
                        user_id = msg.get('from', {}).get('id')
                        text = msg.get('text', '')[:100]
                        print(f"💬 MESSAGE DETECTED:")
                        print(f"   👤 User ID: {user_id}")
                        print(f"   💬 Chat ID: {chat_id}")
                        print(f"   📝 Text: {text}")
                        
                        # Check if it's admin
                        if user_id == OWNER_ID or user_id in ADMIN_IDS:
                            print(f"   👑 ADMIN USER DETECTED!")
                        else:
                            print(f"   👤 NORMAL USER DETECTED!")
                    
                    elif 'callback_query' in json_data:
                        print(f"🔄 CALLBACK QUERY DETECTED")
                    
                    # Process the update
                    update = telebot.types.Update.de_json(json_data)
                    
                    # IMPORTANT: Process in background thread
                    def process_update():
                        try:
                            bot.process_new_updates([update])
                            print(f"✅✅✅ UPDATE PROCESSED SUCCESSFULLY")
                        except Exception as e:
                            print(f"❌❌❌ Error in bot.process_new_updates: {e}")
                            import traceback
                            traceback.print_exc()
                    
                    # Start processing in background
                    import threading
                    thread = threading.Thread(target=process_update)
                    thread.daemon = True
                    thread.start()
                    
                    print(f"✅ Update queued for processing")
                    
                except json.JSONDecodeError as e:
                    print(f"❌❌❌ JSON DECODE ERROR: {e}")
                    print(f"📦 First 500 chars of raw data:")
                    print(raw_data[:500])
                except Exception as e:
                    print(f"❌❌❌ GENERAL ERROR: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"❌ No data received")
        else:
            print(f"⚠️ Not a POST request")
            
        return "OK", 200
        
    except Exception as e:
        print(f"💥💥💥 CRITICAL ERROR in webhook handler: {e}")
        import traceback
        traceback.print_exc()
        return "OK", 200

@app.route("/test-webhook", methods=['POST', 'GET'])
def test_webhook():
    """Test webhook manually"""
    print(f"🧪 TEST WEBHOOK ENDPOINT CALLED")
    
    # Simulate a test update
    test_update = {
        "update_id": 999999999,
        "message": {
            "message_id": 123,
            "from": {
                "id": 6272937931,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": 6272937931,
                "first_name": "Test",
                "username": "testuser",
                "type": "private"
            },
            "date": 1764961559,
            "text": "/start"
        }
    }
    
    try:
        update = telebot.types.Update.de_json(test_update)
        bot.process_new_updates([update])
        return "✅ Test webhook processed", 200
    except Exception as e:
        return f"❌ Error: {e}", 500

@app.route("/", methods=['GET', 'POST'])  
def index():
    print("🌐 Health check received")
    return "✅ Bot is running...", 200

# ===============================
# MANUAL WEBHOOK SETUP WITH VERIFICATION
# ===============================
print("🔄 SETTING UP WEBHOOK...")
try:
    # Remove existing webhook
    print("🗑️ Removing existing webhook...")
    removed = bot.remove_webhook()
    print(f"🗑️ Remove result: {removed}")
    time.sleep(2)
    
    # Set new webhook
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
        
        # Verify webhook
        time.sleep(1)
        try:
            webhook_info = bot.get_webhook_info()
            print(f"🎯 Current Webhook URL: {webhook_info.url}")
            print(f"🎯 Pending updates: {webhook_info.pending_update_count}")
            print(f"🎯 Last error: {webhook_info.last_error_message}")
            
            if webhook_info.url == WEBHOOK_URL:
                print(f"🎯✅ Webhook verified and active!")
            else:
                print(f"🎯❌ Webhook URL mismatch!")
                print(f"🎯 Expected: {WEBHOOK_URL}")
                print(f"🎯 Got: {webhook_info.url}")
        except Exception as e:
            print(f"🎯⚠️ Cannot verify webhook: {e}")
            
    else:
        print("❌❌❌ WEBHOOK SET FAILED")
        
except Exception as e:
    print(f"💥💥💥 WEBHOOK SETUP ERROR: {e}")
    import traceback
    traceback.print_exc()

print("🎂 Birthday Scheduler: ACTIVE")
print("⏰ Will post daily at 8:00 AM Myanmar Time")
print("📚 'စာအုပ်' Auto Reply: RANDOM REPLIES ENABLED (၈မျိုး)")
print("🔗 Link Blocker: ENABLED (UNIFIED HANDLER - FINAL VERSION)")
print("🎲 Random Function: ACTIVE - Different replies each time")
print("👋 Welcome System: FIXED (using online image URL)")
print("🔧 All systems ready!")
print("🚀 Bot is now LIVE!")
print("💡 Available Commands: /start, /forcepost")
print("🔒 Admin Protection: GLOBAL ADMIN IDs -", ADMIN_IDS)
print("🔒 Owner ID:", OWNER_ID)
print("🌐 Test Webhook: https://oscar-library-bot.onrender.com/test-webhook")

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
    print(f"🔒 Admin IDs: {ADMIN_IDS}")
    print(f"👑 Owner ID: {OWNER_ID}")
    print("="*60 + "\n")
    
    # Force print to stdout
    import sys
    sys.stdout.flush()
    
    app.run(host="0.0.0.0", port=port, debug=True)
