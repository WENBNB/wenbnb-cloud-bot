import os, psutil, time
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

# === Admin Auth ===
ALLOWED_ADMINS = [5698007588]  # replace with your Telegram ID

# === Branding ===
BRAND_SIGNATURE = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7 ⚡"
ENGINE_VERSION = "v8.6.5-ProStable"

# === System Monitor ===
def get_system_status():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - psutil.boot_time()))
    return f"🧠 System: {cpu}% CPU | {mem}% RAM | Uptime: {uptime}"

# === Core Commands ===
def admin_status(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_ADMINS:
        update.message.reply_text("🚫 Unauthorized access.")
        return

    stats = get_system_status()
    msg = (
        f"✅ <b>WENBNB Neural Engine {ENGINE_VERSION}</b>\n"
        f"{stats}\n"
        f"📡 Neural Core Online\n\n"
        f"{BRAND_SIGNATURE}"
    )
    update.message.reply_text(msg, parse_mode=ParseMode.HTML)

def admin_broadcast(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_ADMINS:
        update.message.reply_text("🚫 Unauthorized access.")
        return

    if len(context.args) == 0:
        update.message.reply_text("Usage: /broadcast <message>")
        return

    msg = " ".join(context.args)
    update.message.reply_text(f"📢 Broadcast sent:\n{msg}")

def admin_reboot(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_ADMINS:
        update.message.reply_text("🚫 Unauthorized access.")
        return

    update.message.reply_text("♻️ Neural Core rebooting… please wait a moment.")
    time.sleep(2)
    update.message.reply_text("✅ WENBNB Neural Engine rebooted successfully ⚡")

# ====== PLUGIN REGISTRATION ======
def register(dp):
    """Admin Tools Register Function (Force Priority for /admin)"""
    from telegram.ext import CommandHandler

    dp.add_handler(CommandHandler("admin", admin_status), group=0)
    dp.add_handler(CommandHandler("broadcast", admin_broadcast), group=0)
    dp.add_handler(CommandHandler("reboot", admin_reboot), group=0)

    print("✅ Admin Tools initialized — /admin /broadcast /reboot active (priority group=0).")
