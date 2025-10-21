# WENBNB Cloud Bot (V1)
# -*- coding: utf-8 -*-
# Confidential Prototype â€” Stage 1 Build

import sys, types, mimetypes

# Patch for imghdr module (Python 3.13 compatibility)
imghdr = types.ModuleType("imghdr")

def what(filename):
    t = mimetypes.guess_type(filename)[0]
    if t and "image" in t:
        return t.split("/")[-1]
    return None

imghdr.what = what
sys.modules["imghdr"] = imghdr
import os
import signal
import psutil  # make sure psutil is in requirements.txt too

# Kill old bot instance if already running
for proc in psutil.process_iter():
    try:
        if 'wenbot.py' in proc.cmdline() and proc.pid != os.getpid():
            os.kill(proc.pid, signal.SIGTERM)
            print("🛑 Old bot instance stopped.")
    except Exception:
        pass

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
import threading

import telegram
telegram.ext.Updater.stop = lambda self: None


app = Flask(__name__)

@app.route('/')
def home():
    return "WENBNB Bot is alive 💫"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)


import os, logging, sqlite3, glob, importlib
from telegram.ext import Updater, CommandHandler
# --- Fake web server for Render free plan ---
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dp = updater.dispatcher


class PingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"WENBNB Bot running")

def run_server():
    server = HTTPServer(("0.0.0.0", int(os.getenv("PORT", 10000))), PingHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
# ---------------------------------------------


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY") or ""
WEN_TOKEN_ADDRESS = os.getenv("WEN_TOKEN_ADDRESS") or "0x0000000000000000000000000000000000000000"
OWNER_ID = int(os.getenv("OWNER_ID") or 0)
DB_FILE = os.getenv("DB_FILE") or "wenbot.db"

if not TELEGRAM_TOKEN:
    raise SystemExit("Please set TELEGRAM_TOKEN in environment variables.")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("WENBNBCloudBot")

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS giveaways (id INTEGER PRIMARY KEY, chat_id INTEGER, message_id INTEGER, entrants TEXT, active INTEGER DEFAULT 1, created_at INTEGER)''')
conn.commit()

from telegram import ReplyKeyboardMarkup

def start(update, context):
    keyboard = [
        ["💰 Token Info", "📈 BNB Price"],
        ["🎁 Airdrop Check", "😂 Meme Generator"],
        ["🎉 Giveaway Info", "ℹ️ About WENBNB"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        f"👋 Hey {update.effective_user.first_name}!\n\n"
        "Welcome to *WENBNB Cloud Bot* 💎\n"
        "I'm your AI-powered assistant for price, token info, memes & more.\n\n"
        "Choose an option below 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

def menu_cmd(update, context):
    keyboard = [
        ["💰 Token Info", "📈 BNB Price"],
        ["🎁 Airdrop Check", "😂 Meme Generator"],
        ["🎉 Giveaway Info", "ℹ️ About WENBNB"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    update.message.reply_text(
        "📋 Here’s the WENBNB Bot Menu 👇",
        reply_markup=reply_markup
    )


def help_cmd(update, context):
    txt = (
        "🧠 *Available Commands:*\n\n"
        "/start — Welcome Message + Main Menu\n"
        "/menu — Reopen Main Menu Buttons\n"
        "/price — Show Live BNB Price\n"
        "/tokeninfo — Token Supply & Stats\n"
        "/airdropcheck <wallet> — Check Airdrop Eligibility\n"
        "/meme <topic> — Generate Meme Caption\n"
        "/giveaway_start — Start Giveaway (Admin Only)\n"
        "/giveaway_end — End Giveaway (Admin Only)\n\n"
        "💡 *Tip:* You can also use the buttons below the chat!"
    )
    update.message.reply_text(txt, parse_mode="Markdown")


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("menu", menu_cmd))
    
    from telegram.ext import MessageHandler, Filters

def handle_buttons(update, context):
    text = update.message.text

    if "Token Info" in text:
        update.message.reply_text("💰 Fetching WENBNB Token Info... Please wait.")
        context.bot.send_message(chat_id=update.effective_chat.id, text="/tokeninfo")

    elif "BNB Price" in text:
        update.message.reply_text("📈 Getting live BNB price...")
        context.bot.send_message(chat_id=update.effective_chat.id, text="/price")

    elif "Airdrop Check" in text:
        update.message.reply_text("🎁 Please send your wallet address to check eligibility.")

    elif "Meme Generator" in text:
        update.message.reply_text("😂 Send a meme idea or topic, and I’ll generate one!")

    elif "Giveaway Info" in text:
        update.message.reply_text(
            "🎉 Giveaway Commands:\n"
            "/giveaway_start — Start Giveaway (Admin Only)\n"
            "/giveaway_end — End Giveaway (Admin Only)"
        )

    elif "About WENBNB" in text or "About" in text:
        update.message.reply_text(
            "💫 *About WENBNB Bot:*\n"
            "Your all-in-one AI-powered assistant for WENBNB Ecosystem.\n\n"
            "📊 Token Info | 🎁 Airdrops | 😂 Memes | 🎉 Giveaways\n"
            "24x7 Active — Powered by Render Cloud ☁️",
            parse_mode="Markdown"
        )

    else:
        update.message.reply_text("Please choose a valid option from the menu 👇")

    # 👇 Add handler for buttons
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_buttons))

    # 👇 Load all plugins from plugins folder
    for path in sorted(glob.glob("plugins/*.py")):
        name = os.path.basename(path)[:-3]
        try:
            mod = importlib.import_module(f"plugins.{name}")
            if hasattr(mod, "register"):
                mod.register(dp, {
                    "conn": conn,
                    "cur": cur,
                    "logger": logger,
                    "BSCSCAN_API_KEY": BSCSCAN_API_KEY,
                    "OPENAI_API_KEY": OPENAI_API_KEY,
                    "WEN_TOKEN_ADDRESS": WEN_TOKEN_ADDRESS,
                    "OWNER_ID": OWNER_ID
                })
                logger.info(f"Loaded plugin: {name}")
        except Exception as e:
            logger.exception(f"Plugin load failed: {name}, Error: {e}")

# Run Flask in background so Render stays awake
threading.Thread(target=run_flask).start()
print("Bot connected successfully, polling started...")

updater.start_polling()
logger.info("WENBNB Cloud Bot started.")
updater.idle()

    
# --- Keep Alive Ping (Render Safe 24x7 Mode) ---
import requests, threading, os, time

def keep_alive():
    url = "https://wenbnb-cloud-bot.onrender.com"  # apna Render URL
    while True:
        try:
            requests.get(url)
            print("💖 Pinged Render to stay awake 💖")
        except Exception as e:
            print("Ping failed:", e)
        time.sleep(600)  # ping every 10 minutes

threading.Thread(target=keep_alive, daemon=True).start()

# 🩵 Telegram Bot Start (Main Entry)
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_flask).start()
    main()


import signal
import sys
import os

# Auto-restart if Render sends stop signal
signal.signal(signal.SIGTERM, lambda signum, frame: os.execv(sys.executable, ['python'] + sys.argv))

























