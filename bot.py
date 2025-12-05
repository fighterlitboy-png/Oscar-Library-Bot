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
import logging
import random

# ===============================
# DEBUG MODE - FORCE LOGGING
# ===============================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
print("🚀🚀🚀 BOT STARTING UP 🚀🚀🚀", flush=True)
print("Initializing Oscar Library Bot...", flush=True)

# ===============================
# BOT TOKEN & URL
# ===============================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4')
WEBHOOK_URL = "https://oscar-library-bot.onrender.com/" + BOT_TOKEN
PING_URL = "https://oscar-library-bot.onrender.com"
OWNER_ID = 6272937931  
ADMIN_IDS = [6904606472, 6272937931]   # Admin ID list

print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...", flush=True)
print(f"🌐 Webhook URL: {WEBHOOK_URL}", flush=True)

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

ချစ်ရတဲ့မိသားစုနဲ့အတူ ပျော်ရွှင်ရသောနေ့ရက်တွေကို ထာဝရပိုင်ဆိုင်နိုင်ပါစေ အမြဲဆုတောင်းပေးပါမယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊
<b>🌼 Oscar's Library 🌼</b> 
#oscaradminteam"""

# ===============================
# MANUAL CHANNEL ID CONFIGURATION
# ===============================
MANUAL_CHANNEL_IDS = [-1002150199369]
print(f"📢 Target Channels: {MANUAL_CHANNEL_IDS}", flush=True)

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
    print("🌐 Keep-alive thread started", flush=True)
    while True:
        try:
            response = requests.get(PING_URL, timeout=10)
            print("🌐 Keep-alive ping sent - Status:", response.status_code, flush=True)
        except Exception as e:
            print(f"🌐 Keep-alive error: {e}", flush=True)
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
        print(f"⏰ Time check: {current_time} (Myanmar Time) - Date: {current_date}", flush=True)
        if current_time.startswith("08:"):
            global last_birthday_post
            if last_birthday_post != current_date:
                last_birthday_post = current_date
                print("✅✅✅ BIRTHDAY POST TRIGGERED! ✅✅✅", flush=True)
                return True
        return False
    except Exception as e:
        print(f"⏰ Time check error: {e}", flush=True)
        return False

# ===============================
# IMPROVED CHANNEL POSTING SYSTEM
# ===============================
def send_to_target_channels():
    results = []
    if not MANUAL_CHANNEL_IDS:
        print("❌ No channels configured", flush=True)
        return results
    myanmar_time = get_myanmar_time()
    current_date = myanmar_time.strftime("%B %d")
    caption = BIRTHDAY_CAPTION_TEMPLATE.format(current_date=current_date)
    print(f"🎂 Sending to {len(MANUAL_CHANNEL_IDS)} channels...", flush=True)
    for channel_id in MANUAL_CHANNEL_IDS:
        try:
            print(f"📡 Attempting to send to channel: {channel_id}", flush=True)
            chat = bot.get_chat(channel_id)
            print(f"📢 Channel info: {chat.title}", flush=True)
            chat_member = bot.get_chat_member(channel_id, bot.get_me().id)
            print(f"👑 Bot role in channel: {chat_member.status}", flush=True)
            if chat_member.status not in ['administrator', 'creator']:
                error_msg = "Bot is not admin in channel"
                print(f"❌ {error_msg}", flush=True)
                results.append((channel_id, False, error_msg))
                continue
            print(f"🖼️ Sending photo to channel {channel_id}...", flush=True)
            bot.send_photo(
                channel_id,
                BIRTHDAY_IMAGE_URL,
                caption=caption,
                parse_mode="HTML"
            )
            print(f"✅✅✅ Successfully posted to channel: {channel_id}", flush=True)
            results.append((channel_id, True, "Success"))
        except Exception as e:
            error_msg = str(e)
            print(f"❌❌❌ Channel post failed for {channel_id}: {error_msg}", flush=True)
            results.append((channel_id, False, error_msg))
    return results

