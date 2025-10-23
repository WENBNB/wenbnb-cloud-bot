#!/usr/bin/env python3
# ============================================================
#  WENBNB Neural Engine v5.5 — Full Core + Dashboard Integration
#  Core Framework v3.0  |  Hybrid AI + Web3 Command System
#  Developed by: WENBNB AI Labs
# ============================================================

import os
import logging
import threading
import time
import requests
from flask import Flask, jsonify
from telegram import Update, ParseMode, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ---------------- Logging ----------------
logging.basicConfig(format='%(asctime)s | %(levelname)s | %(message)s', level=logging.INFO)
logger = logging.getLogger("WENBNB")

# ---------------- Environment ----------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BSCSCAN_KEY = os.getenv("BSCSCAN_KEY")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
APP_PORT = int(os.getenv("PORT", "10000"))

# Dashboard integration (optional)
DASHBOARD_URL = os.getenv("DASHBOARD_URL")         # e.g. https://wenbnb-dashboard.onrender.com
DASHBOARD_KEY = os.getenv("DASHBOARD_KEY", "")     # optional secret if dashboard protected

CORE_VERSION = "v3.0"
ENGINE_VERSION = "v5.5"
TAGLINE = (
    f"🤖 Powered by WENBNB Neural Engine {ENGINE_VERSION} — "
    f"Core Framework {CORE_VERSION} | AI + Web3 Intelligence 24×7"
)

# ---------------- Helper: Dashboard Event Sender ----------------
def send_dashboard_event(event_text: str, source: str = "bot"):
    """
    Post an event to the Dashboard /update_activity endpoint.
    This is lightweight and best-effort (non-blocking ideally).
    """
    if not DASHBOARD_URL:
        return False
    try:
        url = DASHBOARD_URL.rstrip("/") + "/update_activity"
        headers = {"Content-Type": "application/json"}
        if DASHBOARD_KEY:
            headers["X-DASH-KEY"] = DASHBOARD_KEY
        payload = {"event": event_text, "source": source}
        # non-blocking approach: short timeout
        requests.post(url, json=payload, headers=headers, timeout=3)
        return True
    except Exception as e:
        logger.debug(f"Dashboard event failed: {e}")
        return False

# ---------------- Plugin Loader ----------------
def try_import(module_name):
    try:
        module = __import__(module_name, fromlist=["*"])
        logger.info(f"✅ Loaded module: {module_name}")
        return module
    except Exception as e:
        logger.warning(f"⚠️  Failed to load {module_name}: {e}")
        return None

plugins = {
    "price":        try_import("plugins.price_tracker"),
    "tokeninfo":    try_import("plugins.tokeninfo"),
    "airdrop":      try_import("plugins.airdrop_check"),
    "meme":         try_import("plugins.meme_ai"),
    "ai":           try_import("plugins.ai_auto_reply"),
    "aianalyze":    try_import("plugins.aianalyze"),
    "memory":       try_import("plugins.memory_ai"),
    "admin":        try_import("plugins.admin_panel"),
    "dashboard":    try_import("dashboard.r2_dashboard_sync"),
    "system":       try_import("plugins.system_monitor"),
    "web3":         try_import("plugins.web3_connect"),
}

# ---------------- Helper Decorator ----------------
def safe_call(fn):
    def wrap(update: Update, context: CallbackContext):
        try:
            logger.debug(f"Handling {fn.__name__} for user {update.effective_user.id}")
            result = fn(update, context)
            # log the command to dashboard
            try:
                cmd_name = "/" + fn.__name__ if not fn.__name__.startswith("admin_") else fn.__name__
                send_dashboard_event(f"{cmd_name} used by @{update.effective_user.username or update.effective_user.id}")
            except Exception:
                pass
            return result
        except Exception as e:
            logger.exception(f"Error in {fn.__name__}: {e}")
            try:
                update.message.reply_text("⚠️ Internal Neural Error. Try again later.")
            except Exception:
                pass
    return wrap

