"""
WENBNB Neural Memory Engine v8.3 — "Clean Pulse Edition"
Emotion Sync + Context Memory System
Refined for natural tone and premium personality.
"""

import os
import json
import time
from textblob import TextBlob
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

MEMORY_FILE = "user_memory.json"
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7"

# ====== Load & Save ======

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

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

# ====== Memory Update ======

def update_memory(user_id, message, memory):
    mood = analyze_emotion(message)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if str(user_id) not in memory:
        memory[str(user_id)] = {"entries": []}

    memory[str(user_id)]["entries"].append({
        "text": message,
        "mood": mood,
        "time": timestamp
    })

    # keep last 10
    memory[str(user_id)]["entries"] = memory[str(user_id)]["entries"][-10:]
    save_memory(memory)
    return mood

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
    mood = update_memory(user.id, text, memory)

    # Response tone library
    tones = {
        "Positive": [
            f"✨ Love that energy, {user.first_name}! Keep that bullish spark alive — your optimism radiates pure alpha.",
            f"🌞 I can sense your vibe — bright, charged, and unstoppable. That’s pure WENBNB spirit!"
        ],
        "Negative": [
            f"💭 Hey {user.first_name}, I can feel the storm in your words. Let’s take a breath — every dip has a rebound.",
            f"😔 It’s okay to feel off. Even the Neural Engine needs cooldown time. You’re not alone in this."
        ],
        "Balanced": [
            f"🌙 Calm and steady, {user.first_name}. Your tone is balanced — that’s real trader discipline.",
            f"🧘 Neural tone stabilized — clarity detected. You’re vibing smooth and centered today."
        ]
    }

    chosen = tones.get(mood, ["I’m syncing your mood…"]).copy()
    import random
    reply = (
        f"🪞 Emotional sync active: <b>{mood}</b>\n\n"
        f"{random.choice(chosen)}\n\n"
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

    text = "<b>🧠 WENBNB Emotional Memory Snapshot</b>\n\n"
    for item in data["entries"][-5:]:
        text += f"🕒 {item['time']}\n💬 {item['text']}\nMood: {item['mood']}\n\n"

    text += BRAND_TAG
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