# ===============================
# GROUP DISCOVERY AND POSTING
# ===============================
def discover_all_admin_chats():
    admin_chats = set()
    try:
        print("🕵️ Auto-discovering admin chats...", flush=True)
        for chat_id in list(active_groups):
            try:
                chat_member = bot.get_chat_member(chat_id, bot.get_me().id)
                if chat_member.status in ['administrator', 'creator']:
                    try:
                        bot.send_chat_action(chat_id, 'typing')
                        admin_chats.add(chat_id)
                        print(f"✅ Admin chat found: {chat_id}", flush=True)
                    except Exception as e:
                        print(f"❌ No send permission in {chat_id}: {e}", flush=True)
                        active_groups.discard(chat_id)
            except Exception as e:
                print(f"❌ Cannot access chat {chat_id}: {e}", flush=True)
                active_groups.discard(chat_id)
        print(f"🎯 Total admin groups discovered: {len(admin_chats)}", flush=True)
        return list(admin_chats)
    except Exception as e:
        print(f"❌ Admin discovery error: {e}", flush=True)
        return list(active_groups)

def send_to_groups(admin_groups):
    success_count = 0
    failed_groups = []
    myanmar_time = get_myanmar_time()
    current_date = myanmar_time.strftime("%B %d")
    caption = BIRTHDAY_CAPTION_TEMPLATE.format(current_date=current_date)
    print(f"🎂 Starting group posts to {len(admin_groups)} groups...", flush=True)
    for i, chat_id in enumerate(admin_groups):
        try:
            if i > 0:
                time.sleep(1)
            print(f"📤 Sending to group {i+1}/{len(admin_groups)}: {chat_id}", flush=True)
            bot.send_photo(
                chat_id,
                BIRTHDAY_IMAGE_URL,
                caption=caption,
                parse_mode="HTML"
            )
            success_count += 1
            print(f"✅✅✅ [{i+1}/{len(admin_groups)}] Sent to group: {chat_id}", flush=True)
        except Exception as e:
            error_msg = str(e)
            print(f"❌❌❌ [{i+1}/{len(admin_groups)}] Failed for group {chat_id}: {error_msg}", flush=True)
            failed_groups.append((chat_id, error_msg))
            if any(x in error_msg for x in ["Forbidden", "blocked", "no rights", "kicked"]):
                active_groups.discard(chat_id)
    return success_count, failed_groups

def send_birthday_to_all_chats():
    global post_in_progress
    if post_in_progress:
        print("⚠️ Post already in progress, skipping...", flush=True)
        return
    post_in_progress = True
    try:
        print("🎂🎂🎂 STARTING BIRTHDAY POSTS 🎂🎂🎂", flush=True)
        total_success = 0
        if MANUAL_CHANNEL_IDS:
            print("📢 Posting to channels...", flush=True)
            channel_results = send_to_target_channels()
            for channel_id, success, error in channel_results:
                if success:
                    total_success += 1
                    print(f"✅ Channel {channel_id}: SUCCESS", flush=True)
                else:
                    print(f"❌ Channel {channel_id}: FAILED - {error}", flush=True)
        admin_groups = discover_all_admin_chats()
        print(f"👥 Found {len(admin_groups)} admin groups", flush=True)
        if admin_groups:
            print(f"👥 Posting to {len(admin_groups)} groups...", flush=True)
            groups_success, groups_failed = send_to_groups(admin_groups)
            total_success += groups_success
            print(f"✅ Groups: {groups_success} successful, {len(groups_failed)} failed", flush=True)
        else:
            print("ℹ️ No admin groups found to post", flush=True)
        total_targets = len(MANUAL_CHANNEL_IDS) + len(admin_groups)
        print(f"🎉🎉🎉 BIRTHDAY POSTS COMPLETED: {total_success}/{total_targets} chats 🎉🎉🎉", flush=True)
    except Exception as e:
        print(f"💥💥💥 BIRTHDAY SYSTEM ERROR: {e}", flush=True)
    finally:
        post_in_progress = False

