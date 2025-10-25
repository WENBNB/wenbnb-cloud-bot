"""
WENBNB AI Analyzer v8.4-Pro — Emotion Sync Edition
────────────────────────────────────────────────────
• Integrates Unified Emotion Engine (emotion_ai.py)
• Infuses emotional tone into AI analysis & replies
• Creates real-time “Neural Vibe” connection for users
"""

import os, requests, json, time, random
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from plugins import emotion_ai  # ❤️ Unified Emotion Engine link

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7"
MEMORY_FILE = "memory_data.json"

# === MEMORY LOAD ===
def get_recent_memory(user_id):
    if not os.path.exists(MEMORY_FILE):
        return None
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    user_data = data.get("users", {}).get(str(user_id))
    if not user_data:
        return None
    return user_data.get("last_message"), user_data.get("last_emotion")

# === AI CORE RESPONSE ===
def ai_chat_response(prompt: str, emotion_hint: str = None):
    """Generate emotionally adaptive reply using OpenAI"""
    try:
        base_prompt = (
            "You are WENBNB AI — an emotionally intelligent, crypto-aware assistant. "
            "Always respond with warmth, a little wit, and concise insight. "
            "Keep it human-feeling — not robotic.\n\n"
        )

        if emotion_hint:
            base_prompt += f"Current user mood context: {emotion_hint}\n\n"

        full_prompt = f"{base_prompt}User: {prompt}"

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": full_prompt}],
                "max_tokens": 180,
                "temperature": 0.9,
            },
            timeout=20,
        )

        data = r.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return random.choice([
                "Neural interference detected... syncing tone again ⚡",
                "Hmm... the vibe feels off — recalibrating 💫"
            ])
    except Exception as e:
        return f"⚠️ AI Core Error: {e}"

# === /AIANALYZE COMMAND ===
def aianalyze_cmd(update: Update, context: CallbackContext):
    """Manual AI emotional analysis — /aianalyze <your text>"""
    user = update.effective_user
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("🧠 Use `/aianalyze <your text>` to get emotional AI insight.")
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # 🧩 Inject Emotion Sync
    emotion_prefix = emotion_ai.get_emotion_prefix(user.id, query)
    response = ai_chat_response(query, emotion_prefix)

    reply = f"{emotion_prefix}\n\n{response}\n\n{BRAND_FOOTER}"
    update.message.reply_text(reply, parse_mode="HTML")

# === AUTO REPLY MODE ===
def auto_ai_chat(update: Update, context: CallbackContext):
    """Emotionally aware auto chat"""
    user = update.effective_user
    msg = update.message.text

    if msg.startswith("/"):
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    time.sleep(random.uniform(1.1, 1.8))

    emotion_prefix = emotion_ai.get_emotion_prefix(user.id, msg)
    response = ai_chat_response(msg, emotion_prefix)

    update.message.reply_text(f"{emotion_prefix}\n\n{response}\n\n{BRAND_FOOTER}", parse_mode="HTML")

# === REGISTER ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, auto_ai_chat))
    print("✅ Loaded plugin: plugins.aianalyze (v8.4-Pro — Emotion Sync Edition)")
