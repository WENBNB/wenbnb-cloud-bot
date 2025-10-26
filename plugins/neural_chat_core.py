"""
WENBNB Neural Chat Core v8.6-ProStable
Unified REST AI + Emotion Sync Integration
Default AI Mode ON + /ai_mode toggle + /ai_status monitor
"""

import os, time, datetime, psutil, requests
from telegram import Update
from telegram.ext import MessageHandler, Filters, CommandHandler, CallbackContext

# === API & Config ===
AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = "gpt-4o-mini"

BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7"
AI_MODE = True
ADMIN_IDS = [123456789]  # 🔧 replace with your Telegram ID
conversation_memory = {}
last_emotion = "neutral"
start_time = datetime.datetime.now()

# === Helper: AI Generate ===
def ai_generate(prompt, emotion_hint=None):
    """Universal AI call via REST (no SDK dependency)"""
    try:
        prefix = (
            "You are WENBNB AI — an emotionally intelligent, crypto-aware assistant. "
            "Keep replies human, witty, and context-aware.\n\n"
        )
        if emotion_hint:
            prefix += f"User mood context: {emotion_hint}\n\n"

        data = {
            "model": AI_MODEL,
            "messages": [{"role": "user", "content": prefix + prompt}],
            "temperature": 0.9,
            "max_tokens": 250,
        }

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}"},
            json=data,
            timeout=20,
        )

        res = r.json()
        return res.get("choices", [{}])[0].get("message", {}).get("content", "⚡ Neural silence detected.")
    except Exception as e:
        return f"⚠️ Neural Core Error: {str(e)}"

# === Emotion Detection (Light heuristic) ===
def detect_emotion(message):
    msg = message.lower()
    if any(x in msg for x in ["happy", "great", "love", "awesome", "amazing", "excited"]):
        return "happy"
    elif any(x in msg for x in ["sad", "bad", "depressed", "down", "tired"]):
        return "sad"
    elif any(x in msg for x in ["angry", "mad", "furious", "rage"]):
        return "angry"
    elif any(x in msg for x in ["calm", "peaceful", "okay", "fine"]):
        return "calm"
    else:
        return "neutral"

# === Generate Reply ===
def generate_neural_reply(user_id, message):
    global conversation_memory, last_emotion
    context = conversation_memory.get(user_id, "")
    emotion = detect_emotion(message)
    last_emotion = emotion

    prompt = (
        f"User emotion: {emotion}\n"
        f"Recent context:\n{context}\n\n"
        f"User: {message}\nAI:"
    )

    ai_text = ai_generate(prompt, emotion_hint=emotion)
    conversation_memory[user_id] = (context + f"\nUser: {message}\nAI: {ai_text}")[-1500:]

    emotion_icon = {
        "happy": "😊", "sad": "😢", "angry": "😠",
        "excited": "🤩", "calm": "🧘", "neutral": "💫"
    }.get(emotion, "💫")

    return f"{emotion_icon} {ai_text}\n\n{BRAND_TAG}"

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
