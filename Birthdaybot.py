import os
import telebot
from telebot import types
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
PING_URL = "https://oscar-library-bot.onrender.com"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="MarkdownV2")

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

# ===============================
# Birthday Config
# ===============================
BIRTHDAY_CHANNEL = -1002150199369
BIRTHDAY_PHOTO_RAW = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/Happy_Birthday_Photo.jpg"
yangon_tz = pytz.timezone("Asia/Yangon")

def get_today_date():
    now = datetime.now(yangon_tz)
    return now.strftime("%B %d").replace(" 0", " ")

def generate_birthday_text():
    today = get_today_date()
    return f"""* Birthday Wishes 💌  
Happy Birthday ❤️ ကမ္ဘာ❣️
ပျော်ရွှင်စရာမွေးနေ့လေးဖြစ်ပါစေ..🎂💗

({today}) မွေးနေ့လေးမှစ နောင်နှစ်ပေါင်းများစွာတိုင်အောင်

ကိုယ်၏ ကျန်းမာခြင်း စိတ်၏ချမ်းသာခြင်းများနဲ့ ပြည့်စုံပြီး လိုအပ်ချက်လိုအင်ဆန္ဒများ လည်းပြည့်ဝပါစေ
ဘ၀ခရီးကို မပူမပင်မကြောင့်ကြစေရပဲ
အေးအေးချမ်းချမ်း ဖြတ်သန်းသွားနိုင်ပါစေ 💞

အနာဂတ်မှာ 🤍
နားလည်မှု များစွာနဲ့ 🍒
အရင်ကထက်ပိုပိုပြီး 💕
ဆထက်တပိုး ပိုပြီး ချစ်နိုင်ပါစေ 🤍💞

ချစ်ရတဲ့ မိသားစုနဲ့အတူပျော်ရွှင်ရသော
နေ့ရက်တွေကို ထာဝရပိုင်ဆိုင်နိုင်ပါစေလို့ ဆုတောင်းပေးပါတယ် 🎂

😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊

🌼 Oscar's Library 🌼

#admimteam*"""

def fetch_image_bytes(url):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return io.BytesIO(r.content)
    except Exception as e:
        print(f"Image download error: {e}")
        return None

def post_birthday(chat_id=BIRTHDAY_CHANNEL):
    try:
        img = fetch_image_bytes(BIRTHDAY_PHOTO_RAW)
        if img:
            img.name = "birthday.jpg"
            bot.send_photo(
                chat_id,
                img,
                caption=generate_birthday_text(),
                parse_mode="MarkdownV2"
            )
        else:
            bot.send_message(chat_id, generate_birthday_text(), parse_mode="MarkdownV2")
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
                post_birthday()
                last_post_date = today
                time.sleep(61)
        time.sleep(5)

# Background scheduler
threading.Thread(target=schedule_daily_birthday, daemon=True).start()

# ===============================
# Telegram Command
# ===============================
@bot.message_handler(commands=['showbirthday'])
def cmd_showbirthday(message):
    post_birthday(message.chat.id)
    try:
        bot.reply_to(message, "🎉 Birthday post sent!")
    except:
        pass

# ===============================
# Flask Server
# ===============================
app = Flask(__name__)

# Webhook route
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    json_data = request.get_json(force=True)
    if json_data:
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
    return "OK", 200

# Optional GET route to trigger /showbirthday from browser
@app.route("/showbirthday", methods=['GET'])
def showbirthday_route():
    post_birthday()
    return "Birthday post sent!", 200

@app.route("/", methods=['GET'])
def index():
    return "Bot is running…", 200

# ===============================
# Run Flask
# ===============================
if __name__ == "__main__":
    while True:
        try:
            bot.remove_webhook()
            bot.set_webhook(url=WEBHOOK_URL)
            print("Webhook set successfully!")
            break
        except telebot.apihelper.ApiTelegramException as e:
            if "429" in str(e):
                print("Too many requests, retrying in 2 seconds...")
                time.sleep(2)
            else:
                raise e
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
