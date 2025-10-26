"""
WENBNB AI Analyzer v8.5 — EmotionLink Prime
────────────────────────────────────────────
Integrates:
 • Emotion Detection (TextBlob engine)
 • Memory Persistence (Unified Memory System)
 • Adaptive Human Tone — No 🤖 spam
"""

import os, json, time, random, requests
from textblob import TextBlob
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MEMORY_FILE = "user_memory.json"
BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7"

# ==== Memory Helpers ====

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ==== Emotion Detection ====

def analyze_emotion(text):
    blob = TextBlob(text)
    p = blob.sentiment.polarity
    if p > 0.35:
        return "Positive", "🌞 Tone registered as: Positive"
    elif p < -0.35:
        return "Negative", "🌧 Tone registered as: Reflective"
    else:
        return "Balanced", "🌙 Tone registered as: Calm & Neutral"

# ==== AI Core Response ====

def ai_chat_response(prompt, emotion_hint=None):
    try:
        base_prompt = (
            "You are WENBNB AI — a warm, emotionally aware crypto companion. "
            "Your goal: sound like a thoughtful human, never robotic. "
            "Use a conversational tone with emotional awareness.\n\n"
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
            return "Neural link glitch — recalibrating emotional tone 💫"
    except Exception as e:
        return f"⚠️ AI Core Error: {e}"

# ==== Update Memory Log ====

def update_memory(user_id, message, mood):
    memory = load_memory()
    if str(user_id) not in memory:
        memory[str(user_id)] = {"entries": []}

    memory[str(user_id)]["entries"].append({
        "text": message,
        "mood": mood,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    memory[str(user_id)]["entries"] = memory[str(user_id)]["entries"][-10:]
    save_memory(memory)

# ==== /aianalyze Command ====

def aianalyze_cmd(update: Update, context: CallbackContext):
    user = update.effective_user
    query = " ".join(context.args)
    if not query:
        update.message.reply_text("🧠 Use `/aianalyze <your text>` to analyze your vibe.")
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    mood, mood_line = analyze_emotion(query)
    ai_reply = ai_chat_response(query, mood)

    update_memory(user.id, query, mood)

    reply = (
        f"{mood_line}\n\n"
        f"{ai_reply}\n\n"
        f"{BRAND_FOOTER}"
    )

    update.message.reply_text(reply, parse_mode="HTML")

# ==== Auto Chat ====

def auto_ai_chat(update: Update, context: CallbackContext):
    msg = update.message.text
    if msg.startswith("/"):
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    time.sleep(random.uniform(1.0, 1.6))

    mood, mood_line = analyze_emotion(msg)
    ai_reply = ai_chat_response(msg, mood)

    update_memory(update.effective_user.id, msg, mood)

    update.message.reply_text(
        f"{mood_line}\n\n{ai_reply}\n\n{BRAND_FOOTER}",
        parse_mode="HTML"
    )

# ==== Register ====

def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, auto_ai_chat))
    print("✅ Loaded plugin: aianalyze.py v8.5 — EmotionLink Prime")
