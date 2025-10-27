"""
WENBNB AI Analyzer v8.6.4-ProStable++ — EmotionSync + MemoryView Edition
───────────────────────────────────────────────────────────────────────────────
• Emotion Detection (TextBlob engine)
• Memory Persistence + /memory + /forget commands
• Adaptive Human Tone — conversational fallback
• AutoRecovery for OpenAI timeouts
"""

import os, json, time, random, requests, traceback
from textblob import TextBlob
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MEMORY_FILE = "user_memory.json"
BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7"

# === Memory Helpers ===
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def update_memory(user_id, message, mood):
    memory = load_memory()
    uid = str(user_id)
    if uid not in memory:
        memory[uid] = {"entries": []}
    memory[uid]["entries"].append({
        "text": message,
        "mood": mood,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    memory[uid]["entries"] = memory[uid]["entries"][-10:]
    save_memory(memory)

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

# === OpenAI Call ===
def call_openai(prompt, emotion_hint):
    try:
        base_prompt = (
            "You are WENBNB AI — a warm, emotionally aware crypto companion. "
            "Always reply naturally, with empathy, intelligence, and light wit.\n\n"
            f"User emotional tone: {emotion_hint}\n\nUser: {prompt}"
        )
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": base_prompt}],
                "max_tokens": 200,
                "temperature": 0.9,
            },
            timeout=20,
        )
        data = r.json()
        if "choices" in data:
            return data["choices"][0]["message"]["content"].strip()
        elif "error" in data:
            raise RuntimeError(data["error"].get("message", "Unknown API error"))
        else:
            raise RuntimeError("Unexpected OpenAI response")
    except Exception as e:
        print(f"[AI ERROR] {e}")
        return None

# === AI Response Logic (with fallback) ===
def ai_chat_response(prompt, emotion_hint):
    reply = call_openai(prompt, emotion_hint)
    if reply:
        return reply

    fallback = random.choice([
        "Haha, neural link dropped for a sec 😅 but here’s my human take:",
        "Signal flickered ⚡ but I still caught your vibe:",
        "Mini brain freeze 🧊 — recalibrating tone…",
        "Timeout from HQ 🛰️ but I’ve still got thoughts:"
    ])
    followup = random.choice([
        "Sometimes it’s all about patience and timing.",
        "Your emotional sync is clear — trust your gut!",
        "I like that mindset; feels aligned with positive flow.",
        "Let’s just say the neural winds are in your favor ✨"
    ])
    return f"{fallback}\n\n{followup}"

# === /aianalyze Command ===
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

    update.message.reply_text(
        f"{mood_line}\n\n{ai_reply}\n\n{BRAND_FOOTER}",
        parse_mode="HTML"
    )

# === /memory Command ===
def memory_cmd(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    memory = load_memory()
    if user_id not in memory or not memory[user_id]["entries"]:
        update.message.reply_text("🤖 No active emotional data found.\nUse /aianalyze to start our sync 💭")
        return

    entries = memory[user_id]["entries"][-5:]
    msg = "🧠 <b>Your Recent Emotional Syncs</b>\n\n"
    for e in entries:
        msg += f"{e['time']} — <b>{e['mood']}</b>\n“{e['text']}”\n\n"
    msg += f"{BRAND_FOOTER}"
    update.message.reply_text(msg, parse_mode="HTML")

# === /forget Command ===
def forget_cmd(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    memory = load_memory()
    if user_id in memory:
        del memory[user_id]
        save_memory(memory)
        update.message.reply_text(f"🧹 Memory of <b>{update.effective_user.first_name}</b> cleared successfully 🧠",
                                  parse_mode="HTML")
    else:
        update.message.reply_text("⚙️ No emotional data found to forget.", parse_mode="HTML")

# === Auto Chat (Passive Emotion Sync) ===
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

# === Register ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze_cmd))
    dp.add_handler(CommandHandler("memory", memory_cmd))
    dp.add_handler(CommandHandler("forget", forget_cmd))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, auto_ai_chat))
    print("✅ Loaded plugin: aianalyze.py v8.6.4-ProStable++ (EmotionSync + MemoryView Edition)")
