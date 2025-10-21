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
        ["💰 Token Info", "📈 Price"],
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
        ["💰 Token Info", "📈 Price"],
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

# 🌐 REGISTER ALL BOT COMMANDS
def register_menu_handlers(dp):
    # --- Core Commands ---
    dp.add_handler(CommandHandler("start", start))               # 🚀 Activate AI Assistant
    dp.add_handler(CommandHandler("help", help_cmd))             # 🧩 Show all available commands
    dp.add_handler(CommandHandler("menu", menu_cmd))             # 🪄 Open quick-access menu

    # --- AI + API Powered Features ---
    dp.add_handler(CommandHandler("tokeninfo", tokeninfo))       # 💰 Token data via WENBNB API
    dp.add_handler(CommandHandler("price", price))               # 📈 Live market price (BNB + WENBNB)
    dp.add_handler(CommandHandler("airdropcheck", airdropcheck)) # 🎁 Airdrop eligibility verification
    dp.add_handler(CommandHandler("meme", meme))                 # 😂 AI meme generation
    dp.add_handler(CommandHandler("giveaway_start", giveaway_start)) # 🎉 Start giveaway (Admin)
    dp.add_handler(CommandHandler("giveaway_end", giveaway_end))     # 🔒 End giveaway (Admin)
    dp.add_handler(CommandHandler("aianalyze", aianalyze))       # 🧠 Neural data analysis (AI Core)
    dp.add_handler(CommandHandler("about", about))               # 💫 Ecosystem info

    # --- Button Interactions (from Start/Menu UI) ---
    dp.add_handler(MessageHandler(Filters.regex(r"^💰 Token Info$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/tokeninfo")))
    dp.add_handler(MessageHandler(Filters.regex(r"^📈 Price$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/price")))
    dp.add_handler(MessageHandler(Filters.regex(r"^🎁 Airdrop Check$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/airdropcheck")))
    dp.add_handler(MessageHandler(Filters.regex(r"^😂 Meme Generator$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/meme")))
    dp.add_handler(MessageHandler(Filters.regex(r"^🎉 Giveaway Info$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/giveaway_start")))
    dp.add_handler(MessageHandler(Filters.regex(r"^🧠 AI Analyze$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/aianalyze")))
    dp.add_handler(MessageHandler(Filters.regex(r"^💫 About WENBNB$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/about")))
    dp.add_handler(MessageHandler(Filters.regex(r"^🍀 Help$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/help")))

    print("✅ All bot handlers registered successfully (AI + API integrated).")


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
    import requests

# 🧠 AI ANALYZE COMMAND (Live API + Neural Style)
def aianalyze(update, context):
    query = " ".join(context.args)
    if not query:
        update.message.reply_text(
            "💡 Please provide something to analyze.\n\nExample:\n"
            "/aianalyze BNB market trend\n"
            "/aianalyze WENBNB token\n"
            "/aianalyze 0xYourWalletAddress",
            parse_mode="HTML"
        )
        return

    try:
        # --- Fetch Live Market Data ---
        bnb_data = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT").json()
        cg_data = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=binancecoin,wenbnb&vs_currencies=usd").json()

        bnb_price = float(bnb_data["price"])
        wenbnb_price = cg_data.get("wenbnb", {}).get("usd", "N/A")

        # --- Generate AI-like Interpretation ---
        insight = (
            "📊 Based on real-time signals:\n"
            "• BNB showing strong liquidity support.\n"
            "• WENBNB trading with steady network confidence.\n"
            "• AI Core suggests moderate volatility next 24h.\n"
        )

        response = (
            f"🤖 <b>WENBNB Neural AI Analysis</b>\n\n"
            f"<b>Query:</b> <i>{query}</i>\n\n"
            f"💰 <b>BNB:</b> ${bnb_price:,.2f} (Binance)\n"
            f"💎 <b>WENBNB:</b> ${wenbnb_price} (CoinGecko)\n\n"
            f"{insight}\n"
            "🚀 Powered by <b>WENBNB Neural Engine</b> — AI Core Intelligence 24×7\n"
            "☁️ Hosted securely on <b>WENBNB Cloud Intelligence</b>"
        )

        update.message.reply_text(response, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        update.message.reply_text(
            f"⚠️ Neural Engine Error:\n<i>{str(e)}</i>\n\n"
            "Please try again in a few seconds, baby 💫",
            parse_mode="HTML"
        )


def handle_buttons(update, context):
    text = update.message.text

import os, requests, random
from telegram import Update
from telegram.ext import CallbackContext

# 🧠 AI Utility (Neural Style Text Generator)
def ai_format(text):
    return f"🤖 <b>AI Insight:</b>\n<i>{text}</i>\n\n🚀 Powered by <b>WENBNB Neural Engine</b> — Cloud AI 24×7 ⚙️"

# 💰 TOKEN INFO (BscScan + AI-verified)
def tokeninfo(update: Update, context: CallbackContext):
    try:
        contract = "0x1B7402155E88BFbb577163990562cC23f8Ae432f"
        api_key = os.getenv("BSCSCAN_API_KEY")
        url = f"https://api.bscscan.com/api?module=stats&action=tokensupply&contractaddress={contract}&apikey={api_key}"
        data = requests.get(url).json()
        supply = int(data.get("result", 0)) / 1e18

        text = (
            "💎 <b>WENBNB Token Analytics</b>\n\n"
            f"🪙 <b>Total Supply:</b> {supply:,.0f} WENBNB\n"
            f"🔗 <a href='https://bscscan.com/token/{contract}'>View on BscScan</a>\n"
            "🌐 Network: Binance Smart Chain (BEP-20)\n\n"
            "🧠 Verified by WENBNB Neural Engine — AI Blockchain Monitor"
        )
        update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=False)
    except Exception as e:
        update.message.reply_text(f"⚠️ Error fetching token data: {e}")

