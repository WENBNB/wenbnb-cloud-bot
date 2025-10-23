"""
Neural Chat Core v7.5 — AI Soul Merge Edition
Combines memory, emotion, and contextual intelligence into one unified system.
Built for WENBNB Neural Engine 24×7 Cloud AI Core.
"""

import openai, os, time
from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext

openai.api_key = os.getenv("OPENAI_API_KEY")
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotional Context Intelligence 24×7"

# === Persistent Memory ===
conversation_memory = {}

# === Emotion Detection ===
def detect_emotion(message):
    """Detect emotional tone of user message"""
    try:
        emotion_response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You detect the emotional tone of user messages. Return only: happy, sad, angry, excited, calm, or neutral."},
                {"role": "user", "content": message}
            ],
            max_tokens=10,
            temperature=0.5
        )
        emotion = emotion_response["choices"][0]["message"]["content"].strip().lower()
        return emotion if emotion in ["happy", "sad", "angry", "excited", "calm"] else "neutral"
    except:
        return "neutral"

# === Unified AI Reply ===
def generate_neural_reply(user_id, message):
    """Generate AI response using context + emotion + memory"""
    global conversation_memory

    context = conversation_memory.get(user_id, "")
    emotion = detect_emotion(message)

    prompt = (
        f"You are WENBNB AI — a compassionate, emotionally intelligent blockchain assistant.\n"
        f"User emotion: {emotion}\n"
        f"Conversation history:\n{context}\n"
        f"User: {message}\nAI:"
    )

    try:
        reply = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are WENBNB Neural AI: smart, witty, kind, emotional, crypto-fluent."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250,
            temperature=0.9
        )

        ai_text = reply["choices"][0]["message"]["content"].strip()

        # Store memory context
        conversation_memory[user_id] = (
            (context + f"\nUser: {message}\nAI: {ai_text}")[-1200:]
        )

        emotion_emoji = {
            "happy": "😊", "sad": "😢", "angry": "😠",
            "excited": "🤩", "calm": "🧘", "neutral": "🤖"
        }.get(emotion, "🤖")

        return f"{emotion_emoji} {ai_text}\n\n{BRAND_TAG}"

    except Exception as e:
        return f"⚠️ Neural Core Unavailable: {e}"

# === Telegram Handler ===
def neural_chat_handler(update: Update, context: CallbackContext):
    message = update.message.text.strip()
    if message.startswith("/"):
        return

    user_id = update.effective_user.id
    update.message.chat.send_action("typing")
    time.sleep(1.3)

    ai_reply = generate_neural_reply(user_id, message)
    update.message.reply_text(ai_reply, parse_mode="HTML")

# === Register Handler ===
def register_handlers(dp):
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, neural_chat_handler))
