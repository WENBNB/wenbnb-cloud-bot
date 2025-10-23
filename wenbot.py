# ==========================================
# 🤖 WENBNB Neural Engine v5.0 (Modular Core)
# Powered by WENBNB AI — Emotion Context Mode v4.1
# ==========================================

import os
import logging
import importlib
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, CallbackContext
)

# ------------------------------------------
# ✅ Logging Configuration
# ------------------------------------------
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ------------------------------------------
# 🚀 Flask Keep-Alive (Render Hosting)
# ------------------------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "🚀 WENBNB Neural Engine is active — AI Core Online."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# ------------------------------------------
# 🤖 Telegram Bot Setup
# ------------------------------------------
TOKEN = os.getenv("TELEGRAM_TOKEN") or "YOUR_TELEGRAM_BOT_TOKEN"
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

# ------------------------------------------
# 🌐 Dynamic Plugin Loader
# ------------------------------------------
PLUGIN_DIR = "plugins"

def load_plugins():
    """Auto-imports all plugin modules from /plugins directory"""
    for filename in os.listdir(PLUGIN_DIR):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            module = importlib.import_module(f"{PLUGIN_DIR}.{module_name}")
            if hasattr(module, "register_handlers"):
                module.register_handlers(dp)
                logger.info(f"✅ Loaded plugin: {module_name}")

# ------------------------------------------
# 💬 Core Commands
# ------------------------------------------

def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("💰 Price", callback_data="price"),
         InlineKeyboardButton("📊 Token Info", callback_data="tokeninfo")],
        [InlineKeyboardButton("🎁 Airdrop", callback_data="airdrop"),
         InlineKeyboardButton("😂 Meme AI", callback_data="meme")],
        [InlineKeyboardButton("🎉 Giveaway", callback_data="giveaway"),
         InlineKeyboardButton("🌐 Web3", callback_data="web3")],
        [InlineKeyboardButton("🧠 AI Chat", callback_data="aianalyze")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        "👋 Welcome to <b>WENBNB Neural Engine</b>!\n\n"
        "I’m your AI-powered assistant — ready to provide live crypto insights, memes, giveaways, and more.\n\n"
        "🚀 Powered by <b>WENBNB Neural Engine</b> — AI Core Intelligence 24×7",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

def help_command(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🧩 <b>Available Commands</b>\n\n"
        "🚀 /start - Launch the AI Assistant\n"
        "📈 /price - View live BNB + WENBNB price\n"
        "💰 /tokeninfo - Token stats & supply info\n"
        "🎁 /airdropcheck - Verify eligibility\n"
        "😂 /meme - AI Meme Generator\n"
        "🎉 /giveaway - Join active giveaways\n"
        "🌐 /web3 - Wallet & blockchain tools\n"
        "🧠 /aianalyze - Chat with Neural Engine\n"
        "💫 /about - Learn about WENBNB Ecosystem\n\n"
        "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7",
        parse_mode="HTML"
    )

def about(update: Update, context: CallbackContext):
    update.message.reply_text(
        "💫 <b>About WENBNB Ecosystem</b>\n\n"
        "WENBNB Neural Engine is an advanced AI-powered multi-utility bot designed for Web3, traders, and communities.\n"
        "It integrates live market data, airdrops, meme AI, giveaways, and blockchain tools — all through one smart interface.\n\n"
        "🚀 Powered by <b>WENBNB Neural Engine</b> — Emotion Context Mode v4.1",
        parse_mode="HTML"
    )

# ------------------------------------------
# 🔄 Callback Query (Buttons)
# ------------------------------------------
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "price":
        query.message.reply_text("📊 Fetching live prices... use /price command.")
    elif query.data == "tokeninfo":
        query.message.reply_text("💰 Checking token info... use /tokeninfo command.")
    elif query.data == "airdrop":
        query.message.reply_text("🎁 Airdrop verification running... use /airdropcheck.")
    elif query.data == "meme":
        query.message.reply_text("😂 Use /meme to generate your AI meme.")
    elif query.data == "giveaway":
        query.message.reply_text("🎉 Use /giveaway to view or start a contest.")
    elif query.data == "web3":
        query.message.reply_text("🌐 Access /web3 tools for wallet & chain data.")
    elif query.data == "aianalyze":
        query.message.reply_text("🧠 Use /aianalyze to chat directly with Neural Engine.")

# ------------------------------------------
# ⚙️ Register Core Handlers
# ------------------------------------------
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help_command))
dp.add_handler(CommandHandler("about", about))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.command, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.text, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.photo, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.video, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.document, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.status_update, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.all, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.caption, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.update, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.user, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.private, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.group, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.forwarded, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.entity, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.regex, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.via_bot, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.audio, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.voice, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.location, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.contact, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.poll, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.dice, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.sticker, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.video_note, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.animation, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.all, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.caption, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.command, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.text, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.update, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.user, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.chat, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.all, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.update, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.all, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.text, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.all, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.text, lambda u, c: None))
dp.add_handler(MessageHandler(Filters.all, lambda u, c: None))

# ------------------------------------------
# 🚀 Initialize
# ------------------------------------------
if __name__ == "__main__":
    logger.info("🚀 Starting WENBNB Neural Engine...")
    load_plugins()

    from threading import Thread
    Thread(target=run_flask).start()

    updater.start_polling()
    updater.idle()
