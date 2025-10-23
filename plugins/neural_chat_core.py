"""
WENBNB Neural Chat Core v7.6 — Hybrid + AI Dashboard Edition
Default AI Mode ON + /ai_mode toggle + /ai_status monitor
Powered by WENBNB Neural Engine — Emotional Context Intelligence 24×7
"""

import openai, os, time, datetime, psutil
from telegram import Update
from telegram.ext import MessageHandler, Filters, CommandHandler, CallbackContext

openai.api_key = os.getenv("OPENAI_API_KEY")

# === Brand Tag ===
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotional Context Intelligence 24×7"

# === State Variables ===
AI_MODE = True
ADMIN_IDS = [123456789]  # 🔧 Replace with your Telegram ID
conversation_memory = {}
last_emotion = "neutral"
start_time = datetime.datetime.now()

# === Emotion Detection ===
def detect_emotion(message):
    global last_emotion
    try:
        analysis = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Detect emotion (happy, sad, angry, calm, excited, neutral)."},
                {"role": "user", "content": message}
            ],
            max_tokens=10,
            temperature=0.4
        )
        emotion = analysis["choices"][0]["message"]["content"].strip().lower()
        last_emotion = emotion if emotion in ["happy", "sad", "angry", "calm", "excited"] else "neutral"
        return last_emotion
    except:
        return "neutral"

# === Generate Neural Reply ===
def generate_neural_reply(user_id, message):
    global conversation_memory, last_emotion
    context = conversation_memory.get(user_id, "")
    emotion = detect_emotion(message)

    prompt = (
        f"You are WENBNB AI — an empathetic crypto assistant.\n"
        f"User emotion: {emotion}\n"
        f"Recent context:\n{context}\n"
        f"User: {message}\nAI:"
    )

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are WENBNB Neural AI. Respond with empathy and intelligence."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=250
        )

        ai_text = completion["choices"][0]["message"]["content"].strip()
        conversation_memory[user_id] = (context + f"\nUser: {message}\nAI: {ai_text}")[-1500:]

        emotion_icon = {
            "happy": "😊", "sad": "😢", "angry": "😠",
            "excited": "🤩", "calm": "🧘", "neutral": "🤖"
        }.get(emotion, "🤖")

        return f"{emotion_icon} {ai_text}\n\n{BRAND_TAG}"

    except Exception as e:
        return f"⚠️ Neural Core Error: {e}"

# === Chat Handler ===
def neural_chat_handler(update: Update, context: CallbackContext):
    global AI_MODE
    if not AI_MODE:
        return
    message = update.message.text.strip()
    if message.startswith("/"):
        return

    user_id = update.effective_user.id
    update.message.chat.send_action("typing")
    time.sleep(1.2)

    ai_reply = generate_neural_reply(user_id, message)
    update.message.reply_text(ai_reply, parse_mode="HTML")

# === Toggle Command ===
def toggle_ai_mode(update: Update, context: CallbackContext):
    global AI_MODE
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("🚫 Only admin can toggle AI mode.")
        return

    args = context.args
    if not args:
        update.message.reply_text(f"🧠 AI Mode: {'ON ✅' if AI_MODE else 'OFF ❌'}")
        return

    if args[0].lower() == "on":
        AI_MODE = True
        update.message.reply_text("🔥 Neural Core activated.\n" + BRAND_TAG)
    elif args[0].lower() == "off":
        AI_MODE = False
        update.message.reply_text("🧊 Neural Core paused. Command mode only.")
    else:
        update.message.reply_text("⚙️ Usage: /ai_mode on OR /ai_mode off")

# === Status Command ===
def ai_status(update: Update, context: CallbackContext):
    uptime = datetime.datetime.now() - start_time
    mem_usage = sum(len(v) for v in conversation_memory.values())
    cpu_usage = psutil.cpu_percent()
    ram_usage = psutil.virtual_memory().percent

    status_msg = (
        "🧠 <b>WENBNB Neural Status</b>\n\n"
        f"⚙️ Mode: {'<b>Active ✅</b>' if AI_MODE else '<b>Paused ❌</b>'}\n"
        f"💫 Last Emotion: <b>{last_emotion}</b>\n"
        f"📊 Memory Context: <b>{mem_usage} chars</b>\n"
        f"🕒 Uptime: <b>{str(uptime).split('.')[0]}</b>\n"
        f"🧩 System Load: <b>CPU {cpu_usage}% | RAM {ram_usage}%</b>\n\n"
        f"{BRAND_TAG}"
    )

    update.message.reply_text(status_msg, parse_mode="HTML")

# === Register Handler ===
def register_handlers(dp):
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, neural_chat_handler))
    dp.add_handler(CommandHandler("ai_mode", toggle_ai_mode))
    dp.add_handler(CommandHandler("ai_status", ai_status))
