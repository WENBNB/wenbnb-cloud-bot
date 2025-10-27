#!/usr/bin/env python3
# ============================================================
#  💫 WENBNB Neural Engine v8.6-ProStable
#  Unified Emotion + Plugin Core + Auto-Healing Poll Protection
#  Render-safe + Background JobQueue + Modular Plugin Loader
# ============================================================

import os
import sys
import time
import json
import logging
import threading
import requests
from flask import Flask, jsonify
from telegram import Update, ParseMode, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

# ===========================
# ⚙️ Engine & Branding
# ===========================
ENGINE_VERSION = "v8.6-ProStable"
CORE_VERSION = "v5.0"
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
logger.info(f"🧠 Initializing WENBNB Neural Engine {ENGINE_VERSION} ...")

# ===========================
# 🔐 Environment Variables
# ===========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = os.getenv("OWNER_ID")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
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


# ===========================
# 🚀 Keep-Alive Pinger
# ===========================
def _keep_alive_loop(ping_url: str, interval: int = 600):
    logger.info(f"Keep-alive thread active → pinging {ping_url} every {interval}s")
    while True:
        try:
            requests.get(ping_url, timeout=8)
        except Exception as e:
            logger.warning(f"KeepAlive error: {e}")
        time.sleep(interval)

def start_keep_alive():
    if not RENDER_APP_URL:
        logger.info("Skipping keep-alive — RENDER_APP_URL not set.")
        return
    threading.Thread(target=_keep_alive_loop, args=(RENDER_APP_URL,), daemon=True).start()


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
# 🛡️ Single Instance Lock
# ===========================
LOCK_FILE = "/tmp/wenbnb_lock"

def check_single_instance():
    """Prevents duplicate polling instances."""
    if os.path.exists(LOCK_FILE):
        logger.error("⚠️ Another bot instance is already running! Aborting startup.")
        raise SystemExit(1)
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))
    logger.info("🔒 Instance lock acquired.")
    return True


# ===========================
# 💬 Telegram Bot Setup
# ===========================
def start_bot():
    check_single_instance()

    logger.info("🚀 Initializing Telegram Updater...")
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.job_queue = updater.job_queue  # ✅ Required for background tasks

    # === Load Plugin Handlers ===
    logger.info("🔍 Loading all plugin modules...")
    register_all_plugins(dp)
    logger.info("🧠 Plugin load sequence complete. Starting core commands...")

    # === Core Commands ===
    def start_cmd(update: Update, context: CallbackContext):
        user = update.effective_user.first_name or "friend"
        text = (
            f"👋 Hello {user}!\n\n"
            f"Welcome to <b>WENBNB Neural Engine {ENGINE_VERSION}</b>\n\n"
            f"{BRAND_SIGNATURE}"
        )
        keyboard = [
            [KeyboardButton("/price"), KeyboardButton("/tokeninfo")],
            [KeyboardButton("/meme"), KeyboardButton("/aianalyze")],
            [KeyboardButton("/airdropcheck"), KeyboardButton("/airdropalert")],
            [KeyboardButton("/web3"), KeyboardButton("/about")]
        ]
        update.message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    def about_cmd(update: Update, context: CallbackContext):
        update.message.reply_text(
            f"🌐 <b>About WENBNB</b>\n\n"
            f"Hybrid AI + Web3 Neural Assistant.\n"
            f"Now running <b>Neural Engine {ENGINE_VERSION}</b>.\n\n"
            f"{BRAND_SIGNATURE}",
            parse_mode=ParseMode.HTML
        )

    # === Register Core Commands ===
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))

    # === Load Emotion + Analyzer Plugins ===
    try:
        from plugins import ai_auto_reply, aianalyze
        aianalyze.register_handlers(dp)  # ✅ Register /aianalyze
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply.ai_auto_chat))
        logger.info("💬 Emotion-Sync + AI Analyzer active.")
    except Exception as e:
        logger.warning(f"⚠️ Emotion/Analyzer not loaded: {e}")

    # === Start Bot ===
    updater.start_polling(clean=True)
    logger.info("✅ Telegram polling started (Render-safe).")
    updater.idle()


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
    finally:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
            logger.info("🔓 Instance lock released.")


if __name__ == "__main__":
    main()
