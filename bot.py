import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== Your Bot Token =====
TOKEN = "7867668478:AAGGHMIAJyGIHp7wZZv99hL0YoFma09bmh4"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


# =======================
#      /start handler
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name

    text = (
        f"မင်္ဂလာပါ **{user}** 🥰\n"
        "🌼 **Oscar's Library** 🌼 မှကြိုဆိုပါတယ်\n\n"
        "**စာအုပ်များရှာဖွေရန်လမ်းညွှန်ပေးမယ်...**\n"
        "(**စာအုပ်ရှာဖို့ နှစ်ပိုင်းခွဲထားတယ် — ကဏ္ဍအလိုက် / စာရေးဆရာ**)\n\n"
        "💢 **စာအုပ်ဖတ်နည်းကိုအရင်ကြည့်ပါရန်**\n"
        "⚠️ အဆင်မပြေမှုများရှိပါက **အထွေထွေမေးမြန်းရန်** ကိုနှိပ်ပြီးမေးမြန်းနိုင်ပါတယ်။"
    )

    keyboard = [
        [InlineKeyboardButton("📚 ကဏ္ဍအလိုက်", callback_data="cat_main")],
        [InlineKeyboardButton("✍️ စာရေးဆရာ", callback_data="author_main")],
        [InlineKeyboardButton("📖 စာအုပ်ဖတ်နည်း", callback_data="read_method")],
        [InlineKeyboardButton("📂 ချန်နယ်ခွဲများ", callback_data="channels")],
        [InlineKeyboardButton("⭐ Review ရေးရန်", callback_data="review")],
        [InlineKeyboardButton("🛠 စာအုပ်ပြုပြင်ရန်", callback_data="edit_book")],
        [InlineKeyboardButton("❓ အထွေထွေမေးမြန်းရန်", callback_data="faq")],
    ]

    await update.message.reply_text(
        text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =======================
#    Callback Handler
# =======================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    await query.answer()

    # ========= CATEGORY =========
    if data == "cat_main":
        await query.edit_message_text(
            "👉 **ကဏ္ဍအလိုက်ရှာရန် ဒီနေရာ**\nhttps://t.me/oscarhelpservices/4",
            parse_mode="Markdown"
        )

    # ========= READ METHOD =========
    elif data == "read_method":
        await query.edit_message_text(
            "📖 **စာအုပ်ဖတ်နည်း**\nhttps://t.me/oscarhelpservices/17",
            parse_mode="Markdown",
        )

    # ========= CHANNELS =========
    elif data == "channels":
        await query.edit_message_text(
            "📂 **ချန်နယ်ခွဲများ**\nhttps://t.me/oscarhelpservices/9",
            parse_mode="Markdown",
        )

    # ========= REVIEW =========
    elif data == "review":
        await query.edit_message_text(
            "⭐ **Review ရေးရန်**\nhttps://t.me/sharebykosoemoe/13498",
            parse_mode="Markdown",
        )

    # ========= EDIT BOOK =========
    elif data == "edit_book":
        await query.edit_message_text(
            "🛠 **စာအုပ်ပြုပြင်ရန်**\nhttps://t.me/oscarhelpservices/29?single",
            parse_mode="Markdown",
        )

    # ========= FAQ =========
    elif data == "faq":
        await query.edit_message_text(
            "❓ **အထွေထွေမေးမြန်းရန်**\nhttps://t.me/kogyisoemoe",
            parse_mode="Markdown",
        )

    # ========= AUTHOR MAIN =========
    elif data == "author_main":
        letters = [
            "က","ခ","ဂ","ဃ","င","စ","ဆ","ဇ","ည","ဋ္ဌ","တ","ထ","ဒ","ဓ","န",
            "ပ","ဖ","ဗ","ဘ","မ","ယ","ရ","လ","ဝ","သ","ဟ","အ","ဥ","Eng"
        ]

        keyboard = []
        row = []
        for i, l in enumerate(letters, start=1):
            row.append(InlineKeyboardButton(l, callback_data=f"author_{l}"))
            if i % 4 == 0:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        await query.edit_message_text(
            "✍️ **စာရေးဆရာနာမည် အစစလုံးဖြင့်ရွေးပါ**",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    # ========= AUTHOR REDIRECT =========
    elif data.startswith("author_"):
        letter = data.split("_")[1]

        links = {
            "က": 5, "ခ": 7, "ဂ": 12, "င": 14, "စ": 16, "ဆ": 18, "ဇ": 20, "ည": 23,
            "ဋ္ဌ": 25, "တ": 27, "ထ": 33, "ဒ": 35, "ဓ": 37, "န": 39, "ပ": 41,
            "ဖ": 43, "ဗ": 45, "ဘ": 47, "မ": 49, "ယ": 51, "ရ": 53, "လ": 55,
            "ဝ": 57, "သ": 59, "ဟ": 61, "အ": 30, "ဥ": 10, "Eng": 920
        }

        if letter in links:
            await query.edit_message_text(
                f"👉 https://t.me/oscarhelpservices/{links[letter]}",
                disable_web_page_preview=True
            )
        else:
            await query.edit_message_text("Link မရှိသေးပါ")


# =======================
#      MAIN
# =======================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.run_polling()


if __name__ == "__main__":
    main()
