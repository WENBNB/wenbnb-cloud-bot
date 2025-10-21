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

# ---------------- WENBNB Bot: Main Commands ---------------- #

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters

# 🚀 START COMMAND — WENBNB Neural Engine Edition
def start(update: Update, context: CallbackContext):
    keyboard = [
        ["💰 Token Info", "📈 BNB Price"],
        ["🎁 Airdrop Check", "🧠 AI Analyze"],
        ["😂 Meme Generator", "💫 About WENBNB"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    welcome_text = (
        f"<b>👋 Hey {update.effective_user.first_name}!</b>\n\n"
        "🤖 <b>Welcome to WENBNB Bot</b> — your intelligent Web3 assistant.\n\n"
        "🧠 I operate on the <b>WENBNB Neural Engine</b> — "
        "an AI Core built to empower your crypto journey 24×7.\n\n"
        "💫 What I can do for you:\n"
        "• 💰 Show live token stats & BNB price (via Binance + CoinGecko APIs)\n"
        "• 🎁 Check airdrop eligibility instantly\n"
        "• 🧠 Analyze wallets, trends, or markets using AI\n"
        "• 😂 Generate custom memes with WENBNB flavor\n"
        "• 🎉 Manage giveaways & engage your community\n\n"
        "✨ Type /help to see all commands or tap a button below 👇\n\n"
        "🚀 <b>Powered by WENBNB Neural Engine — AI Core Intelligence 24×7</b>"
    )

    update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

# 🪄 MENU COMMAND — WENBNB Neural Engine Edition
def menu(update: Update, context: CallbackContext):
    keyboard = [
        ["💰 Token Info", "📈 BNB Price"],
        ["🎁 Airdrop Check", "🧠 AI Analyze"],
        ["😂 Meme Generator", "🎉 Giveaway Info"],
        ["💫 About WENBNB", "🧩 Help"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    menu_text = (
        "🪄 <b>WENBNB Command Menu</b>\n\n"
        "Choose what you’d like me to do 👇\n"
        "Each option is powered by the <b>WENBNB Neural Engine</b> 🤖\n\n"
        "💰 — Get live token stats\n"
        "📈 — Check BNB + WENBNB prices\n"
        "🎁 — Verify your airdrop status\n"
        "🧠 — Let AI analyze wallets or trends\n"
        "😂 — Generate memes with WENBNB humor\n"
        "🎉 — Manage community giveaways\n"
        "💫 — Explore the full WENBNB ecosystem\n\n"
        "🚀 <b>Powered by WENBNB Neural Engine — AI Core Intelligence 24×7</b>"
    )

    update.message.reply_text(
        menu_text,
        reply_markup=reply_markup,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


# 🧩 HELP COMMAND — WENBNB Neural Engine Edition
def help_command(update: Update, context: CallbackContext):
    help_text = (
        "🧩 <b>WENBNB Bot Command Center</b>\n\n"
        "Here’s everything I can do for you — intelligently powered by AI ⚙️\n\n"
        
        "🚀 <b>Core Commands</b>\n"
        "/start — Activate the AI Assistant & show quick menu\n"
        "/help — Display this command list anytime\n"
        "/menu — Open the interactive button menu\n\n"

        "💰 <b>Token & Market Tools</b>\n"
        "/tokeninfo — View WENBNB token stats & supply\n"
        "/price — Check live BNB + WENBNB price (via Binance + CoinGecko)\n"
        "/aianalyze — AI-powered insight for wallet, trend, or text\n\n"

        "🎁 <b>Community Tools</b>\n"
        "/airdropcheck — Verify airdrop eligibility instantly\n"
        "/giveaway_start — Start a giveaway (Admin only)\n"
        "/giveaway_end — End giveaway (Admin only)\n\n"

        "😂 <b>Entertainment & AI Fun</b>\n"
        "/meme — Generate a fresh meme caption using WENBNB AI Humor Engine\n\n"

        "💫 <b>About</b>\n"
        "/about — Learn more about the WENBNB Ecosystem & Vision\n\n"

        "⚙️ <i>Pro Tip:</i> Use buttons from the /menu or type any command directly.\n\n"
        "🚀 <b>Powered by WENBNB Neural Engine — AI Core Intelligence 24×7</b>"
    )

    update.message.reply_text(
        help_text,
        parse_mode="HTML",
        disable_web_page_preview=True
    )



# 🌟 REGISTER HANDLERS
def register_menu_handlers(dp):
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("menu", menu_cmd))
    dp.add_handler(CommandHandler("aianalyze", aianalyze))
    dp.add_handler(MessageHandler(Filters.regex("^💰 Token Info$"), lambda u, c: c.bot.send_message(u.effective_chat.id, "Fetching token info...")))
    dp.add_handler(MessageHandler(Filters.regex("^📈 BNB Price$"), lambda u, c: c.bot.send_message(u.effective_chat.id, "Fetching live BNB price...")))
    dp.add_handler(MessageHandler(Filters.regex("^🎁 Airdrop Check$"), lambda u, c: c.bot.send_message(u.effective_chat.id, "Send your wallet to check eligibility.")))
    dp.add_handler(MessageHandler(Filters.regex("^😂 Meme Generator$"), lambda u, c: c.bot.send_message(u.effective_chat.id, "Send meme topic for AI caption.")))
    dp.add_handler(MessageHandler(Filters.regex("^🎉 Giveaway Info$"), lambda u, c: c.bot.send_message(u.effective_chat.id, "Giveaway module coming soon! 🎁")))
    dp.add_handler(MessageHandler(Filters.regex("^💫 About WENBNB$"), lambda u, c: c.bot.send_message(u.effective_chat.id, "WENBNB — Web3 + AI ecosystem built for the future! 🚀")))


# 🌟 MAIN FUNCTION
def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    register_menu_handlers(dp)

    print("✨ Bot connected successfully, polling started...")
    updater.start_polling()
    updater.idle()


# 🌟 ENTRY POINT
if __name__ == "__main__":
    import threading
    threading.Thread(target=run_flask).start()
    main()
    
    from telegram.ext import MessageHandler, Filters
    
# 🧠 AI ANALYZE COMMAND — WENBNB Neural Engine Edition
def aianalyze(update: Update, context: CallbackContext):
    user_input = ' '.join(context.args) if context.args else None

    if not user_input:
        update.message.reply_text(
            "🧠 <b>WENBNB Neural Engine Active</b>\n\n"
            "Send me what you want to analyze — it can be:\n"
            "• A crypto wallet address 🪙\n"
            "• A project name or token symbol 💼\n"
            "• Or any text you’d like AI insights on 🧩\n\n"
            "Example:\n"
            "<code>/aianalyze 0x1234abcd...</code>\n"
            "<code>/aianalyze Bitcoin trend</code>\n\n"
            "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7",
            parse_mode="HTML"
        )
        return

    # Simulated “AI-style” response logic
    response = f"🤖 <b>Analyzing:</b> <code>{user_input}</code>\n\n"

    if user_input.startswith("0x") and len(user_input) > 20:
        response += "🔍 Detected input as a wallet address.\n"
        response += "⚡ Fetching AI-based wallet risk, transaction pattern, and activity summary..."
    elif "bnb" in user_input.lower() or "wenbnb" in user_input.lower():
        response += "📊 Analyzing BNB & WENBNB market trends using Neural Sentiment Engine..."
    else:
        response += "💬 Processing general context through the WENBNB Neural AI Core..."

    response += "\n\n✨ <i>This is an experimental AI-powered insight module.</i>\n"
    response += "🚀 <b>Powered by WENBNB Neural Engine — Always Online</b>"

    update.message.reply_text(
        response,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

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




































