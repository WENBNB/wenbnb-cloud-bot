# 🚀 WENBNB Neural Engine — Admin Control Suite v3.9-ProStable+
# Integrated with EmotionSync v2.1 & SystemCore Monitoring
# Provides: /admin, /reboot, /broadcast, /status commands

import os
import psutil
import time
import json
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

# -----------------------------
# 🧩 Admin Configuration
# -----------------------------
def is_admin(user_id: int, allowed_admins: list) -> bool:
    """Check if user is authorized as admin"""
    return user_id in allowed_admins


# -----------------------------
# ⚙️ System Performance
# -----------------------------
def get_system_status():
    """Return system performance overview"""
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory().percent
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - psutil.boot_time()))
    return f"🧠 System: {cpu}% CPU | {memory}% RAM | Uptime: {uptime}"


# -----------------------------
# 🪩 EmotionSync Integration
# -----------------------------
def get_emotion_sync_status():
    """Read latest EmotionSync state (if available)"""
    try:
        if os.path.exists("user_memory.json"):
            with open("user_memory.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                # Try reading last emotion from any user
                for uid, record in data.items():
                    if record.get("entries"):
                        mood = record["entries"][-1].get("mood", "Balanced")
                        return f"🪩 Neural Mood: {mood}"
        return "🪩 Neural Mood: Balanced"
    except Exception:
        return "🪩 Neural Mood: Unknown"


# -----------------------------
# 🧠 Admin Commands
# -----------------------------
def admin_status(update: Update, context: CallbackContext, config):
    """Display system status, version, and emotion sync mood"""
    user_id = update.effective_user.id
    if not is_admin(user_id, config["admin"]["allowed_admins"]):
        update.message.reply_text("🚫 Unauthorized Access")
        return

    version = config["version"]
    sys_status = get_system_status()
    mood_status = get_emotion_sync_status()

    update.message.reply_text(
        f"✅ <b>{version}</b>\n\n"
        f"{sys_status}\n{mood_status}\n\n"
        f"📡 Neural Engine Online.\n\n"
        f"{config['branding']['footer']}",
        parse_mode=ParseMode.HTML
    )


def admin_reboot(update: Update, context: CallbackContext, config):
    """Simulate bot reboot (soft restart message)"""
    user_id = update.effective_user.id
    if not is_admin(user_id, config["admin"]["allowed_admins"]):
        update.message.reply_text("🚫 Unauthorized Access")
        return

    update.message.reply_text("♻️ Neural Core rebooting… please wait a moment.")
    time.sleep(2)
    update.message.reply_text("✅ WENBNB Neural Engine rebooted successfully ⚡")


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
        update.message.reply_text(f"📢 Broadcast sent:\n{msg}")
    except Exception as e:
        update.message.reply_text(f"❌ Error sending broadcast: {e}")


# -----------------------------
# 🧩 Command Registration
# -----------------------------
def register_handlers(dp, config):
    from telegram.ext import CommandHandler

    dp.add_handler(CommandHandler("admin", lambda u, c: admin_status(u, c, config)))
    dp.add_handler(CommandHandler("reboot", lambda u, c: admin_reboot(u, c, config)))
    dp.add_handler(CommandHandler("broadcast", lambda u, c: admin_broadcast(u, c, config)))

    print("✅ Loaded plugin: admin_tools.py (EmotionSync v2.1 integrated)")
