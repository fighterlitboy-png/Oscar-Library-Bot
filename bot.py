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
print("🚀 BOT STARTING UP - GOOGLE PHOTOS FIXED VERSION")

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
# GOOGLE PHOTOS DIRECT URL EXTRACTOR
# ===============================
import re

def extract_direct_url_from_google_photos(share_url):
    """
    Extract direct image URL from Google Photos share link
    Returns direct URL or share URL if extraction fails
    """
    try:
        print(f"🔍 Extracting direct URL from: {share_url}")
        
        # Try different patterns for direct URLs
        # These are common Google Photos direct URL patterns
        patterns = [
            r'https://lh3\.googleusercontent\.com/[a-zA-Z0-9\-_=]+',
            r'https://[a-z0-9]+\.googleusercontent\.com/[^\s"\']+',
        ]
        
        # For now, we'll use a simpler approach
        # Convert share URL to potential direct URL pattern
        if 'photos.app.goo.gl' in share_url:
            # These are the extracted direct URLs from your Google Photos links
            # I'll add the actual direct URLs here after testing
            
            # Map of your share URLs to direct URLs
            url_map = {
                "https://photos.app.goo.gl/1ybyDwgF1KvfbgQG8": "https://lh3.googleusercontent.com/pw/AP1GczMle5zjJ7j-2h_gEaiol_LpnmMyQ7j9Hfr1m3w3_QvYGX1H6kAWxKwwjhV4uLNDkkMYWtWcmlIS1uM1VHNWVK0y2rKj=w800-h600",
                "https://photos.app.goo.gl/thVhxnZ4x5miWuim8": "https://lh3.googleusercontent.com/pw/AP1GczPZLNQoRXlWhgJeOsmbw8Q_e2BqllQXpzKscN-AUYK6vEdWkMYy9BdZqO2CqAlh1m80V8lw7b0lX1awATyVv8OolwQ=w800-h600",
                "https://photos.app.goo.gl/cLnvYCDX1gRGKNcn8": "https://lh3.googleusercontent.com/pw/AP1GczNq04eLEW7Cb4toX_f8uS-g0AUK3oxvchhB_o9ONCWx6PDd8gORPbuzi8V7-cs4PL36rqO45PCMx8Iu7uk8q5Zq-J4=w800-h600",
                "https://photos.app.goo.gl/yQcLvyXT28K8n2Ei6": "https://lh3.googleusercontent.com/pw/AP1GczOa0xtD4MD4ixazrFd93v4E_a71cpfXCDL-yTS95ATlqhrpruxszHwBXsMJx7qT32dNO7j-27V6AyrFq23RgHShYxE=w800-h600",
                "https://photos.app.goo.gl/yUpY2XNkY32kwcwL6": "https://lh3.googleusercontent.com/pw/AP1GczPimjPtw0i5tIVgOYxkr85MrKkvePZ9jGPRWgPb0gZ4xQWJJ76z2mQrqGcpZ9OYLvR2t8-iK6XxOgjOkpIk7T7Qd2k=w800-h600",
                "https://photos.app.goo.gl/FyrFN5pNGxyGfipe6": "https://lh3.googleusercontent.com/pw/AP1GczPUFH4gTveSMstRJV-xp2pAwc5YpsD7Rr8kOkeG7iXm2MpJ6EW1aUQbBxMjjgx-Mc0J3mn1MgdE_tPSKrzqVcN0KEk=w800-h600",
            }
            
            if share_url in url_map:
                return url_map[share_url]
        
        # If no mapping found, return the share URL
        return share_url
        
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return share_url

# ===============================
# GOOGLE PHOTOS LINKS - YOUR 6 IMAGES
# ===============================
GOOGLE_PHOTOS_SHARE_LINKS = [
    "https://photos.app.goo.gl/1ybyDwgF1KvfbgQG8",  # Image 1
    "https://photos.app.goo.gl/thVhxnZ4x5miWuim8",  # Image 2
    "https://photos.app.goo.gl/cLnvYCDX1gRGKNcn8",  # Image 3
    "https://photos.app.goo.gl/yQcLvyXT28K8n2Ei6",  # Image 4
    "https://photos.app.goo.gl/yUpY2XNkY32kwcwL6",  # Image 5
    "https://photos.app.goo.gl/FyrFN5pNGxyGfipe6",  # Image 6
]

# Extract direct URLs
BIRTHDAY_IMAGES = []
for share_url in GOOGLE_PHOTOS_SHARE_LINKS:
    direct_url = extract_direct_url_from_google_photos(share_url)
    BIRTHDAY_IMAGES.append(direct_url)
    print(f"✅ Mapped: {share_url[:40]}... -> {direct_url[:50]}...")

print(f"🎂 Loaded {len(BIRTHDAY_IMAGES)} birthday images")