# ===============================
# SCHEDULER SYSTEM
# ===============================
def birthday_scheduler():
    print("🎂 BIRTHDAY SCHEDULER STARTED!", flush=True)
    print("⏰ Will post daily throughout 8:00 AM hour (Myanmar Time)", flush=True)
    print(f"📢 Target Channels: {len(MANUAL_CHANNEL_IDS)}", flush=True)
    last_check = None
    while True:
        try:
            current_time = get_myanmar_time()
            current_minute = current_time.strftime("%H:%M")
            if last_check != current_minute:
                last_check = current_minute
                if should_send_birthday_post():
                    print(f"🚀🚀🚀 TRIGGERING BIRTHDAY POSTS AT {current_time.strftime('%H:%M:%S')} 🚀🚀🚀", flush=True)
                    send_birthday_to_all_chats()
                else:
                    print(f"⏰ Waiting... Current time: {current_minute}", flush=True)
        except Exception as e:
            print(f"🎂 Scheduler error: {e}", flush=True)
        time.sleep(30)

print("🔄 Starting birthday scheduler thread...", flush=True)
birthday_thread = threading.Thread(target=birthday_scheduler, daemon=True)
birthday_thread.start()
print("✅ Birthday scheduler started", flush=True)

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
    import re
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
    print(f"🔍 Checking message from {message.from_user.id if message.from_user else 'unknown'}", flush=True)
    
    # 1. Direct text ထဲက link စစ်ဆေးခြင်း
    if message.text and is_link(message.text):
        print(f"✅ Direct text link found: {message.text[:50]}", flush=True)
        return True
    
    # 2. Caption ထဲက link စစ်ဆေးခြင်း
    if message.caption and is_link(message.caption):
        print(f"✅ Caption link found: {message.caption[:50]}", flush=True)
        return True
    
    # 3. Message entities စစ်ဆေးခြင်း (ဒါက forwarded messages အတွက် အရေးကြီးပါတယ်)
    try:
        if message.entities:
            for entity in message.entities:
                if entity.type in ["url", "text_link"]:
                    print(f"✅ Entity link found: {entity.type}", flush=True)
                    
                    # Get the actual link text from entity
                    if entity.type == "url" and message.text:
                        start = entity.offset
                        end = start + entity.length
                        link_text = message.text[start:end]
                        print(f"📎 URL entity text: {link_text}", flush=True)
                    
                    return True
    except Exception as e:
        print(f"⚠️ Error checking entities: {e}", flush=True)
        pass
    
    # 4. Caption entities စစ်ဆေးခြင်း
    try:
        if message.caption_entities:
            for entity in message.caption_entities:
                if entity.type in ["url", "text_link"]:
                    print(f"✅ Caption entity link found: {entity.type}", flush=True)
                    return True
    except Exception as e:
        print(f"⚠️ Error checking caption entities: {e}", flush=True)
        pass
    
    # 5. Forwarded messages အတွက် အထူးစစ်ဆေးခြင်း
    if message.forward_from_chat or message.forward_from:
        print(f"📩 Forwarded message detected", flush=True)
        
        # Forwarded message ရဲ့ text ကို ရယူကြိုးစားခြင်း
        forwarded_text = ""
        
        if message.text:
            forwarded_text = message.text
            print(f"📩 Forwarded text: {forwarded_text[:100]}", flush=True)
        elif message.caption:
            forwarded_text = message.caption
            print(f"📩 Forwarded caption: {forwarded_text[:100]}", flush=True)
        
        # Forwarded chat info ရှိရင် log ထုတ်ခြင်း
        if message.forward_from_chat:
            print(f"📩 Forwarded from: {message.forward_from_chat.title} (ID: {message.forward_from_chat.id})", flush=True)
        
        if message.forward_from:
            print(f"📩 Forwarded from user: {message.forward_from.first_name}", flush=True)
        
        # Forwarded text ထဲမှာ link ရှိမရှိစစ်ဆေးခြင်း
        if forwarded_text and is_link(forwarded_text):
            print(f"✅ Forwarded link found: {forwarded_text[:50]}", flush=True)
            return True
    
    # 6. Additional check: Message ထဲက text အားလုံးကို ပေါင်းပြီး @username ရှာခြင်း
    all_text = ""
    if message.text:
        all_text += message.text + " "
    if message.caption:
        all_text += message.caption + " "
    
    if all_text:
        # @username pattern အတွက် ထပ်စစ်ဆေးခြင်း
        import re
        usernames = re.findall(r'@[a-zA-Z0-9_]{4,}', all_text)
        if usernames:
            print(f"✅ Usernames found in text: {usernames}", flush=True)
            return True
    
    print(f"❌ No links found in message", flush=True)
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
        "စာဖတ်ချစ်သူလေး ဘယ်လိုအကြိုက်စာအုပ်မျိုးဖတ်ချင်လဲ? <b>စာရေးဆရာ</b>အမည်လေး ပြောပြပါ...🌸",
        "စာဖတ်ချစ်သူလေး ဘယ်လိုအကြိုက်စာအုပ်မျိုးဖတ်ချင်လဲ? <b>စာရေးဆရာ</b>အမည်လေး ပြောပြပါ...🌸",
        "စာအုပ်ရှာဖွေဖို့ <b>စာရေးဆရာ</b>အမည်လေးကို ပြောပြပါ ကူညီရှာပေးပါ့မယ်...💕"
    ]
    return random.choice(replies)

