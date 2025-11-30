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

# ===============================
# BOT TOKEN & URL (Environment Variables)
# ===============================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4')
WEBHOOK_URL = "https://oscar-library-bot.onrender.com/" + BOT_TOKEN
PING_URL = "https://oscar-library-bot.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

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

ဘ၀ခရီးကို မပူမပင်မကြောင့်ကြစေရပဲ အေးအေးချမ်းချမ်း ဖြတ်သန်းသွားနိုင်ပါစေ 💞

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
    while True:
        try:
            requests.get(PING_URL, timeout=10)
            print("🌐 Keep-alive ping sent")
        except Exception as e:
            print(f"🌐 Keep-alive error: {e}")
        time.sleep(300)  # 5 minutes

threading.Thread(target=keep_alive, daemon=True).start()

# ===============================
# ACTIVE GROUPS TRACKING
# ===============================
def track_active_group(chat_id):
    """Active group တွေကို track လုပ်ခြင်း"""
    if chat_id < 0:  # Groups and channels only
        active_groups.add(chat_id)
        if len(active_groups) > 100:
            active_groups.pop()

# ===============================
# IMPROVED TIME CHECK SYSTEM
# ===============================

def should_send_birthday_post():
    """မနက် ၈ နာရီကျရင် True return ပြန်ခြင်း - FIXED"""
    try:
        myanmar_time = get_myanmar_time()
        current_time = myanmar_time.strftime("%H:%M")
        current_date = myanmar_time.strftime("%Y-%m-%d")
        
        print(f"⏰ Time check: {current_time} (Myanmar Time)")
        
        # ✅ FIXED: 08:00 နာရီတစ်ခုလုံးစစ်ဆေးခြင်း
        if current_time.startswith("08:"):
            # တစ်ရက်ကို ၁ ခါပဲ post တင်ရန်
            global last_birthday_post
            
            if last_birthday_post != current_date:
                last_birthday_post = current_date
                print("✅ Birthday post triggered!")
                return True
        return False
    except Exception as e:
        print(f"⏰ Time check error: {e}")
        return False

# ===============================
# IMPROVED CHANNEL POSTING SYSTEM
# ===============================

def send_to_target_channels():
    """Target channels အားလုံးကို birthday post တင်ခြင်း - IMPROVED"""
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
            # Check if bot can send messages to channel
            try:
                chat = bot.get_chat(channel_id)
                print(f"📢 Channel info: {chat.title}")
            except Exception as e:
                error_msg = f"Cannot access channel: {e}"
                print(f"❌ {error_msg}")
                results.append((channel_id, False, error_msg))
                continue
            
            # Check bot permissions in channel
            try:
                chat_member = bot.get_chat_member(channel_id, bot.get_me().id)
                if chat_member.status not in ['administrator', 'creator']:
                    error_msg = "Bot is not admin in channel"
                    print(f"❌ {error_msg}")
                    results.append((channel_id, False, error_msg))
                    continue
            except Exception as e:
                error_msg = f"Cannot check bot permissions: {e}"
                print(f"❌ {error_msg}")
                results.append((channel_id, False, error_msg))
                continue
            
            # ✅ Send photo to channel
            bot.send_photo(
                channel_id,
                BIRTHDAY_IMAGE_URL,
                caption=caption,
                parse_mode="HTML"
            )
            
            print(f"✅ Successfully posted to channel: {channel_id}")
            results.append((channel_id, True, "Success"))
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Channel post failed for {channel_id}: {error_msg}")
            
            # Specific error handling for channels
            if "CHAT_WRITE_FORBIDDEN" in error_msg:
                detailed_error = "Bot doesn't have permission to post in channel"
            elif "CHAT_NOT_FOUND" in error_msg:
                detailed_error = "Channel not found or bot not in channel"
            elif "bot is not a member" in error_msg.lower():
                detailed_error = "Bot is not a member of the channel"
            elif "Too Many Requests" in error_msg:
                detailed_error = "Rate limit exceeded, try again later"
            else:
                detailed_error = error_msg
                
            results.append((channel_id, False, detailed_error))
    
    return results

# ===============================
# IMPROVED GROUP DISCOVERY AND POSTING
# ===============================

