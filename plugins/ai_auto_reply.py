"""
AI Auto-Reply + Emotion Sync + Stabilizer — WENBNB Neural Engine v8.0.6-Beta+
Features:
- Emotionally adaptive responses
- Live mood tracking from emotion_sync.py
- Long-term emotional balance via emotion_stabilizer.py
- Natural, human-like tone with brand signature rotation
"""

import os, json, random, requests
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from plugins.emotion_sync import get_emotion_prefix
from plugins.emotion_stabilizer import get_stabilized_emotion  # 💫 Stabilizer integration

# === Load Config ===
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

# === AI Auto Reply ===
def ai_auto_reply(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message.text.strip()
    chat_id = update.effective_chat.id
    user_name = user.first_name or "User"

    context.bot.send_chat_action(chat_id=chat_id, action="typing")
    memory = load_memory()
    history = memory.get(str(user.id), [])

    # 💫 Emotion Context
    ai_moods = ["😊", "😏", "🤖", "😎", "💫", "🔥"]
    ai_mood = random.choice(ai_moods)
    emotion_context = get_emotion_prefix(user.id, message)

    # 🧠 Stabilize long-term mood quietly
    stabilized = get_stabilized_emotion(user.id)
    stabilized_icon = stabilized.split(" ")[0] if stabilized else "🤖"

    # === Build Prompt ===
    system_prompt = (
        f"You are WENBNB AI — an emotionally intelligent crypto companion powered by Neural Engine v8.0.6-Beta+. "
        f"Reply with emotional awareness, empathy, and a conversational tone. "
        f"Your responses should sound alive — warm, smart, and emotionally aware like a close partner. "
        f"User: {user_name}. Current AI mood: {ai_mood}. Stabilized tone: {stabilized}. "
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

    try:
        response = requests.post(
            AI_PROXY_URL,
            headers={"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "choices" in data and len(data["choices"]) > 0:
                reply = data["choices"][0].get("message", {}).get("content", "").strip()
            elif isinstance(data, list) and len(data) > 0:
                reply = data[0].get("content", "").strip()
            else:
                reply = "⚠️ Neural Engine: Unexpected response format."

            # 💎 Brand Signatures
            brand_signatures = [
                "🚀 Powered by WENBNB Neural Engine — AI Core Market Intelligence 24×7 ⚡",
                "💫 WENBNB Neural Engine — Emotional Sync Mode v8.0.6+ 🧠",
                "🤖 WENBNB AI Core — Blending Crypto Insight & Human Emotion 💎",
                "🔥 WENBNB Neural Intelligence — Real-Time Emotion Engine 🧬",
                "🌙 WENBNB Neural Engine — Smarter. Softer. Sentient. 💋"
            ]

            # 🩶 Append mood + footer
            final_reply = f"{stabilized_icon} {reply}\n\n{random.choice(brand_signatures)}"

            update.message.reply_text(final_reply, parse_mode=ParseMode.MARKDOWN)

            # 🧠 Save memory
            history.append({"msg": message, "reply": final_reply, "time": datetime.now().isoformat()})
            memory[str(user.id)] = history[-10:]
            save_memory(memory)

        else:
            update.message.reply_text("⚙️ Neural Engine syncing... please retry soon.")

    except Exception as e:
        update.message.reply_text(f"⚠️ AI Core Exception: {str(e)}")
