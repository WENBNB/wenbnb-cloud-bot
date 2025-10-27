# plugins/admin_tools.py
# ============================================================
# 🧠 WENBNB Admin Tools v8.6.5 — ProStable+ Build
# Now PluginManager compatible 💫
# ============================================================

import os
import psutil
import time
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, CommandHandler

# --- Helper: Verify admin ---
def is_admin(user_id: int, allowed_admins: list) -> bool:
    return user_id in allowed_admins

# --- System status ---
def get_system_status():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - psutil.boot_time()))
    return f"🧠 System: {cpu}% CPU | {mem}% RAM | Uptime: {uptime}"

# --- /admin Command ---
def admin_status(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    allowed = [5698007588]  # 👈 change if needed

    if not is_admin(user_id, allowed):
        update.message.reply_text("🚫 Unauthorized Access")
        return

    status = get_system_status()
    text = (
        f"✅ <b>WENBNB Neural Engine v8.6.5-ProStable</b>\n\n"
        f"{status}\n"
        f"🌐 Dashboard: https://wenbnb-neural-engine.onrender.com\n\n"
        f"🚀 <b>Powered by WENBNB Neural Engine</b> — Emotional Intelligence 24×7 ⚡"
    )
    update.message.reply_text(text, parse_mode=ParseMode.HTML)

# --- Register with PluginManager ---
def register_handlers(dp):
    dp.add_handler(CommandHandler("admin", admin_status))
    print("✅ Loaded plugin: admin_tools.py (v8.6.5-ProStable+)")
