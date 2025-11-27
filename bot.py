import os
import telebot
from telebot import types
from flask import Flask, request
import threading
import time
import requests
import sys
from datetime import datetime, timedelta
import asyncio

# ===============================
# BOT TOKEN & URL (Environment Variables)
# ===============================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4')
WEBHOOK_URL = "https://oscar-library-bot.onrender.com/" + BOT_TOKEN
PING_URL = "https://oscar-library-bot.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ===============================
# BIRTHDAY WISH BOT CONFIGURATION
# ===============================
BIRTHDAY_CHANNEL_ID = "1002150199369"
BIRTHDAY_PHOTO_URL = "https://raw.githubusercontent.com/yourusername/yourrepo/main/Happy_Birthday_Photo.jpg"

# Editable Birthday Post Template
BIRTHDAY_POST_TEMPLATE = """Birthday Wishes 💌 

Happy Birthday ❤️ ကမ္ဘာ❣️

ပျော်ရွှင်စရာမွေးနေ့လေးဖြစ်ပါစေ..🎂💗

{current_date} မွေးနေ့လေးမှစ 
နောင်နှစ်ပေါင်းများစွာတိုင်အောင်...

ကိုယ်၏ကျန်းမာခြင်း စိတ်၏ချမ်းသာခြင်းများနဲ့ပြည့်စုံပြီး လိုအင်ဆန္ဒများလည်းပြည့်ဝပါစေ...🥰

ဘ၀ခရီးကို မပူမပင်မကြောင့်ကြစေရပဲ        
အေးအေးချမ်းချမ်း ဖြတ်သန်းသွားနိုင်ပါစေ 💞

အနာဂတ်မှာ 🤍
နားလည်မှု များစွာနဲ့ 🍒
အရင်ကထက်ပိုပိုပြီး  💕
ဆထက်တပိုး ပိုပြီး ချစ်နိုင်ပါစေ 🤍💞

ချစ်ရတဲ့ မိသားစုနဲ့အတူပျော်ရွှင်ရသော
နေ့ရက်တွေကို ထာဝရ ပိုင်ဆိုင်နိုင်ပါစေ 
လို့ ဆုတောင်းပေးပါတယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊

🌼 Oscar's Library 🌼
 
#adminteam"""

class BirthdayWishBot:
    def __init__(self):
        self.channel_id = BIRTHDAY_CHANNEL_ID
        self.photo_url = BIRTHDAY_PHOTO_URL
    
    def get_current_date(self):
        """လက်ရှိလနဲ့ရက်ကိုရယူ"""
        now = datetime.now()
        month = now.strftime("%B")
        day = now.day
        return f"{month}, {day}"
    
    def create_birthday_message(self):
        """မွေးနေ့ဆုတောင်းစာဖန်တီး"""
        current_date = self.get_current_date()
        return BIRTHDAY_POST_TEMPLATE.format(current_date=current_date)
    
    async def send_birthday_wish(self):
        """မွေးနေ့ဆုတောင်းစာပို့ရန်"""
        try:
            message = self.create_birthday_message()
            
            await bot.send_photo(
                chat_id=self.channel_id,
                photo=self.photo_url,
                caption=message
            )
            
            print(f"✅ မွေးနေ့ဆုတောင်းစာပို့ပြီး - {datetime.now()}")
            
        except Exception as e:
            print(f"❌ မွေးနေ့ဆုတောင်းစာပို့ရာတွင်အမှား - {e}")
    
    async def schedule_daily_message(self):
        """နေ့စဉ်ပို့ရန် စီစဉ်ခြင်း"""
        while True:
            now = datetime.now()
            
            if now.hour == 8 and now.minute == 0:
                await self.send_birthday_wish()
                await asyncio.sleep(3600)
            else:
                await asyncio.sleep(60)

# ===============================
# BIRTHDAY BOT INITIALIZATION
# ===============================
birthday_bot = BirthdayWishBot()

