#!/usr/bin/env python3
# ============================================================
# 💫 WENBNB Neural Engine v9.0.1 — ChatKeyboardDominantMode (Final Fix)
# ============================================================

import os, sys, time, logging, threading, requests, traceback
from flask import Flask, jsonify
from telegram import Update, ParseMode, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ============================================================
# ⚙️ Engine & Branding
# ============================================================
ENGINE_VERSION = "v9.0.1–ChatKeyboardDominantMode"
CORE_VERSION = "v5.3"
BRAND_SIGNATURE = "🚀 <b>Powered by WENBNB Neural Engine</b> — Emotional Intelligence 24×7 ⚡"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger("WENBNB")

# ============================================================
# 🔐 Env & Render URL
# ============================================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_APP_URL = os.getenv("RENDER_APP_URL", "https://wenbnb-neural-engine.onrender.com")
PORT = int(os.getenv("PORT", "10000"))

if not TELEGRAM_TOKEN:
    raise SystemExit("❌ TELEGRAM_TOKEN missing. Exiting...")

# ============================================================
# 🌐 Flask Keep-Alive
# ============================================================
app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({
        "status": "ok",
        "engine": ENGINE_VERSION,
        "core": CORE_VERSION,
        "timestamp": int(time.time())
    })

def _keep_alive_loop(url: str, interval: int = 600):
    while True:
        try:
            requests.get(url, timeout=8)
            logger.info("💓 KeepAlive Ping → OK")
        except Exception as e:
            logger.warning(f"KeepAlive error: {e}")
        time.sleep(interval)

def start_keep_alive():
    if RENDER_APP_URL:
        threading.Thread(target=_keep_alive_loop, args=(RENDER_APP_URL,), daemon=True).start()
        logger.info("🩵 Keep-alive enabled (RenderSafe++)")

# ============================================================
# 🧩 Plugin Manager & Core Imports
# ============================================================
from plugins import plugin_manager
try:
    from plugins import aianalyze, ai_auto_reply, admin_tools
    logger.info("🧠 Core modules loaded successfully.")
except Exception as e:
    logger.warning(f"⚠️ Core plugin import failed: {e}")

def register_all_plugins(dispatcher):
    try:
        plugin_manager.load_all_plugins(dispatcher)
        logger.info("✅ PluginManager: All plugins loaded successfully.")
    except Exception as e:
        logger.error(f"❌ PluginManager failed: {e}")

# ============================================================
# 💬 Telegram Bot Setup
# ============================================================
LOCK_FILE = "/tmp/wenbnb_lock"
def check_single_instance():
    if os.path.exists(LOCK_FILE):
        logger.error("⚠️ Another WENBNB instance already running.")
        raise SystemExit(1)
    open(LOCK_FILE, "w").write(str(os.getpid()))
def release_instance_lock():
    if os.path.exists(LOCK_FILE): os.remove(LOCK_FILE)

def start_bot():
    check_single_instance()
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    try: dp.handlers.clear()
    except Exception: pass
    register_all_plugins(dp)

    # ----- Keyboard + Map -----
    keyboard = [
        ["💰 Price", "📊 Token Info"],
        ["😂 Meme", "🧠 AI Analyze"],
        ["🎁 Airdrop Check", "🚨 Airdrop Alert"],
        ["🌐 Web3", "ℹ️ About", "⚙️ Admin"]
    ]
    button_map = {
        "💰 Price": "price", "📊 Token Info": "tokeninfo",
        "😂 Meme": "meme", "🧠 AI Analyze": "aianalyze",
        "🎁 Airdrop Check": "airdropcheck", "🚨 Airdrop Alert": "airdropalert",
        "🌐 Web3": "web3", "ℹ️ About": "about", "⚙️ Admin": "admin"
    }

    # /start
    def start_cmd(update: Update, context: CallbackContext):
        user = update.effective_user.first_name or "friend"
        text = (
            f"👋 Hey <b>{user}</b>!\n\n"
            f"✨ Neural Core synced and online.\n"
            f"⚡ <b>WENBNB Neural Engine {ENGINE_VERSION}</b> — running in ProStable Mode.\n\n"
            f"<i>All modules operational — choose your next move!</i>\n\n{BRAND_SIGNATURE}"
        )
        update.message.reply_text(
            text, parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # /about
    def about_cmd(update: Update, context: CallbackContext):
        text = (
            f"🌐 <b>About WENBNB</b>\n\nHybrid AI + Web3 Neural Assistant — blending emotion with precision.\n"
            f"Currently running <b>{ENGINE_VERSION}</b>.\n\n{BRAND_SIGNATURE}"
        )
        update.message.reply_text(text, parse_mode=ParseMode.HTML)

    # Button Handler → Convert button text → /command
    def button_handler(update: Update, context: CallbackContext):
        try:
            msg = update.message
            if not msg or not msg.text: return
            label = msg.text.strip()
            cmd = button_map.get(label)
            if not cmd: return  # normal chat

            logger.info(f"⚡ Button → /{cmd}")
            msg.text = f"/{cmd}"          # turn into a real command
            fake_update = Update(update.update_id, message=msg)
            context.dispatcher.process_update(fake_update)
            msg.text = label               # restore
        except Exception as e:
            logger.error(f"❌ Button error: {e}")
            traceback.print_exc()

    # ============================================================
    # Register Handlers (correct order)
    # ============================================================
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler), group=0)

    # Plugin commands
    dp.add_handler(CommandHandler("aianalyze", aianalyze.aianalyze_cmd))
    dp.add_handler(CommandHandler("admin", lambda u, c: admin_tools.admin_status(u, c, {
        "version": ENGINE_VERSION,
        "branding": {"footer": BRAND_SIGNATURE},
        "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
    })))
    dp.add_handler(CommandHandler("reboot", lambda u, c: admin_tools.admin_reboot(u, c, {
        "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
    })))

    # AI Auto-Reply — only for non-buttons & non-commands
    def safe_ai_auto(update, context):
        try:
            text = update.message.text.strip() if update.message else ""
            if text in button_map or text.startswith("/"):
                return
            ai_auto_reply.ai_auto_chat(update, context)
        except Exception as e:
            logger.error(f"AI Auto-reply error: {e}")
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, safe_ai_auto), group=1)

    # ============================================================
    # Heartbeat
    # ============================================================
    def heartbeat():
        while True:
            time.sleep(30)
            try:
                requests.get(f"{RENDER_APP_URL}/ping", timeout=5)
                logger.info("💓 Heartbeat alive")
            except Exception:
                logger.warning("⚠️ Heartbeat missed")

    threading.Thread(target=heartbeat, daemon=True).start()

    # ============================================================
    # Start Bot
    # ============================================================
    try:
        logger.info("🚀 Starting Telegram polling (v9.0.1 ChatKeyboardDominantMode)")
        updater.start_polling(clean=True)
        updater.idle()
    finally:
        release_instance_lock()

# ============================================================
# 🧠 Entry
# ============================================================
if __name__ == "__main__":
    logger.info(f"💫 Launching WENBNB Neural Engine {ENGINE_VERSION}")
    start_keep_alive()
    start_bot()
