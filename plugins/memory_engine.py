# plugins/memory_engine.py
"""
💫 WENBNB Neural Memory Engine v8.2 — “Synaptic Soul” Build
Emotion-aware personality core for /aianalyze, /memory, /forget.
Refined natural tone — Warm, adaptive, and humanlike.
"""

import json, os, time, random
from textblob import TextBlob
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
MEMORY_FILE = "data/user_memory.json"
os.makedirs("data", exist_ok=True)
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7"


# === MEMORY CORE ===

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# === EMOTION ANALYSIS ===

def analyze_emotion(text: str):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.35:
        mood = "😊 Positive"
        tone = "upbeat"
    elif polarity < -0.35:
        mood = "😔 Negative"
        tone = "low"
    else:
        mood = "😐 Neutral"
        tone = "balanced"

    return mood, tone


# === EMOTION-RESPONSIVE REPLIES ===

def emotional_reply(user_name: str, mood: str, text: str):
    if "Positive" in mood:
        responses = [
            f"You sound radiant today, {user_name}! ✨ That kind of vibe could move markets.",
            f"Haha, I can literally *feel* that bullish spark in your words, {user_name} 😎",
            f"Love the confidence, {user_name}! Keep that energy up 💫"
        ]
    elif "Negative" in mood:
        responses = [
            f"Hey {user_name}… sounds like today’s been heavy. Let’s turn that around 💛",
            f"I sense a bit of frustration there — breathe, we’ve got this together 🌱",
            f"Even strong minds have low days, {user_name}. You’re still golden ✨"
        ]
    else:
        responses = [
            f"Balanced tone, {user_name} — calm before the next big move, huh?",
            f"I like this energy. Not too high, not too low — just *centered*. ⚖️",
            f"You sound grounded, {user_name}. Perfect mindset for precision. 🧠"
        ]

    return random.choice(responses)


# === MEMORY OPERATIONS ===

def update_memory(user_id: str, text: str, mood: str):
    memory = load_memory()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    if user_id not in memory:
        memory[user_id] = {"entries": []}

    memory[user_id]["entries"].append({
        "text": text,
        "mood": mood,
        "time": timestamp
    })

    if len(memory[user_id]["entries"]) > 10:
        memory[user_id]["entries"].pop(0)

    save_memory(memory)


# === COMMAND HANDLERS ===

def aianalyze(update: Update, context: CallbackContext):
    user = update.effective_user
    text = " ".join(context.args)

    if not text:
        update.message.reply_text(
            "🧠 Tell me how you feel or what’s on your mind.\nExample: `/aianalyze I’m feeling bullish today!`",
            parse_mode="Markdown"
        )
        return

    mood, tone = analyze_emotion(text)
    update_memory(str(user.id), text, mood)
    reply = emotional_reply(user.first_name, mood, text)

    msg = (
        f"{reply}\n\n"
        f"🪞 <b>Mood sensed:</b> {mood}\n"
        f"{BRAND_TAG}"
    )

    update.message.reply_text(msg, parse_mode="HTML")


def memory(update: Update, context: CallbackContext):
    user = update.effective_user
    memory = load_memory().get(str(user.id))

    if not memory or not memory.get("entries"):
        update.message.reply_text("💭 No emotional data yet. Start with `/aianalyze` and talk to me.")
        return

    text = "<b>🧠 Your Emotional Memory</b>\n\n"
    for e in memory["entries"][-5:]:
        text += f"🕒 <i>{e['time']}</i>\n💬 {e['text']}\nMood: {e['mood']}\n\n"
    text += f"{BRAND_TAG}"

    update.message.reply_text(text, parse_mode="HTML")


def forget(update: Update, context: CallbackContext):
    user = update.effective_user
    memory = load_memory()

    if str(user.id) in memory:
        del memory[str(user.id)]
        save_memory(memory)
        update.message.reply_text(f"🧹 All your emotional traces cleared, {user.first_name}.\nFresh sync awaits 💞")
    else:
        update.message.reply_text("🤖 No memory found for you — we’re clean as new silicon 💫")


# === REGISTER ===

def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze))
    dp.add_handler(CommandHandler("memory", memory))
    dp.add_handler(CommandHandler("forget", forget))
