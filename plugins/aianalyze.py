"""
WENBNB AI Analyzer v8.6.4-ProStable++ — EmotionSync Resilient Mode
───────────────────────────────────────────────────────────────
• Emotion Detection (TextBlob)
• Adaptive Human Tone + Retry Logic
• Auto-reconnect when OpenAI API lags or fails
• Unified Memory System + Mood Tracking
• Render Debug-Safe (no silent freeze)
"""

import os, json, time, random, requests, traceback
from textblob import TextBlob
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MEMORY_FILE = "user_memory.json"
BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7"

# === Memory ===
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# === Emotion Detection ===
def analyze_emotion(text):
    blob = TextBlob(text)
    p = blob.sentiment.polarity
    if p > 0.35:
        return "Positive", "🌞 Mood vibe detected → Positive"
    elif p < -0.35:
        return "Reflective", "🌧 Mood vibe detected → Reflective"
    else:
        return "Balanced", "🌙 Mood vibe detected → Calm & Balanced"

# === OpenAI Request (with Retry Protection) ===
def call_openai(prompt, emotion_hint):
    base_prompt = (
        "You are WENBNB AI — a warm, emotionally aware crypto companion. "
        "Always reply naturally, with empathy and balance.\n\n"
        f"User mood context: {emotion_hint}\n\n"
        f"User: {prompt}"
    )

    for attempt in range(3):  # Retry 3 times if it fails
        try:
            res = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {AI_API_KEY}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": base_prompt}],
                    "max_tokens": 220,
                    "temperature": 0.9,
                },
                timeout=25,
            )

            data = res.json()
            print(f"[AI DEBUG] Attempt {attempt+1} → {data}")

            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"].strip()

            if "error" in data:
                print(f"[AI ERROR] {data['error']}")
                time.sleep(2)
                continue

        except requests.exceptions.Timeout:
            print(f"⏳ Timeout on attempt {attempt+1}, retrying...")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Exception in call_openai(): {e}")
            time.sleep(1.5)

    return None

# === AI Response Logic (with graceful fallback) ===
def ai_chat_response(prompt, emotion_hint):
    reply = call_openai(prompt, emotion_hint)
    if reply:
        return reply

    # Fallback (offline tone)
    fallback_lines = [
        "Haha, neural link flickered for a sec 😅 — still got my thoughts synced:",
        "Hmm… cloud static interfered ⚡ but I caught the emotional wave:",
        "HQ lagged out 🛰️, but your vibe came through clear:",
        "Lost the OpenAI uplink for a moment 🤖 but here’s my pulse on that:"
    ]
    casual_reply = random.choice([
        "Feels like a moment for patience and focus.",
        "That energy you’re feeling? It’s shifting fast — stay tuned. ⚡",
        "Always trust your internal signal — the markets follow mood.",
        "Momentum’s building; I can sense it in your tone ✨"
    ])
    return f"{random.choice(fallback_lines)}\n\n{casual_reply}"

# === Memory Log ===
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

# === /aianalyze ===
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
    update.message.reply_text(f"{mood_line}\n\n{ai_reply}\n\n{BRAND_FOOTER}", parse_mode="HTML")

# === Auto Chat ===
def auto_ai_chat(update: Update, context: CallbackContext):
    msg = update.message.text
    if msg.startswith("/"):
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    time.sleep(random.uniform(1.0, 1.6))
    mood, mood_line = analyze_emotion(msg)
    ai_reply = ai_chat_response(msg, mood)
    update_memory(update.effective_user.id, msg, mood)
    update.message.reply_text(f"{mood_line}\n\n{ai_reply}\n\n{BRAND_FOOTER}", parse_mode="HTML")

# === Register ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, auto_ai_chat))
    print("✅ Loaded plugin: aianalyze.py v8.6.4-ProStable++ (Resilient Mode)")