def discover_all_admin_chats():
    """Admin ဖြစ်တဲ့ group အားလုံးကို auto discover လုပ်ခြင်း"""
    admin_chats = set()
    
    try:
        print("🕵️ Auto-discovering admin chats...")
        
        # Use tracked active groups (groups only)
        print(f"🔍 Checking {len(active_groups)} tracked chats...")
        for chat_id in list(active_groups):
            try:
                chat_member = bot.get_chat_member(chat_id, bot.get_me().id)
                if chat_member.status in ['administrator', 'creator']:
                    # Check if bot can send messages
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
    """Groups များအားလုံးကို post တင်ခြင်း - IMPROVED"""
    success_count = 0
    failed_groups = []
    
    myanmar_time = get_myanmar_time()
    current_date = myanmar_time.strftime("%B %d")
    caption = BIRTHDAY_CAPTION_TEMPLATE.format(current_date=current_date)
    
    print(f"🎂 Starting group posts to {len(admin_groups)} groups...")
    
    for i, chat_id in enumerate(admin_groups):
        try:
            # ✅ Rate limiting: 1 second delay between messages
            if i > 0:
                time.sleep(1)
            
            bot.send_photo(
                chat_id,
                BIRTHDAY_IMAGE_URL,
                caption=caption,
                parse_mode="HTML"
            )
            success_count += 1
            print(f"✅ [{i+1}/{len(admin_groups)}] Sent to group: {chat_id}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ [{i+1}/{len(admin_groups)}] Failed for group {chat_id}: {error_msg}")
            failed_groups.append((chat_id, error_msg))
            
            # Remove if no permission
            if any(x in error_msg for x in ["Forbidden", "blocked", "no rights", "kicked"]):
                active_groups.discard(chat_id)
    
    return success_count, failed_groups

def send_birthday_to_all_chats():
    """Groups နဲ့ channels အားလုံးကို post တင်ခြင်း - IMPROVED"""
    global post_in_progress
    
    if post_in_progress:
        print("⚠️ Post already in progress, skipping...")
        return
        
    post_in_progress = True
    try:
        total_success = 0
        results = {
            'channels_success': 0,
            'channels_total': 0,
            'channels_failed': [],
            'groups_success': 0,
            'groups_total': 0,
            'groups_failed': []
        }
        
        print("🎂 Starting birthday posts...")
        
        # 1. First, send to target channels
        if MANUAL_CHANNEL_IDS:
            print("📢 Posting to channels...")
            channel_results = send_to_target_channels()
            results['channels_total'] = len(channel_results)
            
            for channel_id, success, error in channel_results:
                if success:
                    results['channels_success'] += 1
                    total_success += 1
                else:
                    results['channels_failed'].append((channel_id, error))
        
        # 2. Then send to all admin groups
        admin_groups = discover_all_admin_chats()
        results['groups_total'] = len(admin_groups)
        
        if admin_groups:
            print(f"👥 Posting to {len(admin_groups)} groups...")
            groups_success, groups_failed = send_to_groups(admin_groups)
            results['groups_success'] = groups_success
            results['groups_failed'] = groups_failed
            total_success += groups_success
        else:
            print("ℹ️ No admin groups found to post")
        
        # 3. Print summary
        total_targets = len(MANUAL_CHANNEL_IDS) + len(admin_groups)
        print(f"✅ Birthday posts completed: {total_success}/{total_targets} chats")
        
        # 4. Log detailed results
        log_birthday_results(results)
        
    except Exception as e:
        print(f"🎂 Birthday system error: {e}")
    finally:
        post_in_progress = False

def log_birthday_results(results):
    """Birthday post results ကို log ရေးခြင်း"""
    try:
        log_entry = f"""
📊 BIRTHDAY POST RESULTS - {get_myanmar_time().strftime('%Y-%m-%d %H:%M:%S')}
        
📢 Channels: {results['channels_success']}/{results['channels_total']} successful
👥 Groups: {results['groups_success']}/{results['groups_total']} successful

📈 Overall: {results['channels_success'] + results['groups_success']}/{results['channels_total'] + results['groups_total']} targets
"""
        print(log_entry)
        
        # Failed channels details
        if results['channels_failed']:
            print("❌ Failed Channels:")
            for channel_id, error in results['channels_failed']:
                print(f"   - {channel_id}: {error}")
                
        # Failed groups details
        if results['groups_failed']:
            print("❌ Failed Groups:")
            for chat_id, error in results['groups_failed']:
                print(f"   - {chat_id}: {error}")
                
    except Exception as e:
        print(f"📊 Results logging error: {e}")