async def start_birthday_bot():
    """Birthday bot ကို start လုပ်မယ်"""
    print("🤖 Birthday Wish Bot စတင်ပါပြီ...")
    print("⏰ နေ့စဉ် နံနက် ၈ နာရီတွင် ပို့ပေးသွားမည်")
    await birthday_bot.schedule_daily_message()

def initialize_birthday_bot():
    """Birthday bot ကို background တွင် start လုပ်မယ်"""
    def run_birthday_bot():
        asyncio.run(start_birthday_bot())
    
    threading.Thread(target=run_birthday_bot, daemon=True).start()

# ===============================
# OWNER SYSTEM
# ===============================
OWNER_ID = 6272937931

def is_owner(user_id):
    """Check if user is the owner"""
    return user_id == OWNER_ID

# ===============================
# BIRTHDAY POST EDITING SYSTEM (Owner Only)
# ===============================
@bot.message_handler(commands=['editbirthday'])
def edit_birthday_post(message):
    """Edit the birthday post - Owner only"""
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ ဒီ command ကို သုံးခွင့်မရှိပါ။ Owner သာသုံးနိုင်သည်။")
        return
    
    help_text = """
🎂 <b>မွေးနေ့ဆုတောင်းစာ ပြင်ဆင်ရန်</b>

<b>Formatting များ အသုံးပြုနည်း:</b>
• <b>Bold</b> - &lt;b&gt;text&lt;/b&gt;
• <i>Italic</i> - &lt;i&gt;text&lt;/i&gt;
• <u>Underline</u> - &lt;u&gt;text&lt;/u&gt;
• <code>Monospace</code> - &lt;code&gt;text&lt;/code&gt;
• <pre>Preformatted</pre> - &lt;pre&gt;text&lt;/pre&gt;
• <a href="https://example.com">Link</a> - &lt;a href="url"&gt;text&lt;/a&gt;

<b>မှတ်ချက်:</b> {current_date} ဆိုတဲ့နေရာမှာ လက်ရှိလနဲ့ရက်ကိုအလိုအလျောက်ထည့်ပေးသွားမှာဖြစ်ပါတယ်။

လက်ရှိစာကို ကြည့်ရှုရန်: /showbirthday
ပြင်ဆင်ရန် စာပိုဒ်အသစ်ကို ရိုက်ပေးပါ...
"""
    
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')
    bot.register_next_step_handler(message, process_birthday_post)

def process_birthday_post(message):
    """Process the new birthday post from owner"""
    global BIRTHDAY_POST_TEMPLATE
    try:
        BIRTHDAY_POST_TEMPLATE = message.text
        
        # Preview the new post
        current_date = birthday_bot.get_current_date()
        preview_text = BIRTHDAY_POST_TEMPLATE.format(current_date=current_date)
        
        bot.send_message(
            message.chat.id,
            "✅ <b>မွေးနေ့ဆုတောင်းစာ အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ!</b>\n\n"
            "Preview ကြည့်ရှုရန်: /showbirthday\n\n"
            f"<b>Preview:</b>\n{preview_text}",
            parse_mode='HTML'
        )
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ ပြင်ဆင်ရာတွင် အမှားတစ်ခုဖြစ်နေသည်: {e}")

@bot.message_handler(commands=['showbirthday'])
def show_birthday_post(message):
    """Show the current birthday post"""
    current_date = birthday_bot.get_current_date()
    preview_text = BIRTHDAY_POST_TEMPLATE.format(current_date=current_date)
    
    bot.send_message(
        message.chat.id, 
        f"<b>လက်ရှိမွေးနေ့ဆုတောင်းစာ:</b>\n\n{preview_text}", 
        parse_mode='HTML'
    )

