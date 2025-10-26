"""
🧠 WENBNB Neural Memory Engine v8.1 — Unified Emotion Core
Integrates /aianalyze + /memory + /forget into a single shared system
Codename: "Synaptic Soul"
"""

import json, os, time, datetime, random
from textblob import TextBlob
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

MEMORY_FILE = "user_memory.json"
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotion Sync Core 24×7"

# ====== STORAGE ======
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

# ====== EMOTION ANALYSIS ======
def analyze_emotion(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.3:
        return "😊 Positive"
    elif polarity < -0.3:
        return "😔 Negative"
    else:
        return "😐 Neutral"

# ====== MEMORY UPDATE ======
def update_user_memory(user_id, message, memory):
    emotion = analyze_emotion(message)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if str(user_id) not in memory:
        memory[str(user_id)] = {"context": []}

    memory[str(user_id)]["context"].append({
        "text": message,
        "emotion": emotion,
        "time": timestamp
    })

    if len(memory[str(user_id)]["context"]) > 10:
        memory[str(user_id)]["context"].pop(0)

    save_memory(memory)
    return emotion, timestamp

# ====== RESPONSE TONES ======
def mood_reply(emotion, name):
    if "Positive" in emotion:
        return random.choice([
            f"🌞 I can feel your bright energy, {name}!",
            f"💫 Love that spark, {name} — keep the vibes high!",
            f"🔥 You’re radiating positivity today!"
        ])
    elif "Negative" in emotion:
        return random.choice([
            f"💭 I can sense the heaviness, {name}. It’s okay — I’m with you.",
            f"🫶 Rough patch, huh? Even the Neural Core feels dips sometimes.",
            f"☁️ Hey {name}, remember — no downtrend lasts forever."
        ])
    else:
        return random.choice([
            f"🤖 Balanced mood detected — stable as WENBNB’s core.",
            f"🧘 Calm flow, {name}. Perfect sync achieved.",
            f"⚙️ Mood steady — equilibrium achieved."
        ])

# ====== COMMANDS ======
def aianalyze(update: Update, context: CallbackContext):
    user = update.effective_user
    text = " ".join(context.args)
    if not text:
        update.message.reply_text(
            "🧩 Try `/aianalyze I feel amazing today!` to let me read your vibe.",
            parse_mode="Markdown"
        )
        return

    memory = load_memory()
    emotion, _ = update_user_memory(user.id, text, memory)
    reply = mood_reply(emotion, user.first_name)

    update.message.reply_text(
        f"{reply}\n\n<b>Mood:</b> {emotion}\n{BRAND_TAG}",
        parse_mode="HTML"
    )

def show_memory(update: Update, context: CallbackContext):
    user = update.effective_user
    memory = load_memory()
    data = memory.get(str(user.id))

    if not data or not data.get("context"):
        update.message.reply_text("🤖 No emotional data stored yet. Use /aianalyze to start.")
        return

    lines = ["🧠 <b>WENBNB Neural Memory Snapshot</b>\n"]
    for c in data["context"][-5:]:
        lines.append(f"🕒 {c['time']}\n💬 {c['text']}\nMood: {c['emotion']}\n")

    update.message.reply_text("\n".join(lines) + f"\n{BRAND_TAG}", parse_mode="HTML")

def reset_memory(update: Update, context: CallbackContext):
    memory = load_memory()
    user = update.effective_user

    if str(user.id) in memory:
        del memory[str(user.id)]
        save_memory(memory)
        update.message.reply_text("🧹 Emotional memory cleared. Ready to start fresh 💞")
    else:
        update.message.reply_text("No stored memory found.")

# ====== REGISTER HANDLERS ======
def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze))
    dp.add_handler(CommandHandler("mymemory", show_memory))
    dp.add_handler(CommandHandler("resetmemory", reset_memory))
