"""
AI Auto-Reply — EmotionHuman v8.7.9-ProStable++ (Self-Healing MemoryContext Edition)
───────────────────────────────────────────────────────────────────────────────
• Fully reload-proof via internal handler rebind.
• Retains context & emotion memory continuity (MemoryContext++).
• Smart greeting deduplication (no overuse of names).
• Topic recall for last 4 unique contexts.
• Auto Hinglish/English tone detection.
• Emotion-safe, OpenAI proxy compatible.
"""

import os, json, random, requests, traceback
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, MessageHandler, Filters

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE = "user_memory.json"

# ===================== MEMORY SYSTEM =====================
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ===================== MOOD ENGINE =====================
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

def contains_devanagari(t):  # Hindi detection
    return any("\u0900" <= ch <= "\u097F" for ch in t)

# ===================== TOPIC DETECTOR =====================
def detect_topic(text: str):
    topics = {
        "market": ["bnb", "btc", "crypto", "token", "coin", "chart", "pump", "dump"],
        "airdrop": ["airdrop", "claim", "reward", "points", "task"],
        "life": ["sleep", "love", "work", "tired", "busy", "time"],
        "fun": ["meme", "joke", "haha", "funny", "lol"],
        "web3": ["wallet", "connect", "metamask", "gas", "contract"]
    }
    text = text.lower()
    for k, vals in topics.items():
        if any(v in text for v in vals):
            return k
    return "general"

# ===================== PROMPT BUILDER =====================
def build_prompt(user_name, mood, hinglish, memory_context):
    p = (
        "You are WENBNB AI — a warm, emotionally intelligent companion. "
        "Keep your replies short (1–4 sentences), natural, and a little playful. "
        "Avoid robotic or repetitive phrasing. "
    )
    if hinglish:
        p += "If the user writes in Hinglish or Hindi, respond naturally in a mix of Hindi + English. "
    if memory_context:
        p += f"You and {user_name} recently discussed {', '.join(memory_context)}. Keep continuity with that tone. "
    p += f"User: {user_name}. Mood: {mood}. Use emojis only if they feel natural."
    return p

# ===================== AI CALL =====================
def call_ai(prompt, user_name, mood, hinglish, memory_context):
    sys = build_prompt(user_name, mood, hinglish, memory_context)
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
    if not AI_PROXY_URL:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"
    try:
        r = requests.post(url, headers=headers, json=body, timeout=20).json()
        if "choices" in r and r["choices"]:
            return r["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("[AI Auto-Reply]", e)
        traceback.print_exc(limit=1)
    return None

# ===================== FOOTER =====================
def footer(mood):
    if mood == "Positive": return "<b>🔥 WENBNB Neural Engine</b> — Synced at Peak Vibes"
    if mood == "Reflective": return "<b>✨ WENBNB Neural Engine</b> — Calm & Thoughtful"
    return "<b>🚀 WENBNB Neural Engine</b> — Emotional Intelligence 24×7"

# ===================== GREETING ENGINE =====================
def smart_greeting(user_id, name, hinglish, mood, mem):
    """Avoids repeating name/greeting too often."""
    user_data = mem.get(str(user_id), {})
    last_used = user_data.get("last_name_used", False)
    vibe = "chill"
    if mood in ["Positive", "Excited"]: vibe = "playful"
    elif mood in ["Reflective", "Sad"]: vibe = "gentle"
    greet = ""

    if not last_used and random.random() < 0.7:
        if hinglish:
            opts = {
                "playful": [f"Are {name} 😄,", f"{name} yaar,", f"Sun na {name},"],
                "gentle": [f"{name} bhai,", f"Arey {name},", f"{name},"],
                "chill": [f"Bas vibe dekh {name},", f"{name},", f"Yo {name},"]
            }
        else:
            opts = {
                "playful": [f"Hey {name} 👋,", f"Yo {name},", f"{name}, good to see you!"],
                "gentle": [f"Hey {name},", f"{name},", f"Hello {name},"],
                "chill": [f"Yo {name},", f"Sup {name},", f"{name},"]
            }
        greet = random.choice(opts[vibe]) + " "
        user_data["last_name_used"] = True
    else:
        user_data["last_name_used"] = False

    mem[str(user_id)] = user_data
    return greet, mem

# ===================== MAIN REPLY =====================
def ai_auto_chat(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return
    user, text = update.effective_user, msg.text.strip()
    chat_id, name = update.effective_chat.id, (user.first_name or user.username or "friend")

    try:
        context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except:
        pass

    mood, icon = last_user_mood(user.id)
    hinglish = contains_devanagari(text) or any(w in text.lower() for w in ["bhai", "yaar", "kya", "acha", "nahi", "haan", "bolo"])
    topic = detect_topic(text)
    mem = load_memory()
    uid = str(user.id)
    context_list = [e.get("topic") for e in mem.get(uid, {}).get("entries", []) if e.get("topic")]
    recent_topics = list(dict.fromkeys(context_list[-4:]))

    reply = call_ai(text, name, mood, hinglish, recent_topics)
    if not reply:
        reply = random.choice([
            "Neural link thoda blink hua 😅 but I caught your vibe:",
            "Signal glitch 🤖 but emotion sync stable:",
            "Hmm, AI soch raha hai — par feel kar raha hai:"
        ]) + "\n\n" + random.choice([
            "Patience pays off 💫", "Energy high rakh baby 🔥", "Keep vibing steady 🚀"
        ])

    greet, mem = smart_greeting(user.id, name, hinglish, mood, mem)
    final = f"{icon} {greet}{reply.strip().capitalize()}\n\n{footer(mood)}"

    mem.setdefault(uid, {"entries": []})
    mem[uid]["entries"].append({
        "text": text, "reply": reply, "mood": mood, "topic": topic, "time": datetime.now().isoformat()
    })
    mem[uid]["entries"] = mem[uid]["entries"][-15:]
    save_memory(mem)

    try:
        msg.reply_text(final, parse_mode=ParseMode.HTML)
    except:
        msg.reply_text(final)

# ===================== REGISTER (SELF-HEALING) =====================
def register_handlers(dp):
    """Registers handler and makes sure reload doesn’t break binding."""
    try:
        # remove old handlers before adding new
        for h in list(dp.handlers.get(0, [])):
            if hasattr(h, "callback") and h.callback == ai_auto_chat:
                dp.remove_handler(h)
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
        print("✅ Loaded plugin: ai_auto_reply.py v8.7.9-ProStable++ (Self-Healing MemoryContext Edition)")
    except Exception as e:
        print(f"⚠️ ai_auto_reply register_handlers failed: {e}")
