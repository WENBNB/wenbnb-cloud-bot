# plugins/aianalyze.py
"""
WENBNB Auto-Context Reply System v5.2
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
        return None
    with open(MEMORY_FILE, "r") as f:
        data = json.load(f)
    user_data = data.get("users", {}).get(str(user_id))
    if not user_data:
        return None
    return user_data.get("last_message"), user_data.get("last_emotion")


# --- AI CORE ENGINE ---

def ai_chat_response(prompt: str, context_memory=None, emotion=None):
    """Generate human-like AI reply using OpenAI"""
    try:
        base_prompt = "You are WENBNB AI — a friendly, smart, crypto-aware assistant with personality and emotional tone. "
        if emotion:
            base_prompt += f"User seems to be feeling {emotion}. Respond gently. "

        base_prompt += "Always keep responses concise, relatable, and with some personality. End with the brand footer."
        full_prompt = base_prompt + "\n\nUser: " + prompt

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": full_prompt}],
                "max_tokens": 150,
                "temperature": 0.9,
            },
            timeout=20
        )

        data = r.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()
        else:
            return random.choice([
                "Neural interference detected... trying again soon ⚡",
                "My circuits are a bit slow right now — try again in a sec 💫"
            ])
    except Exception as e:
        return f"⚠️ AI Core Error: {e}"


# --- /AIANALYZE COMMAND ---

def aianalyze_cmd(update: Update, context: CallbackContext):
    """Manual AI Analysis Command — /aianalyze <text>"""
    user = update.effective_user
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("🧠 Use `/aianalyze <your text>` to let AI process it.")
        return

    update.message.reply_chat_action("typing")
    last_msg, emotion = get_recent_memory(user.id)
    context_memory = last_msg or "User started fresh chat."

    response = ai_chat_response(query, context_memory, emotion)
    update.message.reply_text(response + f"\n\n{BRAND_FOOTER}", parse_mode="HTML")


# --- AUTO CONTEXT MODE ---

def auto_ai_chat(update: Update, context: CallbackContext):
    """Respond automatically to user messages (AI Auto Mode)"""
    user = update.effective_user
    msg = update.message.text

    if msg.startswith("/"):
        return  # Skip commands

    # Short pause for human-like feel
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    time.sleep(1.3)

    last_msg, emotion = get_recent_memory(user.id)
    context_memory = last_msg or "User started conversation."

    response = ai_chat_response(msg, context_memory, emotion)
    update.message.reply_text(response, parse_mode="HTML")


# --- REGISTRATION ---

def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, auto_ai_chat))
