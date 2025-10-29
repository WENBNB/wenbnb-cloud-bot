#!/usr/bin/env python3
# ============================================================
# 💫 WENBNB Neural Engine v8.9.8 — CleanSlate Command Mode
# ============================================================

import os, sys, time, logging, threading, traceback, requests
from flask import Flask, jsonify
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ===========================
# ⚙️ Engine Info
# ===========================
ENGINE_VERSION = "v8.9.8–CleanSlate Command Mode"
CORE_VERSION = "v5.3"
BRAND_SIGNATURE = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7 ⚡"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
    stream=sys.stdout,
)
logger = logging.getLogger("WENBNB")

# ===========================
# 🔐 ENV
# ===========================
TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_APP_URL = os.getenv("RENDER_APP_URL", "")
if not TOKEN:
    raise SystemExit("❌ TELEGRAM_TOKEN not found")

# ===========================
# 🌐 Keep Alive
# ===========================
app = Flask(__name__)

@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "engine": ENGINE_VERSION, "core": CORE_VERSION})

def keep_alive_loop():
    while True:
        try:
            if RENDER_APP_URL:
                requests.get(RENDER_APP_URL, timeout=8)
                logger.info("💓 KeepAlive Ping OK")
        except Exception as e:
            logger.warning(f"KeepAlive error: {e}")
        time.sleep(600)

def start_keep_alive():
    if RENDER_APP_URL:
        threading.Thread(target=keep_alive_loop, daemon=True).start()

# ===========================
# 🧩 Plugin Imports
# ===========================
from plugins import (
    plugin_manager,
    price, tokeninfo, meme, aianalyze,
    airdropcheck, airdropalert, web3, admin_tools, ai_auto_reply
)

# ===========================
# 🚀 Bot Setup
# ===========================
def start_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    plugin_manager.load_all_plugins(dp)

    # --- /start ---
    def start_cmd(update: Update, context: CallbackContext):
        user = update.effective_user.first_name or "friend"
        text = (
            f"👋 Hey <b>{user}</b>!\n\n"
            f"✨ Neural Core synced and online.\n"
            f"⚡ Running <b>{ENGINE_VERSION}</b> in ProStable Mode.\n\n"
            f"Use slash commands below:\n"
            f"/price — Check BNB price\n"
            f"/tokeninfo — Token details\n"
            f"/meme — Generate fun memes\n"
            f"/aianalyze — AI text insight\n"
            f"/airdropcheck — Airdrop status\n"
            f"/web3 — Web3 tools\n"
            f"/about — About this engine\n\n"
            f"{BRAND_SIGNATURE}"
        )
        update.message.reply_text(text, parse_mode=ParseMode.HTML)

    # --- /about ---
    def about_cmd(update: Update, context: CallbackContext):
        text = (
            f"🌐 <b>About WENBNB</b>\n\n"
            f"Hybrid AI + Web3 Neural Engine.\n"
            f"Currently running <b>{ENGINE_VERSION}</b>.\n\n"
            f"{BRAND_SIGNATURE}"
        )
        update.message.reply_text(text, parse_mode=ParseMode.HTML)

    # === Register Commands ===
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    dp.add_handler(CommandHandler("price", price.price_cmd))
    dp.add_handler(CommandHandler("tokeninfo", tokeninfo.tokeninfo_cmd))
    dp.add_handler(CommandHandler("meme", meme.meme_cmd))
    dp.add_handler(CommandHandler("aianalyze", aianalyze.aianalyze_cmd))
    dp.add_handler(CommandHandler("airdropcheck", airdropcheck.airdropcheck_cmd))
    dp.add_handler(CommandHandler("airdropalert", airdropalert.airdropalert_cmd))
    dp.add_handler(CommandHandler("web3", web3.web3_cmd))

    # --- Admin ---
    dp.add_handler(CommandHandler("admin", lambda u, c: admin_tools.admin_status(u, c, {
        "version": ENGINE_VERSION,
        "branding": {"footer": BRAND_SIGNATURE},
        "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
    })))
    dp.add_handler(CommandHandler("reboot", lambda u, c: admin_tools.admin_reboot(u, c, {
        "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
    })))

    # --- AI auto-chat (for casual text) ---
    def safe_ai_auto(update: Update, context: CallbackContext):
        try:
            text = update.message.text.strip()
            if text.startswith("/"):  # skip slash commands
                return
            ai_auto_reply.ai_auto_chat(update, context)
        except Exception as e:
            logger.error(f"AI auto error: {e}")
            traceback.print_exc()

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, safe_ai_auto))

    # --- Start Bot ---
    logger.info(f"🚀 Launching WENBNB Neural Engine {ENGINE_VERSION}")
    updater.start_polling(clean=True)
    updater.idle()

# ===========================
# 🧠 Main
# ===========================
def main():
    start_keep_alive()
    start_bot()

if __name__ == "__main__":
    main()