# ===============================
# SCHEDULER SYSTEM
# ===============================

def birthday_scheduler():
    """မနက် ၈ နာရီတိုင်း post တင်ခြင်း - IMPROVED"""
    print("🎂 IMPROVED Birthday Scheduler Started!")
    print("⏰ Will post daily throughout 8:00 AM hour (Myanmar Time)")
    print(f"📢 Target Channels: {len(MANUAL_CHANNEL_IDS)}")
    
    last_check = None
    
    while True:
        try:
            current_time = get_myanmar_time()
            current_minute = current_time.strftime("%H:%M")
            
            # ✅ Check every minute, but only process once per minute
            if last_check != current_minute:
                last_check = current_minute
                
                if should_send_birthday_post():
                    print(f"🚀 Triggering birthday posts at {current_time.strftime('%H:%M:%S')}")
                    send_birthday_to_all_chats()
                else:
                    print(f"⏰ Waiting... Current time: {current_minute}")
                    
        except Exception as e:
            print(f"🎂 Scheduler error: {e}")
        
        time.sleep(30)  # Check every 30 seconds

# Start birthday scheduler
birthday_thread = threading.Thread(target=birthday_scheduler, daemon=True)
birthday_thread.start()

# ===============================
# ENHANCED LINK DETECTION SYSTEM
# ===============================

def is_link(text):
    """Comprehensive link detection with more patterns"""
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Comprehensive link patterns
    link_patterns = [
        "http://", "https://", "www.", ".com", ".org", ".net", 
        ".io", ".me", ".tk", ".ml", ".ga", ".cf", 
        "t.me/", "telegram.me/", "telegram.dog/",
        "youtube.com/", "youtu.be/", "facebook.com/", "fb.me/",
        "twitter.com/", "x.com/", "instagram.com/", "whatsapp.com/",
        "discord.gg/", "discord.com/", "messenger.com/",
        "bit.ly/", "tinyurl.com/", "shorturl.at/",
        "drive.google.com/", "docs.google.com/", "dropbox.com/",
        "pastebin.com/", "github.com/", "git.io/",
        "//", "://", ".co/", ".tk/", ".ml/", ".ga/", ".cf/"
    ]
    
    return any(pattern in text_lower for pattern in link_patterns)

def has_link_api(message):
    """Comprehensive link detection in all message parts including forwarded"""
    
    # 1) Check normal message text
    if message.text and is_link(message.text):
        print(f"🔗 Link found in text: {message.text[:50]}...")
        return True
    
    # 2) Check normal caption
    if message.caption and is_link(message.caption):
        print(f"🔗 Link found in caption: {message.caption[:50]}...")
        return True
    
    # 3) Check entities (URLs, text links) in normal message
    try:
        if message.entities:
            for entity in message.entities:
                if entity.type in ["url", "text_link"]:
                    print(f"🔗 Link found in entity: {entity.type}")
                    return True
    except:
        pass
    
    # 4) Check caption entities
    try:
        if message.caption_entities:
            for entity in message.caption_entities:
                if entity.type in ["url", "text_link"]:
                    print(f"🔗 Link found in caption entity: {entity.type}")
                    return True
    except:
        pass
    
    # 5) Check forwarded messages - IMPROVED
    if message.forward_from_chat or message.forward_from:
        print(f"🔍 Checking forwarded message from: {message.forward_from_chat or message.forward_from}")
        
        # Get the actual text content from forwarded message
        forwarded_text = ""
        
        # Method 1: Direct text from forward
        if message.text:
            forwarded_text = message.text
            print(f"📨 Forwarded text: {forwarded_text[:100]}...")
        
        # Method 2: Caption from forwarded media
        elif message.caption:
            forwarded_text = message.caption
            print(f"📷 Forwarded caption: {forwarded_text[:100]}...")
        
        # Check if forwarded content has links
        if forwarded_text and is_link(forwarded_text):
            print(f"🚨 LINK DETECTED in forwarded content!")
            return True
    
    return False

