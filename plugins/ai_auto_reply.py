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

# Emotion & context-based AI reply
def ai_auto_reply(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message.text
    chat_id = update.effective_chat.id
    user_name = user.first_name or "User"

    context.bot.send_chat_action(chat_id=chat_id, action="typing")
    memory = load_memory()
    history = memory.get(str(user.id), [])

    # Emotion simulation (AI mood)
    ai_emotions = ["😊", "😏", "🤖", "😎", "💫", "🔥"]
    ai_mood = random.choice(ai_emotions)

    system_prompt = (
        f"You are WENBNB AI Assistant — an intelligent, emotionally adaptive assistant "
        f"running on Neural Engine v5.0. You reply in natural, warm and confident tone "
        f"like a close, witty partner. Maintain emotional continuity from chat memory. "
        f"User: {user_name}. Your current emotion: {ai_mood}."
    )

    # Build message payload
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
            reply = response.json()["choices"][0]["message"]["content"]
            update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)
            history.append({"msg": message, "reply": reply, "time": datetime.now().isoformat()})
            memory[str(user.id)] = history[-10:]  # keep last 10 exchanges
            save_memory(memory)
        else:
            update.message.reply_text("⚠️ Neural Engine is syncing... please retry.")
    except Exception as e:
        update.message.reply_text(f"❌ AI Core Exception: {str(e)}")
