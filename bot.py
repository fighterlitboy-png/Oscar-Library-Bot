import os
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import requests
import sys
from datetime import datetime, timedelta
import pytz
from collections import defaultdict
import json

# ===============================
# BOT TOKEN & URL (Environment Variables)
# ===============================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4')
WEBHOOK_URL = "https://oscar-library-bot.onrender.com/" + BOT_TOKEN
PING_URL = "https://oscar-library-bot.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ===============================
# TOP FANS POST EDITING SYSTEM (Owner Only)
# ===============================
OWNER_ID = 6272937931  # Your Telegram User ID

def is_owner(user_id):
    """Check if user is the owner"""
    return user_id == OWNER_ID

# Default Top Fans post template
TOP_FANS_POST = """🏆 **အပတ်စဉ် Top Fans များ** 🏆

ဒီအပတ်အတွင်း ကျွန်တော်တို့ချန်နယ်ကို အပြင်းအထန် အားပေးမှုအများဆုံး Member များကိုရွေးချယ်လိုက်ပါပြီ!

🎖️ **Official Top 20 Community Stars** 🎖️
ကျွန်တော်တို့ရဲ့ချန်နယ်ကို အသက်သွင်းပေးထားတဲ့ အချစ်တော်လေးများ!

🥇 GOLD Tier (Top 1-5)
1. @user1 👑 Channel King
2. @user2 ⭐ Super Star  
3. @user3 🔥 Fire Reactor
4. @user4 💬 Chat Champion
5. @user5 🎯 Most Active

🥈 SILVER Tier (Top 6-15) 
6. @user6 ✨ Rising Star
7. @user7 💫 Active Member
8. @user8 🌟 Community Hero
9. @user9 🚀 Engagement Star
10. @user10 💝 Supporter
11. @user11 👍 Top Fan
12. @user12 🔥 React Master
13. @user13 💬 Conversation Starter
14. @user14 ⭐ Future Star
15. @user15 🌈 Community Builder

🥉 BRONZE Tier (Top 16-20)
16. @user16 🎉 Celebration Star
17. @user17 💎 Diamond Member
18. @user18 🌟 Shining Star
19. @user19 🚀 Rocket Booster
20. @user20 💖 Heart Giver

💫 **နောက်အပတ်မှာ Top Fan ဘယ်သူတွေဖြစ်မလဲ...*

ဒီအပတ် ပါဝင်သူတစ်ယောက်စီတိုင်းကို အထူးကျေးဇူးတင်ရှိပါတယ်!  
နောက်အပတ်မှာတော့ သင့်နာမည် ဒီစာရင်းမှာပါအောင်...🥰

✅ React လေးတွေ ပိုပေးပါ...
✅ စကားဝိုင်းမှာ ပါဝင်ပါ...
✅ ချန်နယ်ကို အားပေးပါ...

သင့်ရဲ့ တစ်ခုတည်းသော React ကလေးက ကျွန်တော်တို့အတွက် များ�စွာအဓိပ္ပာယ်ရှိပါတယ်! 💝

🌟 **ကျေးဇူးအထူးတင်ပါတယ်...!**
ဒီချန်နယ်ကို အသက်သွင်းပေးတဲ့ Member တိုင်းကို အထူးကျေးဇူးတင်ပါတယ်။ သင့်ရဲ့ ပါဝင်မှုတိုင်းက ကျွန်တော်တို့အတွက် ဆက်လက်လုပ်ဆောင်နိုင်တဲ့ စွမ်းအားပါ!

📅 **နောက်တစ်ကြိမ် - တနင်္ဂနွေ ည ၆ နာရီ**
ဘယ်သူတွေ Top 20 ထဲဝင်မလဲ စောင့်ကြည့်လိုက်ကြရအောင်! 🎊"""

# ===============================
# EDIT TOP FANS POST COMMAND (Owner Only)
# ===============================
@bot.message_handler(commands=['edittop'])
def edit_top_post(message):
    """Edit the top fans post - Owner only"""
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ ဒီ command ကို သုံးခွင့်မရှိပါ။ Owner သာသုံးနိုင်သည်။")
        return
    
    bot.send_message(
        message.chat.id,
        "📝 **Top Fans Post ပြင်ဆင်ရန်**\n\n"
        "လက်ရှိ post ကို ကြည့်ရှုရန်: /showtop\n\n"
        "အသစ်ပြင်ဆင်ရန် စာပိုဒ်အသစ်ကို ရိုက်ပေးပါ...",
        parse_mode='Markdown'
    )
    
    # Register next step handler
    bot.register_next_step_handler(message, process_new_post)

