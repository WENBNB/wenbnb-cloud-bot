"""
WENBNB Neural Analyzer v8.3-Pro — Emotional Realism Mode
──────────────────────────────────────────────────────────────
• Reads tone, emotion drift, and user context
• Feeds mood from emotion_sync + emotion_stabilizer
• Responds like a human — warm, emotional, aware
• Adds expressive hashtags and vibe reflection
"""

import os, requests, json, time, random
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from plugins.emotion_sync import get_emotion_prefix
from plugins.emotion_stabilizer import get_stabilized_emotion

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7"
MEMORY_FILE = "memory_data.json"

# === MEMORY HELPER ===
def get_recent_memory(user_id):
    if not os.path.exists(MEMORY_FILE):
        return None
    try:
        with open(MEMORY_FILE, "r") as f:
            data = json.load(f)
        u = data.get("users", {}).get(str(user_id))
        if not u:
            return None
        return u.get("last_message"), u.get("last_emotion")
    except Exception:
        return None, None


# === OPENAI WRAPPER ===
def ai_chat_response(prompt: str, emotion_label=None, emoji_prefix=None):
    """Generates emotionally adaptive AI response"""
    try:
        base_prompt = (
            "You are WENBNB AI — a friendly, emotionally intelligent crypto assistant. "
            "Keep responses conversational, natural, and slightly playful. "
            "You are aware of user's emotional tone: "
            f"{emotion_label or 'neutral'}. "
            "Use expressive language when needed and close with 1–2 relevant hashtags."
        )
        full_prompt = f"{emoji_prefix or ''} {base_prompt}\n\nUser: {prompt}"

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": full_prompt}],
                "max_tokens": 180,
                "temperature": 0.9,
            },
            timeout=25,
        )

        data = r.json()
        if "choices" in data:
            text = data["choices"][0]["message"]["content"].strip()
            return text
        else:
            return random.choice([
                "Neural static detected... re-syncing soon 💫",
                "Hmm, lost the vibe — give me a sec to recalibrate ⚡"
            ])
    except Exception as e:
        return f"⚠️ Neural Error: {e}"


# === MAIN /AIANALYZE ===
def aianalyze_cmd(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("🧠 Use `/aianalyze <your text>` to let me process it emotionally.")
        return

    # Typing effect
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    time.sleep(1.2)

    # Sync short-term emotion
    emoji_prefix = get_emotion_prefix(user_id, query)

    # Stabilize longer-term tone
    emotion_label = get_stabilized_emotion(user_id, query)

    # AI response
    response = ai_chat_response(query, emotion_label, emoji_prefix)

    # Build final message
    msg = (
        f"{emoji_prefix} <b>Neural Insight:</b>\n{response}\n\n"
        f"💫 <i>Current Mood:</i> {emotion_label}\n\n"
        f"{BRAND_TAG}"
    )

    update.message.reply_text(msg, parse_mode="HTML")


# === REGISTER ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze_cmd))
    print("✅ Loaded plugin: aianalyze.py (v8.3-Pro — Emotional Realism Mode)")