# ---------------- Core Commands ----------------
@safe_call
def start(update, context):
    user = (update.effective_user.first_name or update.effective_user.username or "friend")
    text = (
        f"👋 Hello {user}!\n\n"
        f"Welcome to <b>WENBNB Neural Engine {ENGINE_VERSION}</b> — your AI + Web3 assistant.\n\n"
        "Use /menu or the buttons below to begin:\n\n"
        f"{TAGLINE}"
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
def help_cmd(update, context):
    text = (
        "🧠 <b>WENBNB Bot Command Center</b>\n\n"
        "💰 /price — Check WENBNB or any token price\n"
        "🔍 /tokeninfo — Token details & analytics\n"
        "🎁 /airdropcheck <wallet> — Check airdrop eligibility\n"
        "😂 /meme — Generate AI meme\n"
        "📊 /aianalyze — Market AI insights\n"
        "🧬 /memory — View or reset AI memory\n"
        "🎮 /giveaway_start | /giveaway_end — Admin controls\n"
        "⚙️ /system — System monitor\n\n"
        f"{TAGLINE}"
    )
    update.message.reply_text(text, parse_mode=ParseMode.HTML)
    send_dashboard_event("Help requested", source="bot")

@safe_call
def about(update, context):
    text = (
        f"🌐 <b>About WENBNB AI Bot</b>\n\n"
        "Seamless fusion of Neural AI + Web3 automation.\n"
        "Connected 24×7 — built for meme-lovers and degens alike.\n\n"
        f"{TAGLINE}"
    )
    update.message.reply_text(text, parse_mode=ParseMode.HTML)
    send_dashboard_event("About requested", source="bot")

# ---------------- Plugin Commands ----------------
@safe_call
def price(update, context):
    # Example usage: /price wenbnb or /price 0x... or /price BNB
    if plugins["price"] and hasattr(plugins["price"], "price_cmd"):
        send_dashboard_event("Price command executed", source="bot")
        return plugins["price"].price_cmd(update, context)
    update.message.reply_text("💰 Price plugin unavailable.")

@safe_call
def tokeninfo(update, context):
    if plugins["tokeninfo"] and hasattr(plugins["tokeninfo"], "tokeninfo_cmd"):
        send_dashboard_event("Tokeninfo requested", source="bot")
        return plugins["tokeninfo"].tokeninfo_cmd(update, context)
    update.message.reply_text("⚠️ Token info unavailable.")

@safe_call
def airdropcheck(update, context):
    if plugins["airdrop"] and hasattr(plugins["airdrop"], "airdrop_cmd"):
        send_dashboard_event("Airdropcheck requested", source="bot")
        return plugins["airdrop"].airdrop_cmd(update, context)
    update.message.reply_text("🎁 Airdrop checker unavailable.")

@safe_call
def meme(update, context):
    if plugins["meme"] and hasattr(plugins["meme"], "meme_cmd"):
        send_dashboard_event("Meme command used", source="bot")
        return plugins["meme"].meme_cmd(update, context)
    update.message.reply_text("😂 Meme generator missing.")

@safe_call
def analyze(update, context):
    if plugins["aianalyze"] and hasattr(plugins["aianalyze"], "aianalyze_cmd"):
        send_dashboard_event("AI Analyze run", source="bot")
        return plugins["aianalyze"].aianalyze_cmd(update, context)
    update.message.reply_text("📈 AI analyzer offline.")

@safe_call
def admin_giveaway_start(update, context):
    # Admin-only check
    user_id = str(update.effective_user.id)
    if ADMIN_CHAT_ID and user_id != ADMIN_CHAT_ID and str(update.effective_user.id) != str(ADMIN_CHAT_ID):
        update.message.reply_text("❌ Admin only.")
        return
    if plugins["admin"] and hasattr(plugins["admin"], "giveaway_start"):
        send_dashboard_event("Giveaway started (admin)", source="admin")
        return plugins["admin"].giveaway_start(update, context)
    update.message.reply_text("❌ Admin command unavailable.")

@safe_call
def admin_giveaway_end(update, context):
    user_id = str(update.effective_user.id)
    if ADMIN_CHAT_ID and user_id != ADMIN_CHAT_ID and str(update.effective_user.id) != str(ADMIN_CHAT_ID):
        update.message.reply_text("❌ Admin only.")
        return
    if plugins["admin"] and hasattr(plugins["admin"], "giveaway_end"):
        send_dashboard_event("Giveaway ended (admin)", source="admin")
        return plugins["admin"].giveaway_end(update, context)
    update.message.reply_text("❌ Admin command unavailable.")

@safe_call
def system_status(update, context):
    if plugins["system"] and hasattr(plugins["system"], "system_status"):
        send_dashboard_event("System status requested", source="bot")
        return plugins["system"].system_status(update, context)
    update.message.reply_text("⚙️ System monitor not loaded.")

@safe_call
def ai_auto_reply(update, context):
    # This handles non-command text messages and attempts AI reply via plugin
    msg = update.message.text or ""
    if plugins["ai"] and hasattr(plugins["ai"], "ai_auto_reply"):
        # plugin should return True/False or send reply itself
        try:
            send_dashboard_event(f"AI auto-reply triggered by @{update.effective_user.username or update.effective_user.id}", source="bot")
        except Exception:
            pass
        return plugins["ai"].ai_auto_reply(update, context)
    # fallback simple echo with tagline
    update.message.reply_text(f"💬 {msg}\n\n{TAGLINE}")
    send_dashboard_event("Fallback echo reply sent", source="bot")

# ---------------- Flask Health ----------------
flask_app = Flask(__name__)
@flask_app.route("/ping")
def ping():
    return jsonify({"status": "ok", "engine": ENGINE_VERSION, "core": CORE_VERSION, "time": int(time.time())})

def run_flask():
    # Run flask (Render will use gunicorn for web; this thread ensures /ping available for worker mode)
    flask_app.run(host="0.0.0.0", port=APP_PORT, debug=False)

# ---------------- Startup Event ----------------
def notify_startup():
    send_dashboard_event("WENBNB Bot started", source="system")
    logger.info("Sent startup event to dashboard (if configured)")

# ---------------- Main ----------------
def main():
    logger.info(f"🚀 Starting WENBNB Bot — Engine {ENGINE_VERSION} | Core {CORE_VERSION}")

    # Basic env checks
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN missing in environment. Exiting.")
        return

    # Start Flask in background thread (so health endpoint available)
    threading.Thread(target=run_flask, daemon=True).start()
    # Small delay to let flask start
    time.sleep(0.5)
    notify_startup()

    # Telegram updater
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("tokeninfo", tokeninfo))
    dp.add_handler(CommandHandler("airdropcheck", airdropcheck))
    dp.add_handler(CommandHandler("meme", meme))
    dp.add_handler(CommandHandler("aianalyze", analyze))
    dp.add_handler(CommandHandler("giveaway_start", admin_giveaway_start))
    dp.add_handler(CommandHandler("giveaway_end", admin_giveaway_end))
    dp.add_handler(CommandHandler("system", system_status))

    # AI auto reply for plain messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply))

    # Start polling
    updater.start_polling()
    logger.info("✅ WENBNB Neural Bot is now online and operational 24×7")
    updater.idle()

if __name__ == "__main__":
    main()