# ======================================================
# 1️⃣ GROUP WELCOME SYSTEM (FIXED VERSION)
# ======================================================
WELCOME_IMAGE_URL = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/welcome_photo.jpg"

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    print(f"👋 Welcome message for new member in chat: {message.chat.id}", flush=True)
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
            print(f"🖼️ Sending welcome image from URL...", flush=True)
            bot.send_photo(
                message.chat.id, 
                WELCOME_IMAGE_URL, 
                caption=caption,
                reply_markup=welcome_kb,
                parse_mode="HTML"
            )
            print(f"✅ Welcome message sent successfully", flush=True)
        except Exception as e:
            print(f"❌ Welcome image error: {e}", flush=True)
            # Fallback: Send text-only welcome message
            try:
                bot.send_message(
                    message.chat.id,
                    caption,
                    reply_markup=welcome_kb,
                    parse_mode="HTML"
                )
                print(f"✅ Sent text-only welcome message", flush=True)
            except Exception as e2:
                print(f"❌ Failed to send welcome message: {e2}", flush=True)

# ======================================================
# FIXED ADMIN CHECK FUNCTION - CORRECTED VERSION
# ======================================================
def is_admin(chat_id, user_id):
    """Check if user is admin or owner in chat - CORRECTED VERSION"""
    try:
        # Directly check user's status in chat
        chat_member = bot.get_chat_member(chat_id, user_id)
        
        if chat_member.status in ['administrator', 'creator']:
            print(f"✅ User {user_id} is admin/owner (status: {chat_member.status}) in chat {chat_id}", flush=True)
            return True
        
        print(f"❌ User {user_id} is NOT admin (status: {chat_member.status}) in chat {chat_id}", flush=True)
        return False
        
    except Exception as e:
        print(f"⚠️ Admin check error: {e}", flush=True)
        return False

