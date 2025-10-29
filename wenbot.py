#!/usr/bin/env python3
# ============================================================
# 💫 WENBNB Neural Engine v8.9.2–ChatKeyboardLockdown Final
# Emotion Sync + Real Chat Keyboard + Full Plugin Integration
# ============================================================

import os, sys, time, logging, threading, requests, traceback
from flask import Flask, jsonify
from telegram import Update, ParseMode, ReplyKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import escape_markdown

# ===========================
# ⚙️ Engine & Branding
# ===========================
ENGINE_VERSION = "v8.9.2–ChatKeyboardLockdown Final"
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
# 🔐 Environment Variables
# ===========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_APP_URL = os.getenv("RENDER_APP_URL", "")
PORT = int(os.getenv("PORT", "10000"))

if not TELEGRAM_TOKEN:
    raise SystemExit("❌ TELEGRAM_TOKEN missing. Exiting…")

# ===========================
# 🌐 Flask Keep-Alive Server
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
# 🧩 Plugin Manager Integration
# ===========================
from plugins import plugin_manager
def register_all_plugins(dispatcher):
    try:
        plugin_manager.load_all_plugins(dispatcher)
        logger.info("✅ PluginManager: All plugins loaded successfully.")
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
    try:
        dp.handlers.clear()
    except Exception:
        pass

    register_all_plugins(dp)

    # --- Button Label → Command Mapping ---
    button_map = {
        "/price": "price",
        "/tokeninfo": "tokeninfo",
        "/meme": "meme",
        "/aianalyze": "aianalyze",
        "/airdropcheck": "airdropcheck",
        "/airdropalert": "airdropalert",
        "/web3": "web3",
        "/about": "about",
        "/admin": "admin"
    }

    # --- Keyboard Layout ---
    keyboard = [
        ["💰 Price", "📊 Token Info"],
        ["😂 Meme", "🧠 AI Analyze"],
        ["🎁 Airdrop Check", "🚨 Airdrop Alert"],
        ["🌐 Web3", "ℹ️ About", "⚙️ Admin"]
    ]

    # === /start Command ===
    def start_cmd(update: Update, context: CallbackContext):
        user = update.effective_user.first_name or "friend"
        text = (
            f"👋 Hey <b>{user}</b>!\n\n"
            f"✨ Neural Core synced and online.\n"
            f"⚡ <b>WENBNB Neural Engine {ENGINE_VERSION}</b> — running in ProStable Mode.\n\n"
            f"<i>All modules operational — choose your next move!</i>\n\n"
            f"{BRAND_SIGNATURE}"
        )
        update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # === Chat Button Handler — Lockdown Fix ===
    @run_async
    def button_handler(update: Update, context: CallbackContext):
        try:
            msg = update.message
            if not msg or not msg.text:
                return

            label = msg.text.strip()
            cmd_name = button_map.get(label)
            if not cmd_name:
                return  # normal chat — let AI handle

            # stop AI auto-reply from grabbing the same message
            if hasattr(update, "handled"):
                return
            update.handled = True

            logger.info(f"⚡ Button Pressed → /{cmd_name}")

            commands = {
                "price": ("plugins.price", "price_cmd"),
                "tokeninfo": ("plugins.tokeninfo", "tokeninfo_cmd"),
                "meme": ("plugins.meme", "meme_cmd"),
                "aianalyze": ("plugins.aianalyze", "aianalyze_cmd"),
                "airdropcheck": ("plugins.airdropcheck", "airdropcheck_cmd"),
                "airdropalert": ("plugins.airdropalert", "airdropalert_cmd"),
                "web3": ("plugins.web3", "web3_cmd"),
                "about": (__name__, "about_cmd"),
                "admin": ("plugins.admin_tools", "admin_status")
            }

            module_name, func_name = commands[cmd_name]
            mod = __import__(module_name, fromlist=[func_name])
            func = getattr(mod, func_name)

            if cmd_name == "admin":
                func(update, context, {
                    "version": ENGINE_VERSION,
                    "branding": {"footer": BRAND_SIGNATURE},
                    "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
                })
            else:
                func(update, context)

            logger.info(f"✅ Executed → /{cmd_name}")

        except Exception as e:
            logger.error(f"❌ Chat keyboard trigger error: {e}")
            traceback.print_exc()
            try:
                update.message.reply_text("⚠️ Neural desync — please retry.")
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

    # === Register Handlers (order critical) ===
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler))

    # === Plugin Commands ===
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

    # === AI Auto-Reply (MUST BE LAST) ===
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply.ai_auto_chat))

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
        logger.info("🚀 Starting Telegram polling (ChatKeyboardLockdown Final)…")
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

