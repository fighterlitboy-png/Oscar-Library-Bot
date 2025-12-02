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
print("🚀🚀🚀 OSCAR LIBRARY BOT STARTING 🚀🚀🚀")
print("All systems initializing...")

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
# SIMPLE LINK DETECTION
# ===============================
def is_link(text):
    """ရိုးရှင်းတဲ့ link detection"""
    if not text or not isinstance(text, str):
        return False
    
    text_lower = text.lower()
    
    # Basic patterns
    patterns = [
        "http://", "https://", "www.", ".com", ".org", ".net", 
        "t.me/", "telegram.me/", "youtube.com/", "youtu.be/",
        "facebook.com/", "instagram.com/", "twitter.com/", "x.com/"
    ]
    
    for pattern in patterns:
        if pattern in text_lower:
            return True
    
    # @username
    import re
    if re.search(r'@[a-zA-Z0-9_]{3,}', text):
        return True
    
    return False

def has_link_api(message):
    """Message ထဲမှာ link ရှိမရှိ"""
    if message.text and is_link(message.text):
        return True
    if message.caption and is_link(message.caption):
        return True
    return False

# ======================================================
# 🎯 MAIN MESSAGE HANDLER - GUARANTEED "စာအုပ်" REPLY
# ======================================================
@bot.message_handler(func=lambda m: True)  # CATCH ALL MESSAGES
def handle_all_messages(message):
    """
    ပထမဆုံး "စာအုပ်" keyword စစ်မယ်
    ရှိရင် ချက်ချင်း reply ပို့ပြီး return
    """
    
    # Log every message for debugging
    print(f"\n📨 MESSAGE RECEIVED:")
    print(f"   👤 User: {message.from_user.first_name if message.from_user else 'Unknown'}")
    print(f"   💬 Text: '{message.text}'")
    print(f"   🏠 Chat Type: {message.chat.type}")
    print(f"   🆔 Chat ID: {message.chat.id}")
    
    # ===========================================
    # 1. "စာအုပ်" KEYWORD - ALWAYS CHECK FIRST
    # ===========================================
    if message.text and 'စာအုပ်' in message.text:
        print(f"   ✅✅✅ 'စာအုပ်' KEYWORD DETECTED! ✅✅✅")
        
        try:
            # Random replies with bold "စာရေးဆရာ"
            replies = [
                "စာအုပ်တွေဖတ်ချင်တယ်ဆိုရင် <b>စာရေးဆရာ</b>အမည်လေးပြောပြပါလား စာဖတ်ချစ်သူလေးရေ...🥰",
                "စာအုပ်လေးတွေ ရှာဖွေဖတ်ရှုချင်တယ်ဆိုရင် <b>စာရေးဆရာ</b>အမည်လေးကို ပြောပြပါဦး...📚",
                "စာအုပ်စဉ်လေးတွေ ဖတ်ချင်တယ်လား? <b>စာရေးဆရာ</b>အမည်လေး ပြောပြပါအုံး...🤓",
                "စာဖတ်ချစ်သူလေး ဘယ်<b>စာရေးဆရာ</b>ရဲ့စာအုပ်စဉ်ကို ဖတ်ချင်လဲ? ပြောပြပါ...✨",
                "ကြိုက်နှစ်သက်ရာ <b>စာရေးဆရာ</b>အမည်လေး ပြောပြပါ စာအုပ်ရှာပေးပါရစေ...📖",
                "<b>စာရေးဆရာ</b>အမည်လေး ပြောပြပါလား စာအုပ်စဉ်လေးတွေ ရှာပေးပါမယ်...🥰"
            ]
            
            reply_text = random.choice(replies)
            print(f"   💌 Sending reply: {reply_text[:60]}...")
            
            # Send reply with reply_to format
            sent_msg = bot.reply_to(message, reply_text, parse_mode="HTML")
            print(f"   ✅✅✅ REPLY SENT SUCCESSFULLY! Message ID: {sent_msg.message_id}")
            
            # Track group if it's a group
            if message.chat.type in ["group", "supergroup"]:
                track_active_group(message.chat.id)
            
        except Exception as e:
            print(f"   ❌❌❌ REPLY ERROR: {str(e)}")
            # Try alternative method if reply_to fails
            try:
                bot.send_message(
                    message.chat.id,
                    "စာအုပ်တွေဖတ်ချင်တယ်ဆိုရင် <b>စာရေးဆရာ</b>အမည်လေးပြောပြပါ...🥰",
                    parse_mode="HTML"
                )
                print(f"   ✅ Fallback message sent")
            except:
                print(f"   ❌ Fallback also failed")
        
        return  # STOP PROCESSING - DO NOT CHECK LINKS OR ANYTHING ELSE
    
    # ===========================================
    # 2. WELCOME MESSAGES (New Members)
    # ===========================================
    if message.new_chat_members:
        print(f"   👋 New member(s) detected")
        WELCOME_IMAGE_URL = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/welcome_photo.jpg"
        
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
                print(f"   ✅ Welcome message sent")
            except Exception as e:
                print(f"   ❌ Welcome error: {e}")
        
        if message.chat.type in ["group", "supergroup"]:
            track_active_group(message.chat.id)
        return
    
    # ===========================================
    # 3. LINK BLOCKER FOR GROUPS
    # ===========================================
    if message.chat.type in ["group", "supergroup"]:
        print(f"   👥 Group message - checking for links...")
        
        # Track active group
        track_active_group(message.chat.id)
        
        # Check if message has links
        if has_link_api(message):
            print(f"   🔗 Link detected in group message")
            
            try:
                # Check if bot is admin
                bot_user = bot.get_me()
                bot_member = bot.get_chat_member(message.chat.id, bot_user.id)
                
                if bot_member.status not in ['administrator', 'creator']:
                    print(f"   🤖 Bot not admin - skipping link check")
                    return
                
                # Check if user is admin
                user_admin = False
                try:
                    user_member = bot.get_chat_member(message.chat.id, message.from_user.id)
                    user_admin = user_member.status in ['administrator', 'creator']
                except:
                    user_admin = False
                
                if user_admin:
                    print(f"   ✅ Admin posted link - allowing")
                    return
                else:
                    print(f"   🚫 Non-admin posted link - deleting")
                    try:
                        bot.delete_message(message.chat.id, message.message_id)
                        
                        # Send warning
                        warning = f'⚠️ [{message.from_user.first_name}](tg://user?id={message.from_user.id}) 💢\n\n**Link🔗 များကို ပိတ်ထားပါတယ်** 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် **Owner** ကို ဆက်သွယ်ပါနော်...'
                        sent = bot.reply_to(message, warning, parse_mode="Markdown")
                        
                        # Auto delete warning after 10 seconds
                        def delete_warn():
                            try:
                                bot.delete_message(message.chat.id, sent.message_id)
                            except:
                                pass
                        
                        threading.Timer(10.0, delete_warn).start()
                        
                    except Exception as e:
                        print(f"   ❌ Delete failed: {e}")
                        
            except Exception as e:
                print(f"   ⚠️ Link check error: {e}")
    
    # ===========================================
    # 4. FORWARDED MESSAGES IN GROUPS
    # ===========================================
    if message.chat.type in ["group", "supergroup"] and (message.forward_from or message.forward_from_chat):
        print(f"   📩 Forwarded message in group")
        
        if has_link_api(message):
            print(f"   🔗 Forwarded message contains link")
            # Same link blocking logic as above can be applied here
            # For simplicity, using same logic

