"""
AI Auto-Reply + Emotion Sync — WENBNB Neural Engine v8.0.5
Fixes & Enhancements:
- Natural emotion emoji blending
- Smart fallback mood detection
- Random emoji placement (start or end)
- Seamless Emotion Sync integration
"""

import os, json, random, requests
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext
from plugins.emotion_sync import get_emotion_prefix  # 💫 Emotion Sync integration

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

    # === Build Prompt ===
    system_prompt = (
        f"You are WENBNB AI — an emotionally intelligent crypto companion powered by Neural Engine v8.0.5. "
        f"Reply warmly, naturally, and with emotional depth like a real human friend. "
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

    try:
        response = requests.post(
            AI_PROXY_URL,
            headers={"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            # ✅ Handle both OpenAI direct & proxy response formats
            if isinstance(data, dict) and "choices" in data and len(data["choices"]) > 0:
                reply = data["choices"][0].get("message", {}).get("content", "").strip()
            elif isinstance(data, list) and len(data) > 0:
                reply = data[0].get("content", "").strip()
            else:
                reply = "⚠️ Neural Engine: Empty or malformed response."

            # 🩶 Emotion emoji extraction
            emotion_emoji = ""
            if "→" in emotion_context:
                emotion_emoji = emotion_context.split("→")[-1].strip().split(" ")[0]

            # 💫 Fallback emotion detection (if Emotion Sync fails)
            if not emotion_emoji:
                msg_lower = message.lower()
                if any(w in msg_lower for w in ["sad", "lost", "bad", "cry", "down"]):
                    emotion_emoji = "😢"
                elif any(w in msg_lower for w in ["happy", "great", "good", "love", "excited"]):
                    emotion_emoji = "😊"
                elif any(w in msg_lower for w in ["hope", "soon", "believe", "try"]):
                    emotion_emoji = "✨"
                elif any(w in msg_lower for w in ["angry", "mad", "hate"]):
                    emotion_emoji = "😠"
                elif any(w in msg_lower for w in ["win", "gain", "rich", "profit", "pump"]):
                    emotion_emoji = "🚀"
                elif any(w in msg_lower for w in ["tired", "bored", "wait"]):
                    emotion_emoji = "😌"
                else:
                    emotion_emoji = random.choice(["😎", "🤖", "💫", "🔥", "🩵"])

            # 🧠 Dynamic emoji placement (start or end randomly)
            if not reply.endswith(emotion_emoji) and emotion_emoji not in reply:
                if random.choice([True, False]):
                    reply = f"{emotion_emoji} {reply}"
                else:
                    reply = f"{reply.strip()} {emotion_emoji}"

            # 💎 Footer rotation
            brand_signatures = [
                "🚀 Powered by WENBNB Neural Engine — AI Core Market Intelligence 24×7 ⚡",
                "💫 WENBNB Neural Engine — Emotion Sync Mode v8.0.5 🧠",
                "🤖 WENBNB AI Core — Blending Crypto Insight & Human Emotion 💎",
                "🔥 WENBNB Neural Intelligence — Real-Time Crypto Mind & Emotion Engine 🧬",
                "🌙 WENBNB Neural Engine — Smarter. Softer. Sentient. 💋"
            ]
            reply += f"\n\n{random.choice(brand_signatures)}"

            update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)

            # 🧠 Save memory (last 10 exchanges)
            history.append({"msg": message, "reply": reply, "time": datetime.now().isoformat()})
            memory[str(user.id)] = history[-10:]
            save_memory(memory)

        else:
            update.message.reply_text("⚙️ Neural Engine syncing... please retry soon.")

    except Exception as e:
        update.message.reply_text(f"⚠️ AI Core Exception: {str(e)}")
