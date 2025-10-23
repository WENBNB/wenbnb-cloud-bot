"""
AI Auto-Conversation System v6.2 — Contextual Neural Reply Engine
Transforms the bot into a free-talking AI assistant.
Fully integrated with WENBNB Neural Engine & Emotion Context Memory v4.1
"""

import openai, time, os
from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext

openai.api_key = os.getenv("OPENAI_API_KEY")
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — AI Soul Integration Mode"

# === Emotion-Context Memory ===
conversation_memory = {}

def generate_ai_reply(user_id, user_message):
    """AI contextual response with short memory recall"""
    global conversation_memory

    context = conversation_memory.get(user_id, "")
    prompt = (
        f"You are WENBNB AI, a smart, kind, emotionally intelligent blockchain assistant.\n"
        f"Memory context:\n{context}\n\n"
        f"User: {user_message}\nAI:"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": "You are a friendly crypto AI assistant."},
                      {"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=250,
        )

        ai_text = response["choices"][0]["message"]["content"].strip()
        # Store last 5 messages for user context
        conversation_memory[user_id] = (
            (context + f"\nUser: {user_message}\nAI: {ai_text}")[-1000:]
        )
        return ai_text

    except Exception as e:
        return f"⚠️ AI Core Unavailable: {e}"

# === Telegram Handler ===

def ai_auto_reply(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    user_message = update.message.text.strip()

    # Ignore commands
    if user_message.startswith("/"):
        return

    update.message.chat.send_action("typing")
    time.sleep(1.2)

    ai_response = generate_ai_reply(user_id, user_message)
    update.message.reply_text(f"{ai_response}\n\n{BRAND_TAG}")

# === Register Handler ===
def register_handlers(dp):
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply))
