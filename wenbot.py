#!/usr/bin/env python3
# ============================================================
# 💫 WENBNB Neural Engine v8.8.4-ProConsoleStable++
# Real Command Keyboard • Emotion Sync • Plugin Safe Execution
# ============================================================

import os, sys, time, logging, threading, requests, traceback
from flask import Flask, jsonify
from telegram import Update, ParseMode, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ===========================
# ⚙️ Engine & Branding
# ===========================
ENGINE_VERSION = "v8.8.4-ProConsoleStable++"
CORE_VERSION = "v5.3"
BRAND_SIGNATURE = "🚀 <b>Powered by WENBNB Neural Engine</b> — Emotional Intelligence 24×7 ⚡"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger("WENBNB")

# ===========================
# 🔐 Environment Setup
# ===========================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_APP_URL = os.getenv("RENDER_APP_URL", "")

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

def keep_alive():
    if not RENDER_APP_URL:
        return
    def loop():
        while True:
            try:
                requests.get(RENDER_APP_URL + "/ping", timeout=6)
                logger.info("💓 KeepAlive Ping OK")
            except:
                logger.warning("⚠️ KeepAlive Failed")
            time.sleep(600)
    threading.Thread(target=loop, daemon=True).start()

# ===========================
# 💬 Telegram Bot Core
# ===========================
def start_bot():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # --- Core Plugin Imports
    from plugins import (
        aianalyze,
        ai_auto_reply,
        admin_tools,
        plugin_manager
    )

    # --- Load Plugins
    try:
        plugin_manager.load_all_plugins(dp)
        logger.info("✅ Plugins loaded successfully.")
    except Exception as e:
        logger.error(f"❌ PluginManager failed: {e}")

    # --- Keyboard Layout
    keyboard = [
        ["💰 Price", "📊 Token Info"],
        ["😂 Meme", "🧠 AI Analyze"],
        ["🎁 Airdrop Check", "🚨 Airdrop Alert"],
        ["🌐 Web3", "ℹ️ About", "⚙️ Admin"]
    ]

    # --- Map Buttons to Commands
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

    # --- /start Command
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

    # --- /about Command
    def about_cmd(update: Update, context: CallbackContext):
        update.message.reply_text(
            f"🌐 <b>About WENBNB</b>\n\n"
            f"AI + Web3 Neural Assistant\n"
            f"Currently running <b>{ENGINE_VERSION}</b>\n\n"
            f"{BRAND_SIGNATURE}",
            parse_mode=ParseMode.HTML
        )

    # --- /reload Command (for plugin refresh)
    def reload_cmd(update: Update, context: CallbackContext):
        update.message.reply_text("🔁 Reloading all plugins...")
        try:
            plugin_manager.load_all_plugins(dp)
            update.message.reply_text("✅ Plugins reloaded successfully.")
        except Exception as e:
            update.message.reply_text(f"❌ Reload failed: {e}")

    # --- Button Handler (Executes Commands)
    def button_handler(update: Update, context: CallbackContext):
        label = update.message.text.strip()
        cmd_name = button_map.get(label)
        if not cmd_name:
            return

        try:
            handler = next(
                (h for h in context.dispatcher.handlers[0]
                 if isinstance(h, CommandHandler) and h.command[0] == cmd_name),
                None
            )
            if handler:
                logger.info(f"⚡ Running command: /{cmd_name}")
                fake_update = Update(update.update_id, message=update.message)
                fake_update.message.text = f"/{cmd_name}"
                handler.callback(fake_update, context)
            else:
                update.message.reply_text(f"⚠️ Module /{cmd_name} not found or inactive.")
        except Exception as e:
            logger.error(f"⚠️ Error executing /{cmd_name}: {e}")

    # --- Register Handlers
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    dp.add_handler(CommandHandler("reload", reload_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler))

    # --- Plugin Integrations
    dp.add_handler(CommandHandler("aianalyze", aianalyze.aianalyze_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply.ai_auto_chat))
    dp.add_handler(CommandHandler("admin", lambda u, c: admin_tools.admin_status(u, c, {
        "version": ENGINE_VERSION,
        "branding": {"footer": BRAND_SIGNATURE}
    })))

    keep_alive()
    logger.info("🚀 WENBNB Neural Engine online.")
    updater.start_polling(clean=True)
    updater.idle()

# ===========================
# 🧠 Entry Point
# ===========================
if __name__ == "__main__":
    start_bot()
