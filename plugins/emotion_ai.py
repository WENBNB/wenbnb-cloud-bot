"""
Emotion AI Module v7.0 Beta
Integrates emotional tone detection into WENBNB Neural Engine replies.
Makes AI responses adaptive, human-like, and emotionally aware.
"""

import openai, os, time
from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext

openai.api_key = os.getenv("OPENAI_API_KEY")
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotion Context Mode v7.0"

# === Emotion Detection ===
def detect_emotion(text):
    """Analyze tone of user message"""
    try:
        analysis = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You analyze emotions from messages and return one word tone."},
                {"role": "user", "content": f"Message: {text}\nReturn only tone like: happy, sad, angry, excited, neutral."}
            ],
            temperature=0.5,
            max_tokens=10,
        )
        emotion = analysis["choices"][0]["message"]["content"].strip().lower()
        return emotion
    except:
        return "neutral"

# === Emotionally Adaptive Reply ===
def generate_emotional_reply(user_message, emotion):
    """Generate tone-aware reply"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": f"You are WENBNB AI, an emotionally intelligent crypto assistant."},
                {"role": "user", "content": f"User emotion: {emotion}. Message: {user_message}. Reply empathetically."}
            ],
            temperature=0.9,
            max_tokens=200,
        )
        reply = response["choices"][0]["message"]["content"].strip()
        return reply
    except Exception as e:
        return f"⚠️ Emotion AI unavailable: {e}"

# === Telegram Handler ===
def emotion_ai_handler(update: Update, context: CallbackContext):
    user_message = update.message.text.strip()
    if user_message.startswith("/"):
        return

    update.message.chat.send_action("typing")
    time.sleep(1.2)

    emotion = detect_emotion(user_message)
    reply = generate_emotional_reply(user_message, emotion)

    emotion_icon = {
        "happy": "😊", "sad": "😢", "angry": "😠",
        "excited": "🤩", "neutral": "🤖"
    }.get(emotion, "🤖")

    update.message.reply_text(f"{emotion_icon} {reply}\n\n{BRAND_TAG}")

# === Register Handler ===
def register_handlers(dp):
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, emotion_ai_handler))
