#!/usr/bin/env python3
# ============================================================
# 💫 WENBNB Neural Engine v8.9.0–ChatKeyboardUltraStable (ready)
# Emotion Sync + Real Chat Keyboard + Full Plugin Integration
# ============================================================

import os, sys, time, logging, threading, requests, traceback
from flask import Flask, jsonify
from telegram import Update, ParseMode, ReplyKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)

# ===========================
# ⚙️ Engine & Branding
# ===========================
ENGINE_VERSION = "v8.9.0–ChatKeyboardUltraStable"
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
    raise SystemExit("❌ TELEGRAM_TOKEN missing. Exiting...")

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
        "💰 Price": "price",
        "📊 Token Info": "tokeninfo",
        "😂 Meme": "meme",
        "🧠 AI Analyze": "aianalyze",
        "🎁 Airdrop Check": "airdropcheck",
        "🚨 Airdrop Alert": "airdropalert",
        "🌐 Web3": "web3",
        "ℹ️ About": "about",
        "⚙️ Admin": "admin"
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

    # === Chat Button Handler (sends visible /command then runs plugin) ===
    def button_handler(update: Update, context: CallbackContext):
        try:
            msg = update.message
            if not msg or not msg.text:
                return
            label = msg.text.strip()
            cmd_name = button_map.get(label)
            if not cmd_name:
                return  # normal chat; let other handlers decide

            logger.info(f"⚡ Button Pressed → /{cmd_name} (label='{label}')")

            # 1) Visible bot message showing the command (so user sees "/price")
            try:
                # send as bot message so it appears in chat like you requested
                update.message.reply_text(f"/{cmd_name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to echo /{cmd_name} as bot message: {e}")

            # 2) Execute the plugin command directly (safe: we call plugin function)
            # Map command name -> (module.path, function_name)
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

            # admin needs extra args
            if cmd_name == "admin":
                func(update, context, {
                    "version": ENGINE_VERSION,
                    "branding": {"footer": BRAND_SIGNATURE},
                    "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
                })
            else:
                # call plugin handler - most plugin handlers expect (update, context)
                try:
                    func(update, context)
                except TypeError:
                    # fallback if plugin expects other signature
                    func(update, context)

            logger.info(f"✅ Executed → /{cmd_name}")

            # IMPORTANT: we've handled this input — return so wrapper or other handlers won't re-run
            return
        except Exception as e:
            logger.error(f"❌ Chat keyboard trigger error: {e}")
            traceback.print_exc()
            try:
                update.message.reply_text("⚠️ Neural desync — please retry.")
            except Exception:
                pass

    # === Wrapper to prevent AI double-reply on keyboard label messages ===
    # We wrap the ai_auto_reply handler so it ignores keyboard label presses (the ones in button_map).
    def ai_auto_chat_guard(update: Update, context: CallbackContext):
        try:
            msg = update.message
            if not msg or not msg.text:
                return
            text = msg.text.strip()
            # If the incoming text is one of our keyboard labels, do NOT run auto-reply.
            if text in button_map:
                logger.info(f"🔇 Suppressed ai_auto_reply for keyboard label: {text}")
                return
            # Otherwise delegate to the original ai_auto_reply module
            try:
                return ai_auto_reply.ai_auto_chat(update, context)
            except Exception as e:
                logger.warning(f"⚠️ ai_auto_reply failed: {e}")
                traceback.print_exc()
        except Exception:
            traceback.print_exc()

    # === Register Handlers (order matters) ===
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    # Button handler must come BEFORE the auto-reply guard
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler))
    # Register our guard wrapper (will call ai_auto_reply only if message is not a keyboard label)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat_guard))

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
        logger.info("🚀 Starting Telegram polling (ChatKeyboardUltraStable)...")
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