# ===============================
# TOP FANS POST EDITING SYSTEM (Owner Only)
# ===============================
TOP_FANS_POST = """🏆 <b>အပတ်စဉ် Top Fans များ</b> 🏆

ဒီအပတ်အတွင်းကျွန်တော်တို့ချန်နယ်ကို အပြင်းအထန် အားပေးမှုအများဆုံး Member များကိုရွေးချယ်လိုက်ပါပြီ...!

🎖️ <b>Official Top 20 Community Stars</b> 🎖️

<b>🥇 GOLD Tier (Top 1-5)</b>
1. @user1 👑 Channel King
2. @user2 ⭐ Super Star  
3. @user3 🔥 Fire Reactor
4. @user4 💬 Chat Champion
5. @user5 🎯 Most Active

<b>🥈 SILVER Tier (Top 6-15)</b> 
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

<b>🥉 BRONZE Tier (Top 16-20)</b>
16. @user16 🎉 Celebration Star
17. @user17 💎 Diamond Member
18. @user18 🌟 Shining Star
19. @user19 🚀 Rocket Booster
20. @user20 💖 Heart Giver

💫 <b>နောက်အပတ်မှာ Top Fan ဘယ်သူတွေဖြစ်မလဲ...</b>

ဒီအပတ် ပါဝင်သူတစ်ယောက်စီတိုင်းကို အထူးကျေးဇူးတင်ရှိပါတယ်!  
နောက်အပတ်မှာတော့ သင့်နာမည် ဒီစာရင်းမှာပါအောင်...🥰

✅ React လေးတွေ ပိုပေးပါ...
✅ စကားဝိုင်းမှာ ပါဝင်ပါ...
✅ ချန်နယ်ကို အားပေးပါ...

သင့်ရဲ့တစ်ခုတည်းသော Reactကလေးက ကျွန်တော်တို့အတွက် များစွာအဓိပ္ပာယ်ရှိပါတယ်! 💝

🌟 <b>ကျွန်တော်တို့ရဲ့ချန်နယ်ကို အသက်သွင်းပေးထားတဲ့ အချစ်တော်လေးများကျေးဇူးကမ္ဘာပါ...🤞</b>
သင့်ရဲ့ ပါဝင်မှုတိုင်းက ကျွန်တော်တို့အတွက် ဆက်လက်လုပ်ဆောင်နိုင်တဲ့ စွမ်းအားပါ!

📅 <b>နောက်တစ်ကြိမ် - တနင်္ဂနွေ ည ၆ နာရီ</b>
ဘယ်သူတွေ Top 20 ထဲဝင်မလဲ စောင့်ကြည့်လိုက်ကြရအောင်...! 🎊"""

@bot.message_handler(commands=['edittopfan'])
def edit_top_post(message):
    """Edit the top fans post - Owner only"""
    if not is_owner(message.from_user.id):
        bot.send_message(message.chat.id, "❌ ဒီ command ကို သုံးခွင့်မရှိပါ။ Owner သာသုံးနိုင်သည်။")
        return
    
    help_text = """
📝 <b>Top Fans Post ပြင်ဆင်ရန်</b>

<b>Formatting များ အသုံးပြုနည်း:</b>
• <b>Bold</b> - &lt;b&gt;text&lt;/b&gt;
• <i>Italic</i> - &lt;i&gt;text&lt;/i&gt;
• <u>Underline</u> - &lt;u&gt;text&lt;/u&gt;
• <code>Monospace</code> - &lt;code&gt;text&lt;/code&gt;
• <pre>Preformatted</pre> - &lt;pre&gt;text&lt;/pre&gt;
• <a href="https://example.com">Link</a> - &lt;a href="url"&gt;text&lt;/a&gt;

လက်ရှိစာကို ကြည့်ရှုရန်: /showtopfan
ပြင်ဆင်ရန် စာပိုဒ်အသစ်ကို ရိုက်ပေးပါ...
"""
    
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')
    bot.register_next_step_handler(message, process_new_post)

