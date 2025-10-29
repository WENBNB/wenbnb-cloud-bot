#!/usr/bin/env python3
# ============================================================
# 💫 WENBNB Neural Engine v8.9.8 – HumanTriggerPolish
# Inline Smart Buttons • Clean Start • Real User Command Effect
# ============================================================

import os, sys, time, logging, threading, requests, traceback
from flask import Flask, jsonify
from telegram import (
    Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler, MessageHandler,
    Filters, CallbackContext
)

# ===========================
# ⚙️ Engine & Branding
# ===========================
ENGINE_VERSION = "v8.9.8–HumanTriggerPolish"
CORE_VERSION = "v5.3"
BRAND_SIGNATURE = (
    "🚀 <b>Powered by WENBNB Neural Engine</b> — Emotional Intelligence 24×7 ⚡"
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger("WENBNB")

# ===========================
# 🔐 Environment
# ===========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_APP_URL = os.getenv("RENDER_APP_URL", "")
PORT = int(os.getenv("PORT", "10000"))

if not TELEGRAM_TOKEN:
    raise SystemExit("❌ TELEGRAM_TOKEN missing. Exiting...")

# ===========================
# 🌐 Flask Keep-Alive
# ===========================
app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({
        "status": "ok",
        "engine": ENGINE_VERSION,
        "core": CORE_VERSION,
        "timestamp": int(time.time())
    })

def _keep_alive_loop(ping_url: str, interval: int = 600):
    while True:
        try:
            requests.get(ping_url, timeout=8)
            logger.info("💓 KeepAlive Ping → OK")
        except Exception as e:
            logger.warning(f"KeepAlive error: {e}")
        time.sleep(interval)

def start_keep_alive():
    if RENDER_APP_URL:
        threading.Thread(target=_keep_alive_loop, args=(RENDER_APP_URL,), daemon=True).start()
        logger.info("🩵 Keep-alive enabled (RenderSafe++)")

# ===========================
# 🧩 Plugin Manager
# ===========================
from plugins import plugin_manager

def register_all_plugins(dispatcher):
    try:
        plugin_manager.load_all_plugins(dispatcher)
        logger.info("✅ PluginManager loaded successfully.")
    except Exception as e:
        logger.error(f"❌ PluginManager failed: {e}")

# ===========================
# 🧠 Core Plugin Imports
# ===========================
try:
    from plugins import (
        aianalyze,
        ai_auto_reply,
        admin_tools
    )
    logger.info("🧠 Core modules loaded successfully (AI, Admin, Auto-Reply)")
except Exception as e:
    logger.warning(f"⚠️ Core plugin import failed: {e}")

# ===========================
# 🛡️ Instance Lock
# ===========================
LOCK_FILE = "/tmp/wenbnb_lock"

def check_single_instance():
    if os.path.exists(LOCK_FILE):
        logger.error("⚠️ Another WENBNB instance already running — aborting startup.")
        raise SystemExit(1)
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    logger.info("🔒 Instance lock acquired.")

def release_instance_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
        logger.info("🔓 Instance lock released.")

# ===========================
# 💬 Telegram Bot Setup
# ===========================
def start_bot():
    check_single_instance()

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    try:
        dp.handlers.clear()
    except Exception:
        pass

    register_all_plugins(dp)

    # === Inline Button Layout ===
    inline_keyboard = [
        [
            InlineKeyboardButton("💰 Price", callback_data="price"),
            InlineKeyboardButton("📊 Token Info", callback_data="tokeninfo")
        ],
        [
            InlineKeyboardButton("😂 Meme", callback_data="meme"),
            InlineKeyboardButton("🧠 AI Analyze", callback_data="aianalyze")
        ],
        [
            InlineKeyboardButton("🎁 Airdrop Check", callback_data="airdropcheck"),
            InlineKeyboardButton("🚨 Airdrop Alert", callback_data="airdropalert")
        ],
        [
            InlineKeyboardButton("🌐 Web3", callback_data="web3"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ]
    ]

    # === /start Command ===
    def start_cmd(update: Update, context: CallbackContext):
        user = update.effective_user.first_name or "friend"
        text = (
            f"👋 Hey <b>{user}</b>!\n\n"
            f"✨ Neural Core synced and online.\n"
            f"⚡ <b>WENBNB Neural Engine {ENGINE_VERSION}</b> — running in ProStable Mode.\n\n"
            f"<i>All systems ready — choose your command!</i>\n\n"
            f"{BRAND_SIGNATURE}"
        )

        update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(inline_keyboard)
        )

    # === Inline Button Callback (Instant User Command Trigger) ===
    def button_callback(update: Update, context: CallbackContext):
        query = update.callback_query
        if not query:
            return
        data = query.data.strip()  # e.g. "price"
        chat_id = query.message.chat.id
        user = query.from_user

        try:
            query.answer()  # acknowledge
            command_text = f"/{data}"

            # ⚡ HumanTrigger illusion — bot sends message exactly like user typed it
            context.bot.send_message(
                chat_id=chat_id,
                text=command_text,
                disable_notification=True
            )

            logger.info(f"⚡ Button '{data}' pressed by @{user.username or user.id}")

        except Exception as e:
            logger.error(f"❌ Button handler error: {e}")
            traceback.print_exc()

    # === /about Command ===
    def about_cmd(update: Update, context: CallbackContext):
        text = (
            f"🌐 <b>About WENBNB</b>\n\n"
            f"Hybrid AI + Web3 Neural Assistant — blending emotion with precision.\n"
            f"Currently running <b>{ENGINE_VERSION}</b>.\n\n"
            f"💫 Always learning, always adapting.\n\n"
            f"{BRAND_SIGNATURE}"
        )
        update.message.reply_text(text, parse_mode=ParseMode.HTML)

    # === Register Handlers ===
    dp.add_handler(CallbackQueryHandler(button_callback))  # ⚡ First - handle inline button press
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply.ai_auto_chat))

    # === Plugin Command Handlers ===
    try:
        dp.add_handler(CommandHandler("aianalyze", aianalyze.aianalyze_cmd))
        dp.add_handler(CommandHandler("admin", lambda u, c: admin_tools.admin_status(u, c, {
            "version": ENGINE_VERSION,
            "branding": {"footer": BRAND_SIGNATURE},
            "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
        })))
        dp.add_handler(CommandHandler("reboot", lambda u, c: admin_tools.admin_reboot(u, c, {
            "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
        })))
        logger.info("💬 Plugin command handlers active")
    except Exception as e:
        logger.warning(f"⚠️ Plugin load issue: {e}")
        traceback.print_exc()

    # === Heartbeat ===
    def heartbeat():
        while True:
            time.sleep(30)
            try:
                if RENDER_APP_URL:
                    requests.get(f"{RENDER_APP_URL}/ping", timeout=5)
                logger.info("💓 Poll heartbeat alive")
            except Exception:
                logger.warning("⚠️ Heartbeat missed")

    threading.Thread(target=heartbeat, daemon=True).start()

    # === Start Polling ===
    try:
        logger.info("🚀 Starting Telegram polling (HumanTriggerPolish)...")
        updater.start_polling(clean=True)
        updater.idle()
    except Exception as e:
        logger.error(f"❌ Polling error: {e}")
        traceback.print_exc()

# ===========================
# 🧠 Entry Point
# ===========================
def main():
    logger.info(f"💫 Launching WENBNB Neural Engine {ENGINE_VERSION}")
    start_keep_alive()
    try:
        start_bot()
    except Exception as e:
        logger.error(f"❌ Fatal error in main: {e}")
        traceback.print_exc()
    finally:
        release_instance_lock()

if __name__ == "__main__":
    main()