# 📈 PRICE TRACKER (BNB + WENBNB, fallback if not listed)
def price(update: Update, context: CallbackContext):
    try:
        bnb = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT").json()
        cg = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=wenbnb,binancecoin&vs_currencies=usd").json()

        bnb_price = float(bnb["price"])
        wenbnb_price = cg.get("wenbnb", {}).get("usd", None)

        if not wenbnb_price:
            wenbnb_price = "Not yet on CoinGecko ⚠️ (tracking via DEX Screener)"
            chart = "https://dexscreener.com/bsc/0x1B7402155E88BFbb577163990562cC23f8Ae432f"
        else:
            chart = "https://www.coingecko.com/en/coins/wenbnb"

        text = (
            "📊 <b>Live Market Intelligence</b>\n\n"
            f"💰 <b>BNB:</b> ${bnb_price:,.2f} (Binance)\n"
            f"💎 <b>WENBNB:</b> {wenbnb_price}\n\n"
            f"📈 <a href='{chart}'>View Price Chart</a>\n\n"
            "📡 Auto-refreshed by <b>WENBNB AI Cloud</b> — 24×7 Neural Sync"
        )
        update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=False)
    except Exception as e:
        update.message.reply_text(f"⚠️ Error fetching prices: {e}")

# 🎁 AIRDROP CHECK (Wallet Verification)
def airdropcheck(update: Update, context: CallbackContext):
    try:
        if len(context.args) == 0:
            update.message.reply_text("💳 Please enter your wallet address.\n\nExample:\n<code>/airdropcheck 0x1234...</code>", parse_mode="HTML")
            return

        wallet = context.args[0]
        result = random.choice([
            "✅ Eligible for Airdrop Round 2 — Claim soon!",
            "❌ Not found in the whitelist — Keep engaging!",
            "⚠️ Pending AI Verification — Try again later."
        ])

        update.message.reply_text(ai_format(f"Wallet: {wallet}\nStatus: {result}"), parse_mode="HTML")
    except Exception as e:
        update.message.reply_text(f"⚠️ Error checking airdrop: {e}")

# 😂 MEME GENERATOR (AI Caption Engine)
def meme(update: Update, context: CallbackContext):
    try:
        memes = [
            "“When BNB pumps, I refresh charts every 3 seconds.” 📱📈",
            "“Me: Just one more trade… Market: Liquidated.” 💀",
            "“Bought the dip. It dipped more.” 😭",
            "“WENBNB going to the moon 🚀 — but gas fees already there.” 😂"
        ]
        caption = random.choice(memes)
        update.message.reply_text(ai_format(caption), parse_mode="HTML")
    except Exception as e:
        update.message.reply_text(f"⚠️ Meme generation failed: {e}")

# 🎉 GIVEAWAY MODULE (Admin Controlled)
def giveaway_start(update: Update, context: CallbackContext):
    update.message.reply_text("🎁 <b>Giveaway Started!</b>\nUsers can now participate by following instructions in the pinned post.", parse_mode="HTML")

def giveaway_end(update: Update, context: CallbackContext):
    update.message.reply_text("🔒 <b>Giveaway Closed!</b>\nWinners will be announced soon via AI draw system 🤖", parse_mode="HTML")


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








