def process_new_post(message):
    """Process the new post from owner"""
    global TOP_FANS_POST
    try:
        TOP_FANS_POST = message.text
        bot.send_message(
            message.chat.id,
            "✅ <b>Top Fans Post ကို အောင်မြင်စွာ ပြင်ဆင်ပြီးပါပြီ!</b>\n\n"
            "ကြည့်ရှုရန်: /showtopfan",
            parse_mode='HTML'
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ ပြင်ဆင်ရာတွင် အမှားတစ်ခုဖြစ်နေသည်: {e}")

@bot.message_handler(commands=['showtopfan'])
def show_top_post(message):
    """Show the current top fans post"""
    bot.send_message(message.chat.id, TOP_FANS_POST, parse_mode='HTML')

# ===============================
# AUTO REMOVE SYSTEM - SUNDAY 5:59PM
# ===============================
user_message_count = {}
user_reaction_count = {}
tracking_start_time = datetime.now()

async def get_final_top_20():
    """Sunday 5:59PM မှာ နောက်ဆုံးစစ်ဆေးပြီး Top 20 ထုတ်ပေးမယ်"""
    try:
        print("🕔 Sunday 5:59PM - Finalizing Top 20 List...")
        user_scores = {}
        all_user_ids = set(list(user_message_count.keys()) + list(user_reaction_count.keys()))
        
        for user_id in all_user_ids:
            message_score = user_message_count.get(user_id, 0)
            reaction_score = user_reaction_count.get(user_id, 0)
            user_scores[user_id] = message_score + reaction_score
        
        raw_top_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        current_members = await get_channel_members()
        
        final_top_20 = []
        for user_id, score in raw_top_users:
            if user_id in current_members:
                final_top_20.append((user_id, score))
                if len(final_top_20) >= 20:
                    break
        
        print(f"✅ Final Top 20: {len(final_top_20)} users")
        return final_top_20[:20]
        
    except Exception as e:
        print(f"❌ Error in get_final_top_20: {e}")
        return []

async def get_channel_members():
    """Channel ထဲက လက်ရှိ member list ရယူ"""
    try:
        members = []
        return members
    except Exception as e:
        print(f"❌ Error getting channel members: {e}")
        return []

async def schedule_weekly_post():
    """Sunday 5:59PM မှာ auto remove + 6:00PM မှာ post"""
    while True:
        now = datetime.now()
        next_sunday = now.replace(hour=17, minute=59, second=0, microsecond=0)
        days_until_sunday = (6 - now.weekday()) % 7
        next_sunday += timedelta(days=days_until_sunday)
        
        wait_seconds = (next_sunday - now).total_seconds()
        if wait_seconds > 0:
            print(f"⏰ Waiting until Sunday 5:59PM: {next_sunday}")
            await asyncio.sleep(wait_seconds)
        
        final_top_20 = await get_final_top_20()
        await asyncio.sleep(60)
        
        try:
            print("✅ Weekly Top Fans post published!")
        except Exception as e:
            print(f"❌ Error posting: {e}")

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
# 2️⃣ LINK BLOCKER (GROUP ONLY)
# ======================================================
def is_link(text):
    """Basic raw-text link patterns"""
    if not text:
        return False
    return any(x in text.lower() for x in ["http://", "https://", "www.", "t.me/", "telegram.me/", ".com", ".org", ".net"])

def has_link_api(message):
    """Detect links in all message locations including forwarded text/captions"""
    try:
        if message.text and is_link(message.text):
            return True
    except:
        pass

    try:
        if message.caption and is_link(message.caption):
            return True
    except:
        pass

    try:
        ents = getattr(message, "entities", None)
        if ents:
            for e in ents:
                if e.type in ["url", "text_link"]:
                    return True
    except:
        pass

    try:
        cent = getattr(message, "caption_entities", None)
        if cent:
            for e in cent:
                if e.type in ["url", "text_link"]:
                    return True
    except:
        pass

    if message.forward_from or message.forward_from_chat:
        try:
            if message.text and is_link(message.text):
                return True
        except:
            pass

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
    
    if message.text and message.text.startswith('/'):
        return
    if message.new_chat_members:
        return

    if has_link_api(message):
        if not is_admin(message.chat.id, message.from_user.id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
                warning_msg = f"⚠️ {message.from_user.first_name} 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်..."
                bot.send_message(message.chat.id, warning_msg)
            except Exception as e:
                print(f"Link blocker error: {e}")

# ===============================
# /START MESSAGE
# ===============================
@bot.message_handler(commands=['start'])
def start_message(message):
    first = message.from_user.first_name or "Friend"
    text = f"""သာယာသောနေ့လေးဖြစ်ပါစေ...🌸 **
    {first}** ...🥰
    
🌼 <b>Oscar's Library</b> 🌼 မှ ကြိုဆိုပါတယ်

စာအုပ်များရှာဖွေရန် လမ်းညွှန်ပေးမယ်...

<b>စာအုပ်ရှာဖို့ နှစ်ပိုင်းခွဲထားတယ် 
📚ကဏ္ဍအလိုက် 💠 ✍️စာရေးဆရာ</b>

Fic၊ ကာတွန်း၊ သည်းထိပ်ရင်ဖို 
စသည့်ကဏ္ဍများရှာဖတ်ချင်ရင် 
<b>📚ကဏ္ဍအလိုက်</b> ကိုနှိပ်ပါ။

စာရေးဆရာအလိုက်ရှာဖတ်ချင်ရင် 
<b>✍️စာရေးဆရာ</b> ကိုနှိပ်ပါ။

💢 <b>📖စာအုပ်ဖတ်နည်းကြည့်ပါရန်</b> 💢

⚠️ အဆင်မပြေတာရှိရင် ⚠️ 
<b>❓အထွေထွေမေးမြန်းရန်</b> ကိုနှိပ်ပါ။"""

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

    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=kb)

# ======================================================
# 3️⃣ PRIVATE CHAT MESSAGE HANDLER
# ======================================================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_private_messages(message):
    """Handle private messages including forwarded links"""
    
    if message.text and message.text.startswith('/'):
        return
    
    if message.forward_from_chat or message.forward_from:
        if message.text and is_link(message.text):
            bot.send_message(
                message.chat.id, 
                f"🔗 Forwarded link detected:\n{message.text}\n\nI can see the forwarded link! ✅"
            )
        elif message.caption and is_link(message.caption):
            bot.send_message(
                message.chat.id, 
                f"🔗 Forwarded media with link:\n{message.caption}\n\nI can see the forwarded link! ✅"
            )
        else:
            bot.send_message(
                message.chat.id, 
                "📩 Forwarded message received!\n\nNote: I can process links from forwarded messages in private chats."
            )
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
        "📚 <b>ကဏ္ဍအလိုက် စာအုပ်များ</b>\nhttps://t.me/oscarhelpservices/4\n\n🌼 Oscar's Library 🌼",
        parse_mode='HTML'
    )

# ===============================
# AUTHORS MENU
# ===============================
@bot.callback_query_handler(func=lambda c: c.data == "author_menu")
def author_menu(call):
    text = "✍️ <b>စာရေးဆရာနာမည် 'အစ' စာလုံးရွေးပါ</b>\n\n🌼 Oscar's Library 🌼"
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
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode='HTML', reply_markup=kb)

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
            f"➡️ <b>{key} ဖြင့်စသောစာရေးဆရာများ</b>\n{url}\n\n🌼 Oscar's Library 🌼",
            parse_mode='HTML'
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
# INITIALIZE AUTO REMOVE SYSTEM
# ===============================
def initialize_auto_remove():
    """Auto Remove System ကို start လုပ်မယ်"""
    def run_scheduler():
        asyncio.run(schedule_weekly_post())
    
    threading.Thread(target=run_scheduler, daemon=True).start()
    print("✅ Auto Remove System Started - Sunday 5:59PM")

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    initialize_auto_remove()
    initialize_birthday_bot()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
