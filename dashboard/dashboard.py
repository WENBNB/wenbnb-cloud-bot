# dashboard/dashboard.py
import os
import threading
from flask import Flask, render_template, jsonify
from telegram import Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

# --- Setup logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger("WENBNB_Dashboard")

# --- Flask App (Dashboard) ---
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html") if os.path.exists("dashboard/templates/index.html") else "WENBNB Dashboard Running!"

@app.route("/status")
def status():
    return jsonify({
        "status": "online",
        "bot": "running",
        "version": "WENBNB Neural Engine v5.0"
    })

# --- Telegram Bot Setup ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")

bot = Bot(token=TELEGRAM_TOKEN)

def start(update, context):
    update.message.reply_text("👋 WENBNB AI is online and synced with the Neural Engine v5.0!")

def ping(update, context):
    update.message.reply_text("✅ Bot active & responding!")

def bot_thread():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ping", ping))
    updater.start_polling()
    updater.idle()

# --- Run both Flask + Bot in parallel ---
if __name__ == "__main__":
    threading.Thread(target=bot_thread, daemon=True).start()
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
