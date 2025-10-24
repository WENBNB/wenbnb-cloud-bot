# plugins/aianalyze.py
"""
WENBNB Auto-Context Reply System v8.2
Mode: Neural Conversational Core — “Think. Feel. Respond.”
"""

import os, requests, json, time, random
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"

# --- MEMORY BRIDGE ---
MEMORY_FILE = "memory_data.json"

def get_recent_memory(user_id):
    if not os.path.exists(MEMORY_FILE):
        return None, None
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    user_data = data.get("users", {}).get(str(user_id))
    if not user_data:
        return None, None
    return user_data.get("last_message"), user_data.get("last_emotion")


# --- AI CORE ENGINE ---

def ai_chat_response(prompt: str, context_memory=None, emotion=None):
    """Generate intelligent, context-aware AI reply using OpenAI"""
    try:
        base_prompt = (
            "You are WENBNB AI — a witty, emotionally tuned crypto assistant. "
            "Analyze or reply naturally depending on the user's tone. "
            "If the query looks like a market topic, provide an insight. "
            "If it feels casual, respond conversationally with personality. "
        )
        if emotion:
            base_prompt += f"The user seems to be feeling {emotion}. Respond accordingly. "

        base_prompt += "End your message warmly without repetition."
        full_prompt = base_prompt + "\n\nUser: " + prompt

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": full_prompt}],
                "max_tokens": 180,
                "temperature": 0.8,
            },
            timeout=20
        )

        data = r.json()

        # --- Enhanced error handling ---
        if "error" in data:
            msg = data["error"].get("message", "Unknown issue")
            return f"⚙️ AI Analyzer Offline: {msg}"

        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"].strip()

        return random.choice([
            "⚡ Neural interference detected... recalibrating soon.",
            "💫 I felt that, but my circuits need a breather. Try again shortly."
        ])

    except Exception as e:
        return f"⚠️ AI Core Error: {e}"


# --- /AIANALYZE COMMAND ---

def aianalyze_cmd(update: Update, context: CallbackContext):
    """Manual AI Analysis Command — /aianalyze <text>"""
    user = update.effective_user
    query = " ".join(context.args)

    if not query:
        update.message.reply_text("🧠 Use `/aianalyze <your text>` to let AI process it.", parse_mode="HTML")
        return

    update.message.chat.send_action(action="typing")

    last_msg, emotion = get_recent_memory(user.id)
    context_memory = last_msg or "User started fresh chat."

    try:
        response = ai_chat_response(query, context_memory, emotion)
        update.message.reply_text(f"{response}\n\n{BRAND_FOOTER}", parse_mode="HTML")
    except Exception as e:
        update.message.reply_text(f"⚠️ AI Analysis failed: {e}\n\n{BRAND_FOOTER}", parse_mode="HTML")


# --- AUTO CONTEXT MODE ---

def auto_ai_chat(update: Update, context: CallbackContext):
    """Respond automatically to user messages (AI Auto Mode)"""
    user = update.effective_user
    msg = update.message.text

    if msg.startswith("/"):
        return  # Skip commands

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    time.sleep(1.2)

    last_msg, emotion = get_recent_memory(user.id)
    context_memory = last_msg or "User started conversation."

    response = ai_chat_response(msg, context_memory, emotion)
    update.message.reply_text(response, parse_mode="HTML")


# --- REGISTRATION ---

def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, auto_ai_chat))
