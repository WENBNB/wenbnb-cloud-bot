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

import os, logging, sqlite3, glob, importlib
from telegram.ext import Updater, CommandHandler
# --- Fake web server for Render free plan ---
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

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

def help_cmd(update, context):
    txt = (
        "/meme <topic> - Generate meme caption\n"
        "/price - Show BNB price\n"
        "/tokeninfo - Token supply & stats\n"
        "/airdropcheck <wallet> - Check airdrop eligibility\n"
        "/giveaway_start - Admin only\n"
        "/giveaway_end - Admin only\n"
    )
    update.message.reply_text(txt)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
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


    for path in sorted(glob.glob("plugins/*.py")):
        name = os.path.basename(path)[:-3]
        try:
            mod = importlib.import_module(f"plugins.{name}")
            if hasattr(mod, "register"):
                mod.register(dp, {"conn": conn, "cur": cur, "logger": logger,
                                  "BSCSCAN_API_KEY": BSCSCAN_API_KEY,
                                  "OPENAI_API_KEY": OPENAI_API_KEY,
                                  "WEN_TOKEN_ADDRESS": WEN_TOKEN_ADDRESS,
                                  "OWNER_ID": OWNER_ID})
                logger.info("Loaded plugin %s", name)
        except Exception as e:
            logger.exception("Plugin load failed: %s", e)

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
            print("Pinged Render to stay awake ⏰")
        except Exception as e:
            print("Ping failed:", e)
        time.sleep(600)  # ping every 10 minutes

threading.Thread(target=keep_alive, daemon=True).start()
# ------------------------------------------------
import telegram
telegram.ext.Updater.stop = lambda self: None

if __name__ == "__main__":
    main()

import signal
import sys
import os

# Auto-restart if Render sends stop signal
signal.signal(signal.SIGTERM, lambda signum, frame: os.execv(sys.executable, ['python'] + sys.argv))











