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

Happy Birthday ❤️ ကမ္ဘာ❣️

ပျော်ရွှင်စရာမွေးနေ့လေးဖြစ်ပါစေ..🎂💗

<b>{current_date}</b> မွေးနေ့လေးမှစ နောင်နှစ်ပေါင်းများစွာတိုင်အောင်...

ကိုယ်၏ကျန်းမာခြင်း စိတ်၏ချမ်းသာခြင်းများနဲ့ပြည့်စုံပြီး လိုအပ်ချက်လိုအင်ဆန္ဒများလည်းပြည့်ဝပါစေ...

ဘ၀ခရီးကို မပူမပင်မကြောင့်ကြစေရပဲ        
အေးအေးချမ်းချမ်း ဖြတ်သန်းသွားနိုင်ပါစေ 💞

အနာဂတ်မှာ 🤍
နားလည်မှု များစွာနဲ့ 🍒
အရင်ကထက်ပိုပိုပြီး 💕
ဆထက်တပိုး ပိုပြီး ချစ်နိုင်ပါစေ 🤍💞

ချစ်ရတဲ့ မိသားစုနဲ့အတူပျော်ရွှင်ရသော
နေ့ရက်တွေကို ထာဝရ ပိုင်ဆိုင်နိုင်ပါစေ 
လို့ ဆုတောင်းပေးပါတယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊

<b>🌼 Oscar's Library 🌼</b> 
#adminteam"""

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
# BIRTHDAY AUTO POST SYSTEM
# ===============================
active_groups = set()
last_birthday_post = None

def track_active_group(chat_id):
    """Active group တွေကို track လုပ်ခြင်း"""
    if chat_id < 0:
        active_groups.add(chat_id)
        if len(active_groups) > 50:
            active_groups.pop()

def should_send_birthday_post():
    """မနက် ၈ နာရီကျရင် True return ပြန်ခြင်း"""
    try:
        myanmar_time = get_myanmar_time()
        current_time = myanmar_time.strftime("%H:%M")
        current_date = myanmar_time.strftime("%Y-%m-%d")
        
        print(f"⏰ Time check: {current_time} (Myanmar Time)")
        
        # မနက် ၈ နာရီ (08:00) စစ်ဆေးခြင်း
        if current_time == "08:00":
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

def send_birthday_to_all_admin_groups():
    """Admin ဖြစ်နေတဲ့ group အားလုံးကို auto post တင်ခြင်း"""
    try:
        myanmar_time = get_myanmar_time()
        current_date = myanmar_time.strftime("%B %d")
        caption = BIRTHDAY_CAPTION_TEMPLATE.format(current_date=current_date)
        
        print(f"🎂 Starting birthday posts for {current_date}...")
        print(f"👥 Active groups: {len(active_groups)}")
        
        success_count = 0
        for group_id in list(active_groups):
            try:
                bot.send_photo(
                    group_id,
                    BIRTHDAY_IMAGE_URL,
                    caption=caption,
                    parse_mode="HTML"
                )
                success_count += 1
                print(f"✅ Sent to group: {group_id}")
                time.sleep(2)  # Avoid rate limiting
            except Exception as e:
                print(f"❌ Failed to send to group {group_id}: {e}")
        
        print(f"✅ Birthday posts completed: {success_count}/{len(active_groups)} groups")
        
    except Exception as e:
        print(f"🎂 Birthday system error: {e}")

def birthday_scheduler():
    """မနက် ၈ နာရီစစ်ဆေးခြင်း"""
    print("🎂 Birthday scheduler started - Checking every minute...")
    while True:
        try:
            if should_send_birthday_post():
                send_birthday_to_all_admin_groups()
        except Exception as e:
            print(f"🎂 Scheduler error: {e}")
        time.sleep(60)  # 1 minute check

# Start birthday scheduler
birthday_thread = threading.Thread(target=birthday_scheduler, daemon=True)
birthday_thread.start()

# ======================================================
# 1️⃣ GROUP WELCOME SYSTEM
# ======================================================
WELCOME_IMAGE = "welcome_photo.jpg"

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for user in message.new_chat_members:
        caption = f"""<b>နွေးထွေးစွာကြိုဆိုပါတယ်...🧸</b>
<b> {user.first_name} ...🥰</b>

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

def is_link(text):
    if not text:
        return False
    return any(x in text.lower() for x in ["http://", "https://", "www.", "t.me/", "telegram.me/", ".com"])

def has_link_api(message):
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
                warning_msg = f"⚠️ {message.from_user.first_name} 💢 <b>Link🔗 များကို ပိတ်ထားပါတယ်</b> 🙅🏻\n\n❗လိုအပ်ချက်ရှိရင် <b>Owner</b> ကို ဆက်သွယ်ပါနော်..."
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
    
<b>🌼 Oscar's Library 🌼</b> မှ ကြိုဆိုပါတယ်

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
    kb.row(types.InlineKeyboardButton("📖 စာအုပ်ဖတ်နည်း", url="https://t.me/oscarhelpservices/17"))
    kb.row(types.InlineKeyboardButton("🌼 ချန်နယ်ခွဲများ", url="https://t.me/oscarhelpservices/9"))
    kb.row(types.InlineKeyboardButton("⭐ Review ရေးရန်", url="https://t.me/sharebykosoemoe/13498"))
    kb.row(types.InlineKeyboardButton("📝 စာအုပ်ပြုပြင်ရန်", url="https://t.me/oscarhelpservices/29?single"))
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
# AUTHORS MENU
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
print("🤖 Initializing bot...")
try:
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=WEBHOOK_URL)
    print(f"✅ Webhook set: {WEBHOOK_URL}")
    print("🎂 Auto Birthday System: ACTIVE")
    print("⏰ Will post daily at 8:00 AM Myanmar Time")
except Exception as e:
    print(f"❌ Webhook error: {e}")

# ===============================
# RUN
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