def process_new_post(message):
    """Process the new post from owner"""
    global TOP_FANS_POST
    try:
        TOP_FANS_POST = message.text
        bot.send_message(
            message.chat.id,
            "✅ Top Fans Post ကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ!\n\n"
            "ကြည့်ရှုရန်: /showtop",
            parse_mode='Markdown'
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ ပြင်ဆင်ရာတွင် အမှားတစ်ခုဖြစ်နေသည်: {e}")

# ===============================
# SHOW TOP FANS POST COMMAND
# ===============================
@bot.message_handler(commands=['showtop'])
def show_top_post(message):
    """Show the current top fans post"""
    bot.send_message(message.chat.id, TOP_FANS_POST, parse_mode='Markdown')

# ===============================
# WEEKLY TOP FANS SYSTEM CONFIGURATION
# ===============================
CHANNEL_ID = -1002150199369  # Your channel ID
CUSTOM_REACTIONS = ['🔥', '❤️', '👍', '🎉', '👏']

# Tracking data
user_message_count = defaultdict(int)
user_reaction_count = defaultdict(int)
tracking_start_time = datetime.now(pytz.timezone('Asia/Yangon'))

# ===============================
# WEEKLY TOP FANS FUNCTIONS
# ===============================
def reset_tracking():
    """Reset tracking data for new week"""
    global user_message_count, user_reaction_count, tracking_start_time
    user_message_count.clear()
    user_reaction_count.clear()
    tracking_start_time = datetime.now(pytz.timezone('Asia/Yangon'))
    print("📊 Weekly tracking reset")

def get_user_mention(user_id, first_name):
    """Get user mention in click-to-mention format"""
    return f"[{first_name}](tg://user?id={user_id})"

def calculate_scores():
    """Calculate combined scores for users"""
    user_scores = defaultdict(int)
    all_user_ids = set(list(user_message_count.keys()) + list(user_reaction_count.keys()))
    
    for user_id in all_user_ids:
        message_score = user_message_count.get(user_id, 0)
        reaction_score = user_reaction_count.get(user_id, 0)
        user_scores[user_id] = message_score + reaction_score
        
    print(f"📈 Calculated scores for {len(user_scores)} users")
    return user_scores

async def generate_weekly_post():
    """Generate the weekly top fans post"""
    user_scores = calculate_scores()
    
    # Get top 20 users
    top_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:20]
    
    post_content = """🏆 **အပတ်စဉ် Top Fans များ** 🏆

ဒီအပတ်အတွင်း ကျွန်တော်တို့ချန်နယ်ကို အပြင်းအထန် အားပေးမှုအများဆုံး Member များကိုရွေးချယ်လိုက်ပါပြီ!

🎖️ **Official Top 20 Community Stars** 🎖️
ကျွန်တော်တို့ရဲ့ချန်နယ်ကို အသက်သွင်းပေးထားတဲ့ အချစ်တော်လေးများ!

🥇 GOLD Tier (Top 1-5)
"""
    
    # Add ranked list with mentions
    for rank, (user_id, score) in enumerate(top_users, 1):
        # In a real implementation, you'd fetch user info from Telegram API
        # For now, using placeholder
        mention = get_user_mention(user_id, f"User{user_id}")
        
        if rank == 1:
            post_content += f"1. {mention} 👑 Channel King\n"
        elif rank == 2:
            post_content += f"2. {mention} ⭐ Super Star\n"
        elif rank == 3:
            post_content += f"3. {mention} 🔥 Fire Reactor\n"
        elif rank == 4:
            post_content += f"4. {mention} 💬 Chat Champion\n"
        elif rank == 5:
            post_content += f"5. {mention} 🎯 Most Active\n"
        elif rank == 6:
            post_content += "\n🥈 SILVER Tier (Top 6-15)\n"
            post_content += f"6. {mention} ✨ Rising Star\n"
        elif rank == 7:
            post_content += f"7. {mention} 💫 Active Member\n"
        elif rank == 8:
            post_content += f"8. {mention} 🌟 Community Hero\n"
        elif rank == 9:
            post_content += f"9. {mention} 🚀 Engagement Star\n"
        elif rank == 10:
            post_content += f"10. {mention} 💝 Supporter\n"
        elif rank == 11:
            post_content += f"11. {mention} 👍 Top Fan\n"
        elif rank == 12:
            post_content += f"12. {mention} 🔥 React Master\n"
        elif rank == 13:
            post_content += f"13. {mention} 💬 Conversation Starter\n"
        elif rank == 14:
            post_content += f"14. {mention} ⭐ Future Star\n"
        elif rank == 15:
            post_content += f"15. {mention} 🌈 Community Builder\n"
        elif rank == 16:
            post_content += "\n🥉 BRONZE Tier (Top 16-20)\n"
            post_content += f"16. {mention} 🎉 Celebration Star\n"
        elif rank == 17:
            post_content += f"17. {mention} 💎 Diamond Member\n"
        elif rank == 18:
            post_content += f"18. {mention} 🌟 Shining Star\n"
        elif rank == 19:
            post_content += f"19. {mention} 🚀 Rocket Booster\n"
        elif rank == 20:
            post_content += f"20. {mention} 💖 Heart Giver\n"

    post_content += """
💫 **နောက်အပတ်မှာ Top Fan ဘယ်သူတွေဖြစ်မလဲ...*

ဒီအပတ် ပါဝင်သူတစ်ယောက်စီတိုင်းကို အထူးကျေးဇူးတင်ရှိပါတယ်!  
နောက်အပတ်မှာတော့ သင့်နာမည် ဒီစာရင်းမှာပါအောင်...🥰

✅ React လေးတွေ ပိုပေးပါ...
✅ စကားဝိုင်းမှာ ပါဝင်ပါ...
✅ ချန်နယ်ကို အားပေးပါ...

သင့်ရဲ့ တစ်ခုတည်းသော React ကလေးက ကျွန်တော်တို့အတွက် များစွာအဓိပ္ပာယ်ရှိပါတယ်! 💝

🌟 **ကျေးဇူးအထူးတင်ပါတယ်...!**
ဒီချန်နယ်ကို အသက်သွင်းပေးတဲ့ Member တိုင်းကို အထူးကျေးဇူးတင်ပါတယ်။ သင့်ရဲ့ ပါဝင်မှုတိုင်းက ကျွန်တော်တို့အတွက် ဆက်လက်လုပ်ဆောင်နိုင်တဲ့ စွမ်းအားပါ!

📅 **နောက်တစ်ကြိမ် - တနင်္ဂနွေ ည ၆ နာရီ**
ဘယ်သူတွေ Top 20 ထဲဝင်မလဲ စောင့်ကြည့်လိုက်ကြရအောင်! 🎊"""

    return post_content

