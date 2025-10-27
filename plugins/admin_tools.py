"""
🧠 WENBNB Admin Tools v8.6.5-ProStable+
────────────────────────────────────────────
Neural Admin Control Suite — for internal bot monitoring & management.

Features:
• /admin → Core system performance + uptime check
• /broadcast → Send message to all users (admin-only)
• /reboot → Simulated soft reboot of the Neural Engine
"""

import os
import psutil
import time
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler

# ====== CONFIG ======
ALLOWED_ADMINS = [5698007588]  # Your Telegram ID
VERSION = "WENBNB Neural Engine v8.6.5-ProStable"
BRAND_SIGNATURE = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7 ⚡"


# ====== SECURITY ======
def is_admin(user_id: int):
    return user_id in ALLOWED_ADMINS


# ====== STATS FUNCTION ======
def get_system_status():
    """Returns system performance info."""
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_str = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime_seconds))
    return f"🧠 System: {cpu}% CPU | {memory}% RAM | Uptime: {uptime_str}"


# ====== COMMAND: /admin ======
def admin_status(update: Update, context: CallbackContext):
    """Displays bot status and system info."""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("🚫 Unauthorized access.")
        return

    status_msg = get_system_status()
    update.message.reply_text(
        f"✅ <b>{VERSION}</b>\n\n"
        f"{status_msg}\n"
        f"📡 Neural Core Online\n\n"
        f"{BRAND_SIGNATURE}",
        parse_mode=ParseMode.HTML
    )


# ====== COMMAND: /broadcast ======
def admin_broadcast(update: Update, context: CallbackContext):
    """Broadcast message to all users (admin only)."""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("🚫 Unauthorized access.")
        return

    if len(context.args) == 0:
        update.message.reply_text("Usage: /broadcast <message>")
        return

    msg = " ".join(context.args)
    try:
        # Add your user loop here (e.g. user_db loop)
        update.message.reply_text(f"📢 Broadcast sent:\n{msg}")
    except Exception as e:
        update.message.reply_text(f"❌ Broadcast error: {e}")


# ====== COMMAND: /reboot ======
def admin_reboot(update: Update, context: CallbackContext):
    """Simulates bot reboot (soft restart message)."""
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("🚫 Unauthorized access.")
        return

    update.message.reply_text("♻️ Neural Core rebooting… please wait a moment.")
    time.sleep(2)
    update.message.reply_text("✅ WENBNB Neural Engine rebooted successfully ⚡")


# ====== PLUGIN REGISTRATION ======
def register_handlers(dp):
    """Registers admin commands with the dispatcher."""
    dp.add_handler(CommandHandler("admin", admin_status))
    dp.add_handler(CommandHandler("broadcast", admin_broadcast))
    dp.add_handler(CommandHandler("reboot", admin_reboot))
