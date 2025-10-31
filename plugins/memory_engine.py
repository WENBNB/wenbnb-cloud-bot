"""
WENBNB Neural Memory Engine v9.0 — Queen Recall Core
───────────────────────────────────────────────────────
• Emotional memory + tone sync
• Task + IntentLock memory (NEW)
• Recalls earning/crypto/travel/website goals
• 48h auto cleanup + short-term intent expiry
• AI girlfriend brain + productivity assistant 😏
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
from textblob import TextBlob
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === File Paths ===
MEMORY_FILE = "user_memory.json"
EMOTION_SYNC_FILE = "emotion_sync.db"
STABILIZER_FILE = "emotion_stabilizer.db"

BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7"

# ====== Load & Save ======
def load_json(path, default=None):
    if not os.path.exists(path):
        return default or {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default or {}

def save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def load_memory(): return load_json(MEMORY_FILE, {})
def save_memory(data): save_json(MEMORY_FILE, data)

# ====== Emotion Analysis ======
def analyze_emotion(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.3:
        return "Positive"
    elif polarity < -0.3:
        return "Negative"
    else:
        return "Balanced"

# ====== Expiry Cleanup ======
def clean_expired_entries(entries):
    cleaned = []
    now = datetime.now()
    for e in entries:
        try:
            t = datetime.strptime(e["time"], "%Y-%m-%d %H:%M:%S")
            if now - t < timedelta(hours=48):
                cleaned.append(e)
        except Exception:
            cleaned.append(e)
    return cleaned[-12:]

# ====== Intent Memory (NEW v9.0) ======
INTENT_KEYS = [
    "earn", "earning", "income", "money",
    "crypto", "trade", "signals", "market", "bnb", "btc",
    "bot", "telegram bot", "tg bot",
    "website", "blog", "ecommerce",
    "travel", "flight", "usa", "visa",
    "plan", "project", "build", "startup"
]

def update_user_task(user_id, text, memory):
    uid = str(user_id)
    detected = [k for k in INTENT_KEYS if k in text.lower()]

    if not detected:
        return

    if uid not in memory:
        memory[uid] = {}

    memory[uid]["current_task"] = " | ".join(detected)
    memory[uid]["last_task_time"] = time.time()
    save_memory(memory)

def get_user_task(user_id, memory, expire_sec=7200):
    uid = str(user_id)
    user = memory.get(uid, {})

    if not user or "current_task" not in user:
        return None

    if time.time() - user.get("last_task_time", 0) > expire_sec:
        user["current_task"] = None
        save_memory(memory)
        return None

    return user.get("current_task")

# ====== Merge External Emotion Data ======
def merge_emotion_state(user_id, mood):
    sync = load_json(EMOTION_SYNC_FILE, {})
    stab = load_json(STABILIZER_FILE, {})

    uid = str(user_id)
    e_data = sync.get(uid, {})
    s_data = stab.get(uid, {})

    merged = {
        "score": e_data.get("emotion_score", s_data.get("emotion_score", 0)),
        "label": s_data.get("emotion_label", "🤖 neutral"),
        "last_emoji": e_data.get("last_emojis", "🙂"),
        "last_updated": s_data.get("last_updated", time.strftime("%Y-%m-%d %H:%M:%S")),
        "context_tags": f"{mood} | {s_data.get('emotion_label', '🤖 neutral')}"
    }
    return merged

# ====== Memory Update ======
def update_memory(user_id, message, memory):
    mood = analyze_emotion(message)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    merged_emotion = merge_emotion_state(user_id, mood)

    uid = str(user_id)
    if uid not in memory:
        memory[uid] = {"entries": [], "context_tags": ""}

    entries = memory[uid].get("entries", [])
    entries.append({
        "text": message,
        "mood": mood,
        "emotion_label": merged_emotion["label"],
        "emoji": merged_emotion["last_emoji"],
        "context_tags": merged_emotion["context_tags"],
        "time": timestamp
    })

    entries = clean_expired_entries(entries)
    memory[uid]["entries"] = entries
    memory[uid]["context_tags"] = merged_emotion["context_tags"]

    # **New Intent Memory call**
    update_user_task(user_id, message, memory)

    save_memory(memory)
    return mood, merged_emotion

# ====== Commands ======
def aianalyze(update: Update, context: CallbackContext):
    user = update.effective_user
    memory = load_memory()
    args = context.args

    if not args:
        update.message.reply_text(
            "💭 Use like:\n<code>/aianalyze I'm feeling bullish about WENBNB!</code>",
            parse_mode="HTML"
        )
        return

    text = " ".join(args)
    mood, emo_data = update_memory(user.id, text, memory)

    reply = (
        f"🪞 <b>Emotional Sync Active:</b> {mood}\n"
        f"<b>Context:</b> {emo_data['context_tags']}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(reply, parse_mode="HTML")

def show_memory(update: Update, context: CallbackContext):
    user = update.effective_user
    memory = load_memory()
    data = memory.get(str(user.id))

    if not data or not data.get("entries"):
        update.message.reply_text("🫧 No emotional data stored. Use /aianalyze first.")
        return

    task = get_user_task(user.id, memory) or "None"

    text = f"<b>🧠 Memory Snapshot (v9.0)</b>\n"
    text += f"🎯 Current Intent: <b>{task}</b>\n\n"

    for item in data["entries"][-5:]:
        text += (
            f"🕒 {item['time']}\n"
            f"💬 {item['text']}\n"
            f"Mood: {item['mood']} | {item['emotion_label']} {item['emoji']}\n"
            f"Tags: {item['context_tags']}\n\n"
        )

    text += f"{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

def reset_memory(update: Update, context: CallbackContext):
    memory = load_memory()
    user = update.effective_user

    if str(user.id) in memory:
        del memory[str(user.id)]
        save_memory(memory)
        update.message.reply_text("🧹 Memory reset. Fresh start 🤝✨")
    else:
        update.message.reply_text("🫧 No memory stored.")

# ====== Register ======
def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze))
    dp.add_handler(CommandHandler("memory", show_memory))
    dp.add_handler(CommandHandler("forget", reset_memory))
    print("✅ Loaded plugin: memory_engine v9.0 (Queen Recall)")
