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
    """မြန်မာစံတော်ချိန်ရယူခြင်း"""
    return datetime.now(MYANMAR_TZ)

BIRTHDAY_IMAGE_URL = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/Happy_Birthday_Photo.jpg"
BIRTHDAY_CAPTION_TEMPLATE = """<b>Birthday Wishes 💌</b>

<b>Happy Birthday ❤️ ကမ္ဘာ❣️</b>
<b>ပျော်ရွှင်စရာမွေးနေ့လေးဖြစ်ပါစေ..🎂💗</b>

<b>{current_date}</b> မွေးနေ့လေးမှစ နောင်နှစ်ပေါင်းများစွာတိုင်အောင်... 

ကိုယ်၏ကျန်းမာခြင်း စိတ်၏ချမ်းသာခြင်းများနဲ့ပြည့်စုံပြီး လိုအပ်ချက်လိုအင်ဆန္ဒများ လည်းပြည့်ဝပါစေ...

ဘ၀ခရီးကို မပူမပင်မကြောင့်ကြစေရပဲအေးအေးချမ်းချမ်း ဖြတ်သန်းသွားနိုင်ပါစေ 💞

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
    """Active group တွေကို track လုပ်ခြင်း"""
    if chat_id < 0:
        active_groups.add(chat_id)
        if len(active_groups) > 100:
            active_groups.pop()

# ===============================
# IMPROVED TIME CHECK SYSTEM
# ===============================
def should_send_birthday_post():
    """မနက် ၈ နာရီကျရင် True return ပြန်ခြင်း"""
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
    """Target channels အားလုံးကို birthday post တင်ခြင်း"""
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
            
            # Check channel access
            chat = bot.get_chat(channel_id)
            print(f"📢 Channel info: {chat.title}")
            
            # Check bot permissions
            chat_member = bot.get_chat_member(channel_id, bot.get_me().id)
            print(f"👑 Bot role in channel: {chat_member.status}")
            
            if chat_member.status not in ['administrator', 'creator']:
                error_msg = "Bot is not admin in channel"
                print(f"❌ {error_msg}")
                results.append((channel_id, False, error_msg))
                continue
            
            # Send photo to channel
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
    """Admin ဖြစ်တဲ့ group အားလုံးကို auto discover လုပ်ခြင်း"""
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
    """Groups များအားလုံးကို post တင်ခြင်း"""
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
    """Groups နဲ့ channels အားလုံးကို post တင်ခြင်း"""
    global post_in_progress
    
    if post_in_progress:
        print("⚠️ Post already in progress, skipping...")
        return
        
    post_in_progress = True
    try:
        print("🎂🎂🎂 STARTING BIRTHDAY POSTS 🎂🎂🎂")
        total_success = 0
        
        # 1. Send to target channels
        if MANUAL_CHANNEL_IDS:
            print("📢 Posting to channels...")
            channel_results = send_to_target_channels()
            for channel_id, success, error in channel_results:
                if success:
                    total_success += 1
                    print(f"✅ Channel {channel_id}: SUCCESS")
                else:
                    print(f"❌ Channel {channel_id}: FAILED - {error}")
        
        # 2. Send to all admin groups
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
    """မနက် ၈ နာရီတိုင်း post တင်ခြင်း"""
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

# Start birthday scheduler
print("🔄 Starting birthday scheduler thread...")
birthday_thread = threading.Thread(target=birthday_scheduler, daemon=True)
birthday_thread.start()
print("✅ Birthday scheduler started")

# ===============================
# LINK DETECTION SYSTEM
# ===============================
def is_link(text):
    """Comprehensive link detection"""
    if not text:
        return False
    
    text_lower = text.lower()
    link_patterns = [
        "http://", "https://", "www.", ".com", ".org", ".net", 
        ".io", ".me", ".tk", ".ml", ".ga", ".cf", 
        "t.me/", "telegram.me/", "telegram.dog/",
        "youtube.com/", "youtu.be/", "facebook.com/", "fb.me/",
        "//", "://", ".co/"
    ]
    
    return any(pattern in text_lower for pattern in link_patterns)

def has_link_api(message):
    """Comprehensive link detection in all message parts"""
    if message.text and is_link(message.text):
        return True
    if message.caption and is_link(message.caption):
        return True
    try:
        if message.entities:
            for entity in message.entities:
                if entity.type in ["url", "text_link"]:
                    return True
    except: pass
    try:
        if message.caption_entities:
            for entity in message.caption_entities:
                if entity.type in ["url", "text_link"]:
                    return True
    except: pass
    if message.forward_from_chat or message.forward_from:
        forwarded_text = ""
        if message.text:
            forwarded_text = message.text
        elif message.caption:
            forwarded_text = message.caption
        if forwarded_text and is_link(forwarded_text):
            return True
    return False

# ======================================================
# 1️⃣ GROUP WELCOME SYSTEM
# ======================================================
WELCOME_IMAGE = "welcome_photo.jpg"

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
            with open(WELCOME_IMAGE, "rb") as img:
                bot.send_photo(
                    message.chat.id, 
                    img, 
                    caption=caption,
                    reply_markup=welcome_kb,
                    parse_mode="HTML"
                )
        except Exception as e:
            print(f"Welcome image error: {e}")
            bot.send_message(
                message.chat.id,
                caption,
                reply_markup=welcome_kb,
                parse_mode="HTML"
            )

# ======================================================
# 2️⃣ LINK BLOCKER (GROUP ONLY)
# ======================================================
def is_admin(chat_id, user_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        admin_ids = [admin.user.id for admin in admins]
        return user_id in admin_ids
    except Exception as e:
        print(f"Admin check error: {e}")
        return False

@bot.message_handler(func=lambda m: m.chat.type in ["group", "supergroup"])
def handle_group_messages(message):
    if message.text and message.text.startswith('/'):
        return
    if message.new_chat_members:
        return

    track_active_group(message.chat.id)

    if has_link_api(message):
        if not is_admin(message.chat.id, message.from_user.id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
                warning_msg = f'⚠️ <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> 💢 <b>Link🔗 များကို ပိတ်ထားပါတယ်</b> 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် <b>Owner</b> ကို ဆက်သွယ်ပါနော်...'
                bot.send_message(message.chat.id, warning_msg, parse_mode="HTML")
            except Exception as e:
                print(f"Link blocker error: {e}")

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

စာရေးဆရာအလိုက်ရှာဖတ်ချင်ရင် 
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
# 3️⃣ PRIVATE CHAT MESSAGE HANDLER
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_private_messages(message):
    if message.text and message.text.startswith('/'):
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

# ===============================
# ADMIN MANAGEMENT COMMANDS - ALL USERS CAN USE
# ===============================
@bot.message_handler(commands=['forcepost'])
def force_birthday_post(message):
    """ချက်ချင်း birthday post အားလုံးကိုပို့ခြင်း - ALL USERS"""
    try:
        print(f"🔧 Forcepost command from: {message.from_user.id}")
        
        # ✅ ALL USERS CAN USE - NO ADMIN CHECK
        bot.reply_to(message, "🚀 Force sending birthday posts...")
        send_birthday_to_all_chats()
        bot.reply_to(message, "✅ Force post completed!")
        
    except Exception as e:
        error_msg = f"❌ Force post error: {e}"
        print(error_msg)
        bot.reply_to(message, error_msg)

@bot.message_handler(commands=['testchannel'])
def test_channel_post(message):
    """Channel post test command - ALL USERS"""
    try:
        print(f"🔧 Testchannel command from: {message.from_user.id}")
        
        if not MANUAL_CHANNEL_IDS:
            bot.reply_to(message, "❌ No channels configured")
            return
            
        bot.reply_to(message, "🧪 Testing channel posts...")
        
        results = send_to_target_channels()
        
        response = "📊 **Channel Test Results:**\n\n"
        for channel_id, success, error in results:
            if success:
                response += f"✅ Channel {channel_id}: Success\n"
            else:
                response += f"❌ Channel {channel_id}: {error}\n"
        
        bot.reply_to(message, response, parse_mode="Markdown")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Channel test error: {e}")

@bot.message_handler(commands=['poststatus'])
def post_status(message):
    """Current post status ကြည့်ရန် - ALL USERS"""
    try:
        print(f"🔧 Poststatus command from: {message.from_user.id}")
        
        status = "✅ Idle" if not post_in_progress else "🔄 Post in progress"
        last_post = last_birthday_post or "Never"
        
        response = f"""📊 **Post Status**

