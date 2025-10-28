#!/usr/bin/env python3
# ============================================================
# 💫 WENBNB Neural Engine v8.8.9-ChatKeyboardFinal
# Real Chat Keyboard • Direct Command Trigger • Stable
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
ENGINE_VERSION = "v8.8.9-ChatKeyboardFinal"
CORE_VERSION = "v5.3"
BRAND_SIGNATURE = os.getenv(
    "BRAND_SIGNATURE",
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

    # Clear old handlers (keeps consistent order)
    try:
        dp.handlers.clear()
        logger.info("🧹 Old handlers cleared to prevent keyboard conflicts")
    except Exception:
        # older versions: dp.handlers may be dict; ignore if not available
        pass

    # Register plugins (they may add command handlers)
    register_all_plugins(dp)

    # ----- Chat keyboard layout (labels shown to users) -----
    keyboard = [
        ["💰 Price", "📊 Token Info"],
        ["😂 Meme", "🧠 AI Analyze"],
        ["🎁 Airdrop Check", "🚨 Airdrop Alert"],
        ["🌐 Web3", "ℹ️ About", "⚙️ Admin"]
    ]

    # Map visible button label -> underlying command name (no leading slash)
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

    # === /start command (shows chat keyboard) ===
    def start_cmd(update: Update, context: CallbackContext):
        user = (update.effective_user.first_name or "friend")
        text = (
            f"👋 Hey <b>{user}</b>!\n\n"
            f"✨ Neural Core synced and online.\n"
            f"⚡ <b>WENBNB Neural Engine {ENGINE_VERSION}</b> — running in ProStable Mode.\n\n"
            f"<i>All modules operational — choose your next move!</i>\n\n"
            f"{BRAND_SIGNATURE}"
        )
        # send only the main welcome message with ReplyKeyboard
        update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # === Chat button handler — DIRECTLY executes matched command handler ===
    def button_handler(update: Update, context: CallbackContext):
        try:
            # sanity
            if not update.message or not update.message.text:
                return

            label = update.message.text.strip()
            cmd_name = button_map.get(label)
            if not cmd_name:
                # unknown chat text — ignore so other handlers (ai_auto_reply) can respond
                return

            logger.info(f"⚡ Chat Button Pressed → /{cmd_name}")

            # Search registered handlers (all groups) and directly call matching CommandHandler callback
            found = False
            # dp.handlers is a dict group_index -> [handlers]
            handlers_collections = []
            # safe access
            try:
                handlers_collections = dp.handlers.values()
            except Exception:
                # fallback: dp.handlers might be a list-like in some versions
                handlers_collections = [dp.handlers] if dp.handlers else []

            for handlers_list in handlers_collections:
                for h in handlers_list:
                    # check CommandHandler
                    try:
                        from telegram.ext import CommandHandler as _CH
                        if isinstance(h, _CH):
                            cmds = h.command if isinstance(h.command, (list, tuple)) else [h.command]
                            # make sure cmd_name matches any (strings)
                            if cmd_name in cmds:
                                logger.info(f"🧠 Running handler directly for /{cmd_name}")
                                # call callback directly
                                try:
                                    h.callback(update, context)
                                except TypeError:
                                    # some handlers expect (update, context) signature — try calling with two args
                                    h.callback(update, context)
                                found = True
                                return  # stop after executing
                    except Exception:
                        # ignore handler inspection errors and continue
                        continue

            if not found:
                logger.warning(f"🤖 Command /{cmd_name} not found among registered handlers")
                update.message.reply_text(f"🤖 Command /{cmd_name} not available right now.")
        except Exception as e:
            logger.error(f"❌ Error in button_handler: {e}")
            traceback.print_exc()
            try:
                update.message.reply_text("⚠️ Internal error running that command.")
            except Exception:
                pass

    # === /about command (example) ===
    def about_cmd(update: Update, context: CallbackContext):
        text = (
            f"🌐 <b>About WENBNB</b>\n\n"
            f"Hybrid AI + Web3 Neural Assistant — blending emotion with precision.\n"
            f"Currently running <b>WENBNB Neural Engine {ENGINE_VERSION}</b>.\n\n"
            f"💫 Always learning, always adapting.\n\n"
            f"{BRAND_SIGNATURE}"
        )
        update.message.reply_text(text, parse_mode=ParseMode.HTML)

    # Register core handlers first (so button_handler runs before ai_auto_reply)
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    # button_handler should be BEFORE the ai_auto_reply message handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler))

    # === Plugin command handlers (these rely on plugin modules) ===
    try:
        # plugin-provided commands
        dp.add_handler(CommandHandler("aianalyze", aianalyze.aianalyze_cmd))
        # ai_auto_reply should come AFTER button_handler; it handles general messages
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply.ai_auto_chat))
        # admin commands
        dp.add_handler(CommandHandler("admin", lambda u, c: admin_tools.admin_status(u, c, {
            "version": ENGINE_VERSION,
            "branding": {"footer": BRAND_SIGNATURE},
            "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
        })))
        dp.add_handler(CommandHandler("reboot", lambda u, c: admin_tools.admin_reboot(u, c, {
            "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
        })))
        logger.info("💬 Plugin command handlers registered")
    except Exception as e:
        logger.warning(f"⚠️ Plugin handler registration issue: {e}")
        traceback.print_exc()

    # === Heartbeat Thread ===
    def heartbeat():
        while True:
            time.sleep(30)
            try:
                if RENDER_APP_URL:
                    requests.get(f"{RENDER_APP_URL}/ping", timeout=5)
                logger.info("💓 Poll heartbeat alive")
            except Exception:
                logger.warning("⚠️ Poll heartbeat missed — continuing")

    threading.Thread(target=heartbeat, daemon=True).start()

    # === Start polling ===
    try:
        logger.info("🚀 Starting Telegram polling (ChatKeyboardFinal)...")
        updater.start_polling(clean=True)
        updater.idle()
    except Exception as e:
        if "Conflict" in str(e):
            logger.warning("⚠️ Conflict detected — restarting...")
            release_instance_lock()
            os._exit(1)
        else:
            failure_count += 1
            logger.error(f"❌ Polling crash ({failure_count}): {e}")
            traceback.print_exc()
            if failure_count >= 3:
                logger.error("💥 Too many failures → Full reboot.")
                release_instance_lock()
                os._exit(1)
            else:
                logger.info("🔁 Attempting recovery...")
                time.sleep(5)
                start_bot()

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
