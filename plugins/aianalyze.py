"""
WENBNB AI Analyzer v8.6.1-ProStable+ — EmotionLink Prime+ (Render Debug Edition)
────────────────────────────────────────────
Integrates:
 • Emotion Detection (TextBlob engine)
 • Memory Persistence (Unified Memory System)
 • Adaptive Human Tone — No 🤖 spam
 • Render Debug-Safe Logging + Auto-Retry
"""

import os, json, time, random, requests, traceback
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
        return "Positive", "🌞 Mood vibe detected → Positive"
    elif p < -0.35:
        return "Negative", "🌧 Mood vibe detected → Reflective"
    else:
        return "Neutral", "🌙 Mood vibe detected → Calm & Balanced"

# ==== AI Core Response ====

def ai_chat_response(prompt, emotion_hint=None):
    base_prompt = (
        "You are WENBNB AI — a warm, emotionally aware crypto companion. "
        "Your goal: sound like a thoughtful human, never robotic. "
        "Always blend insight with empathy.\n\n"
    )

    if emotion_hint:
        base_prompt += f"Current user emotional tone: {emotion_hint}\n\n"

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 200,
        "temperature": 0.9,
    }

    # === Safe API call with 1 retry ===
    for attempt in range(2):
        try:
            print(f"🧩 [DEBUG] Sending OpenAI request (try {attempt+1}) → {prompt[:60]}...")
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {AI_API_KEY}"},
                json=payload,
                timeout=25,
            )
            data = r.json()
            print("🧠 [DEBUG] Response:", json.dumps(data, indent=2)[:400])

            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"].strip()
            elif "error" in data:
                err_msg = data["error"].get("message", "Unknown OpenAI Error")
                return f"⚠️ OpenAI Error: {err_msg}"
        except requests.exceptions.Timeout:
            print("⏳ [WARN] OpenAI timeout — retrying...")
            time.sleep(1.5)
        except Exception as e:
            traceback.print_exc()
            return f"⚠️ AI Core Exception: {e}"

    return "💫 Neural silence — emotional sync timed out, try again later."

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

    # Limit memory to last 10 entries
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

    try:
        mood, mood_line = analyze_emotion(query)
        ai_reply = ai_chat_response(query, mood)
        update_memory(user.id, query, mood)
        reply = f"{mood_line}\n\n{ai_reply}\n\n{BRAND_FOOTER}"
        update.message.reply_text(reply, parse_mode="HTML")
    except Exception as e:
        traceback.print_exc()
        update.message.reply_text(f"⚠️ Analyzer internal error: {e}")

# ==== Auto Chat ====

def auto_ai_chat(update: Update, context: CallbackContext):
    msg = update.message.text
    if msg.startswith("/"):
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    time.sleep(random.uniform(1.0, 1.6))

    try:
        mood, mood_line = analyze_emotion(msg)
        ai_reply = ai_chat_response(msg, mood)
        update_memory(update.effective_user.id, msg, mood)
        update.message.reply_text(
            f"{mood_line}\n\n{ai_reply}\n\n{BRAND_FOOTER}",
            parse_mode="HTML"
        )
    except Exception as e:
        traceback.print_exc()
        update.message.reply_text(f"⚠️ Auto-chat error: {e}")

# ==== Register ====

def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, auto_ai_chat))
    print("✅ Loaded plugin: aianalyze.py v8.6.1-ProStable+ — EmotionLink Prime+ (Debug Edition)")
