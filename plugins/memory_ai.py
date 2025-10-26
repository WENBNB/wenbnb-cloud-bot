"""
🧠 WENBNB Memory AI Interface v8.0.6-Pro
Emotion Sync Personality + Neural Recall Bridge
Connects directly with memory_engine.py (SQLite Memory Core)
"""

import os
import sqlite3
import datetime
import random
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

DB_PATH = "data/memory.db"
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotion Sync v8.0.6"

# === INTERNAL DB HANDLERS ===
def fetch_last_memory(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT text, emotion, timestamp FROM user_memory WHERE user_id=? ORDER BY ROWID DESC LIMIT 1", (str(user_id),))
    row = c.fetchone()
    conn.close()
    return row

def clear_memory(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM user_memory WHERE user_id=?", (str(user_id),))
    conn.commit()
    conn.close()

# === EMOTION-BASED PERSONALITY ===
def get_dynamic_reply(emotion, user_name):
    responses = {
        "😊 Positive": [
            f"Your energy is contagious @{user_name}! 🌞",
            f"I love that vibe, @{user_name}. Keep radiating positivity 💫"
        ],
        "😔 Negative": [
            f"Hey @{user_name}, I can sense that. Remember — storms don’t last forever 🌤️",
            f"You’re not alone in this one, @{user_name} 💛"
        ],
        "😐 Neutral": [
            f"Hey @{user_name}, I’m right here if you wanna talk 💬",
            f"Neural calm detected — wanna chat, @{user_name}? 🤖"
        ]
    }
    return random.choice(responses.get(emotion, ["I’m always tuned to your frequency 💫"]))

# === MESSAGE LISTENER ===
def auto_emotion_sync(update: Update, context: CallbackContext):
    """Listens to normal chats and responds emotionally"""
    user = update.effective_user
    text = update.message.text
    if not text or text.startswith("/"):
        return  # skip commands

    # get latest emotion memory
    last_entry = fetch_last_memory(user.id)
    emotion_hint = last_entry[1] if last_entry else "😐 Neutral"
    reply = get_dynamic_reply(emotion_hint, user.username or user.first_name)
    update.message.reply_text(reply + "\n\n" + BRAND_TAG)

# === COMMANDS ===
def recall_memory(update: Update, context: CallbackContext):
    """Shows user’s latest emotional memory snapshot"""
    user = update.effective_user
    entry = fetch_last_memory(user.id)
    if not entry:
        update.message.reply_text("🤖 I haven’t logged any memory for you yet.\nTry chatting with /aianalyze 💭")
        return

    text, emotion, timestamp = entry
    msg = (
        f"🧠 <b>Memory Recall — {user.first_name}</b>\n"
        f"💬 Last message: {text}\n"
        f"❤️ Emotion detected: {emotion}\n"
        f"🕒 Last seen: {timestamp}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(msg, parse_mode="HTML")

def forget_memory(update: Update, context: CallbackContext):
    """Deletes user’s emotional memory"""
    user = update.effective_user
    clear_memory(user.id)
    update.message.reply_text(f"🧹 Memory of @{user.username or user.first_name} cleared.\n{BRAND_TAG}")

# === REGISTRATION ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("memory", recall_memory))
    dp.add_handler(CommandHandler("forget", forget_memory))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, auto_emotion_sync))
    print("💞 memory_ai.py loaded — Emotion Sync active with SQLite Memory Core.")
