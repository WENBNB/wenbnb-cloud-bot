#!/usr/bin/env python3
# ============================================================
# 💫 WENBNB Neural Engine v8.8.3-ChatKeyboardStable
# Real Chat Keyboard • Fixed Button → Command trigger • Clean Start
# ============================================================

import os, sys, time, logging, threading, requests, traceback
from flask import Flask, jsonify
from telegram import Update, ParseMode, ReplyKeyboardMarkup, Message
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)

# ===========================
# ⚙️ Engine & Branding
# ===========================
ENGINE_VERSION = "v8.8.3-ChatKeyboardStable"
CORE_VERSION = "v5.3"
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
# 🧠 Core Plugin Imports
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

    # Clear handlers early to avoid stale keyboards/handlers collisions
    dp.handlers.clear()
    logger.info("🧹 Old handlers cleared to prevent keyboard conflicts")

    register_all_plugins(dp)
    logger.info("🧠 Plugins loaded successfully.")

    # --- Chat Keyboard layout (real keyboard buttons)
    keyboard = [
        ["💰 Price", "📊 Token Info"],
        ["😂 Meme", "🧠 AI Analyze"],
        ["🎁 Airdrop Check", "🚨 Airdrop Alert"],
        ["🌐 Web3", "ℹ️ About", "⚙️ Admin"]
    ]

    # Map the visible label -> command name (without leading slash)
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

    # === /start Command (no extra loading message)
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

    # === Button Handler — reliable (search across all handler groups and call handler)
    def button_handler(update: Update, context: CallbackContext):
        label = (update.message.text or "").strip()
        cmd_name = button_map.get(label)
        if not cmd_name:
            # ignore unknown labels (user may type text)
            return

        try:
            logger.info(f"⚡ Chat keyboard pressed: {label} → /{cmd_name}")

            # Find the CommandHandler for the command across all handler groups
            found_handler = None
            for group_key, handlers in getattr(dp, "handlers", {}).items():
                for h in handlers:
                    if isinstance(h, CommandHandler) and h.command:
                        # CommandHandler.command may be list or tuple
                        handler_cmd = h.command[0] if isinstance(h.command, (list, tuple)) else h.command
                        if handler_cmd == cmd_name:
                            found_handler = h
                            break
                if found_handler:
                    break

            if not found_handler:
                # fallback: maybe plugin registered as function in plugin_manager; respond politely
                logger.warning(f"No active handler for /{cmd_name}")
                update.message.reply_text("🤖 That module isn't active right now.")
                return

            # Set update.message.text to the command (so handler code sees it if it inspects message.text)
            original_text = update.message.text
            update.message.text = f"/{cmd_name}"

            # Call the handler callback directly - this runs the command handler logic
            # Handler callback signature is usually (update, context)
            try:
                found_handler.callback(update, context)
            finally:
                # restore original text to avoid side-effects
                update.message.text = original_text

        except Exception as e:
            logger.exception(f"❌ Error triggering /{cmd_name}: {e}")
            try:
                update.message.reply_text(f"⚠️ Error running /{cmd_name}: {e}")
            except:
                pass

    # === /about Command
    def about_cmd(update: Update, context: CallbackContext):
        text = (
            f"🌐 <b>About WENBNB</b>\n\n"
            f"Hybrid AI + Web3 Neural Assistant — blending emotion with precision.\n"
            f"Currently running <b>WENBNB Neural Engine {ENGINE_VERSION}</b>.\n\n"
            f"💫 Always learning, always adapting.\n\n"
            f"{BRAND_SIGNATURE}"
        )
        update.message.reply_text(text, parse_mode=ParseMode.HTML)

    # Register core handlers
    dp.add_handler(CommandHandler("start", start_cmd))
    dp.add_handler(CommandHandler("about", about_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, button_handler))

    # === AI + Admin Integration (plugin-provided handlers)
    try:
        dp.add_handler(CommandHandler("aianalyze", aianalyze.aianalyze_cmd))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply.ai_auto_chat))
        dp.add_handler(CommandHandler("admin", lambda u, c: admin_tools.admin_status(u, c, {
            "version": ENGINE_VERSION,
            "branding": {"footer": BRAND_SIGNATURE},
            "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
        })))
        dp.add_handler(CommandHandler("reboot", lambda u, c: admin_tools.admin_reboot(u, c, {
            "admin": {"allowed_admins": [int(os.getenv("OWNER_ID", "0"))]}
        })))
        logger.info("💬 EmotionSync + AI Analyzer + Admin tools active")
    except Exception as e:
        logger.warning(f"⚠️ Analyzer/Admin module load failed: {e}")
        traceback.print_exc()

    # === Heartbeat Thread ===
    def heartbeat():
        while True:
            time.sleep(30)
            try:
                if RENDER_APP_URL:
                    requests.get(f"{RENDER_APP_URL}/ping", timeout=5)
                logger.info("💓 Poll heartbeat alive")
            except:
                logger.warning("⚠️ Poll heartbeat missed — restarting poller.")
                release_instance_lock()
                os._exit(1)

    threading.Thread(target=heartbeat, daemon=True).start()

    # === Start polling
    try:
        logger.info("🚀 Starting Telegram polling (ChatKeyboardStable)...")
        updater.start_polling(clean=True)
        updater.idle()
    except Exception as e:
        if "Conflict" in str(e):
            logger.warning("⚠️ Conflict detected — restarting...")
            release_instance_lock()
            os._exit(1)
        else:
            failure_count += 1
            logger.error(f"❌ Polling crash ({failure_count}): {e}")
            if failure_count >= 3:
                logger.error("💥 Too many failures → Full reboot.")
                release_instance_lock()
                os._exit(1)
            else:
                logger.info("🔁 Attempting recovery...")
                time.sleep(5)
                start_bot()

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
        release_instance_lock()

if __name__ == "__main__":
    main()
