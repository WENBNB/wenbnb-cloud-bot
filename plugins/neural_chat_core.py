"""
WENBNB Neural Chat Core v7.5 — AI Soul Merge Edition
Integrates Context, Emotion, and Memory systems for deeply natural AI replies.
"""

import openai, os, time
from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext

openai.api_key = os.getenv("OPENAI_API_KEY")
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotional Context Intelligence 24×7"

# === Persistent Memory Storage ===
conversation_memory = {}

# === Emotion Detection ===
def detect_emotion(message):
    """Analyze tone of user message."""
    try:
        analysis = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Detect the emotional tone (happy, sad, angry, calm, excited, neutral) of the following message."},
                {"role": "user", "content": message}
            ],
            max_tokens=10,
            temperature=0.4
        )
        emotion = analysis["choices"][0]["message"]["content"].strip().lower()
        return emotion if emotion in ["happy", "sad", "angry", "excited", "calm"] else "neutral"
    except:
        return "neutral"

# === Generate Neural Reply ===
def generate_neural_reply(user_id, message):
    """Main AI response system combining context, emotion, and memory."""
    global conversation_memory
    context = conversation_memory.get(user_id, "")
    emotion = detect_emotion(message)

    # Context prompt with emotional alignment
    prompt = (
        f"You are WENBNB AI — a friendly, emotionally intelligent crypto assistant.\n"
        f"User emotion: {emotion}\n"
        f"Recent context:\n{context}\n"
        f"User: {message}\nAI:"
    )

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are WENBNB Neural AI. Respond naturally with empathy, logic, and personality."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=250
        )

        ai_text = completion["choices"][0]["message"]["content"].strip()

        # Memory context limited to 1.5k chars
        conversation_memory[user_id] = (
            (context + f"\nUser: {message}\nAI: {ai_text}")[-1500:]
        )

        # Emotion icons
        emotion_icon = {
            "happy": "😊", "sad": "😢", "angry": "😠",
            "excited": "🤩", "calm": "🧘", "neutral": "🤖"
        }.get(emotion, "🤖")

        return f"{emotion_icon} {ai_text}\n\n{BRAND_TAG}"

    except Exception as e:
        return f"⚠️ Neural Core Error: {e}"

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
