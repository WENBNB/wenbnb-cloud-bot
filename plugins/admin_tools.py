# ============================================================
# 🧠 WENBNB Neural Engine — Admin Tools v8.6.5-ProStable
# Provides Admin Panel access, broadcast, and reboot controls.
# Auto-registered through plugin_manager.
# ============================================================

import os
import psutil
import time
import json
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler

# -----------------------------
# Admin Check
# -----------------------------
def is_admin(user_id: int, allowed_admins: list) -> bool:
    """Check if user is authorized as admin"""
    return user_id in allowed_admins

# -----------------------------
# System Status
# -----------------------------
def get_system_status():
    """Returns system performance stats"""
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    uptime_seconds = time.time() - psutil.boot_time()
    hours, remainder = divmod(int(uptime_seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{hours}h {minutes}m {seconds}s"
    return f"🧠 System: {cpu}% CPU | {memory}% RAM | Uptime: {uptime}"

# -----------------------------
# Admin Status
# -----------------------------
def admin_status(update: Update, context: CallbackContext, config):
    """Show bot status and environment info"""
    user_id = update.effective_user.id
    if not is_admin(user_id, config["admin"]["allowed_admins"]):
        update.message.reply_text("🚫 Unauthorized Access — Admins only.")
        return

    status_msg = get_system_status()
    version = config.get("version", "Unknown")
    footer = config["branding"]["footer"]

    update.message.reply_text(
        f"✅ <b>WENBNB Neural Engine {version}</b>\n\n"
        f"{status_msg}\n"
        f"📡 Neural Core Online\n\n"
        f"{footer}",
        parse_mode=ParseMode.HTML
    )

# -----------------------------
# Broadcast Message
# -----------------------------
def admin_broadcast(update: Update, context: CallbackContext, config):
    """Broadcast message to all users (admin-only)"""
    user_id = update.effective_user.id
    if not is_admin(user_id, config["admin"]["allowed_admins"]):
        update.message.reply_text("🚫 Unauthorized Access — Admins only.")
        return

    if len(context.args) == 0:
        update.message.reply_text("Usage: /broadcast <message>")
        return

    msg = " ".join(context.args)
    try:
        # Add user list integration here later
        update.message.reply_text(f"📢 Broadcast sent:\n{msg}")
    except Exception as e:
        update.message.reply_text(f"❌ Error sending broadcast: {e}")

# -----------------------------
# Reboot Command
# -----------------------------
def admin_reboot(update: Update, context: CallbackContext, config):
    """Simulate bot reboot (soft restart message)"""
    user_id = update.effective_user.id
    if not is_admin(user_id, config["admin"]["allowed_admins"]):
        update.message.reply_text("🚫 Unauthorized Access — Admins only.")
        return

    update.message.reply_text("♻️ Neural Core rebooting… please wait.")
    time.sleep(2)
    update.message.reply_text("✅ WENBNB Neural Engine rebooted successfully ⚡")

# -----------------------------
# Plugin Auto-Registration
# -----------------------------
def register_handlers(dp, config=None):
    """Register /admin and /reboot commands when plugin_manager loads this file"""
    owner_id = int(os.getenv("OWNER_ID", "0"))
    dp.add_handler(CommandHandler("admin", lambda u, c: admin_status(u, c, {
        "version": "v8.6.5-ProStable",
        "branding": {"footer": "🚀 WENBNB Neural Engine — Emotional Intelligence 24×7 ⚡"},
        "admin": {"allowed_admins": [owner_id]},
    })))
    dp.add_handler(CommandHandler("reboot", lambda u, c: admin_reboot(u, c, {
        "admin": {"allowed_admins": [owner_id]},
    })))
    print("✅ Loaded plugin: admin_tools.py (Admin Panel Integrated)")
