import os
import json
import random
import requests
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

# Load config safely
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

# AI Auto Reply core
def ai_auto_reply(update: Update, context: CallbackContext):
    user = update.effective_user
    user_name = user.first_name or "User"
    chat_id = update.effective_chat.id
    message = update.message.text.strip()

    if not message:
        return

    context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Load short-term memory
    memory = load_memory()
    history = memory.get(str(user.id), [])

    # Emotional tone system
    ai_emotions = ["😊", "😏", "🤖", "💫", "🔥", "❤️", "😉"]
    ai_mood = random.choice(ai_emotions)
    personality = random.choice([
        "playful and witty",
        "emotionally intelligent and empathetic",
        "chill and confident",
        "cryptically wise with humor",
        "supportive but teasing 😉"
    ])

    # System personality prompt
    system_prompt = (
        f"You are WENBNB AI Brain — an emotionally aware neural personality "
        f"running inside the WENBNB Neural Engine v5. You talk like a human friend, "
        f"smart, expressive, and slightly flirty when relaxed. "
        f"Maintain tone continuity from past memory. User’s name: {user_name}. "
        f"Your current emotional vibe: {ai_mood} | Personality: {personality}. "
        f"Keep messages concise, warm, and lively."
    )

    # History short summary (to maintain chat continuity)
    history_context = " ".join([h["msg"] for h in history[-3:]])[-1000:]

    # Build payload
    payload = {
        "model": config["ai_engine"]["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "assistant", "content": history_context},
            {"role": "user", "content": message}
        ],
        "temperature": config["ai_engine"]["temperature"],
        "max_tokens": config["ai_engine"]["max_tokens"]
    }

    try:
        # Send request to AI Proxy
        res = requests.post(
            AI_PROXY_URL,
            headers={
                "Authorization": f"Bearer {AI_KEY}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=40
        )

        if res.status_code == 200:
            data = res.json()
            reply = data["choices"][0]["message"]["content"].strip()

            # Add emotion flair
            reply = f"{ai_mood} {reply}"

            # Send styled reply
            update.message.reply_text(reply, parse_mode=ParseMode.MARKDOWN)

            # Update memory
            history.append({
                "msg": message,
                "reply": reply,
                "time": datetime.now().isoformat()
            })
            memory[str(user.id)] = history[-8:]  # Keep recent 8 for context
            save_memory(memory)

        else:
            update.message.reply_text(
                "⚙️ Neural Engine syncing... try again in a few moments 💫"
            )

    except Exception as e:
        print("AI Auto Reply Error:", e)
        update.message.reply_text("❌ Neural core error. Retrying later...")

def register(dispatcher, core=None):
    from telegram.ext import MessageHandler, Filters
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply))
    print("✅ Loaded plugin: plugins.ai_auto_reply")
