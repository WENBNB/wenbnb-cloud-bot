# --- WENBNB Cloud Bot (Stable Build) ---

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

# --- Load environment variables ---
import os
import signal
import psutil  # for auto-kill of old instance
from dotenv import load_dotenv

# Kill old bot instance if already running
for proc in psutil.process_iter():
    try:
        if 'wenbot.py' in proc.cmdline() and proc.pid != os.getpid():
            os.kill(proc.pid, signal.SIGTERM)
            print("🛑 Old bot instance stopped.")
    except Exception:
        pass

load_dotenv()

# --- Flask Keep-Alive Server ---
from flask import Flask
import threading

from telegram.ext import Updater

app = Flask(__name__)

@app.route('/')
def home():
    return "WENBNB Bot is alive 🌙"

def run_flask():
    port = int(os.environ.get("PORT", 9090))
    app.run(host='0.0.0.0', port=port)


import os, logging, sqlite3, glob, importlib
from telegram.ext import Updater, CommandHandler
# --- Fake web server for Render free plan ---
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dp = updater.dispatcher

# --- Telegram Command Handlers (Premium AI Version) ---

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

# ----------------- START / MENU / HELP (replace lines 128-176) -----------------
def start(update, context):
    """
    Friendly AI-styled welcome + main quick keyboard (page 1).
    """
    keyboard = [
        ["💰 Token Info", "📈 BNB Price"],
        ["🎁 Airdrop Check", "😂 Meme Generator"],
        ["🎉 Giveaway Info", "💫 About WENBNB"],
        ["⚙️ More Options ▶️"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # Personalized, AI-feel welcome
    update.message.reply_text(
        f"👋 Hey {update.effective_user.first_name}!\n\n"
        "*Welcome to WENBNB Bot — Your AI Web3 Assistant!* 🚀\n\n"
        "Powered by next-gen AI. I can fetch token stats, check airdrops, "
        "generate memes and manage giveaways — all from here.\n\n"
        "Choose an option below 👇",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


def menu_cmd(update, context):
    """
    Menu command shows main keyboard (same as start).
    """
    keyboard = [
        ["💰 Token Info", "📈 BNB Price"],
        ["🎁 Airdrop Check", "😂 Meme Generator"],
        ["🎉 Giveaway Info", "💫 About WENBNB"],
        ["⚙️ More Options ▶️"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("📚 Here’s the WENBNB Bot menu — choose one:", reply_markup=reply_markup)


def more_options_cmd(update, context):
    """
    Second page (advanced / admin / navigation). Text of buttons matches help.
    """
    keyboard = [
        ["🧩 Help", "🚀 Start"],
        ["🎉 Start Giveaway", "🔒 End Giveaway"],
        ["⬅️ Back to Main"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text("🛠 Advanced / Admin options — choose:", reply_markup=reply_markup)


def help_cmd(update, context):
    """
    Full help text listing all available commands and a small tip.
    """
    txt = (
        "💡 *Available Commands:*\n\n"
        "/start - 🚀 Start the WENBNB Bot & open main menu\n"
        "/help - 🧩 Show all available commands\n"
        "/menu - 🪄 Open quick-access menu\n"
        "/price - 📈 Show live BNB + WENBNB price\n"
        "/tokeninfo - 💰 Show WENBNB token stats & supply\n"
        "/airdropcheck <wallet> - 🎁 Verify airdrop eligibility\n"
        "/meme <topic> - 😂 Generate meme caption using AI\n"
        "/giveaway_start - 🎉 Start a giveaway (Admin only)\n"
        "/giveaway_end - 🔒 End giveaway (Admin only)\n"
        "/about - 💫 Learn about the WENBNB ecosystem\n\n"
        "💡 *Tip:* You can also use the menu buttons below the chat for quick access."
    )
    update.message.reply_text(txt, parse_mode="Markdown")


# Register handlers in the bot main dispatcher
def register_menu_handlers(dp):
    """Call this from your main() or where you set up handlers."""
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("menu", menu_cmd))
    dp.add_handler(CommandHandler("more", more_options_cmd))  # optional shortcut
    # buttons on keyboard like "⚙️ More Options ▶️" or "⬅️ Back to Main"
    dp.add_handler(MessageHandler(Filters.regex(r"^⚙️ More Options ▶️$"), more_options_cmd))
    dp.add_handler(MessageHandler(Filters.regex(r"^⬅️ Back to Main$"), menu_cmd))
    dp.add_handler(MessageHandler(Filters.regex(r"^🚀 Start$"), start))
    dp.add_handler(MessageHandler(Filters.regex(r"^🧩 Help$"), help_cmd))
# ----------------- END REPLACEMENT BLOCK -----------------

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # ✅ Register all handlers (start, help, menu, more, etc.)
    register_menu_handlers(dp)

    # ❌ These below lines are now duplicates — remove or comment them
    # dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help_cmd))
    # dp.add_handler(CommandHandler("menu", menu_cmd))
    
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

if __name__ == "__main__":
    import threading

    # Run Flask (keep-alive server) on a separate thread
    threading.Thread(target=run_flask, daemon=True).start()

    # Start the Telegram bot polling
    try:
        main()
    except Exception as e:
        print(f"Bot stopped due to error: {e}")


import signal
import sys
import os

# Auto-restart if Render sends stop signal
signal.signal(signal.SIGTERM, lambda signum, frame: os.execv(sys.executable, ['python'] + sys.argv))
































