# plugins/ai_auto_reply.py
"""
AI Auto-Reply — EmotionHuman+ Harmonizer Build (v8.6.9-ProStable++)
───────────────────────────────────────────────────────────────────────────────
• Smart Greeting Harmonizer (no duplicate names or robotic tone)
• Context-adaptive greetings: playful, reflective, chill
• Emotion-synced emoji, no spam
• Hinglish + English hybrid detection
• Memory continuity via user_memory.json
• Render/OpenAI safe
"""

import os, json, random, requests, traceback
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE = "user_memory.json"

# ------------------- Memory -------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ------------------- Mood / Emoji -------------------
MOOD_ICON = {
    "Positive": "🔥", "Reflective": "✨", "Balanced": "🙂",
    "Angry": "😠", "Sad": "😔", "Excited": "🤩"
}

def last_user_mood(uid):
    mem = load_memory()
    if str(uid) not in mem or not mem[str(uid)].get("entries"):
        return "Balanced", "🙂"
    last = mem[str(uid)]["entries"][-1]
    mood = last.get("mood", "Balanced")
    return mood, MOOD_ICON.get(mood, "🙂")

def contains_devanagari(t):  # Hindi check
    return any("\u0900" <= ch <= "\u097F" for ch in t)

# ------------------- System Prompt -------------------
def build_prompt(user_name, mood, hinglish):
    p = ("You are WENBNB AI — a warm, witty, emotionally-aware companion. "
         "Keep replies short (1-4 sentences), human-like, and slightly playful. ")
    if hinglish:
        p += "If user writes in Hindi or Hinglish, reply naturally in Hinglish (Hindi + English mix). "
    p += (f"User name: {user_name}. Mood: {mood}. "
          "Avoid repeating greetings or usernames twice. "
          "Use at most one emoji inline, no emoji at start unless natural.")
    return p

# ------------------- OpenAI Call -------------------
def call_ai(prompt, user_name, mood, hinglish):
    sys = build_prompt(user_name, mood, hinglish)
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": sys},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9, "max_tokens": 180
    }
    url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    if not AI_PROXY_URL: headers["Authorization"] = f"Bearer {AI_API_KEY}"
    try:
        r = requests.post(url, headers=headers, json=body, timeout=20).json()
        if "choices" in r and r["choices"]:
            return r["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("[AI Auto-Reply]", e); traceback.print_exc(limit=1)
    return None

# ------------------- Footer -------------------
def footer(mood):
    if mood == "Positive": return "<b>🔥 WENBNB Neural Engine</b> — Synced at Peak Vibes"
    if mood == "Reflective": return "<b>✨ WENBNB Neural Engine</b> — Calm & Thoughtful"
    return "<b>🚀 WENBNB Neural Engine</b> — Emotional Intelligence 24×7"

# ------------------- Greeting Harmonizer -------------------
def smart_greeting(name, hinglish, mood):
    vibe = "chill"
    if mood in ["Positive", "Excited"]: vibe = "playful"
    elif mood in ["Reflective", "Sad"]: vibe = "gentle"

    if random.random() < 0.4:  # 40 % messages greet
        if hinglish:
            opts = {
                "playful": [f"Are {name} 😄,", f"{name} yaar,", f"Sun na {name},"],
                "gentle":  [f"{name} bhai,", f"{name},", f"Arey {name},"],
                "chill":   [f"Bas vibe dekh {name},", f"{name},", f"Yo {name},"]
            }
        else:
            opts = {
                "playful": [f"Hey {name} 👋,", f"Yo {name},", f"{name}, good to see you!"],
                "gentle":  [f"Hey {name},", f"{name},", f"Hello {name},"],
                "chill":   [f"Yo {name},", f"Sup {name},", f"{name},"]
            }
        return random.choice(opts[vibe]) + " "
    return ""

# ------------------- Main -------------------
def ai_auto_chat(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"): return
    user, text = update.effective_user, msg.text.strip()
    chat_id, name = update.effective_chat.id, (user.first_name or user.username or "friend")

    try: context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except: pass

    mood, icon = last_user_mood(user.id)
    hinglish = contains_devanagari(text) or any(w in text.lower() for w in ["bhai","yaar","kya","acha","nahi","haan","bolo"])

    reply = call_ai(text, name, mood, hinglish)
    if not reply:
        reply = random.choice([
            "Hmm, thoda glitch hua lagta hai — but I caught the vibe:",
            "Signal blinked 😅 but here’s what I feel:",
            "AI thoda confuse hua — still, intuition bolta hai:"
        ]) + "\n\n" + random.choice([
            "Trust your instinct.", "Patience always pays.", "Keep your vibe strong."
        ])

    greet = smart_greeting(name, hinglish, mood)
    final = f"{icon} {greet}{reply.strip().capitalize()}\n\n{footer(mood)}"

    # --- memory ---
    try:
        mem = load_memory()
        uid = str(user.id)
        mem.setdefault(uid, {"entries": []})
        mem[uid]["entries"].append({"text": text, "reply": reply, "mood": mood, "time": datetime.now().isoformat()})
        mem[uid]["entries"] = mem[uid]["entries"][-12:]
        save_memory(mem)
    except Exception as e: print("[Memory]", e)

    try: msg.reply_text(final, parse_mode=ParseMode.HTML)
    except: msg.reply_text(final)

# ------------------- Register -------------------
def register_handlers(dp):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
    print("✅ Loaded plugin: ai_auto_reply.py v8.6.9-ProStable++ (EmotionHuman+ Harmonizer Build)")