# ======================================================
# 🌟🌟🌟 NEW UNIFIED GROUP HANDLER 🌟🌟🌟
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

    print(f"--- NEW MESSAGE IN GROUP {chat_id} FROM {user_name} ({user_id}) ---", flush=True)

    # 1️⃣ GLOBAL ADMIN CHECK (ပထမဆုံးစစ်ပါ)
    if user_id == OWNER_ID or user_id in ADMIN_IDS:
        print(f"✅ PASS: User {user_name} ({user_id}) is a GLOBAL ADMIN. Ignoring message completely.", flush=True)
        return

    # 2️⃣ LOCAL ADMIN CHECK (ဒုတိယအနေဲ့ စစ်ပါ)
    print(f"🔍 Checking if user {user_name} ({user_id}) is a local admin in chat {chat_id}...", flush=True)
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        if chat_member.status in ['administrator', 'creator']:
            print(f"✅ PASS: User {user_name} ({user_id}) is a LOCAL ADMIN (status: {chat_member.status}). Ignoring message completely.", flush=True)
            return
        else:
            print(f"❌ FAIL: User {user_name} ({user_id}) is NOT an admin (status: {chat_member.status}).", flush=True)
    except Exception as e:
        print(f"💥 ERROR: Could not check admin status for {user_name} ({user_id}). Error: {e}. Assuming NOT an admin.", flush=True)
        # API call မအောင်ဘဲ သူက admin မဟုတ်ဘူးလို့ ယူဆပါမယ်။

    # --- ဒေါင့်ကနေ့စွဲက အောက်က အပိုင်းတွေက Non-Admin တွေအတွက်ပဲ ---

    # 1. "စာအုပ်" keyword စစ်ပါ (RANDOM REPLY)
    if message.text and 'စာအုပ်' in message.text:
        print(f"📚 Non-admin {user_name} ({user_id}) typed 'စာအုပ်'", flush=True)
        try:
            reply_text = get_random_book_reply()
            bot.reply_to(message, reply_text, parse_mode="HTML")
            print(f"✅ Replied to {user_name} ({user_id}).", flush=True)
        except Exception as e:
            print(f"❌ Failed to reply to {user_name} ({user_id}): {e}", flush=True)
        return

    # 2. Link ရှိမရှိစ်ပါ (Forwarded လည်း အပါအဝင်)
    if has_link_api(message):
        print(f"🚫 Non-admin {user_name} ({user_id}) posted a link. DELETING MESSAGE.", flush=True)
        try:
            bot.delete_message(chat_id, message.message_id)
            warning_msg = f'⚠️ [{message.from_user.first_name}](tg://user?id={user_id}) 💢\n\n**Link🔗 များကို ပိတ်ထားပါတယ်** 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် **Admin** ကို ဆက်သွယ်ပါနော်...'
            bot.send_message(chat_id, warning_msg, parse_mode="Markdown")
        except Exception as e:
            print(f"❌ Error deleting non-admin's link: {e}", flush=True)
        return

    # 3. Normal Message
    print(f"--- Message from {user_name} ({user_id}) was normal. No action taken. ---", flush=True)

# ======================================================
# 🚨 CATCH-ALL HANDLER (FOR DEBUGGING) 🚨
# ======================================================
@bot.message_handler(func=lambda message: True)
def catch_all(message):
    """This handler should catch any message that wasn't handled by others."""
    print(f"🚨 CATCH-ALL: Received message from {message.from_user.id} in chat {message.chat.id} (type: {message.chat.type})", flush=True)
    if message.text:
        print(f"🚨 CATCH-ALL: Message text: {message.text[:100]}", flush=True)
    # We don't do anything, just log it.