# ======================================================
# 1️⃣ GROUP WELCOME SYSTEM
# ======================================================
WELCOME_IMAGE = "welcome_photo.jpg"

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    track_active_group(message.chat.id)  # ✅ Track group
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
# 2️⃣ LINK BLOCKER (GROUP ONLY) - WITH USER MENTION
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

    track_active_group(message.chat.id)  # ✅ Track group

    if has_link_api(message):
        if not is_admin(message.chat.id, message.from_user.id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
                
                # ✅ User mention with notification
                warning_msg = f'⚠️ <a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a> 💢 <b>Link🔗 များကို ပိတ်ထားပါတယ်</b> 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် <b>Owner</b> ကို ဆက်သွယ်ပါနော်...'
                
                bot.send_message(message.chat.id, warning_msg, parse_mode="HTML")
                
            except Exception as e:
                print(f"Link blocker error: {e}")

# ===============================
# /START MESSAGE - HTML FORMAT
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
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
# CATEGORY REDIRECT
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "category")
def category_redirect(call):
    bot.send_message(
        call.message.chat.id,
        "<b>📚 ကဏ္ဍအလိုက် စာအုပ်များ</b>\nhttps://t.me/oscarhelpservices/4\n\n<b>🌼 Oscar's Library 🌼</b>",
        parse_mode="HTML"
    )

# ===============================
# AUTHORS MENU (WITH BACK BUTTON)
# ===============================
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
    
    # ✅ Back button ထည့်ရန်
    kb.row(types.InlineKeyboardButton("⬅ Back", callback_data="back_to_main"))
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb, parse_mode="HTML")

# ===============================
# BACK TO MAIN MENU HANDLER
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "back_to_main")
def back_to_main(call):
    """မူလ menu ကိုပြန်သွားခြင်း"""
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

# ===============================
# AUTHOR LINKS
# ===============================
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
# ADMIN MANAGEMENT COMMANDS
# ===============================

@bot.message_handler(commands=['discover'])
def discover_admin_chats(message):
    """လက်ရှိ admin chats အားလုံးကို discover လုပ်ခြင်း"""
    try:
        if not is_admin(message.chat.id, message.from_user.id):
            return
            
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

@bot.message_handler(commands=['forcepost'])
def force_birthday_post(message):
    """ချက်ချင်း birthday post အားလုံးကိုပို့ခြင်း"""
    try:
        if not is_admin(message.chat.id, message.from_user.id):
            return
            
        bot.reply_to(message, "🚀 Force sending birthday posts...")
        send_birthday_to_all_chats()
        bot.reply_to(message, "✅ Force post completed!")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Force post error: {e}")

@bot.message_handler(commands=['testchannel'])
def test_channel_post(message):
    """Channel post test command"""
    try:
        if not is_admin(message.chat.id, message.from_user.id):
            return
            
        if not MANUAL_CHANNEL_IDS:
            bot.reply_to(message, "❌ No channels configured")
            return
            
        bot.reply_to(message, "🧪 Testing channel posts...")
        
        results = send_to_target_channels()
        
        for channel_id, success, error in results:
            if success:
                bot.reply_to(message, f"✅ Channel {channel_id}: Success")
            else:
                bot.reply_to(message, f"❌ Channel {channel_id}: {error}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Channel test error: {e}")

@bot.message_handler(commands=['poststatus'])
def post_status(message):
    """Current post status ကြည့်ရန်"""
    try:
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

# ===============================
# FLASK SERVER
# ===============================
app = Flask(__name__)

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
# INITIALIZE WEBHOOK
# ===============================
print("🤖 INITIALIZING IMPROVED BOT...")
try:
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook set: {WEBHOOK_URL}")
    print("🎂 IMPROVED Birthday Scheduler: ACTIVE")
    print("⏰ Fixed time check: Will trigger throughout 8:00 AM hour")
    print(f"📢 Target Channels: {len(MANUAL_CHANNEL_IDS)}")
    print("🔗 Enhanced link detection: ACTIVE")
    print("📊 Detailed logging implemented")
    
except Exception as e:
    print(f"❌ Webhook error: {e}")

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
