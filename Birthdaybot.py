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
# BOT TOKEN & URL
# ===============================
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4')
WEBHOOK_URL = f"https://oscar-library-bot.onrender.com/{BOT_TOKEN}"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="MarkdownV2")

# ===============================
# Flask app
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
# Myanmar timezone
# ===============================
yangon_tz = pytz.timezone("Asia/Yangon")

# ===============================
# Birthday config
# ===============================
BIRTHDAY_CHANNEL = -1002150199369
BIRTHDAY_PHOTO_RAW = "https://raw.githubusercontent.com/fighterlitboy-png/Oscar-Library-Bot/main/Happy_Birthday_Photo.jpg"

def get_today_date():
    now = datetime.now(yangon_tz)
    return now.strftime("%B %d").replace(" 0", " ")

def generate_birthday_text():
    today = get_today_date()
    # MarkdownV2 escape certain chars
    return (
        "* Birthday Wishes 💌  \n\n"
        "Happy Birthday ❤️ ကမ္ဘာ❣️  \n\n"
        "ပျော်ရွှင်စရာမွေးနေ့လေးဖြစ်ပါစေ..🎂💗  \n\n"
        f"({today}) မွေးနေ့လေးမှစ နောင်နှစ်ပေါင်းများစွာတိုင်အောင်  \n\n"
        "ကိုယ်၏ ကျန်းမာခြင်း စိတ်၏ချမ်းသာခြင်းများနဲ့ ပြည့်စုံပြီး လိုအပ်ချက်လိုအင်ဆန္ဒများ လည်းပြည့်ဝပါစေ  \n\n"
        "ဘ၀ခရီးကို မပူမပင်မကြောင့်ကြစေရပဲ  \n"
        "အေးအေးချမ်းချမ်း ဖြတ်သန်းသွားနိုင်ပါစေ 💞  \n\n"
        "အနာဂတ်မှာ 🤍  \n"
        "နားလည်မှု များစွာနဲ့ 🍒  \n"
        "အရင်ကထက်ပိုပိုပြီး  💕  \n"
        "ဆထက်တပိုး ပိုပြီး ချစ်နိုင်ပါစေ 🤍💞  \n\n"
        "ချစ်ရတဲ့ မိသားစုနဲ့အတူပျော်ရွှင်ရသော  \n"
        "နေ့ရက်တွေကို ထာဝရ ပိုင်ဆိုင်နိုင်ပါစေ  \n"
        "လို့ ဆုတောင်းပေးပါတယ် 🎂  \n\n"
        "😊ရွှင်လန်းချမ်းမြေ့ပါစေ😊  \n\n"
        "🌼 Oscar's Library 🌼 *"
    )

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
                caption=generate_birthday_text(),
                parse_mode="MarkdownV2"
            )
        else:
            bot.send_message(
                BIRTHDAY_CHANNEL,
                generate_birthday_text(),
                parse_mode="MarkdownV2"
            )
        print("Birthday posted.")
    except Exception as e:
        print("Birthday post error:", e)

# Daily scheduler 8:00 AM Myanmar time
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

threading.Thread(target=schedule_daily_birthday, daemon=True).start()

# ===============================
# /showbirthday command
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
                caption=generate_birthday_text(),
                parse_mode="MarkdownV2"
            )
        else:
            bot.send_message(
                message.chat.id,
                generate_birthday_text(),
                parse_mode="MarkdownV2"
            )
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {e}")

# ===============================
# Run webhook
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
