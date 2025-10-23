#!/usr/bin/env python3
# ============================================================
#  WENBNB Neural Engine v5.0 — Full Hybrid Build (Final)
#  - AI Neural Core + Web3 + Dashboard + Keep-Alive
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
ENGINE_VERSION = "v5.0"
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
# Environment (required)
# -------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY")
OWNER_ID = os.getenv("OWNER_ID")           # string or number
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID") # string or number
WEN_TOKEN_ADDRESS = os.getenv("WEN_TOKEN_ADDRESS")
DASHBOARD_URL = os.getenv("DASHBOARD_URL")
DASHBOARD_KEY = os.getenv("DASHBOARD_KEY", "")
RENDER_APP_URL = os.getenv("RENDER_APP_URL", "")  # used by keep-alive
PORT = int(os.getenv("PORT", "10000"))
DB_FILE = os.getenv("DB_FILE", "memory_data.db")

# Basic validation
if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN not set. Exiting.")
    # If running under gunicorn, don't exit (app is for dashboard). But for worker run we exit.
    if __name__ == "__main__":
        raise SystemExit("Missing TELEGRAM_TOKEN")
    # else continue so Flask app still serves /ping

# -------------------------
# Flask App (for /ping)
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
# Dashboard event helper
# -------------------------
def send_dashboard_event(event_text: str, source: str = "bot"):
    """
    Best-effort send to configured dashboard endpoint.
    Non-blocking intention: short timeout and ignore failures.
    """
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
# Keep-alive (background)
# -------------------------
def _keep_alive_loop(ping_url: str, interval: int = 600):
    logger.info(f"Keep-alive thread started, pinging: {ping_url} every {interval}s")
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
# Plugin loader (modular)
# -------------------------
def try_import(module_name: str):
    try:
        mod = __import__(module_name, fromlist=["*"])
        logger.info(f"Loaded plugin: {module_name}")
        return mod
    except Exception as e:
        logger.warning(f"Plugin load failed ({module_name}): {e}")
        return None

# expected plugin names (put your code in plugins/)
plugins = {
    "price": try_import("plugins.price_tracker"),
    "tokeninfo": try_import("plugins.tokeninfo"),
    "airdrop": try_import("plugins.airdrop_check"),
    "meme": try_import("plugins.meme_ai"),
    "ai": try_import("plugins.ai_auto_reply"),
    "aianalyze": try_import("plugins.aianalyze"),
    "memory": try_import("plugins.memory_ai"),
    "admin": try_import("plugins.admin_panel"),
    "system": try_import("plugins.system_monitor"),
    "web3": try_import("plugins.web3_connect"),
}

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

# safe_call decorator logs exceptions and notifies user
def safe_call(fn):
    def wrapper(update: Update, context: CallbackContext):
        try:
            logger.debug(f"Handling {fn.__name__} from {update.effective_user.id}")
            res = fn(update, context)
            # send dashboard event
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
        "💰 /price — Check WENBNB or other token price\n"
        "🔍 /tokeninfo — Token analytics & supply\n"
        "🎁 /airdropcheck <wallet> — Verify airdrop eligibility\n"
        "😂 /meme — AI meme generator\n"
        "📈 /aianalyze — AI market insight\n"
        "🎮 /giveaway_start | /giveaway_end — Admin only\n"
        "⚙️ /system — System monitor\n"
        "🧩 /about — About this bot\n\n"
        f"{BRAND_SIGNATURE}"
    )
    update.message.reply_text(text, parse_mode=ParseMode.HTML)
    send_dashboard_event("Help requested", source="bot")

@safe_call
def about_cmd(update: Update, context: CallbackContext):
    text = (
        f"🌐 <b>About WENBNB</b>\n\n"
        "Hybrid AI + Web3 assistant. Built for memes, markets, and community.\n\n"
        f"{BRAND_SIGNATURE}"
    )
    update.message.reply_text(text, parse_mode=ParseMode.HTML)
    send_dashboard_event("About requested", source="bot")

# plugin delegations
@safe_call
def price_cmd(update: Update, context: CallbackContext):
    if plugins["price"] and hasattr(plugins["price"], "price_cmd"):
        return plugins["price"].price_cmd(update, context)
    update.message.reply_text("💰 Price plugin missing or failed to load.")

