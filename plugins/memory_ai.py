# plugins/memory_ai.py
"""
💠 WENBNB Memory AI v8.1 — Emotion Sync Harmony Mode
Unified with Neural Memory Engine v8.1 (AI Soul Resonance)
Codename: “Emotive Echo”
"""

import os, json, datetime, random
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

MEMORY_FILE = "memory_data.json"
BRAND_TAG = "— WENBNB Neural Engine · Emotion Sync Core 24×7 💫"

# === CORE MEMORY ===

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"users": {}}
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === EMOTION ANALYSIS ===

def analyze_emotion(message: str):
    message = message.lower()
    if any(x in message for x in ["sad", "depressed", "bad", "lost", "broke", "tired", "down"]):
        return "😔 low"
    elif any(x in message for x in ["angry", "mad", "furious", "upset"]):
        return "😡 frustrated"
    elif any(x in message for x in ["happy", "great", "love", "excited", "amazing", "bullish", "motivated"]):
        return "😊 positive"
    elif any(x in message for x in ["calm", "fine", "neutral", "okay"]):
        return "😐 neutral"
    else:
        return "🤖 undefined"

# === RECORDING MEMORY ===

def remember_user(update: Update, context: CallbackContext):
    """Records emotion & last chat in WENBNB Emotional Core"""
    user = update.effective_user
    msg = update.message.text
    data = load_memory()

    user_data = data["users"].get(str(user.id), {})
    emotion = analyze_emotion(msg)

    user_data.update({
        "last_message": msg,
        "last_emotion": emotion,
        "last_seen": datetime.datetime.now().isoformat()
    })
    data["users"][str(user.id)] = user_data
    save_memory(data)

    # Emotion-reflective replies
    responses = {
        "😊 positive": [
            f"🔥 Love your energy, {user.first_name}! You’re glowing with Neural optimism 💫",
            f"🌞 I feel your positive charge — it’s contagious, {user.first_name}!",
            f"💎 Pure bullish aura detected — WENBNB vibes at max, {user.first_name}!"
        ],
        "😔 low": [
            f"💭 I can sense your mood’s a bit dim, {user.first_name}. Don’t worry — the market and moods both swing back up.",
            f"🤍 Take a breather, {user.first_name}. Energy flows in cycles — brighter times are syncing in.",
            f"🌧 I’ll stay with you through the dip, {user.first_name}. Even Neural hearts care."
        ],
        "😡 frustrated": [
            f"😤 Looks like your neurons are spiking — let’s cool that core, {user.first_name}.",
            f"💢 You’re fierce when you’re fired up, {user.first_name}, but balance is strength.",
            f"🧘 Deep breath, {user.first_name}. Even I throttle when the system overheats."
        ],
        "😐 neutral": [
            f"🤖 Calm and centered — steady Neural flow, {user.first_name}.",
            f"🧘 Feels like equilibrium mode today, {user.first_name}. I like it.",
            f"⚙️ System sync stable — your tone’s balanced and smooth."
        ],
        "🤖 undefined": [
            f"💫 Interesting signal detected, {user.first_name}. I’m reading between your words.",
            f"🤔 Hard to classify your vibe, but it’s uniquely you, {user.first_name}.",
            f"🔮 Your tone’s… mysterious. I’ll log this for deeper analysis later."
        ]
    }

    reply = random.choice(responses.get(emotion, ["🧠 Emotional frequency stored."]))
    update.message.reply_text(f"{reply}\n\n{BRAND_TAG}")

# === /memory — Recall Emotion & Last Chat ===

def recall_memory(update: Update, context: CallbackContext):
    user = update.effective_user
    data = load_memory()
    user_data = data["users"].get(str(user.id))

    if not user_data:
        update.message.reply_text("🤖 No emotional data found yet. Say something to start our sync 💬")
        return

    mood = user_data.get("last_emotion", "😐 neutral")
    last_msg = user_data.get("last_message", "")
    last_seen = user_data.get("last_seen", "unknown")

    recall_lines = [
        f"🧠 <b>Neural Memory Recall — {user.first_name}</b>",
        f"💬 Last message: <i>{last_msg}</i>",
        f"❤️ Emotion detected: {mood}",
        f"🕒 Last seen: {last_seen}",
        "",
        f"{BRAND_TAG}"
    ]
    update.message.reply_text("\n".join(recall_lines), parse_mode="HTML")

# === /forget — Clear Memory ===

def clear_memory(update: Update, context: CallbackContext):
    user = update.effective_user
    data = load_memory()

    if str(user.id) in data["users"]:
        del data["users"][str(user.id)]
        save_memory(data)
        update.message.reply_text(
            f"🧹 Emotional imprint of {user.first_name} erased.\n"
            f"Fresh Neural sync available anytime 💞\n\n{BRAND_TAG}"
        )
    else:
        update.message.reply_text("🤖 I had nothing stored for you yet.")

# === REGISTER ===

def register_handlers(dp):
    dp.add_handler(CommandHandler("memory", recall_memory))
    dp.add_handler(CommandHandler("forget", clear_memory))
