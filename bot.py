import telebot
import requests
import os
from threading import Thread
from flask import Flask

# ----------------- Flask Web Server (For Render Port Binding) -----------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    # Render မှ သတ်မှတ်ပေးသော PORT ကို ဖတ်ယူခြင်း (Default 8080)
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ----------------- Configurations -----------------
BOT_TOKEN = "8802351755:AAGzeBpF0ZMqB6zZQHKbPaghDipZN_w-9Dk"
API_URL = "https://shweboost.com/api/v2"
API_KEY = "dbb7a85b0635f5dca25e4118a8a4bbd6"

# Owner Telegram User ID
OWNER_ID = 8305397892

bot = telebot.TeleBot(BOT_TOKEN)

# ----------------- Helper Functions -----------------
def is_owner(message):
    return message.from_user.id == OWNER_ID

# ----------------- Bot Commands -----------------

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if not is_owner(message):
        bot.reply_to(message, "❌ You are not authorized to use this bot.")
        return

    text = (
        "👋 မင်္ဂလာပါ Owner!\n\n"
        "📌 အသုံးပြုနိုင်သော Commands များ:\n"
        "1️⃣ /balance - Main Provider Balance စစ်ဆေးရန်\n"
        "2️⃣ /order <Service_ID> <Quantity> <Link> - Order တင်ရန်\n\n"
        "💡 Order တင်နည်း ဥပမာ:\n"
        "`/order 101 500 https://t.me/example`"
    )
    bot.reply_to(message, text, parse_mode="Markdown")


@bot.message_handler(commands=['balance'])
def check_balance(message):
    if not is_owner(message):
        return

    bot.send_chat_action(message.chat.id, 'typing')
    
    payload = {
        'key': API_KEY,
        'action': 'balance'
    }
    
    try:
        response = requests.post(API_URL, data=payload, timeout=10)
        data = response.json()
        
        if 'balance' in data:
            balance = data.get('balance')
            currency = data.get('currency', 'USD')
            reply_text = (
                "💰 **Main Provider Balance Report**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"💵 **Balance:** `{balance}` {currency}"
            )
        else:
            reply_text = f"⚠️ Balance စစ်ဆေးရာတွင် Error ဖြစ်ပေါ်နေပါသည်:\n`{data.get('error', response.text)}`"
            
    except Exception as e:
        reply_text = f"❌ ချိတ်ဆက်မှု Error: {str(e)}"
        
    bot.reply_to(message, reply_text, parse_mode="Markdown")


@bot.message_handler(commands=['order'])
def place_order(message):
    if not is_owner(message):
        return

    args = message.text.split(maxsplit=3)
    
    if len(args) < 4:
        usage_text = (
            "⚠️ **ပုံစံမမှန်ကန်ပါ။ အောက်ပါအတိုင်း ပို့ပေးပါ:**\n\n"
            "`/order <Service_ID> <Quantity> <Link>`\n\n"
            "📝 **ဥပမာ:**\n`/order 101 1000 https://t.me/mychannel`"
        )
        bot.reply_to(message, usage_text, parse_mode="Markdown")
        return

    service_id = args[1].strip()
    quantity = args[2].strip()
    link = args[3].strip()

    payload = {
        'key': API_KEY,
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity
    }

    bot.send_chat_action(message.chat.id, 'typing')

    try:
        response = requests.post(API_URL, data=payload, timeout=15)
        data = response.json()

        if 'order' in data:
            main_order_id = data.get('order')
            reply_text = (
                "✅ **Order Successfully Placed!**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"🆔 **Main Provider Order ID:** `{main_order_id}`\n"
                f"🔢 **Quantity:** `{quantity}`\n"
                f"🔗 **Link:** {link}\n"
                f"⚙️ **Service ID:** `{service_id}`\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "✨ Order ကို Main Provider ဆီသို့ အောင်မြင်စွာ တင်ပြီးပါပြီ။"
            )
        else:
            error_msg = data.get('error', 'မသိရှိသော Error ဖြစ်ပေါ်နေပါသည်။')
            reply_text = (
                "❌ **Order တင်၍ မရပါ!**\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"⚠️ **Error Message:** `{error_msg}`"
            )

    except Exception as e:
        reply_text = f"❌ Server သို့ ချိတ်ဆက်ရာတွင် Error ဖြစ်ပေါ်ပါသည်:\n`{str(e)}`"

    bot.reply_to(message, reply_text, parse_mode="Markdown")


# ----------------- Main Execution -----------------
if __name__ == "__main__":
    keep_alive()  # Render Web Server ကို Run ခြင်း
    print("Bot is successfully running...")
    bot.infinity_polling()