@safe_call
def tokeninfo_cmd(update: Update, context: CallbackContext):
    if plugins["tokeninfo"] and hasattr(plugins["tokeninfo"], "tokeninfo_cmd"):
        return plugins["tokeninfo"].tokeninfo_cmd(update, context)
    update.message.reply_text("🔍 Token info plugin missing.")

@safe_call
def airdrop_cmd(update: Update, context: CallbackContext):
    if plugins["airdrop"] and hasattr(plugins["airdrop"], "airdrop_cmd"):
        return plugins["airdrop"].airdrop_cmd(update, context)
    update.message.reply_text("🎁 Airdrop plugin missing.")

@safe_call
def meme_cmd(update: Update, context: CallbackContext):
    if plugins["meme"] and hasattr(plugins["meme"], "meme_cmd"):
        return plugins["meme"].meme_cmd(update, context)
    update.message.reply_text("😂 Meme generator plugin missing.")

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

# Admin / giveaway
@safe_call
def giveaway_start_cmd(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_owner(user_id) and not is_admin(user_id):
        update.message.reply_text("❌ Admin only.")
        return
    if plugins["admin"] and hasattr(plugins["admin"], "giveaway_start"):
        send_dashboard_event("Giveaway started (admin)", source="admin")
        return plugins["admin"].giveaway_start(update, context)
    update.message.reply_text("❌ Giveaway admin plugin missing.")

@safe_call
def giveaway_end_cmd(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_owner(user_id) and not is_admin(user_id):
        update.message.reply_text("❌ Admin only.")
        return
    if plugins["admin"] and hasattr(plugins["admin"], "giveaway_end"):
        send_dashboard_event("Giveaway ended (admin)", source="admin")
        return plugins["admin"].giveaway_end(update, context)
    update.message.reply_text("❌ Giveaway admin plugin missing.")

# AI-auto-reply for general text messages
@safe_call
def ai_auto_reply(update: Update, context: CallbackContext):
    # If we have AI plugin, delegate
    if plugins["ai"] and hasattr(plugins["ai"], "ai_auto_reply"):
        return plugins["ai"].ai_auto_reply(update, context)
    # fallback: simple context-aware echo with brand
    incoming = (update.message.text or "").strip()
    if not incoming:
        return
    reply = f"💬 You said: {incoming}\n\n{BRAND_SIGNATURE}"
    update.message.reply_text(reply)

# -------------------------
# Startup / Runner
# -------------------------
def _start_bot():
    """Initialize and run the telegram bot polling loop. Called in __main__ worker mode."""
    logger.info("Initializing Telegram Updater...")
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Register handlers
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    dp.add_handler(CommandHandler("price", price_cmd))
    dp.add_handler(CommandHandler("tokeninfo", tokeninfo_cmd))
    dp.add_handler(CommandHandler("airdropcheck", airdrop_cmd))
    dp.add_handler(CommandHandler("meme", meme_cmd))
    dp.add_handler(CommandHandler("aianalyze", aianalyze_cmd))
    dp.add_handler(CommandHandler("giveaway_start", giveaway_start_cmd))
    dp.add_handler(CommandHandler("giveaway_end", giveaway_end_cmd))
    dp.add_handler(CommandHandler("system", system_cmd))

    # catch-all AI text handler
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply))

    # Start polling
    updater.start_polling()
    logger.info("✅ Telegram bot polling started.")
    send_dashboard_event("Bot polling started", source="system")
    updater.idle()

# -------------------------
# Entry point
# -------------------------
def main():
    logger.info("WENBNB Neural Engine main() starting...")
    # Start keep-alive thread (if configured)
    start_keep_alive()

    # Optionally notify dashboard that startup happened
    send_dashboard_event("WENBNB Bot startup", source="system")

    # On normal run, we start the bot polling loop.
    # If this module is imported by gunicorn (to run Flask app), __main__ won't run.
    if __name__ == "__main__":
        # run bot in main thread (worker process)
        try:
            _start_bot()
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt caught - shutting down.")
        except Exception as e:
            logger.exception(f"Fatal error in bot: {e}")
            raise

# allow gunicorn to serve flask app variable named 'app'
# bot only starts when script executed directly (worker: python wenbot.py)
if __name__ == "__main__":
    main()
