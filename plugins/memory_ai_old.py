"""
💠 WENBNB Memory AI v8.1 — Harmony Layer
Uses same shared memory as memory_engine.py
"""

import json, os
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

MEMORY_FILE = "user_memory.json"
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotion Sync Core 24×7"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === /memory command ===
def recall_memory(update: Update, context: CallbackContext):
    user = update.effective_user
    data = load_memory()
    record = data.get(str(user.id))

    if not record or not record.get("context"):
        update.message.reply_text("🤖 No active emotional data found. Use /aianalyze to start our sync 💬")
        return

    last = record["context"][-1]
    msg = (
        f"🧠 <b>Neural Memory Recall — {user.first_name}</b>\n"
        f"💬 Last message: <i>{last['text']}</i>\n"
        f"❤️ Emotion detected: {last['emotion']}\n"
        f"🕒 Last seen: {last['time']}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(msg, parse_mode="HTML")

# === /forget command ===
def clear_memory(update: Update, context: CallbackContext):
    user = update.effective_user
    data = load_memory()

    if str(user.id) in data:
        del data[str(user.id)]
        save_memory(data)
        update.message.reply_text(f"🧹 Memory of {user.first_name} deleted.\n{BRAND_TAG}")
    else:
        update.message.reply_text("🤖 Nothing stored yet — clean as new silicon 💫")

def register_handlers(dp):
    dp.add_handler(CommandHandler("memory", recall_memory))
    dp.add_handler(CommandHandler("forget", clear_memory))
