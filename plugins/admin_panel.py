"""
WENBNB Neural Admin Control Panel v3.8
Handles Broadcasts, Memory Reset, and Live Stats for Admins
Locked & Approved — "Core Access Only"
"""

from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
import json, os, time

ADMIN_IDS = [123456789, 987654321]  # 🔹 Replace with real admin Telegram IDs
MEMORY_FILE = "user_memory.json"
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"

# ===== HELPER FUNCTIONS =====

def is_admin(user_id):
    return user_id in ADMIN_IDS

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

# ===== ADMIN COMMANDS =====

def admin_panel(update: Update, context: CallbackContext):
    user = update.effective_user
    if not is_admin(user.id):
        update.message.reply_text("🚫 Access Denied. Neural Control requires admin authority.")
        return

    text = (
        f"🧠 <b>WENBNB Neural Control Panel</b>\n"
        f"👑 Admin: {user.full_name}\n\n"
        "Available Commands:\n"
        "🔹 /broadcast <msg> — Send message to all users\n"
        "🔹 /users — View active users count\n"
        "🔹 /reset_all_memory — Full system memory wipe\n"
        "🔹 /stats — System activity snapshot\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

# ===== BROADCAST =====

def broadcast(update: Update, context: CallbackContext):
    user = update.effective_user
    if not is_admin(user.id):
        update.message.reply_text("🚫 Unauthorized access.")
        return

    msg = " ".join(context.args)
    if not msg:
        update.message.reply_text("📢 Use: /broadcast <message>")
        return

    memory = load_memory()
    total = len(memory)
    success = 0

    for user_id in memory.keys():
        try:
            context.bot.send_message(chat_id=int(user_id), text=f"📢 Admin Broadcast:\n\n{msg}")
            success += 1
            time.sleep(0.5)
        except Exception:
            continue

    update.message.reply_text(
        f"✅ Broadcast sent to {success}/{total} users.\n\n{BRAND_TAG}",
        parse_mode="HTML"
    )

# ===== USER STATS =====

def show_users(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        update.message.reply_text("🚫 You are not authorized.")
        return

    memory = load_memory()
    total_users = len(memory)
    update.message.reply_text(f"👥 Total active users: <b>{total_users}</b>", parse_mode="HTML")

# ===== FULL MEMORY RESET =====

def reset_all_memory(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        update.message.reply_text("🚫 Access Denied.")
        return

    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
        update.message.reply_text("🧹 All user memory wiped.\nFresh neural state activated ⚙️")
    else:
        update.message.reply_text("No memory file found.")

# ===== SYSTEM STATS =====

def system_stats(update: Update, context: CallbackContext):
    if not is_admin(update.effective_user.id):
        update.message.reply_text("🚫 Restricted.")
        return

    memory = load_memory()
    users = len(memory)
    uptime = time.strftime("%Y-%m-%d %H:%M:%S")

    text = (
        f"<b>📊 WENBNB Neural Engine — System Status</b>\n\n"
        f"👥 Users Stored: {users}\n"
        f"🕒 Uptime Snapshot: {uptime}\n"
        f"💾 Memory File: {MEMORY_FILE}\n"
        f"⚙️ Status: Stable\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(text, parse_mode="HTML")

# ===== REGISTER HANDLERS =====

def register_handlers(dp):
    dp.add_handler(CommandHandler("admin", admin_panel))
    dp.add_handler(CommandHandler("broadcast", broadcast))
    dp.add_handler(CommandHandler("users", show_users))
    dp.add_handler(CommandHandler("reset_all_memory", reset_all_memory))
    dp.add_handler(CommandHandler("stats", system_stats))