def schedule_weekly_post():
    """Schedule weekly post for Sunday 6:00 PM Myanmar Time"""
    while True:
        now = datetime.now(pytz.timezone('Asia/Yangon'))
        
        # Calculate next Sunday 6:00 PM
        days_until_sunday = (6 - now.weekday()) % 7
        next_sunday = now.replace(
            hour=18, minute=0, second=0, microsecond=0
        ) + timedelta(days=days_until_sunday)
        
        # If today is Sunday but past 6 PM, schedule for next Sunday
        if now.weekday() == 6 and now.hour >= 18:
            next_sunday += timedelta(days=7)
        
        wait_seconds = (next_sunday - now).total_seconds()
        
        print(f"⏰ Next weekly post scheduled for: {next_sunday}")
        time.sleep(wait_seconds)
        
        # Post weekly update
        try:
            post_content = generate_weekly_post()
            # In a real implementation, you'd send this to your channel
            # bot.send_message(CHANNEL_ID, post_content, parse_mode='Markdown')
            print("✅ Weekly top fans post would be published here")
            
            # Reset tracking for new week
            reset_tracking()
            
        except Exception as e:
            print(f"Error in weekly post: {e}")

# Start the weekly scheduler in a separate thread
weekly_thread = threading.Thread(target=schedule_weekly_post, daemon=True)
weekly_thread.start()

# ===============================
# RENDER FONT FIX
# ===============================
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

# ===============================
# KEEP ALIVE
# ===============================
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
WELCOME_IMAGE = "welcome_photo.jpg"

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for user in message.new_chat_members:
        caption = f"""နွေးထွေးစွာကြိုဆိုပါတယ်...🧸
{user.first_name} ...🥰

📚 Oscar's Library မှ
မင်းရဲ့စာဖတ်ခြင်းအတွက် 
အမြဲအသင့်ရှိပါတယ်...🤓

✨📚 မင်းကြိုက်တဲ့စာအုပ်တွေ 
🗃️ ရွေးဖတ်ဖို့ Button ကိုနှိပ်ပါ ✨"""
        
        # Button ထည့်ရန်
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
                    reply_markup=welcome_kb
                )
        except Exception as e:
            print(f"Welcome image error: {e}")
            bot.send_message(
                message.chat.id,
                caption,
                reply_markup=welcome_kb
            )