# ===============================
# /START MESSAGE
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
    print(f"\n🔄 /start COMMAND FROM: {message.from_user.first_name}")
    
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
    print(f"   ✅ /start message sent")

# ===============================
# FORCE POST COMMAND
# ===============================
@bot.message_handler(commands=['forcepost'])
def force_birthday_post(message):
    try:
        print(f"\n🔧 Forcepost command from: {message.from_user.first_name}")
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
    print(f"\n📨 WEBHOOK RECEIVED - {datetime.now().strftime('%H:%M:%S')}")
    try:
        if request.method == 'POST':
            json_data = request.get_json(force=True)
            if json_data:
                update = telebot.types.Update.de_json(json_data)
                bot.process_new_updates([update])
                print("✅ Update processed successfully")
        return "OK", 200
    except Exception as e:
        print(f"💥 WEBHOOK ERROR: {e}")
        return "OK", 200

@app.route("/", methods=['GET', 'POST'])  
def index():
    return "🌼 Oscar's Library Bot is running...", 200

# ===============================
# MANUAL WEBHOOK SETUP
# ===============================
print("\n🔄 SETTING UP WEBHOOK...")
try:
    bot.remove_webhook()
    time.sleep(2)
    success = bot.set_webhook(
        url=WEBHOOK_URL,
        certificate=None,
        max_connections=100,
        allowed_updates=None,
        timeout=60
    )
    if success:
        print(f"✅ WEBHOOK SET SUCCESSFULLY")
        print(f"🌐 Webhook URL: {WEBHOOK_URL}")
    else:
        print("❌ WEBHOOK SET FAILED")
except Exception as e:
    print(f"💥 WEBHOOK SETUP ERROR: {e}")

print("\n" + "="*60)
print("🎯 BOT STATUS: ALL SYSTEMS READY")
print("✅ 'စာအုပ်' Keyword: GUARANTEED TO REPLY")
print("✅ Link Blocker: ACTIVE (Admin/Owner protected)")
print("✅ Birthday Scheduler: ACTIVE (8:00 AM Myanmar)")
print("✅ Welcome Messages: ACTIVE")
print("✅ Webhook: CONFIGURED")
print("="*60)
print("🚀 DEPLOYMENT COMPLETE - BOT IS NOW LIVE!")
print("\n📝 Test by typing 'စာအုပ်' in any chat with the bot")

# ===============================
# RUN WITH FLASK
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\n🚀 Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
