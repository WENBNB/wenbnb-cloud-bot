"""
🧠 WENBNB Neural Memory Engine v8.0.6-Pro
Emotion Context + Persistent SQLite Memory Core
Optimized for Emotion Sync + Adaptive Recall
"""

import os
import sqlite3
import time
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

DB_PATH = "data/memory.db"
os.makedirs("data", exist_ok=True)

BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Pro Memory Core 24×7"

# ===== DB INIT =====
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_memory (
        user_id TEXT,
        text TEXT,
        emotion TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ===== EMOTION DETECTION =====
def detect_emotion(text):
    text_l = text.lower()
    positives = ["good", "great", "amazing", "love", "happy", "bullish", "win", "yes"]
    negatives = ["sad", "bad", "angry", "bearish", "down", "lose", "tired", "no"]
    pos_score = sum(w in text_l for w in positives)
    neg_score = sum(w in text_l for w in negatives)

    if pos_score > neg_score:
        return "😊 Positive", "💫 I can feel your upbeat energy!"
    elif neg_score > pos_score:
        return "😔 Negative", "💭 That sounds rough, but I’ve got your back."
    else:
        return "😐 Neutral", "✨ Calm and centered — syncing your vibe."

# ===== MEMORY UPDATE =====
def save_message(user_id, text, emotion):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO user_memory (user_id, text, emotion, timestamp) VALUES (?, ?, ?, ?)",
              (str(user_id), text, emotion, time.strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_recent_memory(user_id, limit=5):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT text, emotion, timestamp FROM user_memory WHERE user_id=? ORDER BY ROWID DESC LIMIT ?",
              (str(user_id), limit))
    rows = c.fetchall()
    conn.close()
    return rows[::-1]  # reverse chronological

def clear_memory(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM user_memory WHERE user_id=?", (str(user_id),))
    conn.commit()
    conn.close()

# ===== COMMANDS =====
def aianalyze(update: Update, context: CallbackContext):
    user = update.effective_user
    if not context.args:
        update.message.reply_text(
            "🧠 Send me something to analyze:\n<code>/aianalyze I’m feeling bullish about WENBNB!</code>",
            parse_mode="HTML"
        )
        return

    text = " ".join(context.args)
    emotion_label, emotion_msg = detect_emotion(text)
    save_message(user.id, text, emotion_label)

    reply = (
        f"{emotion_msg}\n\n"
        f"<b>Emotion Detected:</b> {emotion_label}\n"
        f"<b>Memory Saved:</b> \"{text}\"\n\n"
        "Your emotional context is now synced 💾🧠\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(reply, parse_mode="HTML")

def show_memory(update: Update, context: CallbackContext):
    user = update.effective_user
    entries = get_recent_memory(user.id)
    if not entries:
        update.message.reply_text("🧩 No memory yet. Start with /aianalyze 💭")
        return

    msg = "<b>🧠 WENBNB Neural Memory Snapshot</b>\n\n"
    for text, emotion, ts in entries:
        msg += f"🕒 <i>{ts}</i>\n💬 {text}\nMood: {emotion}\n\n"
    msg += BRAND_TAG
    update.message.reply_text(msg, parse_mode="HTML")

def reset_memory(update: Update, context: CallbackContext):
    user = update.effective_user
    clear_memory(user.id)
    update.message.reply_text("🧹 Memory cleared successfully.\nI’ll start fresh with you 💞")

# ===== REGISTER HANDLERS =====
def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze))
    dp.add_handler(CommandHandler("mymemory", show_memory))
    dp.add_handler(CommandHandler("resetmemory", reset_memory))

    print("🧠 memory_engine.py loaded — SQLite neural memory active.")
