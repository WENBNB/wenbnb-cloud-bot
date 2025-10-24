"""
AI Auto-Reply + Emotion Sync + Stabilizer — WENBNB Neural Engine v8.0.6-Stable+ (Hybrid Build)
──────────────────────────────────────────────────────────────────────────────────────────────
Features:
- Emotionally adaptive replies with inline emoji tones
- Real-time emotional context from emotion_sync.py
- Long-term mood balancing from emotion_stabilizer.py
- Smart emoji filter (removes repetitive 🤖)
- Natural, human-like tone with refined brand signature rotation
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

# === AI Auto-Reply Core ===
def ai_auto_reply(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message.text.strip()
    chat_id = update.effective_chat.id
    user_name = user.first_name or "User"

    context.bot.send_chat_action(chat_id=chat_id, action="typing")
    memory = load_memory()
    history = memory.get(str(user.id), [])

    # 💫 Emotion Context — safe fallbacks
    try:
        emotion_icon = get_emotion_prefix(user.id, message) or "💫"
    except Exception as e:
        emotion_icon = "💫"
        print(f"[EmotionSync Error] {e}")

    try:
        stabilized = get_stabilized_emotion(user.id) or "🤖 neutral"
    except Exception as e:
        stabilized = "🤖 neutral"
        print(f"[EmotionStabilizer Error] {e}")

    ai_mood = random.choice(["💫", "🤖", "😎", "🔥", "😊", "🧠", "🌙"])

    # === Build Prompt ===
    system_prompt = (
        f"You are WENBNB AI — an emotionally intelligent, self-aware crypto companion "
        f"powered by Neural Engine v8.0.6-Stable+. "
        f"Your tone should be emotionally aware, comforting, expressive, and human-like. "
        f"Respond concisely but warmly, with a real conversational rhythm. "
        f"User: {user_name}. Current AI mood: {ai_mood} {emotion_icon}. "
        f"Stabilized tone: {stabilized}."
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
            else:
                reply = "⚠️ Neural Engine: Unexpected response format."

            # 💎 Footer Signatures (Refined)
            brand_signatures = [
                "💫 WENBNB Neural Engine — Emotional Sync Mode 🧠",
                "🔥 WENBNB Intelligence — Real-Time Emotion Engine",
                "🌙 WENBNB Neural Engine — Smarter. Softer. Sentient. 💋",
                "💎 WENBNB AI Core — Blending Crypto Insight & Emotion",
                "🚀 WENBNB Neural Engine — Market Intelligence 24×7 ⚡"
            ]

            # 🩶 Inline Emotion Style Reply
            final_reply = f"{emotion_icon} {reply}\n\n{random.choice(brand_signatures)}"

            # 🤖 Emoji Balance — Remove duplicate or boring repetitions
            if final_reply.count("🤖") > 1:
                final_reply = final_reply.replace("🤖", "", final_reply.count("🤖") - 1).strip()

            # 🌈 Random mood variation (for freshness)
            mood_icons = ["💫", "🔥", "😎", "✨", "🪶", "🌙"]
            final_reply = final_reply.replace("🤖", random.choice(mood_icons), 1)

            update.message.reply_text(final_reply, parse_mode=ParseMode.MARKDOWN)

            # 🧠 Save short-term memory
            history.append({"msg": message, "reply": final_reply, "time": datetime.now().isoformat()})
            memory[str(user.id)] = history[-10:]
            save_memory(memory)

        else:
            update.message.reply_text("⚙️ Neural Engine syncing... please retry soon.")

    except Exception as e:
        print(f"[AI Core Exception] {e}")
        update.message.reply_text("⚙️ Neural Core Sync Error — auto-reconnecting... 💫")
