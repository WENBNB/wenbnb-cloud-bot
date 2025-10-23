#!/usr/bin/env python3
# ============================================================
#  WENBNB Neural Engine v5.0 — AI Soul Integration Series
#  Core Framework v3.0  |  Hybrid AI + Web3 Command System
#  Developed by: WENBNB AI Labs
# ============================================================

import os
import logging
import threading
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

CORE_VERSION = "v3.0"
ENGINE_VERSION = "v5.0"
TAGLINE = (
    f"🤖 Powered by WENBNB Neural Engine {ENGINE_VERSION} — "
    f"Core Framework {CORE_VERSION} | AI + Web3 Intelligence 24×7"
)

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
            return fn(update, context)
        except Exception as e:
            logger.error(f"Error in {fn.__name__}: {e}")
            update.message.reply_text("⚠️ Internal Neural Error. Try again later.")
    return wrap

# ---------------- Core Commands ----------------
@safe_call
def start(update, context):
    user = update.effective_user.first_name or "friend"
    text = (
        f"👋 Hello {user}!\n\n"
        f"Welcome to <b>WENBNB Neural Engine {ENGINE_VERSION}</b> — "
        "your AI + Web3 assistant.\n\n"
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

@safe_call
def help(update, context):
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

@safe_call
def about(update, context):
    text = (
        f"🌐 <b>About WENBNB AI Bot</b>\n\n"
        "Seamless fusion of Neural AI + Web3 automation.\n"
        "Deployed on Cloud Render — connected 24×7.\n\n"
        f"{TAGLINE}"
    )
    update.message.reply_text(text, parse_mode=ParseMode.HTML)

# ---------------- Plugin Commands ----------------
@safe_call
def price(update, context):
    if plugins["price"] and hasattr(plugins["price"], "price_cmd"):
        return plugins["price"].price_cmd(update, context)
    update.message.reply_text("💰 Price plugin unavailable.")

@safe_call
def tokeninfo(update, context):
    if plugins["tokeninfo"] and hasattr(plugins["tokeninfo"], "tokeninfo_cmd"):
        return plugins["tokeninfo"].tokeninfo_cmd(update, context)
    update.message.reply_text("⚠️ Token info unavailable.")

@safe_call
def airdrop(update, context):
    if plugins["airdrop"] and hasattr(plugins["airdrop"], "airdrop_cmd"):
        return plugins["airdrop"].airdrop_cmd(update, context)
    update.message.reply_text("🎁 Airdrop checker unavailable.")

@safe_call
def meme(update, context):
    if plugins["meme"] and hasattr(plugins["meme"], "meme_cmd"):
        return plugins["meme"].meme_cmd(update, context)
    update.message.reply_text("😂 Meme generator missing.")

@safe_call
def analyze(update, context):
    if plugins["aianalyze"] and hasattr(plugins["aianalyze"], "aianalyze_cmd"):
        return plugins["aianalyze"].aianalyze_cmd(update, context)
    update.message.reply_text("📈 AI analyzer offline.")

@safe_call
def admin_giveaway_start(update, context):
    if plugins["admin"] and hasattr(plugins["admin"], "giveaway_start"):
        return plugins["admin"].giveaway_start(update, context)
    update.message.reply_text("❌ Admin panel not active.")

@safe_call
def admin_giveaway_end(update, context):
    if plugins["admin"] and hasattr(plugins["admin"], "giveaway_end"):
        return plugins["admin"].giveaway_end(update, context)
    update.message.reply_text("❌ Admin panel not active.")

@safe_call
def system_status(update, context):
    if plugins["system"] and hasattr(plugins["system"], "system_status"):
        return plugins["system"].system_status(update, context)
    update.message.reply_text("⚙️ System monitor not loaded.")

@safe_call
def ai_auto_reply(update, context):
    msg = update.message.text
    if plugins["ai"] and hasattr(plugins["ai"], "ai_auto_reply"):
        return plugins["ai"].ai_auto_reply(update, context)
    update.message.reply_text(f"💬 {msg}\n\n{TAGLINE}")

# ---------------- Flask Health ----------------
flask_app = Flask(__name__)
@flask_app.route("/ping")
def ping():
    return jsonify({"status": "ok", "engine": ENGINE_VERSION, "core": CORE_VERSION})

def run_flask():
    flask_app.run(host="0.0.0.0", port=APP_PORT, debug=False)

# ---------------- Main ----------------
def main():
    logger.info(f"🚀 Starting WENBNB Bot — Engine {ENGINE_VERSION} | Core {CORE_VERSION}")
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("tokeninfo", tokeninfo))
    dp.add_handler(CommandHandler("airdropcheck", airdrop))
    dp.add_handler(CommandHandler("meme", meme))
    dp.add_handler(CommandHandler("aianalyze", analyze))
    dp.add_handler(CommandHandler("giveaway_start", admin_giveaway_start))
    dp.add_handler(CommandHandler("giveaway_end", admin_giveaway_end))
    dp.add_handler(CommandHandler("system", system_status))

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply))

    threading.Thread(target=run_flask, daemon=True).start()
    updater.start_polling()
    logger.info("✅ WENBNB Neural Bot is now online and operational 24×7")
    updater.idle()

if __name__ == "__main__":
    main()
