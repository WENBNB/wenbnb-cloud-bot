#!/usr/bin/env python3
# ============================================================
# 💫 WENBNB Neural Engine v8.9.6 – InlinePremiumStable (patched)
# Emotion Sync + Inline Smart Buttons + Full Plugin Integration
# ============================================================

import os, sys, time, logging, threading, requests, traceback
from flask import Flask, jsonify
from telegram import (
    Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    Updater, CommandHandler, CallbackQueryHandler, MessageHandler,
    Filters, CallbackContext
)

# ===========================
# ⚙️ Engine & Branding
# ===========================
ENGINE_VERSION = "v8.9.6–InlinePremiumStable"
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
failure_count = 0

def start_bot():
    global failure_count
    check_single_instance()

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # try to clear prior handlers (safe)
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
        chat_id = update.effective_chat.id
        user = update.effective_user.first_name or "friend"

        # 1) Remove any lingering reply-keyboards from clients by sending a remove and deleting it quickly
        try:
            rem = context.bot.send_message(chat_id=chat_id, text=".", reply_markup=ReplyKeyboardRemove())
            # delete the temporary removal message to keep chat clean
            try:
                context.bot.delete_message(chat_id=chat_id, message_id=rem.message_id)
            except Exception:
                pass
        except Exception:
            # ignore if sending/removing fails
            pass

        # 2) delete previous start/welcome message if we stored one (clean UX)
        try:
            prev_mid = context.chat_data.get("start_msg_id")
            if prev_mid:
                context.bot.delete_message(chat_id=chat_id, message_id=prev_mid)
        except Exception:
            pass

        # 3) send inline welcome message and save its message_id for deletion later
        text = (
            f"👋 Hey <b>{user}</b>!\n\n"
            f"✨ Neural Core synced and online.\n"
            f"⚡ <b>WENBNB Neural Engine {ENGINE_VERSION}</b> — running in ProStable Mode.\n\n"
            f"<i>All modules operational — choose your next move!</i>\n\n"
            f"{BRAND_SIGNATURE}"
        )
        try:
            sent = context.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(inline_keyboard)
            )
            context.chat_data["start_msg_id"] = sent.message_id
        except Exception as e:
            logger.warning(f"⚠️ Failed to send start inline message: {e}")

    # === Inline Button Handler ===
    def button_callback(update: Update, context: CallbackContext):
        query = update.callback_query
        if not query:
            return
        data = query.data  # e.g. "price"
        chat_id = query.message.chat_id
        user = query.from_user

        # Acknowledge the press quickly
        try:
            query.answer(text="⚡ Sent command...")
        except Exception:
            pass

        try:
            # Delete the inline welcome message (clean)
            try:
                context.bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)
            except Exception:
                pass

            # Send exact /command text in chat (visible)
            command_text = f"/{data}"
            context.bot.send_message(chat_id=chat_id, text=command_text)

            logger.info(f"⚡ Inline Button Triggered by @{user.username or user.id}: {command_text}")

        except Exception as e:
            logger.error(f"❌ Inline button handler error: {e}")
            traceback.print_exc()
            try:
                query.message.reply_text("⚠️ Error executing that option.")
            except Exception:
                pass

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

    # === Register Handlers (order matters) ===
    # CallbackQueryHandler must be registered before general message handlers
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CallbackQueryHandler(button_callback))
    dp.add_handler(CommandHandler("about", about_cmd))

    # Register ai_auto_reply AFTER the button callback (prevents double triggers)
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
        logger.info("🚀 Starting Telegram polling (InlinePremiumStable)...")
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