🔄 Current Status: {status}
📅 Last Post Date: {last_post}
👥 Tracked Groups: {len(active_groups)}
📢 Target Channels: {len(MANUAL_CHANNEL_IDS)}

⏰ Next check: Every minute
🕐 Myanmar Time: {get_myanmar_time().strftime('%H:%M:%S')}"""

        bot.reply_to(message, response, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Status error: {e}")

@bot.message_handler(commands=['discover'])
def discover_admin_chats(message):
    """လက်ရှိ admin chats အားလုံးကို discover လုပ်ခြင်း - ALL USERS"""
    try:
        print(f"🔧 Discover command from: {message.from_user.id}")
        
        bot.reply_to(message, "🕵️ Discovering all admin chats...")
        admin_chats = discover_all_admin_chats()
        
        response = f"""👑 **Admin Chats Discovery**

✅ **Total Admin Groups Found**: {len(admin_chats)}
📊 **Tracked Active Groups**: {len(active_groups)}
📢 **Manual Channels**: {len(MANUAL_CHANNEL_IDS)}

မနက် ၈ နာရီတိုင်း ဒီ chat {len(admin_chats)} ခုဆီ ပို့ပေးပါလိမ့်မယ်!"""

        bot.reply_to(message, response, parse_mode="Markdown")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Discovery error: {e}")

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

စာရေးဆရာအလိုက်ရှာဖတ်ချင်ရင် 
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
    """Webhook handler with FORCE PRINTING"""
    print(f"📨 WEBHOOK RECEIVED - {datetime.now()}")
    
    try:
        if request.method == 'POST':
            json_data = request.get_json(force=True)
            if json_data:
                print(f"📊 Processing update")
                update = telebot.types.Update.de_json(json_data)
                bot.process_new_updates([update])
            else:
                print("❌ No JSON data received")
        return "OK", 200
    except Exception as e:
        print(f"❌ WEBHOOK ERROR: {e}")
        return "OK", 200

@app.route("/", methods=['GET', 'POST'])  
def index():
    print("🌐 Health check received")
    return "Bot is running with DEBUG MODE...", 200

# ===============================
# INITIALIZE WEBHOOK
# ===============================
print("🔄 INITIALIZING WEBHOOK...")
try:
    print("🗑️ Removing existing webhook...")
    bot.remove_webhook()
    time.sleep(3)
    
    print("🔧 Setting up new webhook...")
    bot.set_webhook(
        url=WEBHOOK_URL,
        max_connections=100,
        timeout=60
    )
    
    print(f"✅ WEBHOOK SET SUCCESSFULLY: {WEBHOOK_URL}")
    print("🎂 Birthday Scheduler: ACTIVE")
    print("⏰ Will post daily at 8:00 AM Myanmar Time")
    print("🔧 All systems ready!")
    print("🚀 Bot is now LIVE!")
    print("💡 Available Commands: /start, /forcepost, /testchannel, /poststatus, /discover")
    
except Exception as e:
    print(f"❌❌❌ CRITICAL ERROR IN INITIALIZATION: {e}")

# ===============================
# RUN WITH FLASK
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
