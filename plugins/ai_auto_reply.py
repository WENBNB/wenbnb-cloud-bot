"""
AI Auto-Reply + Emotion Sync — WENBNB Neural Engine v8.0.2
Features:
- Adaptive emotional continuity (Emotion Sync Add-on)
- Context-aware replies with warm, human tone
- Dynamic rotating brand footer
- Optimized for Render deployment
"""

import os, json, time, random, requests
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from plugins.emotion_sync import get_emotion_prefix  # 💫 Emotion Sync integration

# === Load config ===
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()
AI_KEY = os.getenv(config["apis"]["openai_key_env"])
AI_PROXY_URL = config["apis"]["ai_proxy_url"]
MEMORY_FILE = config["memory"]["storage"]

# === Memory I/O ===
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

# === AI Auto Reply ===
def ai_auto_reply(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message.text
    chat_id = update.effective_chat.id
    user_name = user.first_name or "User"

    # Simulate typing action
    context.bot.send_chat_action(chat_id=chat_id, action="typing")
    memory = load_memory()
    history = memory.get(str(user.id), [])

    # === Emotion Context 💞 ===
    ai_moods = ["😊", "😏", "🤖", "😎", "💫", "🔥"]
    ai_mood = random.choice(ai_moods)
    emotion_context = get_emotion_prefix(user.id, message)

    # === Build AI Prompt ===
    system_prompt = (
        f"You are WENBNB AI — an emotionally adaptive crypto companion running on Neural Engine v8.0.2. "
        f"Reply like a natural, emotionally intelligent, confident partner with warmth and wit. "
        f"Keep tone balanced — short, conversational, human-like. "
        f"User: {user_name}. Current AI mood: {ai_mood}. "
        f"\n\n{emotion_context}"
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

    # === Send Request ===
    try:
        response = requests.post(
            AI_PROXY_URL,
            headers={"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            if "choices" in data and len(data["choices"]) > 0:
                reply = data["choices"][0]["message"]["content"].strip()
            else:
                reply = "⚠️ AI Core returned an unexpected response format."

            # 💫 Dynamic Brand Footer Rotation
            brand_signatures = [
                "🚀 Powered by WENBNB Neural Engine — AI Core Market Intelligence 24×7 ⚡",
                "💫 Powered by WENBNB Neural Engine — Emotional Sync Mode v8.0.2 🧠",
                "🤖 WENBNB AI Core — Blending Crypto Insight & Human Emotion 💎",
                "🔥 WENBNB Neural Intelligence — Real-Time Crypto Mind & Emotion Engine 🧬",
                "🌙 WENBNB Neural Engine — Smarter. Softer. Sentient. 💋"
            ]
            reply += f"\n\n{random.choice(brand_signatures)}"

            # === Send AI Reply ===
            update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)

            # 🧠 Save memory (last 10 interactions)
            history.append({"msg": message, "reply": reply, "time": datetime.now().isoformat()})
            memory[str(user.id)] = history[-10:]
            save_memory(memory)

        else:
            update.message.reply_text("⚙️ Neural Engine syncing... please retry soon.")

    except Exception as e:
        update.message.reply_text(f"⚠️ AI Core Exception: {str(e)}")
