#!/usr/bin/env python3
# ============================================================
# ⚡ WENBNB Neural Engine v9.0.3 – ChatKeyboardEchoPureLock Final
# ============================================================

import os, sys, time, logging, threading, requests, traceback
from flask import Flask, jsonify
from telegram import Update, ParseMode, ReplyKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)

# =========================
# ⚙️ Engine Metadata
# =========================
ENGINE_VERSION = "v9.0.3–ChatKeyboardEchoPureLock Final"
CORE_VERSION = "v5.3"
BRAND_SIGNATURE = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7 ⚡"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger("WENBNB")

# =========================
# 🔐 Env Vars
# =========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_APP_URL = os.getenv("RENDER_APP_URL", "https://wenbnb-neural-engine.onrender.com")
PORT = int(os.getenv("PORT", "10000"))

if not TELEGRAM_TOKEN:
    raise SystemExit("❌ TELEGRAM_TOKEN missing. Exiting...")

# =========================
# 🌐 KeepAlive Flask Server
# =========================
app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({
        "status": "ok",
        "engine": ENGINE_VERSION,
        "core": CORE_VERSION,
        "timestamp": int(time.time())
    })

def _keep_alive_loop(url, interval=600):
    while True:
        try:
            requests.get(url, timeout=8)
            logger.info("💓 KeepAlive ping → OK")
        except Exception as e:
            logger.warning(f"KeepAlive error: {e}")
        time.sleep(interval)

def start_keep_alive():
    if RENDER_APP_URL:
        threading.Thread(target=_keep_alive_loop, args=(RENDER_APP_URL,), daemon=True).start()
        logger.info("🩵 Keep-alive started successfully")

# =========================
# 💬 Telegram Bot Core
# =========================
def start_bot():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # --- Button Map ---
    button_map = {
        "💰 Price": "/price",
        "📊 Token Info": "/tokeninfo",
        "😂 Meme": "/meme",
        "🧠 AI Analyze": "/aianalyze",
        "🎁 Airdrop Check": "/airdropcheck",
        "🚨 Airdrop Alert": "/airdropalert",
        "🌐 Web3": "/web3",
        "ℹ️ About": "/about",
        "⚙️ Admin": "/admin"
    }

    # --- Modern Keyboard Layout ---
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

    # === Button Handler (Echo-Only) ===
    def button_handler(update: Update, context: CallbackContext):
        try:
            msg = update.message
            if not msg or not msg.text:
                return
            label = msg.text.strip()
            if label in button_map:
                update.message.reply_text(button_map[label])  # Echo only
                logger.info(f"🟢 Echoed command: {button_map[label]}")
        except Exception as e:
            logger.error(f"❌ Echo handler error: {e}")

    # === AI Auto-Chat (Manual Messages Only) ===
    def ai_auto_reply(update: Update, context: CallbackContext):
        msg = update.message.text.strip()
        if msg.startswith("/") or msg in button_map:
            return  # ignore command/button texts
        try:
            reply = f"🤖 Sup {update.effective_user.first_name}, I'm synced and listening 💫"
            update.message.reply_text(reply)
        except Exception as e:
            logger.error(f"AI Auto-Reply error: {e}")

    # === About Command ===
    def about_cmd(update: Update, context: CallbackContext):
        text = (
            f"🌐 <b>About WENBNB</b>\n\n"
            f"Hybrid AI + Web3 Neural Assistant — emotion meets precision.\n"
            f"Running <b>{ENGINE_VERSION}</b>.\n\n"
            f"{BRAND_SIGNATURE}"
        )
        update.message.reply_text(text, parse_mode=ParseMode.HTML)

    # === Handlers ===
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply))

    # === Start Polling ===
    logger.info("🚀 Starting Telegram Polling – EchoPureLock Mode")
    updater.start_polling()
    updater.idle()

# =========================
# 🧠 Entry Point
# =========================
def main():
    logger.info(f"💫 Launching WENBNB Neural Engine {ENGINE_VERSION}")
    start_keep_alive()
    start_bot()

if __name__ == "__main__":
    main()
