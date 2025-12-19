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
# BIRTHDAY IMAGES DATABASE (6 IMAGES ONLY)
# ===============================
BIRTHDAY_IMAGES = [
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_2.jpg",
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_3.jpg",
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_4.jpg",
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_5.jpg",
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_6.jpg",
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/HBD_7.jpg"
]

# Track current image index for birthday
current_birthday_index = 0

def get_next_birthday_image():
    """Get next birthday image in rotation (6 images only)"""
    global current_birthday_index
    image_url = BIRTHDAY_IMAGES[current_birthday_index]
    print(f"🖼️ Using birthday image {current_birthday_index + 1}/{len(BIRTHDAY_IMAGES)}")
    
    # Move to next image for next post
    current_birthday_index = (current_birthday_index + 1) % len(BIRTHDAY_IMAGES)
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
ချစ်ခင်နိုင်ကြပါစေ 💞

ချစ်ရတဲ့မိသားစုနဲ့အတူ ပျော်ရွှင်ရသောနေ့ရက်တွေကို ထာဝရပိုင်ဆိုင်နိုင်ပါစေ အမြဲဆုတောင်းပေးပါတယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊
<b>🌼 Oscar's Library 🌼</b>

#oscarlibrary
#oscaradminteam"""

# ===============================
# CONTENT IMAGES & VIDEOS DATABASE
# ===============================

# Myanmar Music Post
MUSIC_MYANMAR_IMAGE = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/M_Music.jpg"
MUSIC_MYANMAR_CAPTION = """🎼 <b>သီချင်း‌လေးတွေနားဆင်ရအောင်</b>

<b>🎶 Join</b> ထားကြပါ...🥰

#oscarlibrary"""

# English Music Post
MUSIC_ENGLISH_IMAGE = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/E_Music.jpg"
MUSIC_ENGLISH_CAPTION = """🎧 <b>English သီးချင်းကြိုက်သူများ</b>

<b>🎶 Join</b> ထားကြပါ...🥰

#oscarlibrary"""

# Poem Posts (5 images rotation)
POEM_IMAGES = [
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/CH%20(1).jpg",
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/CH%20(2).jpg",
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/CH%20(3).jpg",
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/CH%20(4).jpg",
    "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/CH%20(5).jpg"
]

POEM_CAPTION = """<b>စွယ်တော်ရွက်လေးများ၏အတ္ထုပ္ပတ္တိ 🍃</b>

နှလုံးသားဒဿနလေးတွေ 
တဒင်္ဂအချိန်လေးတစ်ခုအတွက်
ကြည်နူးစိတ်လေးတွေခံစားမိပါစေ... 🌸

🍂 ကဗျာ၊ စာတို၊ ဟာသလေးတွေကို
react လေးပေးပြီး Best Friends 
လေးတွေကို မျှ‌ဝေပေးကြပါ 💞

#oscarlibrary"""

# Bot Promo Video
PROMO_VIDEO = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/Bot_Video.mp4"
PROMO_CAPTION = """<b>မင်းရဲ့စာဖတ်ခရီးကို
အတူလိုက်ပြီး ကြင်နာစွာနဲ့ 
လမ်းညွှန်ပေးဖို အမြဲရှိနေတယ်...🥰</b>

မင်းရဲ့စိတ်ကူးထဲက စာအုပ်တွေ၊ 
မင်းရင်ထဲကဖတ်ချင်တဲ့ ဝတ္ထုတွေကို 
အတူရှာဖွေကြမယ်...📚

မင်းရဲ့စာဖတ်သံကြားရဖို...💕
မင်းစာသားတွေကိုဖတ်ရင်း ပြုံးလာမယ့် မျက်နှာလေးကို မြင်ရဖို...😍

<b>🌼 Oscar's Library 🌼</b> လေးထဲက
မင်းကြိုက်တဲ့စာအုပ်တွေ 
ရွေးကြည့်မလား... 📚✨

#oscarlibrary"""

# Track current poem image index
current_poem_index = 0

def get_next_poem_image():
    """Get next poem image in rotation (5 images)"""
    global current_poem_index
    image_url = POEM_IMAGES[current_poem_index]
    print(f"🖼️ Using poem image {current_poem_index + 1}/{len(POEM_IMAGES)}")
    
    # Move to next image for next post
    current_poem_index = (current_poem_index + 1) % len(POEM_IMAGES)
    return image_url

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
last_myanmar_music_post_time = None
last_english_music_post_time = None
last_poem_post_time = None
last_promo_post_time = None
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
# ACTIVE GROUPS TRACKING - IMPROVED
# ===============================
def track_active_group(chat_id):
    """Track groups/channels where bot is active"""
    try:
        if chat_id < 0:  # Only track groups/channels (negative IDs)
            active_groups.add(chat_id)
            
            # Keep only last 300 groups to avoid memory issues
            if len(active_groups) > 300:
                oldest = list(active_groups)[0]
                active_groups.remove(oldest)
                
    except Exception as e:
        print(f"❌ Error in track_active_group: {e}")

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
        
        print(f"⏰ Birthday Time check: {current_time_str} (Myanmar Time) - Date: {current_date}")
        
        # Check for exactly 8:00 AM
        if current_hour == 8 and current_minute == 0:
            if last_birthday_post_date != current_date:
                last_birthday_post_date = current_date
                print("✅✅✅ BIRTHDAY POST TRIGGERED! ✅✅✅")
                return True
        
        return False
    except Exception as e:
        print(f"⏰ Birthday Time check error: {e}")
        return False

def should_send_myanmar_music():
    """Check if should send Myanmar music post at 10:00 AM and 6:00 PM"""
    try:
        global last_myanmar_music_post_time
        
        myanmar_time = get_myanmar_time()
        current_hour = myanmar_time.hour
        current_minute = myanmar_time.minute
        current_time_str = myanmar_time.strftime("%H:%M")
        
        print(f"🎶 Myanmar Music Time check: {current_time_str}")
        
        # Check for exactly 10:00 AM or 6:00 PM
        if (current_hour == 10 and current_minute == 0) or (current_hour == 18 and current_minute == 0):
            if last_myanmar_music_post_time != current_time_str:
                last_myanmar_music_post_time = current_time_str
                print("✅✅✅ MYANMAR MUSIC POST TRIGGERED! ✅✅✅")
                return True
        
        return False
    except Exception as e:
        print(f"🎶 Myanmar Music Time check error: {e}")
        return False

def should_send_english_music():
    """Check if should send English music post at 2:00 PM and 10:00 PM"""
    try:
        global last_english_music_post_time
        
        myanmar_time = get_myanmar_time()
        current_hour = myanmar_time.hour
        current_minute = myanmar_time.minute
        current_time_str = myanmar_time.strftime("%H:%M")
        
        print(f"🎧 English Music Time check: {current_time_str}")
        
        # Check for exactly 2:00 PM or 10:00 PM
        if (current_hour == 14 and current_minute == 0) or (current_hour == 22 and current_minute == 0):
            if last_english_music_post_time != current_time_str:
                last_english_music_post_time = current_time_str
                print("✅✅✅ ENGLISH MUSIC POST TRIGGERED! ✅✅✅")
                return True
        
        return False
    except Exception as e:
        print(f"🎧 English Music Time check error: {e}")
        return False

def should_send_poem():
    """Check if should send poem post at 4:00 PM and 8:00 PM"""
    try:
        global last_poem_post_time
        
        myanmar_time = get_myanmar_time()
        current_hour = myanmar_time.hour
        current_minute = myanmar_time.minute
        current_time_str = myanmar_time.strftime("%H:%M")
        
        print(f"🍃 Poem Time check: {current_time_str}")
        
        # Check for exactly 4:00 PM or 8:00 PM
        if (current_hour == 16 and current_minute == 0) or (current_hour == 20 and current_minute == 0):
            if last_poem_post_time != current_time_str:
                last_poem_post_time = current_time_str
                print("✅✅✅ POEM POST TRIGGERED! ✅✅✅")
                return True
        
        return False
    except Exception as e:
        print(f"🍃 Poem Time check error: {e}")
        return False

def should_send_promo():
    """Check if should send promo post at 12:00 AM and 12:00 PM"""
    try:
        global last_promo_post_time
        
        myanmar_time = get_myanmar_time()
        current_hour = myanmar_time.hour
        current_minute = myanmar_time.minute
        current_time_str = myanmar_time.strftime("%H:%M")
        
        print(f"📚 Promo Time check: {current_time_str}")
        
        # Check for exactly 12:00 AM or 12:00 PM
        if (current_hour == 0 and current_minute == 0) or (current_hour == 12 and current_minute == 0):
            if last_promo_post_time != current_time_str:
                last_promo_post_time = current_time_str
                print("✅✅✅ PROMO POST TRIGGERED! ✅✅✅")
                return True
        
        return False
    except Exception as e:
        print(f"📚 Promo Time check error: {e}")
        return False

