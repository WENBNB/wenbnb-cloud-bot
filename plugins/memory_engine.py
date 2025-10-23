"""
WENBNB Neural Memory Engine v4.1-E
Emotion Context + Persistent Hybrid Memory System
Locked & Approved — "AI Soul Integration"
"""

import json
import os
import time
from textblob import TextBlob
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

MEMORY_FILE = "user_memory.json"
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"

# ===== LOAD + SAVE MEMORY =====

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

# ===== EMOTION DETECTION =====

def analyze_emotion(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.3:
        return "😊 Positive", "💫 Glad to feel your energy!"
    elif polarity < -0.3:
        return "😔 Negative", "💭 I sense you’re upset, but I’m here for you."
    else:
        return "😐 Neutral", "✨ I’m calm and listening."

# ===== MEMORY UPDATE =====

def update_user_memory(user_id, message, memory):
    emotion_label, emotion_text = analyze_emotion(message)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if str(user_id) not in memory:
        memory[str(user_id)] = {"context": [], "last_emotion": "Neutral"}

    memory[str(user_id)]["context"].append({
        "text": message,
        "emotion": emotion_label,
        "time": timestamp
    })
    memory[str(user_id)]["last_emotion"] = emotion_label
    if len(memory[str(user_id)]["context"]) > 10:
        memory[str(user_id)]["context"].pop(0)

    save_memory(memory)
    return emotion_label, emotion_text

# ===== COMMANDS =====

def aianalyze(update: Update, context: CallbackContext):
    user = update.effective_user
    memory = load_memory()
    user_id = str(user.id)

    text = " ".join(context.args)
    if not text:
        update.message.reply_text(
            "🧠 Send me a message like:\n<code>/aianalyze I feel bullish about WENBNB!</code>",
            parse_mode="HTML"
        )
        return

    emotion_label, emotion_text = update_user_memory(user_id, text, memory)
    reply = (
        f"{emotion_text}\n\n"
        f"<b>Emotion Detected:</b> {emotion_label}\n"
        f"<b>Context Saved:</b> \"{text}\"\n\n"
        "Your vibe is now synced with WENBNB Neural Memory 🧠💫\n\n"
        f"{BRAND_TAG}"
    )

    update.message.reply_text(reply, parse_mode="HTML")

def show_memory(update: Update, context: CallbackContext):
    user = update.effective_user
    memory = load_memory()
    data = memory.get(str(user.id))

    if not data:
        update.message.reply_text("🧩 No active memory found. Start by talking to me using /aianalyze.")
        return

    text = "<b>🧠 Your WENBNB Neural Memory Snapshot</b>\n\n"
    for c in data["context"][-5:]:
        text += f"🕒 <i>{c['time']}</i>\n💬 {c['text']}\nMood: {c['emotion']}\n\n"

    text += f"{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

def reset_memory(update: Update, context: CallbackContext):
    memory = load_memory()
    user = update.effective_user

    if str(user.id) in memory:
        del memory[str(user.id)]
        save_memory(memory)
        update.message.reply_text("🧹 Memory cleared successfully.\nI’ll start fresh with you 💞")
    else:
        update.message.reply_text("No stored memory found for you.")

# ===== REGISTRATION =====

def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze))
    dp.add_handler(CommandHandler("mymemory", show_memory))
    dp.add_handler(CommandHandler("resetmemory", reset_memory))
