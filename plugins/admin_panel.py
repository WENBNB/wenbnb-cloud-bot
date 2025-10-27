import os, psutil, time
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler

ALLOWED_ADMINS = [5698007588]
ENGINE_VERSION = "v8.6.5-ProStable"
BRAND_SIGNATURE = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7 ⚡"

def get_system_status():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    uptime = time.time() - psutil.boot_time()
    uptime_str = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime))
    return f"🧠 System: {cpu}% CPU | {mem}% RAM | Uptime: {uptime_str}"

def admin_status(update: Update, context: CallbackContext):
    if update.effective_user.id not in ALLOWED_ADMINS:
        return update.message.reply_text("🚫 Unauthorized access.")
    stats = get_system_status()
    msg = (
        f"✅ <b>WENBNB Neural Engine {ENGINE_VERSION}</b>\n"
        f"{stats}\n📡 Neural Core Online\n\n{BRAND_SIGNATURE}"
    )
    update.message.reply_text(msg, parse_mode=ParseMode.HTML)

def admin_reboot(update: Update, context: CallbackContext):
    if update.effective_user.id not in ALLOWED_ADMINS:
        return update.message.reply_text("🚫 Unauthorized access.")
    update.message.reply_text("♻️ Rebooting Neural Core...")
    time.sleep(1)
    os._exit(0)

def admin_broadcast(update: Update, context: CallbackContext):
    if update.effective_user.id not in ALLOWED_ADMINS:
        return update.message.reply_text("🚫 Unauthorized access.")
    if not context.args:
        return update.message.reply_text("Usage: /broadcast <message>")
    msg = " ".join(context.args)
    update.message.reply_text(f"📢 Broadcast message queued:\n{msg}")

def register(dp):
    dp.add_handler(CommandHandler("admin", admin_status), group=-1)
    dp.add_handler(CommandHandler("broadcast", admin_broadcast), group=-1)
    dp.add_handler(CommandHandler("reboot", admin_reboot), group=-1)
    print("✅ Admin Panel initialized — /admin /broadcast /reboot active.")
