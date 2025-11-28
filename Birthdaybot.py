import os
import telebot
from flask import Flask, request
import threading
import time
import requests
import io
from datetime import datetime
import pytz

# ===============================
# BOT TOKEN & URL (Environment Variables)
# ===============================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4')
WEBHOOK_URL = "https://oscar-library-bot.onrender.com/" + BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = Flask(__name__)

# ===============================
# Channel & Image Setup
# ===============================
BIRTHDAY_CHANNEL = -1002150199369
BIRTHDAY_PHOTO_RAW = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/Happy_Birthday_Photo.jpg"

# ===============================
# Timezone setup
# ===============================
yangon_tz = pytz.timezone("Asia/Yangon")

# ===============================
# Helper Functions
# ===============================
def get_today_date():
    now = datetime.now(yangon_tz)
    return now.strftime("%B %d").replace(" 0", " ")

def generate_birthday_text():
    today = get_today_date()
    return f"""<b>🎉 Birthday Wishes 💌</b>

<b>Happy Birthday ❤️ ကမ္ဘာ❣️</b>

<i>ပျော်ရွှင်စရာမွေးနေ့လေးဖြစ်ပါစေ..🎂💗</i>

(<u>{today}</u>) မွေးနေ့လေးမှစ နောင်နှစ်ပေါင်းများစွာတိုင်အောင်  

ကိုယ်၏ကျန်းမာခြင်း၊ စိတ်၏ချမ်းသာခြင်းများနဲ့ပြည့်စုံပြီး လိုအပ်ချက်၊လိုအင်ဆန္ဒများလည်း ပြည့်ဝပါစေ...💖

ဘ၀ခရီးကို မပူမပင် မကြောင့်ကြစေရပဲ  
အေးအေးချမ်းချမ်း ဖြတ်သန်းသွားနိုင်ပါစေ 💞

အနာဂတ်မှာ 🤍  
နားလည်မှုများစွာနဲ့ 🍒  
အရင်ကထက်ပိုပိုပြီး 💕  
ဆထက်တပိုးပိုပြီး ချစ်နိုင်ပါစေ 🤍💞

ချစ်ရတဲ့ မိသားစုနဲ့အတူပျော်ရွှင်ရသော  
နေ့ရက်တွေကို ထာဝရပိုင်ဆိုင်နိုင်ပါစေ  
ဆုတောင်းပေးပါတယ် 🎂

😊 <i>ရွှင်လန်းချမ်းမြေ့ပါစေ</i> 😊

🌼 <b>Oscar's Library</b> 🌼
#adminteam """

def fetch_image_bytes(url):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return io.BytesIO(r.content)
    except Exception as e:
        print(f"Image download error: {e}")
        return None

def post_birthday_to_channel():
    try:
        img = fetch_image_bytes(BIRTHDAY_PHOTO_RAW)
        if img:
            img.name = "birthday.jpg"
            bot.send_photo(
                BIRTHDAY_CHANNEL,
                img,
                caption=generate_birthday_text()
            )
        else:
            bot.send_message(
                BIRTHDAY_CHANNEL,
                generate_birthday_text()
            )
        print("Birthday posted.")
    except Exception as e:
        print("Birthday post error:", e)

def schedule_daily_birthday(hour=8, minute=0):
    last_post_date = None
    while True:
        now = datetime.now(yangon_tz)
        today = now.date()
        if now.hour == hour and now.minute == minute:
            if last_post_date != today:
                post_birthday_to_channel()
                last_post_date = today
                time.sleep(61)
        time.sleep(5)

# ===============================
# Background Scheduler
# ===============================
threading.Thread(target=schedule_daily_birthday, daemon=True).start()

# ===============================
# /showbirthday Command
# ===============================
@bot.message_handler(commands=['showbirthday'])
def cmd_showbirthday(message):
    try:
        img = fetch_image_bytes(BIRTHDAY_PHOTO_RAW)
        if img:
            img.name = "birthday.jpg"
            bot.send_photo(
                message.chat.id,
                img,
                caption=generate_birthday_text()
            )
        else:
            bot.send_message(
                message.chat.id,
                generate_birthday_text()
            )
        try:
            bot.reply_to(message, "🎉 Birthday post sent!")
        except:
            pass
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

# ===============================
# Flask Webhook
# ===============================
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
# Run Flask App
# ===============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