# ===============================
# POST SENDING FUNCTIONS
# ===============================
def send_post_to_channels(image_url, caption, reply_markup=None, is_video=False):
    """Send post to fixed channels"""
    results = []
    if not MANUAL_CHANNEL_IDS:
        print("❌ No channels configured")
        return results
    
    print(f"📤 Sending post to {len(MANUAL_CHANNEL_IDS)} fixed channels...")
    
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
            
            if is_video:
                print(f"🎬 Sending video to channel {channel_id}...")
                bot.send_video(
                    channel_id,
                    image_url,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            else:
                print(f"🖼️ Sending photo to channel {channel_id}...")
                bot.send_photo(
                    channel_id,
                    image_url,
                    caption=caption,
                    reply_markup=reply_markup,
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
# ULTIMATE ADMIN CHECK FUNCTION
# ===============================
def check_bot_admin(chat_id):
    """Check if bot is admin in chat - ROBUST VERSION"""
    try:
        chat_member = bot.get_chat_member(chat_id, bot.get_me().id)
        return chat_member.status in ['administrator', 'creator']
    except Exception as e:
        error_msg = str(e).lower()
        
        # Check specific errors
        if "chat not found" in error_msg:
            print(f"❌ Chat not found: {chat_id}")
            return False
        elif "bot was kicked" in error_msg or "bot is not a member" in error_msg:
            print(f"❌ Bot kicked/not member: {chat_id}")
            return False
        elif "not enough rights" in error_msg:
            print(f"❌ No rights in chat: {chat_id}")
            return False
        elif "forbidden" in error_msg:
            print(f"❌ Bot forbidden in chat: {chat_id}")
            return False
        else:
            print(f"⚠️ Unknown error checking admin for {chat_id}: {error_msg[:50]}")
            return False

# ===============================
# ULTIMATE SEND TO ALL TARGETS
# ===============================
def send_to_all_targets_ultimate(image_url, caption, reply_markup=None, is_video=False):
    """Send to ALL targets - ULTIMATE VERSION"""
    print("🚀 ULTIMATE SEND TO ALL TARGETS")
    
    all_targets = []
    
    # 1. Add fixed channels
    for channel_id in MANUAL_CHANNEL_IDS:
        if check_bot_admin(channel_id):
            all_targets.append(channel_id)
    
    print(f"✅ Fixed channels ready: {len(all_targets)}")
    
    # 2. Add active groups that are admin
    admin_groups_count = 0
    for chat_id in list(active_groups):
        if chat_id not in all_targets:  # Avoid duplicates
            if check_bot_admin(chat_id):
                all_targets.append(chat_id)
                admin_groups_count += 1
    
    print(f"✅ Active admin groups: {admin_groups_count}")
    print(f"🎯 Total targets: {len(all_targets)}")
    
    # Send to all targets
    success_count = 0
    failed_targets = []
    
    for i, chat_id in enumerate(all_targets):
        try:
            # Small delay to avoid flood
            if i > 0:
                time.sleep(0.3)
            
            # Get chat info for logging
            try:
                chat_info = bot.get_chat(chat_id)
                chat_title = chat_info.title if hasattr(chat_info, 'title') else f"Chat {chat_id}"
            except:
                chat_title = f"Chat {chat_id}"
            
            print(f"📤 [{i+1}/{len(all_targets)}] Sending to: {chat_title}")
            
            # Send the post
            if is_video:
                bot.send_video(
                    chat_id,
                    image_url,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            else:
                bot.send_photo(
                    chat_id,
                    image_url,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            
            success_count += 1
            print(f"✅ SUCCESS: {chat_title}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ FAILED [{chat_id}]: {error_msg[:100]}")
            failed_targets.append((chat_id, error_msg))
    
    print(f"\n📊 ULTIMATE RESULTS:")
    print(f"✅ Success: {success_count}/{len(all_targets)}")
    print(f"❌ Failed: {len(failed_targets)}")
    
    return success_count, failed_targets

# ===============================
# BIRTHDAY POSTING FUNCTION - ULTIMATE
# ===============================
def send_birthday_to_all_chats():
    global post_in_progress
    if post_in_progress:
        print("⚠️ Post already in progress, skipping...")
        return
    
    post_in_progress = True
    try:
        print("🎂🎂🎂 ULTIMATE BIRTHDAY POSTS STARTING 🎂🎂🎂")
        
        myanmar_time = get_myanmar_time()
        current_time = myanmar_time.strftime("%H:%M:%S")
        current_date = myanmar_time.strftime("%B %d")
        print(f"🕐 Posting time: {current_time}")
        
        # Prepare birthday post
        caption = BIRTHDAY_CAPTION_TEMPLATE.format(current_date=current_date)
        birthday_image = get_next_birthday_image()
        
        # Use ULTIMATE sending function
        success_count, failed_targets = send_to_all_targets_ultimate(
            birthday_image, 
            caption,
            is_video=False
        )
        
        print(f"\n🎉🎉🎉 ULTIMATE BIRTHDAY POSTS COMPLETED 🎉🎉🎉")
        print(f"📊 SUMMARY:")
        print(f"   Total Targets: {success_count + len(failed_targets)}")
        print(f"   Success: {success_count}")
        print(f"   Failed: {len(failed_targets)}")
        
    except Exception as e:
        print(f"💥💥💥 ULTIMATE BIRTHDAY SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        post_in_progress = False

# ===============================
# CONTENT POSTING FUNCTIONS
# ===============================
def send_myanmar_music_to_all_chats():
    """Send Myanmar music post to all channels"""
    global post_in_progress
    if post_in_progress:
        print("⚠️ Post already in progress, skipping...")
        return
    
    post_in_progress = True
    try:
        print("🎶🎶🎶 MYANMAR MUSIC POSTS STARTING 🎶🎶🎶")
        
        myanmar_time = get_myanmar_time()
        current_time = myanmar_time.strftime("%H:%M:%S")
        print(f"🕐 Posting time: {current_time}")
        
        # Create inline keyboard
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton("Oscar's Music 🎶", url="https://t.me/oscarmyanmarmusic")
        )
        
        # Use ULTIMATE sending
        success_count, failed_targets = send_to_all_targets_ultimate(
            MUSIC_MYANMAR_IMAGE,
            MUSIC_MYANMAR_CAPTION,
            reply_markup=keyboard,
            is_video=False
        )
        
        print(f"\n🎉 MYANMAR MUSIC POSTS COMPLETED 🎉")
        print(f"📊 SUMMARY: {success_count} successful, {len(failed_targets)} failed")
        
    except Exception as e:
        print(f"💥💥💥 MYANMAR MUSIC SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        post_in_progress = False

def send_english_music_to_all_chats():
    """Send English music post to all channels"""
    global post_in_progress
    if post_in_progress:
        print("⚠️ Post already in progress, skipping...")
        return
    
    post_in_progress = True
    try:
        print("🎧🎧🎧 ENGLISH MUSIC POSTS STARTING 🎧🎧🎧")
        
        myanmar_time = get_myanmar_time()
        current_time = myanmar_time.strftime("%H:%M:%S")
        print(f"🕐 Posting time: {current_time}")
        
        # Create inline keyboard
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton("English Music 🎶", url="https://t.me/oscarenglishmusic")
        )
        
        # Use ULTIMATE sending
        success_count, failed_targets = send_to_all_targets_ultimate(
            MUSIC_ENGLISH_IMAGE,
            MUSIC_ENGLISH_CAPTION,
            reply_markup=keyboard,
            is_video=False
        )
        
        print(f"\n🎉 ENGLISH MUSIC POSTS COMPLETED 🎉")
        print(f"📊 SUMMARY: {success_count} successful, {len(failed_targets)} failed")
        
    except Exception as e:
        print(f"💥💥💥 ENGLISH MUSIC SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        post_in_progress = False

def send_poem_to_all_chats():
    """Send poem post to all channels"""
    global post_in_progress
    if post_in_progress:
        print("⚠️ Post already in progress, skipping...")
        return
    
    post_in_progress = True
    try:
        print("🍃🍃🍃 POEM POSTS STARTING 🍃🍃🍃")
        
        myanmar_time = get_myanmar_time()
        current_time = myanmar_time.strftime("%H:%M:%S")
        print(f"🕐 Posting time: {current_time}")
        
        # Get next poem image
        poem_image = get_next_poem_image()
        
        # Create inline keyboard
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton("နှလုံးသားဒဿန 🍃", url="https://t.me/oscarpoem")
        )
        
        # Use ULTIMATE sending
        success_count, failed_targets = send_to_all_targets_ultimate(
            poem_image,
            POEM_CAPTION,
            reply_markup=keyboard,
            is_video=False
        )
        
        print(f"\n🎉 POEM POSTS COMPLETED 🎉")
        print(f"📊 SUMMARY: {success_count} successful, {len(failed_targets)} failed")
        
    except Exception as e:
        print(f"💥💥💥 POEM SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        post_in_progress = False

def send_promo_to_all_chats():
    """Send promo video post to all channels"""
    global post_in_progress
    if post_in_progress:
        print("⚠️ Post already in progress, skipping...")
        return
    
    post_in_progress = True
    try:
        print("📚📚📚 PROMO VIDEO POSTS STARTING 📚📚📚")
        
        myanmar_time = get_myanmar_time()
        current_time = myanmar_time.strftime("%H:%M:%S")
        print(f"🕐 Posting time: {current_time}")
        
        # Create inline keyboard
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton("စာပေချစ်သူများအတွက် 🍓", url="https://t.me/bookbykosoemoe")
        )
        keyboard.row(
            types.InlineKeyboardButton("စာအုပ်ရှာရန် 📚📖", url="https://t.me/oscar_libray_bot")
        )
        
        # Use ULTIMATE sending
        success_count, failed_targets = send_to_all_targets_ultimate(
            PROMO_VIDEO,
            PROMO_CAPTION,
            reply_markup=keyboard,
            is_video=True
        )
        
        print(f"\n🎉 PROMO VIDEO POSTS COMPLETED 🎉")
        print(f"📊 SUMMARY: {success_count} successful, {len(failed_targets)} failed")
        
    except Exception as e:
        print(f"💥💥💥 PROMO SYSTEM ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        post_in_progress = False

# ===============================
# UPDATED SCHEDULER SYSTEM
# ===============================
def content_scheduler():
    print("🚀 ULTIMATE CONTENT SCHEDULER STARTED!")
    print("⏰ POSTING SCHEDULE:")
    print("   • Birthday Posts: 8:00 AM Daily")
    print("   • Myanmar Music: 10:00 AM & 6:00 PM")
    print("   • English Music: 2:00 PM & 10:00 PM")
    print("   • Poem Posts: 4:00 PM & 8:00 PM")
    print("   • Promo Video: 12:00 AM & 12:00 PM")
    print(f"📢 Fixed Channels: {len(MANUAL_CHANNEL_IDS)}")
    print(f"📊 Active Groups Tracked: {len(active_groups)}")
    
    last_minute = None
    
    while True:
        try:
            current_time = get_myanmar_time()
            current_minute = current_time.strftime("%H:%M")
            
            # Only check once per minute
            if last_minute != current_minute:
                last_minute = current_minute
                
                # Check birthday posts
                if should_send_birthday_post():
                    print(f"🚀🚀🚀 TRIGGERING BIRTHDAY POSTS AT {current_time.strftime('%H:%M:%S')} 🚀🚀🚀")
                    send_birthday_to_all_chats()
                
                # Check Myanmar music posts
                if should_send_myanmar_music():
                    print(f"🎶🎶🎶 TRIGGERING MYANMAR MUSIC POSTS AT {current_time.strftime('%H:%M:%S')} 🎶🎶🎶")
                    send_myanmar_music_to_all_chats()
                
                # Check English music posts
                if should_send_english_music():
                    print(f"🎧🎧🎧 TRIGGERING ENGLISH MUSIC POSTS AT {current_time.strftime('%H:%M:%S')} 🎧🎧🎧")
                    send_english_music_to_all_chats()
                
                # Check poem posts
                if should_send_poem():
                    print(f"🍃🍃🍃 TRIGGERING POEM POSTS AT {current_time.strftime('%H:%M:%S')} 🍃🍃🍃")
                    send_poem_to_all_chats()
                
                # Check promo video posts
                if should_send_promo():
                    print(f"📚📚📚 TRIGGERING PROMO VIDEO POSTS AT {current_time.strftime('%H:%M:%S')} 📚📚📚")
                    send_promo_to_all_chats()
            
            time.sleep(30)
            
        except Exception as e:
            print(f"🎂 Scheduler error: {e}")
            time.sleep(30)

# Start the scheduler thread
print("🔄 Starting ultimate content scheduler thread...")
content_thread = threading.Thread(target=content_scheduler, daemon=True)
content_thread.start()
print("✅ Ultimate content scheduler started")

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
    elif message.from_user:
        user_id = message.from_user.id
    
    if not user_id:
        return True
    
    if user_id == 1087968824:
        return True
    
    try:
        chat_member = bot.get_chat_member(chat_id, user_id)
        return chat_member.status in ['administrator', 'creator']
            
    except Exception:
        return True

# ======================================================
# PRE-DEFINED AUTHORS WITH LINKS
# ======================================================
AUTHOR_LINKS = {
    "ကလျာ(ဝိဇ္ဇာ၊သိပ္ပံ)": "https://t.me/sharebykosoemoe/9650",
    "ကံချွန်": "https://t.me/sharebykosoemoe/9891",
    "ကံ၀င်း": "https://t.me/sharebykosoemoe/9883",
    "ကောင်းထက်": "https://t.me/sharebykosoemoe/9857",
    "ကောင်းထက်ညွန့်": "https://t.me/sharebykosoemoe/10210",
    "ကို(တက္ကသိုလ်)": "https://t.me/sharebykosoemoe/10640",
    "ကိုကို(စက်မှုတက္ကသိုလ်)": "https://t.me/sharebykosoemoe/10644",
    "ကိုမောင်စံသိန်း": "https://t.me/sharebykosoemoe/10270",
    "ကောင်းသန့်": "https://t.me/sharebykosoemoe/1583",
    "ကျော်ဦးလှိုင်": "https://t.me/sharebykosoemoe/11203",
    "ကြည်အေး": "https://t.me/sharebykosoemoe/1078",
    "ကိုငြိမ်းဦး": "https://t.me/sharebykosoemoe/7881",
    "ကျော်ထူး": "https://t.me/sharebykosoemoe/7084",
    "ကိုတာ": "https://t.me/sharebykosoemoe/5003",
    "ကျေးကို": "https://t.me/sharebykosoemoe/1237",
    "ကိုပိုက်": "https://t.me/sharebykosoemoe/10688",
    "ကိုစစ": "https://t.me/sharebykosoemoe/10777",
    "ကိုရွှေထူး": "https://t.me/sharebykosoemoe/10795",
    "ကာတွန်း သန်းကြွယ်": "https://t.me/sharebykosoemoe/10842",
    "ကိုရွှေတောသား": "https://t.me/sharebykosoemoe/10684",
    "ကို၀မ်း": "https://t.me/sharebykosoemoe/10649",
    "ကို‌ယော": "https://t.me/sharebykosoemoe/10851",
    "ကွန်ဖူးစိုးမြင့်": "https://t.me/sharebykosoemoe/10950",
    "ကြယ်နီ": "https://t.me/sharebykosoemoe/10928",
    "ကြေးမုံဦးသောင်း": "https://t.me/sharebykosoemoe/10931",
    "ကုသ": "https://t.me/sharebykosoemoe/10934",
    "ကြယ်စင်မှူး‌ဝေ": "https://t.me/sharebykosoemoe/10995",
    "ကြပ်ကလေး": "https://t.me/sharebykosoemoe/10972",
    "ကျော်တင့်ဆွေ": "https://t.me/sharebykosoemoe/10991",
    "ကျောက်ဘီလူး တင်မောင်ဆွေ": "https://t.me/sharebykosoemoe/11052",
    "ကျီးသဲလေးထပ်ဆရာတော်ဘုရားကြီး": "https://t.me/sharebykosoemoe/11194",
    "ကျော်လှိုင်ဦး": "https://t.me/sharebykosoemoe/11203",
    "ကျော်ထက်ထွန်း": "https://t.me/sharebykosoemoe/11317",
    "ကျော်ကျော်": "https://t.me/sharebykosoemoe/11320",
    "ကျော်မိုးဇော်": "https://t.me/sharebykosoemoe/11272",
    "ကြည်လွင်မြင့်": "https://t.me/sharebykosoemoe/11655",
    "ကျော်မြသန်း": "https://t.me/sharebykosoemoe/11229",
    "ကျော်အောင်": "https://t.me/sharebykosoemoe/11283",
    "ကျော်နိုင်": "https://t.me/sharebykosoemoe/11565",
    "ကျော်ငြိမ်း": "https://t.me/sharebykosoemoe/11560",
    "ကျော်စိုးဗို": "https://t.me/sharebykosoemoe/11583",
    "ကျော်သက်ခိုင်": "https://t.me/sharebykosoemoe/11450",
    "ကာတွန်းကျော်သစ်": "https://t.me/sharebykosoemoe/11539",
    "ကျော်ဝင်း": "https://t.me/sharebykosoemoe/11594",
    "ကျော်ဇေယျ": "https://t.me/sharebykosoemoe/11667",
    "ကြည်ရွှန်း": "https://t.me/sharebykosoemoe/11663",
    "ကောင်းမြတ်မင်း": "https://t.me/sharebykosoemoe/11707",
    "ကြည်မင်း": "https://t.me/sharebykosoemoe/11682",
    "ကြည်နုခေတ်": "https://t.me/sharebykosoemoe/11695",
    "ကြည်ကြည်မာ": "https://t.me/sharebykosoemoe/11820",
    "ကာတွန်းအောင်ရှိန်": "https://t.me/sharebykosoemoe/11795",
    "ကြည်နိုင်": "https://t.me/sharebykosoemoe/11692",
    "ကြည်ဦး": "https://t.me/sharebykosoemoe/11702",
    "ကြူးနှစ်": "https://t.me/sharebykosoemoe/11996",
    "ကျော်ရင်မြင့်": "https://t.me/sharebykosoemoe/12036",
    "ကြူကြူသင်း": "https://t.me/sharebykosoemoe/11982",
    "ကြူမွှေး": "https://t.me/sharebykosoemoe/11979",
    "ကြီးကြီးစော": "https://t.me/sharebykosoemoe/11971",
    "ကျွန်း": "https://t.me/sharebykosoemoe/11965",
    "ကာတွန်းမောင်ဝဏ္ဏ": "https://t.me/sharebykosoemoe/12033",
    "ကာတွန်းမိမန်းလေး": "https://t.me/sharebykosoemoe/11960",
    "ကာတွန်းကျော်ဦး": "https://t.me/sharebykosoemoe/11860",
    "ကာတွန်းငွေကြည်": "https://t.me/sharebykosoemoe/11952",
    "ကာတွန်းဦးဖေသိန်း": "https://t.me/sharebykosoemoe/11946",
    "ကာတွန်းမောင်မောင်": "https://t.me/sharebykosoemoe/11890",
    "ကိုဆွေ": "https://t.me/sharebykosoemoe/11922",
    "ကောင်းဆက်နိုင်": "https://t.me/sharebykosoemoe/11900",
    "ကြည်စိုးထွန်း": "https://t.me/sharebykosoemoe/11882",
    "ကိုရွှေသိမ်းမင်း": "https://t.me/sharebykosoemoe/11870",
    "ကက်စပါဇော်": "https://t.me/sharebykosoemoe/14259",
    "ကင်းဝန်မင်းကြီး": "https://t.me/sharebykosoemoe/17701",
    "ချမ်းမြေ့ဝင်း": "https://t.me/sharebykosoemoe/615",
    "ခိုင်မိမိဇင်": "https://t.me/sharebykosoemoe/12655",
    "ခင်ကြီးပျော်": "https://t.me/sharebykosoemoe/12754",
    "ချစ်ငယ်": "https://t.me/sharebykosoemoe/12766",
    "ချမ်းမြေ့အရှင်ဣန္ဒက": "https://t.me/sharebykosoemoe/12719",
    "ချစ်မင်းသူ": "https://t.me/sharebykosoemoe/12797",
    "ချစ်မျှားရှင်": "https://t.me/sharebykosoemoe/12822",
    "ချစ်နိုင်": "https://t.me/sharebykosoemoe/12902",
    "ချစ်ဦးညို": "https://t.me/sharebykosoemoe/712",
    "ချစ်စရာ": "https://t.me/sharebykosoemoe/13031",
    "ချစ်စံဝင်း": "https://t.me/sharebykosoemoe/10167",
    "ချိုနွယ်": "https://t.me/sharebykosoemoe/13052",
    "ခြူသစ်": "https://t.me/sharebykosoemoe/13069",
    "ခင်နှင်းယု": "https://t.me/sharebykosoemoe/849",
    "ခင်ခင်ထူး": "https://t.me/sharebykosoemoe/719",
    "ခင်ခင်မြတ်နိုး": "https://t.me/sharebykosoemoe/13181",
    "ခင်မောင်ညို": "https://t.me/sharebykosoemoe/13151",
    "ခင်မောင်ဇော်": "https://t.me/sharebykosoemoe/13402",
    "ခင်မောင်တိုး": "https://t.me/sharebykosoemoe/13365",
    "ခင်မြဇင်": "https://t.me/sharebykosoemoe/13357",
    "ခင်မျိုးချစ်": "https://t.me/sharebykosoemoe/13346",
    "ခင်ဦးခင်ခင်": "https://t.me/sharebykosoemoe/13327p",
    "ခင်စောတင့်": "https://t.me/sharebykosoemoe/13612",
    "ခင်ဆွေဦး": "https://t.me/sharebykosoemoe/13604",
    "ခင်သူဇာ": "https://t.me/sharebykosoemoe/13600",
    "ခိုင်ကျော်": "https://t.me/sharebykosoemoe/13705",
    "ခိုင်ဇင်သက်": "https://t.me/sharebykosoemoe/13553",
    "ခေတ်ပျိုဖြူ": "https://t.me/sharebykosoemoe/13660",
    "ခူးခူး": "https://t.me/sharebykosoemoe/13642",
    "ခင်မောင်အေး": "https://t.me/sharebykosoemoe/13543",
    "ခွန်းချိုငြိမ်းချမ်း": "https://t.me/sharebykosoemoe/13632",
    "ခက်ဇော်": "https://t.me/sharebykosoemoe/9518",
    "ခက်ဦး": "https://t.me/sharebykosoemoe/13536",
    "ခိုင်ဖွား": "https://t.me/sharebykosoemoe/13532",
    "ခင်မောင်သန်း": "https://t.me/sharebykosoemoe/13526",
    "ဧကန်မင်း": "https://t.me/sharebykosoemoe/12381",
    "ဧရာ": "https://t.me/sharebykosoemoe/12353",
    "ဦးတင်ဦး(ကျူရှင်)": "https://t.me/sharebykosoemoe/13800",
    "ဦးကျော်လွင်": "https://t.me/sharebykosoemoe/13796",
    "ဦးထွန်းလှ": "https://t.me/sharebykosoemoe/13793",
    "ဦးဝမ်ထိန်": "https://t.me/sharebykosoemoe/13785",
    "ဦးစိုးရှိန်": "https://t.me/sharebykosoemoe/13836",
    "ဦးတင်ဦး(‌မြောင်)": "https://t.me/sharebykosoemoe/13829",
    "ဦးဦးသာထွန်း": "https://t.me/sharebykosoemoe/13821",
    "ဦးကုလား": "https://t.me/sharebykosoemoe/13929",
    "ဦးသော်ဇင်": "https://t.me/sharebykosoemoe/13935",
    "ဦးဝရသာမီဘိဝံသ": "https://t.me/sharebykosoemoe/13923",
    "ဦးသန်းထွန်း": "https://t.me/sharebykosoemoe/13911",
    "ဦးဝင်းထိန်": "https://t.me/sharebykosoemoe/13888",
    "ဦးညွန့်မောင်": "https://t.me/sharebykosoemoe/13846",
    "ဦးသန့်": "https://t.me/sharebykosoemoe/13863",
    "ဦးစိုးတင့်": "https://t.me/sharebykosoemoe/13853",
    "ဦးဆန်းမောင်": "https://t.me/sharebykosoemoe/13960",
    "ဦးသိန်းလွင်": "https://t.me/sharebykosoemoe/13987",
    "ဦးသန်းလွင်": "https://t.me/sharebykosoemoe/13994",
    "ဦးသောင်းငွေ": "https://t.me/sharebykosoemoe/14001",
    "ဥတ္တရာခေမာ": "https://t.me/sharebykosoemoe/14023",
    "ဦးသက်ထွန်း": "https://t.me/sharebykosoemoe/14084",
    "ဥက္ကာဦး": "https://t.me/sharebykosoemoe/14089",
    "ဦးအောင်လင်း": "https://t.me/sharebykosoemoe/14228",
    "ဦးအဂ္ဂ": "https://t.me/sharebykosoemoe/14096",
    "ဦးအောင်ဟိန်းကျော်": "https://t.me/sharebykosoemoe/14191",
    "ဦးနန္ဒ": "https://t.me/sharebykosoemoe/14688",
    "ဦးအောင်မွန်": "https://t.me/sharebykosoemoe/14222",
    "ဦးအောင်သန်း": "https://t.me/sharebykosoemoe/14170",
    "ဦးအေးမောင်": "https://t.me/sharebykosoemoe/14155",
    "ဦးဘဂျမ်း": "https://t.me/sharebykosoemoe/14218",
    "ဦးဘိုသိန်း": "https://t.me/sharebykosoemoe/14151",
    "ဦးလှဒင်": "https://t.me/sharebykosoemoe/14128",
    "ဦးလှမြင့်": "https://t.me/sharebykosoemoe/14123",
    "ဦးဂိုအင်ကာ": "https://t.me/sharebykosoemoe/14107",
    "ဦးလှအောင်": "https://t.me/sharebykosoemoe/14140",
    "ဦးလှဝင်း": "https://t.me/sharebykosoemoe/1992",
    "ဦးကံညွန့်": "https://t.me/sharebykosoemoe/14113",
    "ဦးကောင်းထူး": "https://t.me/sharebykosoemoe/14741",
    "ဦးခင်မောင်ကြီး": "https://t.me/sharebykosoemoe/14679",
    "ဦးကျော်ဇေယျ": "https://t.me/sharebykosoemoe/14721",
    "ဦးမောင်မောင်သန်း": "https://t.me/sharebykosoemoe/14746",
    "ဦးမြင့်လွင်": "https://t.me/sharebykosoemoe/14703",
    "ဦးမြင့်ဆွေ": "https://t.me/sharebykosoemoe/14695",
    "ဦးနု": "https://t.me/sharebykosoemoe/644",
    "ဦးမိုးမြင့်": "https://t.me/sharebykosoemoe/14801",
    "ဦးဉာဏ": "https://t.me/sharebykosoemoe/14962",
    "ဦးဥတ္တမသာရ": "https://t.me/sharebykosoemoe/14951",
    "ဦးအုန်းမြိုင်": "https://t.me/sharebykosoemoe/14942",
    "ဦးအုန်းမြင့်": "https://t.me/sharebykosoemoe/14938",
    "ဦးဖိုးကျား": "https://t.me/sharebykosoemoe/14924",
    "ဦးဘုန်း(ဓါတု)": "https://t.me/sharebykosoemoe/12175",
    "ဦးပုည": "https://t.me/sharebykosoemoe/14905",
    "ဦးပုကလေး": "https://t.me/sharebykosoemoe/14901",
    "ဦးပြည်သိန်း": "https://t.me/sharebykosoemoe/14907",
    "ဦးပညာ": "https://t.me/sharebykosoemoe/14892",
    "ဦးပညာဝံသ": "https://t.me/sharebykosoemoe/14881",
    "ဦးပြုံးချို": "https://t.me/sharebykosoemoe/14996",
    "ဦးရွှေအောင်": "https://t.me/sharebykosoemoe/14845",
    "ဦးသန်းထွတ်": "https://t.me/sharebykosoemoe/15073",
    "ဦးသောင်းလွင်": "https://t.me/sharebykosoemoe/15055",
    "ဦးဖေမောင်တင်": "https://t.me/sharebykosoemoe/15046",
    "ဦးသောင်းဝင်း": "https://t.me/sharebykosoemoe/15065",
    "ဦးသုခ": "https://t.me/sharebykosoemoe/15033",
    "ဦးခင်မောင်သန်း": "https://t.me/sharebykosoemoe/16473",
    "ဂါမဏီ": "https://t.me/sharebykosoemoe/15105",
    "ဂမ္ဘီရမောင်ရွှေ": "https://t.me/sharebykosoemoe/15200",
    "ဂမ္ဘီရစာရေးဆရာကြီး ဘဘိုးဖြူ": "https://t.me/sharebykosoemoe/15255",
    "ဂန္ဓာရီဝိဇ္ဇာ": "https://t.me/sharebykosoemoe/15109",
    "ဂုဏ်ဝင်း": "https://t.me/sharebykosoemoe/15149",
    "ဂျင်မီ": "https://t.me/sharebykosoemoe/15159",
    "ဂျာနယ်ကျော်ဦးချစ်မောင်": "https://t.me/sharebykosoemoe/15212",
    "ဂျိမ်း(စ်)လှကျော်": "https://t.me/sharebykosoemoe/15193",
    "ဂျက်ကွမ်းခြံကုန်း": "https://t.me/sharebykosoemoe/15165",
    "ဂျာနယ်ကျော်မမလေး": "https://t.me/sharebykosoemoe/707",
    "ဂီတနက်သံ ကိုစောညိန်း": "https://t.me/sharebykosoemoe/15235",
    "ဂျူး": "https://t.me/sharebykosoemoe/716",
    "ဂျိမ်း": "https://t.me/sharebykosoemoe/15241",
    "ငွေဥဒေါင်း": "https://t.me/sharebykosoemoe/15324",
    "ငွေလင်း": "https://t.me/sharebykosoemoe/15341",
    "ငွေတာရီ": "https://t.me/sharebykosoemoe/883",
    "ငြိမ်းချမ်းမေ": "https://t.me/sharebykosoemoe/15345",
    "ငြိမ်းအေးအိမ်": "https://t.me/sharebykosoemoe/15348",
    "ငြိမ်းကျော်": "https://t.me/sharebykosoemoe/15356",
    "စံရွှေမြင့်": "https://t.me/sharebykosoemoe/15407",
    "စိန်စိန်ဦး": "https://t.me/sharebykosoemoe/15413",
    "စစ်ကိုင်းလှရွှေ": "https://t.me/sharebykosoemoe/15410",
    "စိန်ထွန်း(ပခုက္ကူ)": "https://t.me/sharebykosoemoe/15420",
    "စိန်စိန်": "https://t.me/sharebykosoemoe/7951",
    "စံပယ်ဖြူနု": "https://t.me/sharebykosoemoe/8690",
    "စိုင်းလားရှိုး": "https://t.me/sharebykosoemoe/15395",
    "စိုင်းဗေဒါ": "https://t.me/sharebykosoemoe/15379",
    "စောခတ်": "https://t.me/sharebykosoemoe/15375",
    "စိန်ဝင်းစိန်": "https://t.me/sharebykosoemoe/9128",
    "စစ်ကိုင်းဦးဘိုသင်း": "https://t.me/sharebykosoemoe/15509",
    "စိုင်းစိုင်းခမ်းလှိုင်": "https://t.me/sharebykosoemoe/9706",
    "စိမ့်(ပညာရေး)": "https://t.me/sharebykosoemoe/15664",
    "စမ်းချောင်းကိုကိုအောင်": "https://t.me/sharebykosoemoe/15698",
    "စမ်းစမ်းနွဲ့": "https://t.me/sharebykosoemoe/15654",
    "စံ-ဇာဏီဘို": "https://t.me/sharebykosoemoe/15645",
    "စက္ကောမ": "https://t.me/sharebykosoemoe/15640",
    "စိတြ": "https://t.me/sharebykosoemoe/15637",
    "စိတြအဂ္ဂ": "https://t.me/sharebykosoemoe/15582",
    "စိုးသွေး": "https://t.me/sharebykosoemoe/15576",
    "စောညို": "https://t.me/sharebykosoemoe/15820",
    "စောပြည့်ချမ်းသာ": "https://t.me/sharebykosoemoe/15812",
    "စောပြည့်မာလာ": "https://t.me/sharebykosoemoe/15802",
    "စောမုံညင်း": "https://t.me/sharebykosoemoe/15798",
    "စုံထောက်‌မောင်ရေခဲ": "https://t.me/sharebykosoemoe/15794",
    "စိုးမောင်မောင်": "https://t.me/sharebykosoemoe/15994",
    "စိုးမြတ်သူဇာ": "https://t.me/sharebykosoemoe/16000",
    "စိုးမြင့်လတ်": "https://t.me/sharebykosoemoe/15997",
    "စောဝေ": "https://t.me/sharebykosoemoe/16028",
    "စွမ်းထက်အောင်": "https://t.me/sharebykosoemoe/16035",
    "စွဲမက်သျှင်": "https://t.me/sharebykosoemoe/16039",
    "စုလှဖြူ": "https://t.me/sharebykosoemoe/16050",
    "စိုးဝင်းထွဋ်": "https://t.me/sharebykosoemoe/16056",
    "စိုးဝင်း": "https://t.me/sharebykosoemoe/16062",
    "စိုးသိဏ်း": "https://t.me/sharebykosoemoe/16066",
    "စပယ်ဦး": "https://t.me/sharebykosoemoe/16082",
    "စုကြည်ထွေး": "https://t.me/sharebykosoemoe/16093",
    "ဆွေမြင့်": "https://t.me/sharebykosoemoe/16119",
    "ဆွေမင်း(ဓနုဖြူ)": "https://t.me/sharebykosoemoe/16150",
    "ဆွေလှိုင်ဦး": "https://t.me/sharebykosoemoe/16169",
    "ဆွေဆွေအောင်": "https://t.me/sharebykosoemoe/16267",
    "ဆရာဦးသိန်းလွင်": "https://t.me/sharebykosoemoe/16530",
    "ဆလိုင်းလျန်မှုန်း": "https://t.me/sharebykosoemoe/16522",
    "ဆရာဇေယျာမိုး": "https://t.me/sharebykosoemoe/16511",
    "ဆရာစိန်ဆန်း": "https://t.me/sharebykosoemoe/16500",
    "ဆရာကြီးဦးကြင်ရွှေ": "https://t.me/sharebykosoemoe/16486",
    "ဆန်းလွင်": "https://t.me/sharebykosoemoe/16624",
    "ဆန်းလင်း": "https://t.me/sharebykosoemoe/16674",
    "ဆန်းထွန်း": "https://t.me/sharebykosoemoe/16614",
    "ဆောင်းလုလင်": "https://t.me/sharebykosoemoe/16974",
    "ဆောင်းဝင်းလတ်": "https://t.me/sharebykosoemoe/17037",
    "ဆရာတော်ဦးဇောတိက": "https://t.me/sharebykosoemoe/16950",
    "ဆုထက်": "https://t.me/sharebykosoemoe/17073",
    "ဆရာကြီးဦးတင်ဦး": "https://t.me/sharebykosoemoe/16947",
    "ဆရာတော်ဘဒ္ဒန္တဝေပုလ္လ": "https://t.me/sharebykosoemoe/17145",
    "ဆင်ဖြူကျွန်းအောင်သိန်း": "https://t.me/sharebykosoemoe/995",
    "ဆုအဉ္ဇလီ": "https://t.me/sharebykosoemoe/17315",
    "ဆုလေးနွယ်": "https://t.me/sharebykosoemoe/1620",
    "ဆူးငှက်": "https://t.me/sharebykosoemoe/17393",
    "ဆုမြတ်မွန်မွန်": "https://t.me/sharebykosoemoe/17432",
    "ဆရာတော်ဓမ္မပိယ": "https://t.me/sharebykosoemoe/23866",
    "ဇဝန": "https://t.me/sharebykosoemoe/8869",
    "ဇာဂနာ": "https://t.me/sharebykosoemoe/9600",
    "ဇာနည်": "https://t.me/sharebykosoemoe/17571",
    "ဇော်ဂျီ": "https://t.me/sharebykosoemoe/8146",
    "ဇော်ထက်": "https://t.me/sharebykosoemoe/17644",
    "ဇော်ထက်အောင်": "https://t.me/sharebykosoemoe/17627",
    "ဇော်ဇော်အောင်": "https://t.me/sharebykosoemoe/16347",
    "ဇော်ပိုင်ဖြိုး": "https://t.me/sharebykosoemoe/2252",
    "ဇော်သန့်": "https://t.me/sharebykosoemoe/17665",
    "ဇေယျသူ": "https://t.me/sharebykosoemoe/17671",
    "ဇေယျ": "https://t.me/sharebykosoemoe/17675",
    "ဇော်လင်း": "https://t.me/sharebykosoemoe/17679",
    "ဇင်သန့်": "https://t.me/sharebykosoemoe/17712",
    "ဇင်ယော်နီ": "https://t.me/sharebykosoemoe/17714",
    "ဇော်နိုင်ငံစိုး": "https://t.me/sharebykosoemoe/17723",
    "ဇော်လွင်ဦး": "https://t.me/sharebykosoemoe/17772",
    "ဇော်ဝင်းကြူ": "https://t.me/sharebykosoemoe/17776",
    "ဇာနီအောင်": "https://t.me/sharebykosoemoe/17781",
    "ဇေယျမင်းသျှင်": "https://t.me/sharebykosoemoe/17785",
    "ဇေယျာမောင်": "https://t.me/sharebykosoemoe/17952",
    "ဇင်ယော်(မာန်)": "https://t.me/sharebykosoemoe/17964",
    "ဇင်မင်း (သမိန်ထော)": "https://t.me/sharebykosoemoe/17969",
    "ဇော်မျိုးဟန်": "https://t.me/sharebykosoemoe/17981",
    "ဇူးဇူး": "https://t.me/sharebykosoemoe/17987",
    "ညောင်ကန်အေးဆရာတော်ဘဒ္ဒန္တဣန္ဒက": "https://t.me/sharebykosoemoe/18057",
    "ညောင်လေးပင်ဆရာတော်": "https://t.me/sharebykosoemoe/18048",
    "ညေး": "https://t.me/sharebykosoemoe/843",
    "ညီနောင်": "https://t.me/sharebykosoemoe/18198",
    "ညီညီနိုင်": "https://t.me/sharebykosoemoe/18156",
    "ညီပုလေး": "https://t.me/sharebykosoemoe/1154",
    "ညီသစ်": "https://t.me/sharebykosoemoe/638",
    "ညိုမြ": "https://t.me/sharebykosoemoe/804",
    "ညွန့်ဦး": "https://t.me/sharebykosoemoe/18359",
    "ညောင်ရမ်းဇေယျပဏ္ဍိတ": "https://t.me/sharebykosoemoe/18350",
    "တက္ကသိုလ်မင်းသူ": "https://t.me/sharebykosoemoe/18534",
    "တက္ကသိုလ်နေလင်းအောင်": "https://t.me/sharebykosoemoe/18538",
    "တက္ကသိုလ်လှကြွယ်": "https://t.me/sharebykosoemoe/18568",
    "တာတေ": "https://t.me/sharebykosoemoe/9950",
    "တန်ခူးလေပြေ": "https://t.me/sharebykosoemoe/18572",
    "တာရာမင်းဝေ": "https://t.me/sharebykosoemoe/1247",
    "တိက္ကမ": "https://t.me/sharebykosoemoe/9867",
    "တက္ကသိုလ်ခင်မောင်အေး": "https://t.me/sharebykosoemoe/18937",
    "တက္ကသိုလ်နန္ဒမိတ်": "https://t.me/sharebykosoemoe/19071",
    "တက္ကသိုလ်‌နေဝင်း": "https://t.me/sharebykosoemoe/19040",
    "တက္ကသိုလ်ဘုန်းနိုင်": "https://t.me/sharebykosoemoe/656",
    "တက္ကသိုလ်စိန်တင်": "https://t.me/sharebykosoemoe/917",
    "တက္ကသိုလ်သျှင်သီရိ": "https://t.me/sharebykosoemoe/19490",
    "တက္ကသိုလ်တင်မြင့်": "https://t.me/sharebykosoemoe/19641",
    "တက္ကသိုလ်ဝင်းကြွယ်": "https://t.me/sharebykosoemoe/19826",
    "တက်တိုး": "https://t.me/sharebykosoemoe/822",
    "တင့်ဆန်း": "https://t.me/sharebykosoemoe/19898",
    "တင်အောင်နီ": "https://t.me/sharebykosoemoe/19885",
    "တင်ထွေး": "https://t.me/sharebykosoemoe/20053",
    "တင်မောင်မြင့်": "https://t.me/sharebykosoemoe/17015",
    "တင်မောင်အေး": "https://t.me/sharebykosoemoe/20033",
    "တင်မော်(ဓာတု)": "https://t.me/sharebykosoemoe/8086",
    "တင်မောင်ဝင်း": "https://t.me/sharebykosoemoe/20126",
    "တင်နိုင်တိုး": "https://t.me/sharebykosoemoe/20157",
    "တင်ဆွေမိုး": "https://t.me/sharebykosoemoe/20216",
    "တင်သန်းဦး": "https://t.me/sharebykosoemoe/20236",
    "တင့်တယ်": "https://t.me/sharebykosoemoe/1134",
    "တိုက်စိုး": "https://t.me/sharebykosoemoe/20210",
    "တိုးတက်": "https://t.me/sharebykosoemoe/20254",
    "တွင်းကြီးဝမ်းမောင်": "https://t.me/sharebykosoemoe/20205",
    "တွင်းကြီးသားတင်ဝင်းဦး": "https://t.me/sharebykosoemoe/20202",
    "တြိစက္က": "https://t.me/sharebykosoemoe/1557",
    "တြိသင်္ခ": "https://t.me/sharebykosoemoe/20460",
    "တင်မိုး": "https://t.me/sharebykosoemoe/20452",
    "တက္ကသိုလ်မြစိမ်း": "https://t.me/sharebykosoemoe/20549",
    "တက္ကသိုလ် ရဲလင်းအောင်": "https://t.me/sharebykosoemoe/20762",
    "တင်ညွန့်": "https://t.me/sharebykosoemoe/757",
    "တက္ကသိုလ် စိုးယဉ်": "https://t.me/sharebykosoemoe/20756",
    "အောင်ကျော်ဟိန်း": "https://t.me/sharebykosoemoe/20798",
    "အောင်ဇေရတု": "https://t.me/sharebykosoemoe/20840",
    "အရှင်ရေဝတ": "https://t.me/sharebykosoemoe/20831",
    "အောင်မြတ်ဌေး": "https://t.me/sharebykosoemoe/20900",
    "အောက်စ်ဖို့ဒ်ဆရာတော် ဒေါက်တာဓမ္မဿာမိ": "https://t.me/sharebykosoemoe/20876",
    "အောင်ခြိမ့်": "https://t.me/sharebykosoemoe/836",
    "အောင်ကိုဦး": "https://t.me/sharebykosoemoe/17610",
    "အကြည်တော်": "https://t.me/sharebykosoemoe/648",
    "အောင်သင်း": "https://t.me/sharebykosoemoe/737",
    "အထောင်တော်လှအောင်": "https://t.me/sharebykosoemoe/938",
    "အချော့တော်": "https://t.me/sharebykosoemoe/10975",
    "အိမောင်": "https://t.me/sharebykosoemoe/10317",
    "အတ္တကျော်": "https://t.me/sharebykosoemoe/8500",
    "အက္ခရာ": "https://t.me/sharebykosoemoe/946",
    "အရှင်တေဇနိယ": "https://t.me/sharebykosoemoe/20869",
    "အရှင်စက္ကိန္ဒ": "https://t.me/sharebykosoemoe/20894",
    "အရှင်ဓမ္မပါလ": "https://t.me/sharebykosoemoe/21064",
    "အရှင်ဉာဏသာမိ": "https://t.me/sharebykosoemoe/21068",
    "အောင်ဝင်း": "https://t.me/sharebykosoemoe/21123",
    "အထင်ကရ": "https://t.me/sharebykosoemoe/21126",
    "အလင်းသစ်": "https://t.me/sharebykosoemoe/21129",
    "အရှင်ပုညာနန္ဒ": "https://t.me/sharebykosoemoe/21131",
    "အရှင်ဝါသေဋ္ဌာဘိဝံသ": "https://t.me/sharebykosoemoe/21133",
    "အသင်": "https://t.me/sharebykosoemoe/21215",
    "အရိုး": "https://t.me/sharebykosoemoe/21217",
    "အရှင်နာဂသိန်": "https://t.me/sharebykosoemoe/21219",
    "M ရှိန်မြင့်": "https://t.me/sharebykosoemoe/21223",
    "အဏ္ဏဝါစိုးမိုး": "https://t.me/sharebykosoemoe/21225",
    "အရှင်အာစာရလင်္ကာရ": "https://t.me/sharebykosoemoe/21229",
    "အရှင်ဆန္ဒာဓိက": "https://t.me/sharebykosoemoe/21337",
    "အရှင်ဆေကိန္ဒ": "https://t.me/sharebykosoemoe/21547",
    "အရှင်ဓမ္မဿာမီဘိဝံသ": "https://t.me/sharebykosoemoe/21750",
    "အရှင်ဣန္ဒကာဘိဝံသ": "https://t.me/sharebykosoemoe/21741",
    "အရှင်ကေလာသ": "https://t.me/sharebykosoemoe/21862",
    "အောင်ဆန်းဆရာတော် ဘဒ္ဒန္တသဒ္ဓမ္မ ကိတ္တိသာရ": "https://t.me/sharebykosoemoe/21864",
    "အရှင်ကုမာရ": "https://t.me/sharebykosoemoe/21866",
    "အရှင်သုန္ဒရ": "https://t.me/sharebykosoemoe/21868",
    "အရှင်ဇေယျပဏ္ဍိတ": "https://t.me/sharebykosoemoe/21870",
    "အောင်အေး": "https://t.me/sharebykosoemoe/21942",
    "အောင်ထိုက်": "https://t.me/sharebykosoemoe/21944",
    "အောင်ခန့်": "https://t.me/sharebykosoemoe/22033",
    "အောင်ခင်စိုး": "https://t.me/sharebykosoemoe/22036",
    "အောင်ကိုဦး": "https://t.me/sharebykosoemoe/22039",
    "အောင်ကြောင်းဖြာ": "https://t.me/sharebykosoemoe/22097",
    "အောင်ကျော်စွာ": "https://t.me/sharebykosoemoe/22297",
    "အောင်လင်း": "https://t.me/sharebykosoemoe/22299",
    "အောင်လှိုင်": "https://t.me/sharebykosoemoe/22302",
    "အောင်စိုး": "https://t.me/sharebykosoemoe/22531",
    "အောင်ဆန်းစုကြည်": "https://t.me/sharebykosoemoe/22537",
    "အောင်ပြည့်": "https://t.me/sharebykosoemoe/22543",
    "အောင်နိမိတ်": "https://t.me/sharebykosoemoe/22560",
    "အောင်မြတ်ဦး": "https://t.me/sharebykosoemoe/22569",
    "အောင်မင်းအောင်": "https://t.me/sharebykosoemoe/22587",
    "အဂ္ဂရာဇာ": "https://t.me/sharebykosoemoe/22590",
    "အနော်မာ": "https://t.me/sharebykosoemoe/22611",
    "အဂ္ဂဇော်": "https://t.me/sharebykosoemoe/22615",
    "အလိမ္မာ": "https://t.me/sharebykosoemoe/20954",
    "အောင်သစ်": "https://t.me/sharebykosoemoe/22619",
    "အောင်ဝေး": "https://t.me/sharebykosoemoe/22623",
    "အုံးစိန်": "https://t.me/sharebykosoemoe/22657",
    "အောင်ရဲလင်း": "https://t.me/sharebykosoemoe/22662",
    "အောင်ဇေရတု": "https://t.me/sharebykosoemoe/22678",
    "အောင်ဇေယျ": "https://t.me/sharebykosoemoe/22682",
    "အောင်ဇင်": "https://t.me/sharebykosoemoe/22749",
    "အေးထွန်းမင်း": "https://t.me/sharebykosoemoe/22757",
    "အေးမောင်ကျော်": "https://t.me/sharebykosoemoe/22764",
    "အိမ်းကြာသိုက်": "https://t.me/sharebykosoemoe/22769",
    "အိမ့်(ရန်ကုန်တက္ကသိုလ်)": "https://t.me/sharebykosoemoe/22779",
    "အီကြာကွေး": "https://t.me/sharebykosoemoe/22793",
    "အင်ဂျန်း": "https://t.me/sharebykosoemoe/22805",
    "အင်းစိန်အောင်စိုး": "https://t.me/sharebykosoemoe/22810",
    "Lလင်း": "https://t.me/sharebykosoemoe/22821",
    "အိုမာဆမ်": "https://t.me/sharebykosoemoe/22823",
    "အိုစွမ်းပြည့်": "https://t.me/sharebykosoemoe/22825",
    "အော်ပီကျယ်": "https://t.me/sharebykosoemoe/22828",
    "အရိန္ဒမာ": "https://t.me/sharebykosoemoe/22830",
    "အရှင်နန္ဒမာလာဘိဝံသ": "https://t.me/sharebykosoemoe/23408",
    "ထိပ်တင်ထွဋ်": "https://t.me/sharebykosoemoe/22885",
    "ထက်အောင်ဇင်": "https://t.me/sharebykosoemoe/22968",
    "ထက်ထက်ထွန်း": "https://t.me/sharebykosoemoe/815",
    "ထက်မြက်": "https://t.me/sharebykosoemoe/22895",
    "ထောင်မှူးကြီးသိန်းဝင်း": "https://t.me/sharebykosoemoe/22909",
    "ထင်လင်း": "https://t.me/sharebykosoemoe/1293",
    "ထက်ထက်တင်ဇာ": "https://t.me/sharebykosoemoe/13207",
    "ထူးမြတ်ကြယ်": "https://t.me/sharebykosoemoe/22992",
    "ထူးဆွေအောင်": "https://t.me/sharebykosoemoe/23007",
    "ထွန်းလင်း": "https://t.me/sharebykosoemoe/23022",
    "ထွန်းလွင်": "https://t.me/sharebykosoemoe/23027",
    "ထွန်းမြင့်ဌေး": "https://t.me/sharebykosoemoe/23033",
    "ထွန်းရွှေခိုင်": "https://t.me/sharebykosoemoe/23334",
    "ဒဂုန်ခင်ခင်လေး": "https://t.me/sharebykosoemoe/591",
    "ဒဂုန်တာယာ": "https://t.me/sharebykosoemoe/929",
    "ဒေါက်တာစိုးလွင်": "https://t.me/sharebykosoemoe/8539",
    "ဒေါက်တာမောင်မောင်ညို": "https://t.me/sharebykosoemoe/8596",
    "ဒေါက်တာအုန်းမောင်": "https://t.me/sharebykosoemoe/8512",
    "ဒေါက်တာဖြိုးသီဟ": "https://t.me/sharebykosoemoe/4733",
    "ဒဂုန်ရွှေမျှား": "https://t.me/sharebykosoemoe/1194",
    "ဒီနိုင်းခ": "https://t.me/sharebykosoemoe/23190",
    "ဒေဝီ": "https://t.me/sharebykosoemoe/23277",
    "ဒေါက်တာမာမာဆွေ": "https://t.me/sharebykosoemoe/23346",
    "ဒွါရာဝတီ-အသျှင်ကုသလ": "https://t.me/sharebykosoemoe/23353",
    "ဒေါက်တာမြင့်လွင်": "https://t.me/sharebykosoemoe/23361",
    "ဒေါက်တာအုန်းမောင်": "https://t.me/sharebykosoemoe/23369",
    "ဒေါက်တာလှဘေ": "https://t.me/sharebykosoemoe/23373",
    "ဒဂုန်ဦးစန်း‌ငွေ": "https://t.me/sharebykosoemoe/23380",
    "ထွဏ်းအောင်ကျော်": "https://t.me/sharebykosoemoe/23390",
    "ဒေါက်တာညဏ်ဟိန်းလတ်": "https://t.me/sharebykosoemoe/23402",
    "ဒီရဲဂျာ": "https://t.me/sharebykosoemoe/23419",
    "ဒေါ်ခင်လှတင်": "https://t.me/sharebykosoemoe/23787",
    "ဒေါင်းနွယ်စကြာ": "https://t.me/sharebykosoemoe/23794",
    "ဒဿကျော်စွာ": "https://t.me/sharebykosoemoe/23810",
    "ဒေဝစကြာ": "https://t.me/sharebykosoemoe/24332",
    "ဒဂုန်ဦးထွန်းမြင့်": "https://t.me/sharebykosoemoe/23857",
    "ဒေါ်အုန်းကြည်သား": "https://t.me/sharebykosoemoe/24330",
    "ဒေါ်မိုး": "https://t.me/sharebykosoemoe/23945",
    "ဒေဝတာ": "https://t.me/sharebykosoemoe/24470",
    "ဓနုတ်ကိုကိုဇော်": "https://t.me/sharebykosoemoe/10980",
    "ဓူဝံ": "https://t.me/sharebykosoemoe/1197",
    "နေဝင်းမြင့်": "https://t.me/sharebykosoemoe/1178",
    "နတ်နွယ်": "https://t.me/sharebykosoemoe/925",
    "နိုင်ဝင်းဆွေ": "https://t.me/sharebykosoemoe/1280",
    "နိုင်းနိုင်းစနေ": "https://t.me/sharebykosoemoe/694",
    "နုနုရည် အင်းဝ": "https://t.me/sharebykosoemoe/11124",
    "နွေအိမ်မောင်ဝင်း": "https://t.me/sharebykosoemoe/9123",
    "နွယ်ဂျာသိုင်း": "https://t.me/sharebykosoemoe/9069",
    "နေဗလ်": "https://t.me/sharebykosoemoe/1130",
    "နိုင်ဦး119": "https://t.me/sharebykosoemoe/8344",
    "နတ်သမီး": "https://t.me/sharebykosoemoe/1657",
    "ပုညခင်": "https://t.me/sharebykosoemoe/577",
    "ပါပီယွန်": "https://t.me/sharebykosoemoe/2495",
    "ပါရဂူ": "https://t.me/sharebykosoemoe/7667",
    "ပီမိုးနင်း": "https://t.me/sharebykosoemoe/807",
    "ဖရော်ဆန်": "https://t.me/sharebykosoemoe/8970",
    "ဖြိုးကျော်": "https://t.me/sharebykosoemoe/8908",
    "ဖေမြင့်": "https://t.me/sharebykosoemoe/624",
    "ဖြိုးဝေ": "https://t.me/sharebykosoemoe/2639",
    "ဗန်းမော်တင်အောင်": "https://t.me/sharebykosoemoe/7999",
    "‌ဗန်းမော်သိန်းဖေ": "https://t.me/sharebykosoemoe/652",
    "ဗျူး": "https://t.me/sharebykosoemoe/1268",
    "ဘဲဥ": "https://t.me/sharebykosoemoe/9187",
    "မြသန်းတင့်": "https://t.me/sharebykosoemoe/628",
    "မောင်ထွန်းသူ": "https://t.me/sharebykosoemoe/7875",
    "မယ်ညို": "https://t.me/sharebykosoemoe/1015",
    "မင်းဒင်": "https://t.me/sharebykosoemoe/16288",
    "မောင်မိုးသူ": "https://t.me/sharebykosoemoe/7885",
    "မောင်စိန်ဝင်း(ပုတီးကုန်း)": "https://t.me/sharebykosoemoe/13880",
    "မစန္ဒာ": "https://t.me/sharebykosoemoe/704",
    "မအိုဇာ": "https://t.me/sharebykosoemoe/12723",
    "မိုးမိုး(အင်းလျား)": "https://t.me/sharebykosoemoe/611",
    "မင်းယုဝေ": "https://t.me/sharebykosoemoe/883",
    "မင်းသုဝဏ်": "https://t.me/sharebykosoemoe/8149",
    "မင်းခိုက်စိုးစန်": "https://t.me/sharebykosoemoe/878",
    "မောင်ညိုမှိုင်း": "https://t.me/sharebykosoemoe/11142",
    "မောင်သိန်းဆိုင်": "https://t.me/sharebykosoemoe/732",
    "မောင်မြင့်ကြွယ်": "https://t.me/sharebykosoemoe/765",
    "မောင်ဖေငယ်": "https://t.me/sharebykosoemoe/10367",
    "မောင်ဉာဏ်ကြွယ်": "https://t.me/sharebykosoemoe/10363",
    "မောင်ခင်မင်": "https://t.me/sharebykosoemoe/10339",
    "မောင်ထင်": "https://t.me/sharebykosoemoe/10291",
    "မွန်ဟော်စီ": "https://t.me/sharebykosoemoe/2297",
    "မောင်ချောနွယ်": "https://t.me/sharebykosoemoe/8939",
    "မောင်ကျောက်တိုင်": "https://t.me/sharebykosoemoe/768",
    "မောင်ဆုရှင်": "https://t.me/sharebykosoemoe/1853",
    "မောင်သာချို": "https://t.me/sharebykosoemoe/751",
    "မြကျေး": "https://t.me/sharebykosoemoe/9301",
    "မိုးရှင်း": "https://t.me/sharebykosoemoe/608",
    "မင်းလူ": "https://t.me/sharebykosoemoe/1919",
    "မျိုးလွင်(MBA)": "https://t.me/sharebykosoemoe/683",
    "မောရိသျှ": "https://t.me/sharebykosoemoe/1214",
    "မယ်လွင့်": "https://t.me/sharebykosoemoe/2202",
    "မယ်ခိုင်": "https://t.me/sharebykosoemoe/6854",
    "မနောဟရီ": "https://t.me/sharebykosoemoe/3505",
    "မောင်ဆန္ဒ": "https://t.me/sharebykosoemoe/1265",
    "မင်းသိင်္ခ": "https://t.me/sharebykosoemoe/1524",
    "မမသဒ္ဒါမောင်": "https://t.me/sharebykosoemoe/1623",
    "မင်းမြတ်သူရ": "https://t.me/sharebykosoemoe/1640",
    "မြတ်ငြိမ်း": "https://t.me/sharebykosoemoe/667",
    "မဟာဆွေ": "https://t.me/sharebykosoemoe/777",
    "ယဉ်ကျေးမှုဝန်ကြီးဌာန": "https://t.me/sharebykosoemoe/23054",
    "ယူနီဆက်စ်": "https://t.me/sharebykosoemoe/23062",
    "ယောဆရာတော်": "https://t.me/sharebykosoemoe/23066",
    "ယဉ်ယဉ်လဲ့": "https://t.me/sharebykosoemoe/23114",
    "ယွန်းအိန္ဒြေ": "https://t.me/sharebykosoemoe/23119",
    "ယုဝတီခင်ဦး": "https://t.me/sharebykosoemoe/23123",
    "ယုဝတီခင်စိန်လှိုင်": "https://t.me/sharebykosoemoe/23130",
    "ယုဝတီမာလာသိန်း": "https://t.me/sharebykosoemoe/23399",
    "ရွှေကူမေနှင်း": "https://t.me/sharebykosoemoe/10314",
    "ရှိတ်": "https://t.me/sharebykosoemoe/9828",
    "ရွှေဥဒေါင်း": "https://t.me/sharebykosoemoe/632",
    "ရန်ကုန်ဘဆွေ": "https://t.me/sharebykosoemoe/774",
    "လင်းခါး": "https://t.me/sharebykosoemoe/5557",
    "လူထုဒေါ်အမာ": "https://t.me/sharebykosoemoe/864",
    "လယ်တီပဏ္ဍိတဦးမောင်ကြီး": "https://t.me/sharebykosoemoe/12493",
    "လင်္ကာရည်ကျော်": "https://t.me/sharebykosoemoe/12772",
    "လင်းယုန်သစ်လွင်": "https://t.me/sharebykosoemoe/833",
    "လူနေ": "https://t.me/sharebykosoemoe/895",
    "လွန်းထားထား": "https://t.me/sharebykosoemoe/861",
    "လယ်တွင်းသားစောချစ်": "https://t.me/sharebykosoemoe/830",
    "လင်းရောင်စင်": "https://t.me/sharebykosoemoe/9805",
    "လင်းယုန်မောင်မောင်": "https://t.me/sharebykosoemoe/3901",
    "လမင်းမိုမို": "https://t.me/sharebykosoemoe/6159",
    "လင်းသိုက်ညွန့်": "https://t.me/sharebykosoemoe/741",
    "လရောင်ကျူးရင့်": "https://t.me/sharebykosoemoe/1256",
    "သော်တာဆွေ": "https://t.me/sharebykosoemoe/1604",
    "သာဓု": "https://t.me/sharebykosoemoe/12483",
    "သိုးဆောင်း": "https://t.me/sharebykosoemoe/571",
    "သုမောင်": "https://t.me/sharebykosoemoe/8221",
    "သခင်ဘသောင်း": "https://t.me/sharebykosoemoe/12487",
    "သိပ္ပံမောင်ဝ": "https://t.me/sharebykosoemoe/761",
    "သတိုးနွယ်": "https://t.me/sharebykosoemoe/10445",
    "သော်တာမင်း": "https://t.me/sharebykosoemoe/9832",
    "သန်းတင့်": "https://t.me/sharebykosoemoe/9434",
    "သိန်းဖေမြင့်": "https://t.me/sharebykosoemoe/1161",
    "သဟာဆွေလှိုင်း": "https://t.me/sharebykosoemoe/5170",
    "ဟိန်းဇော်": "https://t.me/sharebykosoemoe/17606",
    "ဟိန်းလတ်": "https://t.me/sharebykosoemoe/12665"
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
    
    print(f"🔍 AUTHOR DETECTION - Input: '{text[:100]}'")
    
    import re
    
    def normalize_string(s):
        s = re.sub(r'[၊။\s()\-]+', '', s)
        return s.lower()
    
    normalized_text = normalize_string(text)
    
    for author_name in AUTHOR_LINKS.keys():
        normalized_author = normalize_string(author_name)
        
        if normalized_author in normalized_text:
            print(f"✅✅✅ AUTHOR FOUND: '{author_name}' in text")
            return {
                "name": author_name,
                "link": AUTHOR_LINKS[author_name]
            }
    
    print(f"❌ No author found in text")
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
ပျော်ရွှင်စရာ စာဖတ်ချိန်လေးဖြစ်ပါစေ... 🥰
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
            bot.send_photo(
                message.chat.id, 
                WELCOME_IMAGE_URL, 
                caption=caption,
                reply_markup=welcome_kb,
                parse_mode="HTML"
            )
        except Exception as e:
            try:
                bot.send_message(
                    message.chat.id,
                    caption,
                    reply_markup=welcome_kb,
                    parse_mode="HTML"
                )
            except:
                pass

# ======================================================
# MAIN GROUP MESSAGE HANDLER
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"], content_types=['text', 'photo', 'video', 'document', 'audio'])
def handle_group_messages(message):
    """Group messages handler"""
    
    if message.text and message.text.startswith('/'):
        track_active_group(message.chat.id)
        return
    if message.new_chat_members:
        return
    
    track_active_group(message.chat.id)
    
    try:
        chat_info = bot.get_chat(message.chat.id)
        chat_title = chat_info.title if hasattr(chat_info, 'title') else f"Chat {message.chat.id}"
        print(f"\n" + "="*50)
        print(f"📨 GROUP MESSAGE")
        print(f"📝 Chat: {chat_title} (Type: {chat_info.type})")
    except:
        print(f"\n" + "="*50)
        print(f"📨 GROUP MESSAGE")
        print(f"📝 Chat ID: {message.chat.id}")
    
    print(f"👤 From: {message.from_user.first_name if message.from_user else 'Unknown'}")
    print(f"💬 Text: {message.text[:100] if message.text else 'Media'}")
    print(f"📊 Active Groups: {len(active_groups)}")
    
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
                warning_msg = f'⚠️ [{user_name}](tg://user?id={user_id}) 💢\n\n**Link🔗 များကို ပိတ်ထားပါတယ်** 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် **Owner** ကို ဆက်သွယ်ပါ...'
            else:
                warning_msg = f'⚠️ {user_name} 💢\n\n**Link🔗 များကို ပိတ်ထားပါတယ်** 🙅🏻\n\n ❗လိုအပ်ချက်ရှိရင် **Owner** ကို ဆက်သွယ်ပါ...'
            
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
# /SHOWPOST COMMAND
# ======================================================
@bot.message_handler(commands=['showpost'])
def show_all_posts_preview(message):
    """Show preview of ALL posts"""
    print(f"📊 /showpost command from user: {message.from_user.id}")
    
    try:
        print("🎨 Preparing ALL posts preview...")
        
        myanmar_time = get_myanmar_time()
        current_date = myanmar_time.strftime("%B %d")
        current_time = myanmar_time.strftime("%H:%M:%S")
        
        status_msg = bot.send_message(
            message.chat.id,
            "<b>📊 PREPARING ALL POSTS PREVIEW...</b>\n\nPlease wait while I gather all post information...",
            parse_mode="HTML"
        )
        
        # 1. BIRTHDAY POST PREVIEW
        birthday_caption = BIRTHDAY_CAPTION_TEMPLATE.format(current_date=current_date)
        birthday_image = get_next_birthday_image()
        
        # 2. MYANMAR MUSIC POST PREVIEW
        myanmar_music_keyboard = types.InlineKeyboardMarkup()
        myanmar_music_keyboard.row(
            types.InlineKeyboardButton("Oscar's Music 🎶", url="https://t.me/oscarmyanmarmusic")
        )
        
        # 3. ENGLISH MUSIC POST PREVIEW
        english_music_keyboard = types.InlineKeyboardMarkup()
        english_music_keyboard.row(
            types.InlineKeyboardButton("English Music 🎶", url="https://t.me/oscarenglishmusic")
        )
        
        # 4. POEM POST PREVIEW
        poem_image = get_next_poem_image()
        poem_keyboard = types.InlineKeyboardMarkup()
        poem_keyboard.row(
            types.InlineKeyboardButton("နှလုံးသားဒဿန 🍃", url="https://t.me/oscarpoem")
        )
        
        # 5. PROMO VIDEO PREVIEW
        promo_keyboard = types.InlineKeyboardMarkup()
        promo_keyboard.row(
            types.InlineKeyboardButton("စာပေချစ်သူများအတွက် 🍓", url="https://t.me/bookbykosoemoe")
        )
        promo_keyboard.row(
            types.InlineKeyboardButton("စာအုပ်ရှာရန် 📚📖", url="https://t.me/oscar_libray_bot")
        )
        
        # Stats
        stats_text = f"""
<b>📊 ALL POSTS PREVIEW & SCHEDULE</b>

<b>⏰ Current Myanmar Time:</b> {current_time}
<b>📅 Current Date:</b> {current_date}

<b>🎯 POSTING SCHEDULE:</b>
1️⃣ <b>Birthday Posts:</b> 8:00 AM Daily
2️⃣ <b>Myanmar Music:</b> 10:00 AM & 6:00 PM
3️⃣ <b>English Music:</b> 2:00 PM & 10:00 PM
4️⃣ <b>Poem Posts:</b> 4:00 PM & 8:00 PM
5️⃣ <b>Promo Video:</b> 12:00 AM & 12:00 PM

<b>📢 FIXED CHANNELS:</b> {len(MANUAL_CHANNEL_IDS)} channels
<b>📊 ACTIVE GROUPS:</b> {len(active_groups)} groups

<b>🖼️ IMAGE ROTATION:</b>
• Birthday: {len(BIRTHDAY_IMAGES)} images
• Poem: {len(POEM_IMAGES)} images

<i>Now showing previews...</i>
"""
        
        bot.edit_message_text(
            stats_text,
            message.chat.id,
            status_msg.message_id,
            parse_mode="HTML"
        )
        
        time.sleep(1)
        
        # Send previews
        bot.send_message(message.chat.id, "<b>🎂 POST 1: BIRTHDAY POST</b>", parse_mode="HTML")
        bot.send_photo(message.chat.id, birthday_image, caption=birthday_caption, parse_mode="HTML")
        
        time.sleep(1)
        
        bot.send_message(message.chat.id, "<b>🎶 POST 2: MYANMAR MUSIC</b>", parse_mode="HTML")
        bot.send_photo(message.chat.id, MUSIC_MYANMAR_IMAGE, caption=MUSIC_MYANMAR_CAPTION, reply_markup=myanmar_music_keyboard, parse_mode="HTML")
        
        time.sleep(1)
        
        bot.send_message(message.chat.id, "<b>🎧 POST 3: ENGLISH MUSIC</b>", parse_mode="HTML")
        bot.send_photo(message.chat.id, MUSIC_ENGLISH_IMAGE, caption=MUSIC_ENGLISH_CAPTION, reply_markup=english_music_keyboard, parse_mode="HTML")
        
        time.sleep(1)
        
        bot.send_message(message.chat.id, "<b>🍃 POST 4: POEM POST</b>", parse_mode="HTML")
        bot.send_photo(message.chat.id, poem_image, caption=POEM_CAPTION, reply_markup=poem_keyboard, parse_mode="HTML")
        
        time.sleep(1)
        
        bot.send_message(message.chat.id, "<b>📚 POST 5: PROMO VIDEO</b>", parse_mode="HTML")
        bot.send_video(message.chat.id, PROMO_VIDEO, caption=PROMO_CAPTION, reply_markup=promo_keyboard, parse_mode="HTML")
        
        print("✅ All posts preview completed")
        
    except Exception as e:
        error_msg = f"❌ Error showing posts preview: {e}"
        print(error_msg)
        bot.reply_to(message, error_msg)

# ======================================================
# /ALLADMINLIST COMMAND - WITH ACTIVE CHECK
# ======================================================
@bot.message_handler(commands=['alladminlist'])
def list_all_admin_command(message):
    """Find and list ALL chats where bot is admin - WITH ACTIVE CHECK"""
    print(f"🔍 /alladminlist command from user: {message.from_user.id}")
    
    try:
        # Send initial message
        status_msg = bot.reply_to(message, 
            "🔍 <b>ADMIN SCAN STARTED</b>\n\n"
            "Scanning all chats where bot is admin...\n"
            "Checking active status...\n"
            "This may take a moment...", 
            parse_mode="HTML"
        )
        
        admin_chats = []
        fixed_channels = []
        active_admin_groups = []
        
        print(f"🔍 Starting admin scan with active check...")
        
        # 1. Check fixed channels
        print(f"📢 Checking {len(MANUAL_CHANNEL_IDS)} fixed channels...")
        
        for channel_id in MANUAL_CHANNEL_IDS:
            try:
                chat_info = bot.get_chat(channel_id)
                chat_title = chat_info.title if hasattr(chat_info, 'title') else f"Channel {channel_id}"
                
                # Check admin status
                if check_bot_admin(channel_id):
                    fixed_channels.append({
                        'id': channel_id,
                        'title': chat_title,
                        'type': 'channel',
                        'active': True
                    })
                    print(f"✅ Fixed channel active: {chat_title}")
                else:
                    fixed_channels.append({
                        'id': channel_id,
                        'title': chat_title,
                        'type': 'channel',
                        'active': False
                    })
                    print(f"❌ Fixed channel not admin: {chat_title}")
            except Exception as e:
                print(f"⚠️ Error checking fixed channel {channel_id}: {e}")
                fixed_channels.append({
                    'id': channel_id,
                    'title': f"Channel {channel_id}",
                    'type': 'channel',
                    'active': False,
                    'error': str(e)[:100]
                })
        
        # 2. Check active groups for admin status
        print(f"\n👥 Checking {len(active_groups)} active groups...")
        
        for chat_id in list(active_groups):
            try:
                # Don't duplicate fixed channels
                if chat_id in MANUAL_CHANNEL_IDS:
                    continue
                    
                chat_info = bot.get_chat(chat_id)
                chat_title = chat_info.title if hasattr(chat_info, 'title') else f"Group {chat_id}"
                
                # Check admin status
                if check_bot_admin(chat_id):
                    active_admin_groups.append({
                        'id': chat_id,
                        'title': chat_title,
                        'type': chat_info.type,
                        'active': True
                    })
                    print(f"✅ Active group admin: {chat_title}")
                else:
                    # Remove non-admin groups
                    active_groups.discard(chat_id)
                    print(f"❌ Removed non-admin group: {chat_title}")
                    
            except Exception as e:
                print(f"⚠️ Error checking active group {chat_id}: {e}")
                # Remove errored groups
                active_groups.discard(chat_id)
        
        # Combine all admin chats
        for chat in fixed_channels:
            if chat['active']:
                admin_chats.append(chat)
        
        for chat in active_admin_groups:
            if chat['active']:
                admin_chats.append(chat)
        
        # Prepare response
        response = f"""
<b>🔍 ADMIN SCAN RESULTS</b>

<b>📊 STATISTICS:</b>
• Total Admin Chats Found: <b>{len(admin_chats)}</b>
• Fixed Channels: {len([c for c in fixed_channels if c['active']])}/{len(fixed_channels)} active
• Active Admin Groups: {len(active_admin_groups)} groups
• Total Active Groups Tracked: {len(active_groups)}

<b>🎯 TOTAL POST TARGETS: {len(admin_chats)}</b>
└─ Fixed Channels: {len([c for c in fixed_channels if c['active']])}
└─ Auto-discovered Admin Groups: {len(active_admin_groups)}

<b>📢 FIXED CHANNELS ({len(fixed_channels)}):</b>
"""
        
        # List fixed channels with status
        for i, chat in enumerate(fixed_channels):
            status_icon = "✅" if chat['active'] else "❌"
            response += f"\n{i+1}. {status_icon} {chat['title']}"
            if not chat['active']:
                response += f" (Not Admin)"
            response += f" (ID: <code>{chat['id']}</code>)"
        
        response += f"\n\n<b>👥 AUTO-DISCOVERED ADMIN GROUPS ({len(active_admin_groups)}):</b>"
        
        # List admin groups
        if active_admin_groups:
            for i, chat in enumerate(active_admin_groups[:20]):  # Show first 20
                response += f"\n{i+1}. ✅ {chat['title']} ({chat['type']}) - ID: <code>{chat['id']}</code>"
            
            if len(active_admin_groups) > 20:
                response += f"\n... and {len(active_admin_groups) - 20} more groups"
        else:
            response += "\n❌ No admin groups found via auto-discovery!"
            response += f"\n\n<b>💡 How to add groups:</b>"
            response += f"\n1. Make bot admin in your group"
            response += f"\n2. Send any message in that group"
            response += f"\n3. Bot will automatically track it"
        
        response += f"""
        
<b>📈 SYSTEM STATUS:</b>
• Active Groups in Memory: {len(active_groups)}
• Will Receive Next Birthday Post: {len(admin_chats)} chats
• Next Birthday Image: {current_birthday_index + 1}/{len(BIRTHDAY_IMAGES)}

<b>🔄 To refresh groups list:</b>
• Send any message in each group where bot is admin
• Bot will automatically track active groups
"""
        
        # Add a note about missing groups
        if len(active_groups) < 5:  # If very few groups tracked
            response += f"""
            
<b>⚠️ WARNING: Few groups tracked ({len(active_groups)})</b>
• Bot needs to receive messages in groups to track them
• Visit each group and send a test message
• Check /myid in each group to ensure bot is working
"""
        
        # Update the message
        bot.edit_message_text(
            response,
            message.chat.id,
            status_msg.message_id,
            parse_mode="HTML"
        )
        
        print(f"✅ /alladminlist completed:")
        print(f"   - Admin chats found: {len(admin_chats)}")
        print(f"   - Fixed channels: {len([c for c in fixed_channels if c['active']])}")
        print(f"   - Active admin groups: {len(active_admin_groups)}")
        
    except Exception as e:
        error_msg = f"❌ Error in alladminlist: {e}"
        print(error_msg)
        bot.reply_to(message, error_msg)

# ======================================================
# /MYID COMMAND
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
"""
    
    # Check if bot is admin in this chat
    try:
        is_admin = check_bot_admin(message.chat.id)
        response += f"<b>Bot Admin Status:</b> {'✅ YES' if is_admin else '❌ NO'}\n"
        response += f"<b>Will Receive Birthday Posts:</b> {'✅ YES' if is_admin else '❌ NO'}\n"
        
        # Add to active groups if admin
        if is_admin and message.chat.id < 0:
            active_groups.add(message.chat.id)
            response += f"<b>Added to Active Groups:</b> ✅ YES\n"
    except:
        response += f"<b>Bot Admin Status:</b> ❓ Unknown\n"
    
    response += f"""
<b>Active Groups Tracking:</b> {len(active_groups)} groups
<b>For link posting:</b>
✅ Admin users can post links
❌ Non-admin users cannot post links
"""
    
    bot.reply_to(message, response, parse_mode="HTML")
    print(f"📊 User {user_id} checked ID in chat {message.chat.id}")

# ======================================================
# /STATUS COMMAND
# ======================================================
@bot.message_handler(commands=['status'])
def bot_status(message):
    """Show bot status and next post time"""
    
    try:
        myanmar_time = get_myanmar_time()
        current_time = myanmar_time.strftime("%H:%M:%S")
        current_date = myanmar_time.strftime("%Y-%m-%d")
        
        # Count admin groups
        admin_groups_count = 0
        for chat_id in list(active_groups):
            if check_bot_admin(chat_id) and chat_id not in MANUAL_CHANNEL_IDS:
                admin_groups_count += 1
        
        status_text = f"""
<b>🤖 BOT STATUS REPORT</b>

<b>⏰ Current Myanmar Time:</b> {current_time}
<b>📅 Current Date:</b> {current_date}
<b>📍 Timezone:</b> Asia/Yangon

<b>🎂 BIRTHDAY POST SYSTEM:</b>
<b>Last Post Date:</b> {last_birthday_post_date or "Never"}
<b>Next Post:</b> Tomorrow at 8:00 AM
<b>Images in Rotation:</b> {len(BIRTHDAY_IMAGES)} images
<b>Current Image Index:</b> {current_birthday_index + 1}/{len(BIRTHDAY_IMAGES)}

<b>🎶 CONTENT POSTING SCHEDULE:</b>
• Myanmar Music: 10:00 AM & 6:00 PM
• English Music: 2:00 PM & 10:00 PM
• Poem Posts: 4:00 PM & 8:00 PM (5 images rotation)
• Promo Video: 12:00 AM & 12:00 PM

<b>📊 STATISTICS:</b>
<b>Fixed Channels:</b> {len(MANUAL_CHANNEL_IDS)}
<b>Active Chats Tracked:</b> {len(active_groups)}
<b>Admin Chats (Auto-discovered):</b> {admin_groups_count}
<b>Total Auto-Post Targets:</b> {len(MANUAL_CHANNEL_IDS) + admin_groups_count}

<b>🔧 COMMANDS:</b>
• /start - Bot start
• /showpost - Preview ALL posts
• /alladminlist - List all groups & admin status (with active check)
• /status - This status report
• /myid - Show your Telegram ID

<b>🌟 AUTO DISCOVERY:</b>
✅ No manual adding needed
✅ Automatically tracks groups when messages received
✅ Just make bot admin and send message in group
✅ Admin status checked before each post
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
    "န": "https://t.me/sharebykosoemoe/39",
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
print(f"📊 Active Groups Tracked: {len(active_groups)}")

print("\n📅 POSTING SCHEDULE:")
print("="*60)
print("✅ Birthday Posts: 8:00 AM Daily")
print("✅ Myanmar Music: 10:00 AM & 6:00 PM")
print("✅ English Music: 2:00 PM & 10:00 PM")
print("✅ Poem Posts: 4:00 PM & 8:00 PM")
print("✅ Promo Video: 12:00 AM & 12:00 PM")

print("\n🔧 COMMANDS:")
print("="*60)
print("✅ /start - Bot start")
print("✅ /showpost - Preview ALL posts")
print("✅ /alladminlist - List all groups & admin status (with active check)")
print("✅ /status - Bot status report")
print("✅ /myid - Show your Telegram ID")

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
