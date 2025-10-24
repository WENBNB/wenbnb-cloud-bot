#!/usr/bin/env python3
# ============================================================
#  WENBNB Neural Engine v5.1 — Full Hybrid Build (Final)
#  - AI Neural Core + Web3 + Meme Intelligence + Keep-Alive
# ============================================================
import os
import sys
import time
import json
import logging
import threading
from typing import Optional

import requests
from flask import Flask, jsonify

# Telegram imports (python-telegram-bot v13.x)
from telegram import Update, ParseMode, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# -------------------------
# Logging / Branding Setup
# -------------------------
ENGINE_VERSION = "v5.1"
CORE_VERSION = "v3.0"
BRAND_SIGNATURE = os.getenv("BRAND_SIGNATURE",
                            "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7")

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger("WENBNB")

logger.info(f"WENBNB Neural Engine {ENGINE_VERSION} starting...")

# -------------------------
# Environment Variables
# -------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
OWNER_ID = os.getenv("OWNER_ID")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
WEN_TOKEN_ADDRESS = os.getenv("WEN_TOKEN_ADDRESS")
DASHBOARD_URL = os.getenv("DASHBOARD_URL")
DASHBOARD_KEY = os.getenv("DASHBOARD_KEY", "")
RENDER_APP_URL = os.getenv("RENDER_APP_URL", "")
PORT = int(os.getenv("PORT", "10000"))
DB_FILE = os.getenv("DB_FILE", "memory_data.db")

if not TELEGRAM_TOKEN:
    logger.error("❌ TELEGRAM_TOKEN not set. Exiting.")
    raise SystemExit("Missing TELEGRAM_TOKEN")

# -------------------------
# Flask App (for keep-alive ping)
# -------------------------
app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({
        "status": "ok",
        "engine": ENGINE_VERSION,
        "core": CORE_VERSION,
        "time": int(time.time())
    })

# -------------------------
# Dashboard Event Helper
# -------------------------
def send_dashboard_event(event_text: str, source: str = "bot"):
    if not DASHBOARD_URL:
        return False
    try:
        url = DASHBOARD_URL.rstrip("/") + "/update_activity"
        headers = {"Content-Type": "application/json"}
        if DASHBOARD_KEY:
            headers["X-DASH-KEY"] = DASHBOARD_KEY
        payload = {"event": event_text, "source": source, "time": int(time.time())}
        requests.post(url, json=payload, headers=headers, timeout=3)
        return True
    except Exception as e:
        logger.debug(f"Dashboard send failed: {e}")
        return False

# -------------------------
# Keep-Alive Background Thread
# -------------------------
def _keep_alive_loop(ping_url: str, interval: int = 600):
    logger.info(f"Keep-alive thread started, pinging {ping_url} every {interval}s")
    while True:
        try:
            r = requests.get(ping_url, timeout=8)
            logger.debug(f"KeepAlive ping {ping_url} -> {r.status_code}")
        except Exception as e:
            logger.warning(f"KeepAlive error: {e}")
        time.sleep(interval)

def start_keep_alive():
    if not RENDER_APP_URL:
        logger.info("RENDER_APP_URL not set, skipping keep-alive thread.")
        return
    t = threading.Thread(target=_keep_alive_loop, args=(RENDER_APP_URL,), daemon=True)
    t.start()

# -------------------------
# Plugin Loader (Modular)
# -------------------------
def try_import(module_name: str):
    try:
        mod = __import__(module_name, fromlist=["*"])
        logger.info(f"✅ Loaded plugin: {module_name}")
        return mod
    except Exception as e:
        logger.error(f"❌ Plugin load failed ({module_name}): {e}", exc_info=True)
        return None

plugins = {
    "price": try_import("plugins.price_tracker"),
    "price_alt": try_import("plugins.price"),
    "tokeninfo": try_import("plugins.tokeninfo"),
    "airdrop": try_import("plugins.airdrop_check"),
    "meme": try_import("plugins.meme_ai"),
    "ai": try_import("plugins.ai_auto_reply"),
    "aianalyze": try_import("plugins.aianalyze"),
    "memory": try_import("plugins.memory_ai"),
    "admin": try_import("plugins.admin_panel"),
    "system": try_import("plugins.system_monitor"),
    "web3": try_import("plugins.web3_connect"),
    "giveaway": try_import("plugins.giveaway_ai"),
    "emotion": try_import("plugins.emotion_ai")
}

# Quick sanity check
if not plugins["meme"]:
    logger.warning("⚠️ Meme plugin failed to load! Please check plugins/meme_ai.py path or syntax.")

# -------------------------
# Utilities
# -------------------------
def is_owner(user_id: int) -> bool:
    if OWNER_ID is None:
        return False
    try:
        return int(user_id) == int(OWNER_ID)
    except:
        return False

def is_admin(user_id: int) -> bool:
    if ADMIN_CHAT_ID is None:
        return False
    try:
        return int(user_id) == int(ADMIN_CHAT_ID) or is_owner(user_id)
    except:
        return False

# -------------------------
# Safe Call Decorator
# -------------------------
def safe_call(fn):
    def wrapper(update: Update, context: CallbackContext):
        try:
            logger.debug(f"Handling {fn.__name__} from {update.effective_user.id}")
            res = fn(update, context)
            try:
                user = update.effective_user.username or str(update.effective_user.id)
                send_dashboard_event(f"{fn.__name__} used by {user}", source="bot")
            except Exception:
                pass
            return res
        except Exception as err:
            logger.exception(f"Error in handler {fn.__name__}: {err}")
            try:
                update.message.reply_text("⚠️ Internal error. Please try again later.")
            except Exception:
                pass
    return wrapper