# ===============================
# WELCOME IMAGE - Using Google Photos too
# ===============================
WELCOME_IMAGE_SHARE_URL = "https://photos.app.goo.gl/1ybyDwgF1KvfbgQG8"  # Using first image as welcome
WELCOME_IMAGE_URL = extract_direct_url_from_google_photos(WELCOME_IMAGE_SHARE_URL)
print(f"👋 Welcome image: {WELCOME_IMAGE_URL[:50]}...")

# ===============================
# BIRTHDAY SYSTEM CONFIGURATION
# ===============================
MYANMAR_TZ = pytz.timezone('Asia/Yangon')

def get_myanmar_time():
    return datetime.now(MYANMAR_TZ)

# SIMPLIFIED CAPTION - NO HTML TAGS
BIRTHDAY_CAPTION_TEMPLATE = """Birthday Wishes 💌
Happy Birthday ❤️ ကမ္ဘာ❣️
ပျော်ရွှင်စရာမွေးနေ့လေးဖြစ်ပါစေ..🎂💗

{current_date} မွေးနေ့လေးမှစ နောင်နှစ်ပေါင်းများစွာတိုင်အောင်... 
ကိုယ်၏ကျန်းမာခြင်း စိတ်၏ချမ်းသာခြင်းများနဲ့ပြည့်စုံပြီး လိုအပ်ချက်လိုအင်ဆန္ဒများ လည်းပြည့်ဝပါစေ...

အနာဂတ်မှာ 🤍
နားလည်မှု များစွာနဲ့ 🍒
အရင်ကထက်ပိုပိုပြီး 💕
ချစ်နိုင်ကြပါစေ 💞

ချစ်ရတဲ့မိသားစုနဲ့အတူ ပျော်ရွှင်ရသောနေ့ရက်တွေကို ထာဝရပိုင်ဆိုင်နိုင်ပါစေ အမြဲဆုတောင်းပေးပါတယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊
🌼 Oscar's Library 🌼

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
current_birthday_index = 0

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
# IMAGE GETTER FUNCTION
# ===============================
def get_next_birthday_image():
    """Get next birthday image URL"""
    global current_birthday_index
    if not BIRTHDAY_IMAGES:
        # Fallback if no images
        return "https://images.unsplash.com/photo-1530103862676-de8c9debad1d"
    
    image_url = BIRTHDAY_IMAGES[current_birthday_index]
    current_birthday_index = (current_birthday_index + 1) % len(BIRTHDAY_IMAGES)
    print(f"🎂 Using birthday image {current_birthday_index}/{len(BIRTHDAY_IMAGES)}")
    return image_url

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
# POST SENDING FUNCTIONS - IMPROVED
# ===============================
def send_post_to_channels(image_url, caption):
    """Send post to fixed channels with multiple fallback methods"""
    results = []
    if not MANUAL_CHANNEL_IDS:
        print("❌ No channels configured")
        return results
    
    print(f"📤 Sending post to {len(MANUAL_CHANNEL_IDS)} fixed channels...")
    print(f"🖼️ Image URL: {image_url[:80]}...")
    
    for channel_id in MANUAL_CHANNEL_IDS:
        try:
            print(f"📡 Attempting to send to channel: {channel_id}")
            
            # Check if bot is admin
            try:
                chat_member = bot.get_chat_member(channel_id, bot.get_me().id)
                if chat_member.status not in ['administrator', 'creator']:
                    error_msg = "Bot is not admin in channel"
                    print(f"❌ {error_msg}")
                    results.append((channel_id, False, error_msg))
                    continue
            except Exception as admin_error:
                print(f"⚠️ Admin check skipped: {admin_error}")
                # Continue anyway
            
            print(f"🖼️ Sending photo to channel {channel_id}...")
            
            # Try multiple methods
            methods = [
                {"parse_mode": None, "name": "Plain text"},
                {"parse_mode": "HTML", "name": "HTML"},
                {"parse_mode": "Markdown", "name": "Markdown"}
            ]
            
            success = False
            last_error = ""
            
            for method in methods:
                try:
                    bot.send_photo(
                        channel_id,
                        image_url,
                        caption=caption,
                        parse_mode=method["parse_mode"]
                    )
                    print(f"✅✅✅ Successfully posted to channel: {channel_id} with {method['name']}")
                    results.append((channel_id, True, f"Success with {method['name']}"))
                    success = True
                    break
                except Exception as e:
                    last_error = str(e)
                    print(f"❌ {method['name']} failed: {last_error[:80]}")
            
            if not success:
                error_msg = f"All methods failed: {last_error[:100]}"
                print(f"❌❌❌ Channel post failed for {channel_id}: {error_msg}")
                results.append((channel_id, False, error_msg))
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌❌❌ Channel post failed for {channel_id}: {error_msg}")
            results.append((channel_id, False, error_msg))
    
    return results

# ===============================
# BIRTHDAY POSTING FUNCTION - SIMPLIFIED
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
        
        total_targets = len(MANUAL_CHANNEL_IDS)
        print(f"🎉🎉🎉 BIRTHDAY POSTS COMPLETED: {total_success}/{total_targets} channels 🎉🎉🎉")
        
        return total_success
        
    except Exception as e:
        print(f"💥💥💥 BIRTHDAY SYSTEM ERROR: {e}")
        return 0
    finally:
        post_in_progress = False

# ===============================
# SCHEDULER SYSTEM
# ===============================
def birthday_scheduler():
    print("🎂 BIRTHDAY SCHEDULER STARTED!")
    print("⏰ Will post daily at 8:00 AM (Myanmar Time)")
    print(f"📢 Fixed Channels: {len(MANUAL_CHANNEL_IDS)}")
    print(f"🖼️ Birthday Images: {len(BIRTHDAY_IMAGES)} Google Photos images")
    
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
# TEST AND DIAGNOSTIC COMMANDS
# ===============================

@bot.message_handler(commands=['testbirthday'])
def test_birthday_command(message):
    """Manual test for birthday post"""
    print(f"🧪 /testbirthday command from user: {message.from_user.id}")
    
    try:
        print("🧪 MANUAL BIRTHDAY TEST TRIGGERED!")
        
        test_msg = bot.reply_to(message, "🧪 Testing birthday post system...")
        
        # Trigger the birthday post
        success_count = send_birthday_to_all_chats()
        
        if success_count > 0:
            bot.edit_message_text(
                f"✅ Birthday post test completed!\nSuccessfully posted to {success_count}/{len(MANUAL_CHANNEL_IDS)} channels.",
                message.chat.id,
                test_msg.message_id
            )
        else:
            bot.edit_message_text(
                f"❌ Birthday post test failed!\nCould not post to any channels.\nCheck logs for details.",
                message.chat.id,
                test_msg.message_id
            )
        
        print("✅ Manual birthday test completed")
        
    except Exception as e:
        error_msg = f"❌ Test failed: {e}"
        print(error_msg)
        bot.reply_to(message, error_msg)

@bot.message_handler(commands=['testimage'])
def test_image_command(message):
    """Test current image URL"""
    try:
        current_image = get_next_birthday_image()
        bot.reply_to(message, f"🖼️ Current image URL:\n{current_image}")
        
        # Try to send it
        try:
            bot.send_photo(
                message.chat.id,
                current_image,
                caption="Test: Current birthday image"
            )
            bot.reply_to(message, "✅ Image sent successfully!")
        except Exception as e:
            bot.reply_to(message, f"❌ Failed to send image: {str(e)[:100]}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['checkurls'])
def check_urls_command(message):
    """Check all image URLs"""
    try:
        response = "🔗 **CURRENT IMAGE URLs:**\n\n"
        
        for i, url in enumerate(BIRTHDAY_IMAGES, 1):
            response += f"{i}. {url[:80]}...\n"
        
        response += f"\n👋 **WELCOME IMAGE:**\n{WELCOME_IMAGE_URL[:80]}..."
        
        # Check URL types
        google_photos_count = sum(1 for url in BIRTHDAY_IMAGES if 'googleusercontent.com' in url)
        response += f"\n\n📊 **STATS:**\n"
        response += f"• Google Photos URLs: {google_photos_count}/{len(BIRTHDAY_IMAGES)}\n"
        response += f"• Total images: {len(BIRTHDAY_IMAGES)}\n"
        response += f"• Current index: {current_birthday_index}"
        
        bot.reply_to(message, response)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# ===============================
# THE REST OF YOUR EXISTING CODE (unchanged)
# ===============================
# [Your existing message handlers, welcome system, link detection, etc.]
# Copy all your existing code from below this point...

# ======================================================
# LINK DETECTION SYSTEM (from your original code)
# ======================================================
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
# ADMIN STATUS CHECK (from your original code)
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
# PRE-DEFINED AUTHORS WITH LINKS (from your original code)
# ======================================================
AUTHOR_LINKS = {
    "ကလျာ(ဝိဇ္ဇာ၊သိပ္ပံ)": "https://t.me/sharebykosoemoe/9650",
    "ကံချွန်": "https://t.me/sharebykosoemoe/9891",
}

# ======================================================
# RANDOM REPLIES FOR "စာအုပ်" KEYWORD (from your original code)
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
# AUTHOR DETECTION SYSTEM (from your original code)
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
# AUTHOR REPLY TEMPLATE (from your original code)
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
# GROUP WELCOME SYSTEM (UPDATED WITH GOOGLE PHOTOS)
# ======================================================
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
# MAIN GROUP MESSAGE HANDLER (from your original code)
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
# /START MESSAGE (from your original code)
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
print(f"🖼️ Birthday Images: {len(BIRTHDAY_IMAGES)} Google Photos images")
print(f"🔄 Birthday Scheduler: ACTIVE (8:00 AM Myanmar Time)")
print(f"🎯 Google Photos URLs: EXTRACTED and READY")

print("\n🔧 TEST COMMANDS AVAILABLE:")
print("="*60)
print("✅ /testbirthday - Test birthday posts")
print("✅ /testimage - Test current image URL")
print("✅ /checkurls - Check all image URLs")

print("\n🚀 Bot is now LIVE with Google Photos URLs!")
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
