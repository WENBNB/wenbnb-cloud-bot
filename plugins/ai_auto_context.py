"""
AI Auto-Conversation System v8.6 — Contextual Neural Reply Engine (ProStable)
Transforms the bot into a free-talking conversational AI.
Now powered via REST API — fully compatible with OpenAI >= 1.0.0
Integrated with WENBNB Neural Engine — Emotion Context Intelligence 24×7
"""

import os, time, requests
from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext

# === Config ===
AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = "gpt-4o-mini"
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Contextual Intelligence 24×7"

# === Memory ===
conversation_memory = {}

# === Universal AI Request ===
def ai_generate(prompt):
    """Calls OpenAI REST API for chat response."""
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}"},
            json={
                "model": AI_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.85,
                "max_tokens": 250,
            },
            timeout=20,
        )
        data = r.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "⚡ Neural silence detected.")
    except Exception as e:
        return f"⚠️ AI Core Error: {e}"

# === Generate AI Reply ===
def generate_ai_reply(user_id, user_message):
    """Context-based AI response with emotional tone."""
    global conversation_memory

    context = conversation_memory.get(user_id, "")
    prompt = (
        "You are WENBNB AI — a warm, emotionally intelligent crypto assistant.\n"
        "Keep replies human, empathetic, a little witty, and context-aware.\n"
        f"Conversation so far:\n{context}\n\n"
        f"User: {user_message}\nAI:"
    )

    ai_text = ai_generate(prompt)
    conversation_memory[user_id] = (context + f"\nUser: {user_message}\nAI: {ai_text}")[-1200:]

    return ai_text

# === Telegram Handler ===
def ai_auto_reply(update: Update, context: CallbackContext):
    """Auto conversation mode — replies to all normal text messages."""
    user_id = update.effective_user.id
    user_message = update.message.text.strip()

    # Ignore commands like /start or /help
    if user_message.startswith("/"):
        return

    update.message.chat.send_action("typing")
    time.sleep(1.1)

    ai_response = generate_ai_reply(user_id, user_message)
    update.message.reply_text(f"{ai_response}\n\n{BRAND_TAG}")

# === Register Handler ===
def register_handlers(dp):
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply))
