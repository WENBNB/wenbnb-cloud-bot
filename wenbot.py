#!/usr/bin/env python3
# ============================================================
# 💫 WENBNB Neural Engine v8.9.1–ChatKeyboardCommandEcho Stable
# Emotion Sync + Real Chat Keyboard + Full Plugin Integration
# (Modern keyboard layout, button → "/command" echo + safe execution)
# ============================================================

import os
import sys
import time
import logging
import threading
import requests
import traceback

from flask import Flask, jsonify
from telegram import Update, ParseMode, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    DispatcherHandlerStop
)

# ===========================
# ⚙️ Engine & Branding
# ===========================
ENGINE_VERSION = "v8.9.1–ChatKeyboardCommandEcho Stable"
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
# 🧠 Core Plugin Imports (kept as before)
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

    # Try to clear old handlers to keep order deterministic (safe)
    try:
        dp.handlers.clear()
        logger.info("🧹 Old handlers cleared to prevent keyboard conflicts")
    except Exception:
        pass

    # load plugins (they add their own handlers)
    register_all_plugins(dp)

    # --- Modern Chat keyboard layout (what I picked) ---
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
        update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # === Chat Button Handler — echoes "/command" and runs the corresponding plugin handler ===
    def button_handler(update: Update, context: CallbackContext):
        try:
            if not update.message or not update.message.text:
                return

            label = update.message.text.strip()
            cmd_name = button_map.get(label)
            if not cmd_name:
                # not our keyboard, let other handlers handle (AI reply etc.)
                return

            logger.info(f"⚡ Chat Button Pressed → {label} -> /{cmd_name}")

            # First — echo the command as bot message (so user sees /price)
            try:
                update.message.reply_text(f"/{cmd_name}")
            except Exception:
                # ignore reply failures
                pass

            # Map commands to modules/functions (safe direct calls)
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

            module_name, func_name = commands.get(cmd_name, (None, None))
            if not module_name:
                update.message.reply_text(f"🤖 Command /{cmd_name} not configured.")
                # prevent other handlers from running on this keyboard press
                raise DispatcherHandlerStop()

            mod = __import__(module_name, fromlist=[func_name])
            func = getattr(mod, func_name)

            # For admin_status signature expects (update, context, config) — handle separately
            if cmd_name == "admin":
                func(update, context, {
                    "version": ENGINE_VERSION,
                    "branding": {"footer": BRAND_SIGNATURE},
                    "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
                })
            else:
                # call plugin command function (most plugin cmd funcs expect (update, context))
                try:
                    func(update, context)
                except TypeError:
                    # if plugin exposed a CommandHandler object instead, attempt direct dispatch
                    logger.info("Handler call TypeError — attempting fallback dispatch.")
                    # fallback: try to run registered CommandHandler callback if exists
                    for handlers_list in dp.handlers.values():
                        for h in handlers_list:
                            try:
                                if isinstance(h, CommandHandler):
                                    cmds = h.command if isinstance(h.command, (list, tuple)) else [h.command]
                                    if cmd_name in cmds:
                                        h.callback(update, context)
                                        raise DispatcherHandlerStop()
                            except DispatcherHandlerStop:
                                raise
                            except Exception:
                                continue

            logger.info(f"✅ Executed → /{cmd_name}")
            # stop further message handlers from receiving the original keyboard text
            raise DispatcherHandlerStop()

        except DispatcherHandlerStop:
            # intentionally stop propagation
            raise
        except Exception as e:
            logger.error(f"❌ Chat keyboard trigger error: {e}")
            traceback.print_exc()
            try:
                update.message.reply_text("⚠️ Neural desync — please retry.")
            except Exception:
                pass
            # stop other handlers for safety on error
            raise DispatcherHandlerStop()

    # === /about Command (kept as plugin-like function) ===
    def about_cmd(update: Update, context: CallbackContext):
        text = (
            f"🌐 <b>About WENBNB</b>\n\n"
            f"Hybrid AI + Web3 Neural Assistant — blending emotion with precision.\n"
            f"Currently running <b>WENBNB Neural Engine {ENGINE_VERSION}</b>.\n\n"
            f"💫 Always learning, always adapting.\n\n"
            f"{BRAND_SIGNATURE}"
        )
        update.message.reply_text(text, parse_mode=ParseMode.HTML)

    # === Register core handlers — note order: button_handler before ai_auto_reply ===
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    # button handler MUST run before ai_auto_reply (so it stops propagation on keyboard press)
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler), group=0)

    # === Plugin Command Handlers & AI handler (register AFTER button handler) ===
    try:
        dp.add_handler(CommandHandler("aianalyze", aianalyze.aianalyze_cmd))
        # ai_auto_reply should be in a later group so button_handler can stop propagation
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply.ai_auto_chat), group=1)
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
        logger.info("🚀 Starting Telegram polling (ChatKeyboardCommandEcho Stable)...")
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
