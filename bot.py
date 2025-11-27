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

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ===============================
# BIRTHDAY WISH BOT CONFIGURATION
# ===============================
BIRTHDAY_CHANNEL_ID = "1002150199369"
BIRTHDAY_PHOTO_URL = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/Happy_Birthday_Photo.jpg"

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
        
        message = f"""Birthday Wishes 💌 

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
        
        return message
    
    async def send_birthday_wish(self):
        """မွေးနေ့ဆုတောင်းစာပို့ရန်"""
        try:
            message = self.create_birthday_message()
            
            # ပုံနဲ့တကွ မက်ဆေ့ပို့ခြင်း
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
            
            # နံနက် ၈ နာရီစစ်ဆေးခြင်း
            if now.hour == 8 and now.minute == 0:
                await self.send_birthday_wish()
                
                # ၂၄ နာရီစောင့်ခြင်း
                await asyncio.sleep(3600)
            else:
                # ၁ မိနစ်တစ်ကြိမ်စစ်ဆေးခြင်း
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
    
    birthday_thread = threading.Thread(target=run_birthday_bot, daemon=True)
    birthday_thread.start()

# ===============================
# BIRTHDAY PREVIEW COMMAND
# ===============================
@bot.message_handler(commands=['showbirthday'])
def show_birthday_post(message):
    """Show the current birthday post with image preview"""
    try:
        current_date = birthday_bot.get_current_date()
        preview_text = birthday_bot.create_birthday_message()
        
        # ပုံနဲ့တကွ ပြသရန်
        bot.send_photo(
            message.chat.id,
            photo=BIRTHDAY_PHOTO_URL,
            caption=preview_text
        )
        
    except Exception as e:
        # ပုံမရရင် text ပဲပို့
        bot.send_message(message.chat.id, preview_text)
        print(f"❌ ပုံမတင်နိုင်: {e}")

# ===============================
# TOP FANS POST TEMPLATE
# ===============================
TOP_FANS_POST = """🏆 **အပတ်စဉ် Top Fans များ** 🏆

ဒီအပတ်အတွင်းကျွန်တော်တို့ချန်နယ်ကို အပြင်းအထန် အားပေးမှုအများဆုံး Member များကိုရွေးချယ်လိုက်ပါပြီ...!

🎖️ **Official Top 20 Community Stars** 🎖️

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

💫 **နောက်အပတ်မှာ Top Fan ဘယ်သူတွေဖြစ်မလဲ...**

ဒီအပတ် ပါဝင်သူတစ်ယောက်စီတိုင်းကို အထူးကျေးဇူးတင်ရှိပါတယ်!  
နောက်အပတ်မှာတော့ သင့်နာမည် ဒီစာရင်းမှာပါအောင်...🥰

✅ React လေးတွေ ပိုပေးပါ...
✅ စကားဝိုင်းမှာ ပါဝင်ပါ...
✅ ချန်နယ်ကို အားပေးပါ...

သင့်ရဲ့တစ်ခုတည်းသော Reactကလေးက ကျွန်တော်တို့အတွက် များစွာအဓိပ္ပာယ်ရှိပါတယ်! 💝

🌟 **ကျွန်တော်တို့ရဲ့ချန်နယ်ကို အသက်သွင်းပေးထားတဲ့ အချစ်တော်လေးများကျေးဇူးကမ္ဘာပါ...🤞**
သင့်ရဲ့ ပါဝင်မှုတိုင်းက ကျွန်တော်တို့အတွက် ဆက်လက်လုပ်ဆောင်နိုင်တဲ့ စွမ်းအားပါ!

📅 **နောက်တစ်ကြိမ် - တနင်္ဂနွေ ည ၆ နာရီ**
ဘယ်သူတွေ Top 20 ထဲဝင်မလဲ စောင့်ကြည့်လိုက်ကြရအောင်...! 🎊"""

# ===============================
# SHOW TOP FANS POST COMMAND
# ===============================
@bot.message_handler(commands=['showtopfan'])
def show_top_post(message):
    """Show the current top fans post"""
    bot.send_message(message.chat.id, TOP_FANS_POST, parse_mode='Markdown')

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
                
                # Send warning message with mention
                user_first_name = message.from_user.first_name
                user_id = message.from_user.id
                warning_msg = f"⚠️ [{user_first_name}](tg://user?id={user_id}) 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်..."
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
    
    user_first_name = message.from_user.first_name
    user_id = message.from_user.id
    
    # Check for forwarded messages containing links
    if message.forward_from_chat or message.forward_from:
        # For forwarded messages with text
        if message.text and is_link(message.text):
            bot.send_message(
                message.chat.id, 
                f"🔗 [{user_first_name}](tg://user?id={user_id}) 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်..."
            )
        # For forwarded media messages with captions containing links
        elif message.caption and is_link(message.caption):
            bot.send_message(
                message.chat.id, 
                f"🔗 [{user_first_name}](tg://user?id={user_id}) 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်..."
            )
        else:
            # Regular forwarded message without links
            bot.send_message(
                message.chat.id, 
                f"📩 [{user_first_name}](tg://user?id={user_id}) ရဲ့ Forwarded message received!\n\nNote: I can process links from forwarded messages in private chats."
            )
    # Regular text messages (not commands)
    elif message.text and not message.text.startswith('/'):
        if is_link(message.text):
            bot.send_message(
                message.chat.id, 
                f"🔗 [{user_first_name}](tg://user?id={user_id}) 💢 Link🔗 များကို ပိတ်ထားပါတယ် 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် Owner ကို ဆက်သွယ်ပါနော်..."
            )
        else:
            bot.send_message(
                message.chat.id, 
                f"🤖 [{user_first_name}](tg://user?id={user_id}) ရဲ့ Message:\n{message.text}"
            )

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
    # Initialize birthday bot only
    initialize_birthday_bot()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
