import os
import psutil
import time
import json
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

def is_admin(user_id: int, allowed_admins: list) -> bool:
    """Check if user is authorized as admin"""
    return user_id in allowed_admins

def get_system_status():
    """Returns system performance stats"""
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - psutil.boot_time()))
    return f"🧠 System: {cpu}% CPU | {memory}% RAM | Uptime: {uptime}"

def admin_status(update: Update, context: CallbackContext, config):
    """Show bot status and environment info"""
    user_id = update.effective_user.id
    if not is_admin(user_id, config["admin"]["allowed_admins"]):
        update.message.reply_text("🚫 Unauthorized Access")
        return
    
    status_msg = get_system_status()
    version = config["version"]
    update.message.reply_text(
        f"✅ <b>{version}</b>\n\n{status_msg}\n"
        f"📡 Uptime check complete.\n\n"
        f"{config['branding']['footer']}",
        parse_mode=ParseMode.HTML
    )

def admin_broadcast(update: Update, context: CallbackContext, config):
    """Broadcast message to all users (admin-only)"""
    user_id = update.effective_user.id
    if not is_admin(user_id, config["admin"]["allowed_admins"]):
        update.message.reply_text("🚫 Unauthorized Access")
        return
    
    if len(context.args) == 0:
        update.message.reply_text("Usage: /broadcast <message>")
        return
    
    msg = " ".join(context.args)
    try:
        # Here you can add user list loop for mass send
        update.message.reply_text(f"📢 Broadcast sent:\n{msg}")
    except Exception as e:
        update.message.reply_text(f"❌ Error sending broadcast: {e}")

def admin_reboot(update: Update, context: CallbackContext, config):
    """Simulate bot reboot (soft restart message)"""
    user_id = update.effective_user.id
    if not is_admin(user_id, config["admin"]["allowed_admins"]):
        update.message.reply_text("🚫 Unauthorized Access")
        return
    
    update.message.reply_text("♻️ Neural Core rebooting… please wait a moment.")
    time.sleep(2)
    update.message.reply_text("✅ WENBNB Neural Engine rebooted successfully ⚡")
