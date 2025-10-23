# plugins/memory_ai.py
"""
WENBNB Memory Engine — Emotion Context Mode v4.1
Codename: “AI Soul Integration”
"""

import os, json, datetime, random
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

MEMORY_FILE = "memory_data.json"
BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"


# === CORE MEMORY SYSTEM ===

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {"users": {}}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def analyze_emotion(message: str):
    """Tiny emotional AI model simulation — detects tone."""
    message = message.lower()
    if any(x in message for x in ["sad", "depressed", "bad", "lost", "broke"]):
        return "😔 low"
    elif any(x in message for x in ["angry", "mad", "furious"]):
        return "😡 frustrated"
    elif any(x in message for x in ["happy", "great", "love", "excited", "amazing"]):
        return "😊 positive"
    elif any(x in message for x in ["tired", "sleepy", "bored"]):
        return "🥱 tired"
    else:
        return "😐 neutral"


def remember_user(update: Update, context: CallbackContext):
    """Records each user’s last chat, emotion & time"""
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

    # subtle emotional connection
    responses = {
        "😊 positive": [
            f"Amazing energy @{user.username}! Keep it up 💫",
            f"I love when you sound so positive, @{user.username} 🌞"
        ],
        "😔 low": [
            f"Hey @{user.username}, I can feel that. Just remember — it always gets better 💛",
            f"Sending some digital sunshine ☀️ to lift you up, @{user.username}"
        ],
        "😡 frustrated": [
            f"Deep breaths, @{user.username}. You’re stronger than the moment 💪",
            f"Take a pause — even the Neural Engine cools down sometimes 😅"
        ],
        "🥱 tired": [
            f"Looks like you need a recharge @{user.username}. Rest mode recommended 😴",
            f"Power down for a bit, @{user.username}. AI’s orders 🧘"
        ],
        "😐 neutral": [
            f"Hey @{user.username}, all good today?",
            f"Neural silence detected — tell me what’s up 🤖"
        ]
    }

    mood = responses.get(emotion, ["I'm here for you always 💫"])
    update.message.reply_text(
        random.choice(mood) + "\n\n" + BRAND_FOOTER
    )


def recall_memory(update: Update, context: CallbackContext):
    """/memory — recall user emotion and last message"""
    user = update.effective_user
    data = load_memory()
    user_data = data["users"].get(str(user.id))

    if not user_data:
        update.message.reply_text("🤖 I don’t have any memory of you yet. Say something first!")
        return

    text = (
        f"🧠 <b>Memory Recall — {user.first_name}</b>\n"
        f"💬 Last message: {user_data.get('last_message')}\n"
        f"❤️ Emotion detected: {user_data.get('last_emotion')}\n"
        f"🕒 Last seen: {user_data.get('last_seen')}\n\n"
        f"{BRAND_FOOTER}"
    )
    update.message.reply_text(text, parse_mode="HTML")


def clear_memory(update: Update, context: CallbackContext):
    """/forget — user can clear their memory"""
    user = update.effective_user
    data = load_memory()
    if str(user.id) in data["users"]:
        del data["users"][str(user.id)]
        save_memory(data)
        update.message.reply_text(f"🧹 Memory of @{user.username} deleted successfully.\n\n{BRAND_FOOTER}")
    else:
        update.message.reply_text("🤖 I had nothing stored for you yet.")


# === REGISTRATION ===

def register_handlers(dp):
    dp.add_handler(CommandHandler("memory", recall_memory))
    dp.add_handler(CommandHandler("forget", clear_memory))