# ===============================
# /START MESSAGE
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
    print(f"🔄 /start command from user: {message.from_user.id}", flush=True)
    first = message.from_user.first_name or "Friend"
    text = f"""<b>သာယာသောနေ့လေးဖြစ်ပါစေ...🌸</b>
<b>{first}</b> ...🥰
<b>🌼 Oscar's Library 🌼</b> မှကြိုဆိုပါတယ်။
စာအုပ်များရှာဖွေရန် လမ်းညွှန်ပေးမယ်...

<b>စာအုပ်ရှာဖို့ နှစ်ပေါင်းခွဲထားတယ်</b>
<b>📚 ကဏ္ဍအလိုက် 💠 ✍️စာရေးဆရာ</b>

Fic၊ ကာတွန်း၊ သည်းထိပ်ရင်ဖို 
စသည့်ကဏ္ဍများရှာဖတ်ချင်ရင် 
<b>📚 ကဏ္ဍအလိုက်</b> ကိုနှိပ်ပါ။

စာရေးဆရာအအလိုက်ရှာဖတ်ချင်ရင် 
<b>✍️စာရေးဆရာ</b> ကိုနှိပါ။

<b>💢 📖စာအုပ်ဖတ်နည်းကြည့်ပါရန် 💢</b>

⚠️ အဆင်မပြေတာရှိရင် ⚠️
<b>❓အထွေထွေမေးမြန်းရန်</b> ကို နှိပါ။"""
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("📚 ကဏ္ဍအလိုက်", callback_data="category"),
        types.InlineKeyboardButton("✍️ စာရေးဆရာ", callback_data="author_menu")
    )
    kb.row(
        types.InlineKeyboardButton("📖 စာအုပ်ဖတ်နည်းကြည့်ပါရန်", url="https://t.me/oscarhelpservices/17"),
        types.InlineKeyboardButton("📝 စာအုပ်ပြုပြင်ရန်", url="https://t.me/oscarhelpservices/29?single")
    )
    kb.row(
        types.InlineKeyboardButton("🌼 ချန်နယ်ခွဲများ", url="https://t.me/oscarhelpservices/9"),
        types.InlineKeyboardButton("⭐ Review ရေးရန်", url="https://t.me/sharebykosoemoe/13498")
    )
    kb.row(types.InlineKeyboardButton("❓ အထွေထွေမေးမြန်းရန်", url="https://t.me/kogyisoemoe"))
    bot.send_message(message.chat.id, text, reply_markup=kb, parse_mode="HTML")

# ======================================================
# PRIVATE CHAT MESSAGE HANDLER
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_private_messages(message):
    if message.text and message.text.startswith('/'):
        return
    
    # Private chat တွင် "စာအုပ်" keyword အတွက် RANDOM REPLY
    if message.text and 'စာအုပ်' in message.text:
        print(f"📚 Private chat မှာ 'စာအုပ်' keyword ရှာတွေ့: {message.from_user.id}", flush=True)
        try:
            reply_text = get_random_book_reply()
            bot.send_message(message.chat.id, reply_text, parse_mode="HTML")
            print(f"✅ Private chat မှာ RANDOM book reply ပြန်လိုက်ပြီ", flush=True)
        except Exception as e:
            print(f"❌ Private chat မှာ reply မပြန်နိုင်: {e}", flush=True)
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
# 🔗 LINK BLOCK SYSTEM (Private Chat Only)
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type not in ["group", "supergroup"], content_types=['text'])
def check_links_private(message):
    # 🟢 GLOBAL OWNER / ADMIN BYPASS
    if message.from_user.id == OWNER_ID or message.from_user.id in ADMIN_IDS:
        return

    text = message.text.lower()

    # 🔗 Link detector
    if "http://" in text or "https://" in text or "t.me/" in text:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.reply_to(message, "⚠️ Link မပို့နိုင်ပါဘူး…")
        except Exception as e:
            print("Delete error:", e, flush=True)
            pass


# ===============================
# FORCE POST COMMAND ONLY
# ===============================
@bot.message_handler(commands=['forcepost'])
def force_birthday_post(message):
    try:
        print(f"🔧 Forcepost command from: {message.from_user.id}", flush=True)
        bot.reply_to(message, "🚀 Force sending birthday posts...")
        send_birthday_to_all_chats()
        bot.reply_to(message, "✅ Force post completed!")
    except Exception as e:
        error_msg = f"❌ Force post error: {e}"
        print(error_msg, flush=True)
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
<b>📚 ကဏ္ဍအလိုက် 💠 ✍️စာရေးဆရာ</b>

