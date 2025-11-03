"""
AI Auto-Reply — Emotion Continuum Reforged (v8.6.5-ProStable++)
───────────────────────────────────────────────────────────────────────────────
• Restores v8.4-Pro tone & emoji personality
• Uses user_memory.json for emotional continuity
• Dynamic branded footers by vibe
• Render-safe OpenAI integration (auto-fallback)
"""

import os, json, random, requests, traceback
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MEMORY_FILE = "user_memory.json"

# === Memory ===
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def last_user_mood(user_id):
    mem = load_memory()
    if str(user_id) not in mem or not mem[str(user_id)]["entries"]:
        return "Balanced", "🌙"
    last = mem[str(user_id)]["entries"][-1]
    mood = last.get("mood", "Balanced")
    icon = {"Positive": "🌞", "Reflective": "🌧", "Balanced": "🌙"}.get(mood, "🌙")
    return mood, icon

# === OpenAI Call ===
def call_openai(prompt, user_name, short_emotion):
    try:
        sys_prompt = (
            f"You are WENBNB AI — a warm, emotionally aware companion with charm, humor, "
            f"and emotional continuity. You remember user moods.\n\n"
            f"User: {user_name}\nMood context: {short_emotion}\n"
            f"Keep your replies short, natural, slightly witty, never robotic."
        )

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": 160,
                "temperature": 0.9,
            },
            timeout=20,
        )
        data = r.json()
        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"].strip()
        elif "error" in data:
            raise RuntimeError(data["error"].get("message"))
    except Exception as e:
        print(f"[AI Auto-Reply Error] {e}")
        traceback.print_exc()
        return None

# === Footer Picker ===
def get_footer(mood):
    if mood == "Positive":
        return "🔥 WENBNB Neural Engine — Synced at Peak Vibes"
    elif mood == "Reflective":
        return "🌙 WENBNB AI — Calm Circuits. Steady Heartbeat."
    else:
        return "🚀 WENBNB Neural Engine — Emotional Intelligence 24×7 ⚡"

# === Main Auto-Reply ===
def ai_auto_chat(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return

    text = msg.text.strip()
    user = update.effective_user
    chat_id = update.effective_chat.id
    user_name = user.first_name or "friend"

    context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # Mood continuity
    mood, icon = last_user_mood(user.id)

    # Call AI
    reply_text = call_openai(text, user_name, mood)
    if not reply_text:
        reply_text = random.choice([
            "Neural link flickered for a sec 😅 but I caught your vibe.",
            "Hmm… brain cloud passing overhead ☁️ — still feeling the energy.",
            "Signal blinked 🤖💫 but my circuits say: stay confident!",
        ])

    footer = get_footer(mood)
    final_reply = f"{icon} {reply_text}\n\n{footer}"

    # Save memory (continuity log)
    memory = load_memory()
    entry = {"text": text, "reply": reply_text, "mood": mood, "time": datetime.now().isoformat()}
    uid = str(user.id)
    if uid not in memory:
        memory[uid] = {"entries": []}
    memory[uid]["entries"].append(entry)
    memory[uid]["entries"] = memory[uid]["entries"][-10:]
    save_memory(memory)

    msg.reply_text(final_reply, parse_mode=ParseMode.HTML)

# === Register ===
def register_handlers(dp):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
    print("✅ Loaded plugin: ai_auto_reply.py v8.6.5-ProStable++ (Continuum Reforged)")