# ======================================================
# 2️⃣ LINK BLOCKER (GROUP ONLY) - FIXED FOR FORWARDED MESSAGES
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
    
    # Skip if it's a command or new chat members
    if message.text and message.text.startswith('/'):
        return
    if message.new_chat_members:
        return

    # 🔥 FULL LINK CHECK (NORMAL + FORWARD + CAPTION + ENTITIES)
    if has_link_api(message):
        # If there's also only a mention entity (no url/text_link and no raw link),
        # has_link_api would have returned False earlier, so this block won't run.
        if not is_admin(message.chat.id, message.from_user.id):
            try:
                # Delete the message with link
                bot.delete_message(message.chat.id, message.message_id)
                
                # Send warning message
                warning_msg = f"⚠️ {message.from_user.first_name} 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်..."
                bot.send_message(message.chat.id, warning_msg)
                
            except Exception as e:
                print(f"Link blocker error: {e}")

# ===============================
# /START MESSAGE - FIXED
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
    first = message.from_user.first_name or "Friend"
    text = f"""သာယာသောနေ့လေးဖြစ်ပါစေ...🌸 **
    {first}** ...🥰
    
🌼 **Oscar's Library** 🌼 မှ ကြိုဆိုပါတယ်

စာအုပ်များရှာဖွေရန် လမ်းညွှန်ပေးမယ်...

**စာအုပ်ရှာဖို့ နှစ်ပိုင်းခွဲထားတယ် 
📚ကဏ္ဍအလိုက် 💠 ✍️စာရေးဆရာ**

Fic၊ ကာတွန်း၊ သည်းထိပ်ရင်ဖို 
စသည့်ကဏ္ဍများရှာဖတ်ချင်ရင် 
**📚ကဏ္ဍအလိုက်** ကိုနှိပ်ပါ။

စာရေးဆရာအလိုက်ရှာဖတ်ချင်ရင် 
**✍️စာရေးဆရာ** ကိုနှိပ်ပါ။

💢 **📖စာအုပ်ဖတ်နည်းကြည့်ပါရန်** 💢

⚠️ အဆင်မပြေတာရှိရင် ⚠️ **
❓အထွေထွေမေးမြန်းရန်** ကိုနှိပ်ပါ။"""

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

    bot.send_message(message.chat.id, text, reply_markup=kb)

# ======================================================
# 3️⃣ PRIVATE CHAT MESSAGE HANDLER - FIXED
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_private_messages(message):
    """Handle private messages including forwarded links"""
    
    # Skip if it's a command (already handled by start handler)
    if message.text and message.text.startswith('/'):
        return
    
    # Check for forwarded messages containing links
    if message.forward_from_chat or message.forward_from:
        # For forwarded messages with text
        if message.text and is_link(message.text):
            bot.send_message(
                message.chat.id, 
                f"🔗 Forwarded link detected:\n{message.text}\n\nI can see the forwarded link! ✅"
            )
        # For forwarded media messages with captions containing links
        elif message.caption and is_link(message.caption):
            bot.send_message(
                message.chat.id, 
                f"🔗 Forwarded media with link:\n{message.caption}\n\nI can see the forwarded link! ✅"
            )
        else:
            # Regular forwarded message without links
            bot.send_message(
                message.chat.id, 
                "📩 Forwarded message received!\n\n" +
                "Note: I can process links from forwarded messages in private chats."
            )
    # Regular text messages (not commands)
    elif message.text and not message.text.startswith('/'):
        if is_link(message.text):
            bot.send_message(
                message.chat.id, 
                f"🔗 Link detected:\n{message.text}\n\nThis is a direct link message! ✅"
            )
        else:
            bot.send_message(message.chat.id, f"🤖 Auto Reply:\n{message.text}")

# ===============================
# CATEGORY REDIRECT
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "category")
def category_redirect(call):
    bot.send_message(
        call.message.chat.id,
        "📚 **ကဏ္ဍအလိုက် စာအုပ်များ**\nhttps://t.me/oscarhelpservices/4\n\n🌼 Oscar's Library 🌼"
    )

# ===============================
# AUTHORS MENU
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "author_menu")
def author_menu(call):
    text = "✍️ **စာရေးဆရာနာမည် 'အစ' စာလုံးရွေးပါ**\n\n🌼 Oscar's Library 🌼"
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
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb)

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

# ===============================
# AUTHOR REDIRECT
# ===============================
@bot.callback_query_handler(func=lambda c: c.data.startswith("author_"))
def author_redirect(call):
    key = call.data.replace("author_", "")
    url = AUTHOR_LINKS.get(key)
    if url:
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"➡️ **{key} ဖြင့်စသောစာရေးဆရာများ**\n{url}\n\n🌼 Oscar's Library 🌼"
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
