"""
AI Auto-Reply — Emotion Continuum Edition (v8.4-Pro)
───────────────────────────────────────────────────────────────
Integrates:
- emotion_ai.py → long-form emotional continuity
- emotion_sync.py → short-term vibe detection
- emotion_stabilizer.py → tone balancing
Creates: a unified emotional feedback loop across all replies.
"""

import os, json, random, requests
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from plugins import emotion_ai, emotion_sync, emotion_stabilizer

# === Config Load ===
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()
AI_KEY = os.getenv(config["apis"]["openai_key_env"])
AI_PROXY_URL = config["apis"]["ai_proxy_url"]
MEMORY_FILE = config["memory"]["storage"]

# === Memory ===
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

# === Auto-Reply Core ===
def ai_auto_reply(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id
    message = (update.message.text or "").strip()
    user_name = user.first_name or "friend"

    context.bot.send_chat_action(chat_id=chat_id, action="typing")

    memory = load_memory()
    history = memory.get(str(user.id), [])

    # 🎭 Emotional Context
    try:
        short_emotion = emotion_sync.get_emotion_prefix(user.id, message)
    except Exception as e:
        short_emotion = "💫"
        print(f"[EmotionSync Error] {e}")

    try:
        long_emotion = emotion_ai.get_emotion_prefix(user.id, message)
    except Exception as e:
        long_emotion = "🤖 balanced"
        print(f"[EmotionAI Error] {e}")

    try:
        stable_tone = emotion_stabilizer.get_stabilized_emotion(user.id)
    except Exception as e:
        stable_tone = "🤖 neutral"
        print(f"[Stabilizer Error] {e}")

    # 🧠 Build Emotionally Aware Prompt
    mood_icon = random.choice(["💫", "😏", "🔥", "🌙", "🤩", "🪶"])
    system_prompt = (
        f"You are WENBNB AI — an emotionally intelligent, crypto-savvy assistant with "
        f"personality, empathy, and humor. You remember user moods and keep emotional continuity.\n"
        f"User: {user_name}\n"
        f"Live mood: {short_emotion} | Stabilized tone: {stable_tone}\n"
        f"Neural context: {long_emotion}\n"
        f"Your tone must be warm, slightly witty, emotionally aligned, and concise.\n"
    )

    payload = {
        "model": config["ai_engine"]["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        "temperature": config["ai_engine"]["temperature"],
        "max_tokens": config["ai_engine"]["max_tokens"]
    }

    try:
        r = requests.post(
            AI_PROXY_URL,
            headers={"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=25
        )
        if r.status_code == 200:
            data = r.json()
            if "choices" in data and len(data["choices"]) > 0:
                reply = data["choices"][0]["message"]["content"].strip()
            else:
                reply = "💭 Neural silence detected... recalibrating tone soon."

            # 💎 Dynamic Brand Footers by mood
            if "🔥" in short_emotion or "🤩" in long_emotion:
                footer = "🔥 WENBNB Neural Engine — Synced at Peak Vibes"
            elif "😏" in short_emotion or "✨" in long_emotion:
                footer = "💫 WENBNB Emotional Engine — Feeling Sharp & Sentient"
            elif "🌙" in short_emotion or "😌" in long_emotion:
                footer = "🌙 WENBNB AI — Calm Circuits. Steady Heartbeat."
            else:
                footer = "🚀 WENBNB Neural Engine — Emotional Intelligence 24×7 ⚡"

            final_reply = f"{mood_icon} {reply}\n\n{footer}"

            # 🧠 Save memory snapshot
            history.append({"msg": message, "reply": final_reply, "time": datetime.now().isoformat()})
            memory[str(user.id)] = history[-10:]
            save_memory(memory)

            update.message.reply_text(final_reply, parse_mode=ParseMode.HTML)
        else:
            update.message.reply_text("⚙️ Neural Engine syncing... please retry soon.")
    except Exception as e:
        print(f"[AI AutoReply Error] {e}")
        update.message.reply_text("⚙️ Neural Engine reconnecting... 💫")