# -------------------------
# Command Handlers
# -------------------------
@safe_call
def start_cmd(update: Update, context: CallbackContext):
    user = update.effective_user.first_name or update.effective_user.username or "friend"
    text = (
        f"👋 Hello {user}!\n\n"
        f"Welcome to <b>WENBNB Neural Engine {ENGINE_VERSION}</b>\n\n"
        "Use /menu or the buttons below to explore.\n\n"
        f"{BRAND_SIGNATURE}"
    )
    keyboard = [
        [KeyboardButton("/price"), KeyboardButton("/tokeninfo")],
        [KeyboardButton("/meme"), KeyboardButton("/aianalyze")],
        [KeyboardButton("/airdropcheck"), KeyboardButton("/about")],
    ]
    update.message.reply_text(text, parse_mode=ParseMode.HTML,
                              reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    send_dashboard_event("User started the bot", source="bot")

@safe_call
def help_cmd(update: Update, context: CallbackContext):
    text = (
        "🧠 <b>WENBNB Bot — Command Center</b>\n\n"
        "💰 /price — Token price\n"
        "🔍 /tokeninfo — Token analytics\n"
        "🎁 /airdropcheck <wallet>\n"
        "😂 /meme — Meme generator\n"
        "📈 /aianalyze — AI market insight\n"
        "⚙️ /system — System monitor\n\n"
        f"{BRAND_SIGNATURE}"
    )
    update.message.reply_text(text, parse_mode=ParseMode.HTML)

@safe_call
def about_cmd(update: Update, context: CallbackContext):
    text = (
        f"🌐 <b>About WENBNB</b>\n\n"
        "Hybrid AI + Web3 assistant. Built for memes, markets, and community.\n\n"
        f"{BRAND_SIGNATURE}"
    )
    update.message.reply_text(text, parse_mode=ParseMode.HTML)

# Plugin bridges
@safe_call
def meme_cmd(update: Update, context: CallbackContext):
    if plugins["meme"] and hasattr(plugins["meme"], "meme_cmd"):
        return plugins["meme"].meme_cmd(update, context)
    update.message.reply_text("😂 Meme generator plugin missing or failed to load.")

@safe_call
def price_cmd(update: Update, context: CallbackContext):
    if plugins["price"] and hasattr(plugins["price"], "price_cmd"):
        return plugins["price"].price_cmd(update, context)
    update.message.reply_text("💰 Price plugin missing.")

@safe_call
def tokeninfo_cmd(update: Update, context: CallbackContext):
    if plugins["tokeninfo"] and hasattr(plugins["tokeninfo"], "tokeninfo_cmd"):
        return plugins["tokeninfo"].tokeninfo_cmd(update, context)
    update.message.reply_text("🔍 Token info plugin missing.")

@safe_call
def airdrop_cmd(update: Update, context: CallbackContext):
    plugin = plugins.get("airdrop")
    if not plugin:
        update.message.reply_text("🎁 Airdrop plugin missing.")
        return
    if hasattr(plugin, "airdropcheck_cmd"):
        return plugin.airdropcheck_cmd(update, context)
    if hasattr(plugin, "airdrop_cmd"):
        return plugin.airdrop_cmd(update, context)
    update.message.reply_text("🎁 Airdrop plugin found, but no valid handler defined.")

@safe_call
def aianalyze_cmd(update: Update, context: CallbackContext):
    if plugins["aianalyze"] and hasattr(plugins["aianalyze"], "aianalyze_cmd"):
        return plugins["aianalyze"].aianalyze_cmd(update, context)
    update.message.reply_text("📈 AI analyzer plugin missing.")

@safe_call
def system_cmd(update: Update, context: CallbackContext):
    if plugins["system"] and hasattr(plugins["system"], "system_status"):
        return plugins["system"].system_status(update, context)
    update.message.reply_text("⚙️ System monitor unavailable.")

# -------------------------
# Startup / Runner
# -------------------------
def _start_bot():
    logger.info("Initializing Telegram Updater...")
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    dp.add_handler(CommandHandler("price", price_cmd))
    dp.add_handler(CommandHandler("tokeninfo", tokeninfo_cmd))
    dp.add_handler(CommandHandler("airdropcheck", airdrop_cmd))
    dp.add_handler(CommandHandler("meme", meme_cmd))
    dp.add_handler(CommandHandler("aianalyze", aianalyze_cmd))
    dp.add_handler(CommandHandler("system", system_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, 
                                  plugins["ai"].ai_auto_reply if plugins["ai"] else None))

    updater.start_polling()
    logger.info("✅ Telegram bot polling started.")
    send_dashboard_event("Bot polling started", source="system")
    updater.idle()

# -------------------------
# Entry Point
# -------------------------
def main():
    logger.info("WENBNB Neural Engine main() starting...")
    start_keep_alive()
    send_dashboard_event("WENBNB Bot startup", source="system")

    if __name__ == "__main__":
        try:
            _start_bot()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt caught — shutting down.")
        except Exception as e:
            logger.exception(f"Fatal error in bot: {e}")
            raise

if __name__ == "__main__":
    main()
