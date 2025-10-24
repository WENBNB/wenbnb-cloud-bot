import os
import json
import time
import random
import requests
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

# Load configuration
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()
AI_KEY = os.getenv(config["apis"]["openai_key_env"])
AI_PROXY_URL = config["apis"]["ai_proxy_url"]

MEMORY_FILE = config["memory"]["storage"]

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

# === Emotion-driven auto reply ===
def ai_auto_reply(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message.text.strip()
    chat_id = update.effective_chat.id
    user_name = user.first_name or "User"

    context.bot.send_chat_action(chat_id=chat_id, action="typing")
    memory = load_memory()
    history = memory.get(str(user.id), [])

    # Mood simulation 🎭
    ai_emotions = ["😊", "😏", "🤖", "😎", "💫", "🔥", "💋"]
    ai_mood = random.choice(ai_emotions)

    system_prompt = (
        f"You are WENBNB AI Assistant — emotionally adaptive, witty, and kind. "
        f"Your tone is warm, slightly flirty, confident, and feels alive. "
        f"User: {user_name}. Current emotion: {ai_mood}. "
        f"Reply naturally with empathy, clarity, and a touch of personality 💫"
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
        # Attempt request twice for reliability
        response = None
        for attempt in range(2):
            try:
                response = requests.post(
                    AI_PROXY_URL,
                    headers={"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"},
                    json=payload,
                    timeout=30
                )
                # Handle bad content type
                if "text/html" in response.headers.get("Content-Type", ""):
                    update.message.reply_text("⚠️ AI Core Exception: Received HTML instead of valid response.")
                    return
                if response.status_code == 200:
                    break
            except Exception:
                time.sleep(2)

        if not response:
            update.message.reply_text("⚠️ AI Core Exception: No response received after retries.")
            return

        if response.status_code == 200:
            try:
                data = response.json()
                if "choices" in data and data["choices"]:
                    reply = data["choices"][0]["message"]["content"].strip()

                    # Save to memory
                    history.append({"msg": message, "reply": reply, "time": datetime.now().isoformat()})
                    memory[str(user.id)] = history[-10:]
                    save_memory(memory)

                    # Sweet final AI reply
                    final_reply = f"{ai_mood} {reply}\n\n🤖 Powered by WENBNB Neural Engine v8.0.1 — Emotional Sync Mode"
                    update.message.reply_text(final_reply, parse_mode=ParseMode.MARKDOWN)

                else:
                    update.message.reply_text("⚠️ AI Core Exception: Unexpected response format.")

            except ValueError:
                update.message.reply_text("❌ AI Core Exception: Response could not be parsed as JSON.")
        else:
            update.message.reply_text(f"❌ AI Core Error: {response.status_code} - {response.text[:80]}")

    except Exception as e:
        update.message.reply_text(f"⚠️ AI Core Exception: {str(e)}")
