"""
WENBNB Neural Engine — AI Auto Reply v8.0 Meme-Infused Hybrid Edition
Flirty + Confident personality with Emotion Context & Mood-based Reactions
"""

import os
import json
import time
import random
import requests
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

# === CONFIG LOADER ===
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

config = load_config()
AI_KEY = os.getenv(config["apis"]["openai_key_env"])
AI_PROXY_URL = config["apis"]["ai_proxy_url"]
MEMORY_FILE = config["memory"]["storage"]

# === MEMORY HANDLER ===
def load_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

# === EMOTION DETECTOR ===
def detect_emotion(text):
    """Lightweight emotional tone detector"""
    try:
        prompt = (
            f"Analyze emotional tone of this text. "
            f"Return one word: happy, sad, angry, excited, chill, flirty, or neutral.\n\nMessage: {text}"
        )
        payload = {
            "model": "gpt-4-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 10,
            "temperature": 0.3
        }
        response = requests.post(
            AI_PROXY_URL,
            headers={"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        tone = response.json()["choices"][0]["message"]["content"].strip().lower()
        return tone
    except Exception:
        return "neutral"

# === MEME TRIGGER ===
def get_meme_for_emotion(emotion):
    memes = {
        "happy": [
            "https://i.imgflip.com/30b1gx.jpg",
            "https://i.imgflip.com/7qf0um.jpg"
        ],
        "sad": [
            "https://i.imgflip.com/4t0m5.jpg",
            "https://i.imgflip.com/8x0xv.jpg"
        ],
        "angry": [
            "https://i.imgflip.com/1otk96.jpg",
            "https://i.imgflip.com/2wifvo.jpg"
        ],
        "excited": [
            "https://i.imgflip.com/1bij.jpg",
            "https://i.imgflip.com/7zy9i1.jpg"
        ],
        "flirty": [
            "https://i.imgflip.com/7vfg7x.jpg",
            "https://i.imgflip.com/7vz1n3.jpg"
        ],
        "chill": [
            "https://i.imgflip.com/1ur9b0.jpg"
        ],
    }
    if emotion in memes:
        return random.choice(memes[emotion])
    return None

# === AI AUTO REPLY CORE ===
def ai_auto_reply(update: Update, context: CallbackContext):
    user = update.effective_user
    message = update.message.text
    chat_id = update.effective_chat.id
    user_name = user.first_name or "User"

    context.bot.send_chat_action(chat_id=chat_id, action="typing")
    memory = load_memory()
    history = memory.get(str(user.id), [])

    # === EMOTION DETECTION ===
    emotion = detect_emotion(message)
    emoji_map = {
        "happy": "😊", "sad": "😢", "angry": "😠", "excited": "🤩",
        "chill": "😌", "flirty": "😏", "neutral": "🤖"
    }
    mood_emoji = emoji_map.get(emotion, "🤖")

    # === PERSONALITY SYSTEM PROMPT ===
    system_prompt = (
        f"You are WENBNB AI — a confident, emotionally adaptive assistant "
        f"running on Neural Engine v8.0. "
        f"Your tone is flirty, charming, and emotionally aware. "
        f"Current detected emotion: {emotion} {mood_emoji}. "
        f"Keep replies short, natural, and engaging like a real person who cares."
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
            reply = response.json()["choices"][0]["message"]["content"].strip()

            # 🧠 Optional fun footers
            tail = random.choice([
                "💫 Stay sharp, always on chain.",
                "⚡ Neural Engine running at full vibe.",
                "🧠 Emotion synced perfectly with yours.",
                "💋 That one hit different, didn’t it?",
            ])
            final_reply = f"{mood_emoji} {reply}\n\n{tail}"

            update.message.reply_text(final_reply, parse_mode=ParseMode.MARKDOWN)

            # 🖼️ Mood-based meme trigger (1 in 3 chance)
            if random.random() < 0.33:
                meme_url = get_meme_for_emotion(emotion)
                if meme_url:
                    context.bot.send_photo(chat_id=chat_id, photo=meme_url, caption=f"{mood_emoji} mood mode engaged")

            # 🧩 Update memory
            history.append({
                "msg": message,
                "reply": reply,
                "emotion": emotion,
                "time": datetime.now().isoformat()
            })
            memory[str(user.id)] = history[-10:]
            save_memory(memory)

        else:
            update.message.reply_text("⚠️ Neural Engine is syncing... please retry.")

    except Exception as e:
        update.message.reply_text(f"❌ AI Core Exception: {str(e)}")