Fic၊ ကာတွန်း�ည သည်းထိပ်ရင်ဖို 
စသည့်ကဏ္ဍများရှာဖတ်ချင်ရင် 
<b>📚 ကဏ္ဍအလိုက်</b> ကိုနှိပါ။

စာရေးဆရာအအလိုက်ရှာဖတ်ချင်ရင် 
<b>✍️စာရေးဆရာ</b> ကိုနှိပါ။

<b>💢 📖စာအုပ်ဖတ်နည်းကြည့်ပါရန် 💢</b>

⚠️ အဆင်မပြေတာရှိရင် ⚠️
<b>❓အထွေထွေမေးမြန်းရန်</b> ကို နှိပါ။

⚠️ အဆင်မပြေတာရှိရင် ⚠️
<b>❓အထွေထွေမေးမြန်းရန်</b> ကို နှိပါ။"""
    kb = types.InlineKeyboardMarkup()
    kb.row(
        types.InlineKeyboardButton("📚 ကဏ္ဍအလိုက်", callback_data="category"),
        types.InlineKeyboardButton("✍️ စာရေးဆရာ", callback_data="author_menu")
    )
    kb.row(
        types.InlineKeyboardButton("📖 စာအုပ်ဖတ်နည်းကြည့်ပါရန်", url="https://t.me/oscarhelpservices/17"),
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
    print(f"📨 WEBHOOK RECEIVED - {datetime.now()}", flush=True)
    try:
        if request.method == 'POST':
            json_data = request.get_json(force=True)
            if json_data:
                print(f"📦 Processing update...", flush=True)
                update = telebot.types.Update.de_json(json_data)
                bot.process_new_updates([update])
                print("✅ Update processed", flush=True)
            else:
                print("❌ No JSON data", flush=True)
        return "OK", 200
    except Exception as e:
        print(f"💥 WEBHOOK ERROR: {e}", flush=True)
        return "OK", 200

@app.route("/", methods=['GET', 'POST'])  
def index():
    print("🌐 Health check received", flush=True)
    return "Bot is running...", 200

# ===============================
# MANUAL WEBHOOK SETUP
# ===============================
print("🔄 SETTING UP WEBHOOK...", flush=True)
try:
    print("🗑️ Removing existing webhook...", flush=True)
    bot.remove_webhook()
    time.sleep(2)
    print("🔧 Setting up new webhook...", flush=True)
    success = bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=None,
        max_connections=100,
        allowed_updates=None,
        timeout=60
    )
    if success:
        print(f"✅ WEBHOOK SET SUCCESSFULLY: {WEBHOOK_URL}", flush=True)
    else:
        print("❌ WEBHOOK SET FAILED", flush=True)
except Exception as e:
    print(f"💥 WEBHOOK SETUP ERROR: {e}", flush=True)

print("🎂 Birthday Scheduler: ACTIVE", flush=True)
print("⏰ Will post daily at 8:00 AM Myanmar Time", flush=True)
print("📚 'စာအုပ်' Auto Reply: RANDOM REPLIES ENABLED (၈မျိုး)", flush=True)
print("🔗 Link Blocker: ENABLED (UNIFIED HANDLER - FINAL VERSION)", flush=True)
print("🎲 Random Function: ACTIVE - Different replies each time", flush=True)
print("👋 Welcome System: FIXED (using online image URL)", flush=True)
print("🔧 All systems ready!", flush=True)
print("🚀 Bot is now LIVE!", flush=True)
print("💡 Available Commands: /start, /forcepost", flush=True)

# ===============================
# RUN WITH FLASK
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask server on port {port}...", flush=True)
    app.run(host="0.0.0.0", port=port, debug=False)
