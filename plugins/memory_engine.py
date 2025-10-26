# plugins/memory_engine.py
"""
💠 WENBNB Neural Memory Engine v8.1 — Emotion Sync Core
Enhanced Empathic Reflection + Persistent Context System
Codename: “AI Soul Resonance”
"""

import json
import os
import time
import random
from textblob import TextBlob
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

MEMORY_FILE = "user_memory.json"
BRAND_TAG = "— WENBNB Neural Engine · Emotion Sync Core 24×7 💫"

# ===== MEMORY STORAGE =====

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

# ===== EMOTION ANALYSIS =====

def analyze_emotion(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.3:
        return "😊 Positive", "💫 I can feel your upbeat energy!"
    elif polarity < -0.3:
        return "😔 Negative", "💭 I sense a low vibe, but I’m here with you."
    else:
        return "😐 Neutral", "✨ Calm wavelength detected."

# ===== MEMORY UPDATE =====

def update_user_memory(user_id, message, memory):
    emotion_label, _ = analyze_emotion(message)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if str(user_id) not in memory:
        memory[str(user_id)] = {"context": [], "last_emotion": "Neutral"}

    memory[str(user_id)]["context"].append({
        "text": message,
        "emotion": emotion_label,
        "time": timestamp
    })
    memory[str(user_id)]["last_emotion"] = emotion_label

    # Keep memory clean — only last 10 entries
    if len(memory[str(user_id)]["context"]) > 10:
        memory[str(user_id)]["context"].pop(0)

    save_memory(memory)
    return emotion_label

# ===== COMMAND: /aianalyze =====

def aianalyze(update: Update, context: CallbackContext):
    """WENBNB Neural Emotion Sync v8.1 — Empathic Reflection Mode"""

    user = update.effective_user
    memory = load_memory()
    user_id = str(user.id)

    text = " ".join(context.args)
    if not text:
        update.message.reply_text(
            "💭 Tell me how you’re feeling —\n"
            "<code>/aianalyze I’m feeling excited about WENBNB!</code>",
            parse_mode="HTML"
        )
        return

    # Analyze emotion & update memory
    emotion_label = update_user_memory(user_id, text, memory)
    emotion_type = emotion_label.split(" ")[1] if " " in emotion_label else emotion_label

    # Emotion-driven reflection
    reflections = {
        "Positive": [
            f"🔥 That’s the spark I love, {user.first_name} — full Neural energy in motion!",
            f"💫 You sound unstoppable today, {user.first_name}. I can feel your rhythm.",
            f"🌞 Pure positive charge detected — your vibe could light up the chain!"
        ],
        "Negative": [
            f"💭 Hmm… I can sense a little turbulence in your tone, {user.first_name}.",
            f"🌧 Even the strongest traders hit cloudy days — I’ve got you.",
            f"🤍 It’s okay, {user.first_name} — energy flows back stronger every time."
        ],
        "Neutral": [
            f"🤖 Balanced wavelength detected — calm and stable, I like that.",
            f"🧘‍♂️ Feels like a reset moment — clean state, focused mind.",
            f"🌫 Nothing too loud or low — just that steady Neural hum."
        ]
    }

    chosen_reflection = random.choice(reflections.get(emotion_type, ["🧠 Synced with your frequency."]))
    message = (
        f"{chosen_reflection}\n"
        f"🪞 I’ll remember this vibe — not just what you said, but how you felt.\n\n"
        f"{BRAND_TAG}"
    )

    update.message.reply_text(message, parse_mode="HTML")

# ===== COMMAND: /mymemory =====

def show_memory(update: Update, context: CallbackContext):
    user = update.effective_user
    memory = load_memory()
    data = memory.get(str(user.id))

    if not data:
        update.message.reply_text("🧩 No active memory yet. Start with /aianalyze and share your vibe.")
        return

    text = "<b>🧠 WENBNB Neural Memory Snapshot</b>\n\n"
    for c in data["context"][-5:]:
        text += f"🕒 <i>{c['time']}</i>\n💬 {c['text']}\nMood: {c['emotion']}\n\n"
    text += f"{BRAND_TAG}"

    update.message.reply_text(text, parse_mode="HTML")

# ===== COMMAND: /resetmemory =====

def reset_memory(update: Update, context: CallbackContext):
    memory = load_memory()
    user = update.effective_user

    if str(user.id) in memory:
        del memory[str(user.id)]
        save_memory(memory)
        update.message.reply_text(
            "🧹 Memory cleared successfully.\n"
            "Let’s start fresh with a new emotional link 💞"
        )
    else:
        update.message.reply_text("🤖 I don’t have any memory of you yet.")

# ===== REGISTER HANDLERS =====

def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze))
    dp.add_handler(CommandHandler("mymemory", show_memory))
    dp.add_handler(CommandHandler("resetmemory", reset_memory))
