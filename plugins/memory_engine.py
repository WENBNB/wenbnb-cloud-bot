"""
WENBNB Neural Memory Engine v8.7.5 — MemoryContext++ Edition
──────────────────────────────────────────────────────────────
Purpose:
• Fuses user memory + emotion_sync + stabilizer data
• Adds long-term tone continuity and emotional drift balance
• Smart expiry (auto-cleans entries >48h old)
• Provides emotional context tags for AI core replies
• 100% backward compatible with v8.3 memory file
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
    """Remove entries older than 48 hours"""
    cleaned = []
    now = datetime.now()
    for e in entries:
        try:
            t = datetime.strptime(e["time"], "%Y-%m-%d %H:%M:%S")
            if now - t < timedelta(hours=48):
                cleaned.append(e)
        except Exception:
            cleaned.append(e)
    return cleaned[-12:]  # keep last 12 recent ones

# ====== Merge External Emotion Data ======

def merge_emotion_state(user_id, mood):
    """Merges mood with external emotion_sync or stabilizer files"""
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

    tones = {
        "Positive": [
            f"✨ Love that energy, {user.first_name}! Your {emo_data['label']} vibe is on fire — pure WENBNB alpha!",
            f"🌞 Radiating optimism, {user.first_name}. Neural tone synced: {emo_data['label']} {emo_data['last_emoji']}"
        ],
        "Negative": [
            f"💭 Hey {user.first_name}, I can feel some turbulence — but your {emo_data['label']} tone will stabilize soon.",
            f"😔 Storms don’t last forever, {user.first_name}. Emotional state synced as {emo_data['label']}."
        ],
        "Balanced": [
            f"🌙 Steady and mindful, {user.first_name}. Your tone {emo_data['label']} {emo_data['last_emoji']} shows real discipline.",
            f"🧘 Calm pulse detected, {user.first_name}. Context: {emo_data['context_tags']}."
        ]
    }

    chosen = random.choice(tones.get(mood, ["Processing your vibe..."]))
    reply = (
        f"🪞 <b>Emotional Sync Active:</b> {mood}\n"
        f"<b>Context:</b> {emo_data['context_tags']}\n\n"
        f"{chosen}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(reply, parse_mode="HTML")

def show_memory(update: Update, context: CallbackContext):
    user = update.effective_user
    memory = load_memory()
    data = memory.get(str(user.id))

    if not data or not data.get("entries"):
        update.message.reply_text("🫧 No emotional data found yet. Use /aianalyze to start syncing 💫")
        return

    text = f"<b>🧠 WENBNB Emotional Memory Snapshot — v8.7.5 MemoryContext++</b>\n\n"
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
        update.message.reply_text("🧹 Memory cleared successfully.\nStarting fresh with you ✨")
    else:
        update.message.reply_text("🫧 No stored memory to reset.")

# ====== Register ======
def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze))
    dp.add_handler(CommandHandler("memory", show_memory))
    dp.add_handler(CommandHandler("forget", reset_memory))
    print("✅ Loaded plugin: memory_engine.py v8.7.5 MemoryContext++ Edition")
