"""
AI Auto-Reply — Flirty + Warm Medium Intensity Build
────────────────────────────────────────────────────────────
Version: v8.6.9-ProStable++
• Human-tone balance (friendly + emotional)
• Uses username mentions for personal touch
• Hinglish fallback (auto detects Hindi / Hinglish)
• Emotional continuity via user_memory.json
• Minimal emoji (adaptive mood emoji only)
• Fully Render-safe + OpenAI fallback text
"""

import os, json, random, requests, traceback
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE = "user_memory.json"

# === Memory ===
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# === Mood mapping ===
MOOD_ICON_MAP = {
    "Positive": "🔥",
    "Reflective": "✨",
    "Balanced": "🙂",
    "Excited": "🤩",
    "Calm": "😌",
    "Playful": "😉",
}

def last_user_mood(user_id):
    mem = load_memory()
    uid = str(user_id)
    if uid not in mem or not mem[uid].get("entries"):
        return "Balanced", "🙂"
    last = mem[uid]["entries"][-1]
    mood = last.get("mood", "Balanced")
    return mood, MOOD_ICON_MAP.get(mood, "🙂")

def contains_devanagari(text):
    return any("\u0900" <= ch <= "\u097F" for ch in text)

# === Prompt builder ===
def build_system_prompt(user_name, mood, wants_hinglish):
    tone = (
        "You are WENBNB AI — a warm, charming, emotionally aware companion. "
        "Your tone is flirty-friendly, witty, and naturally human. "
        "Keep it medium-warm, as if talking to someone you care about."
    )
    if wants_hinglish:
        tone += " If user speaks Hindi or Hinglish, reply in Hinglish mix (Hindi + English, casual and natural)."
    tone += f" Keep replies short (1-4 lines). Current user mood: {mood}. "
    tone += "Address the user by name when possible for a personal feel. Avoid robotic tone. Minimal emoji."
    return tone

# === OpenAI call ===
def call_openai(prompt, user_name, mood, wants_hinglish):
    sys_prompt = build_system_prompt(user_name, mood, wants_hinglish)
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.88,
        "max_tokens": 180,
    }

    headers = {"Content-Type": "application/json"}
    if AI_PROXY_URL:
        target = AI_PROXY_URL
    else:
        target = "https://api.openai.com/v1/chat/completions"
        headers["Authorization"] = f"Bearer {AI_API_KEY}"

    try:
        r = requests.post(target, headers=headers, json=payload, timeout=20)
        data = r.json()
        if "choices" in data and data["choices"]:
            msg = data["choices"][0].get("message", {}).get("content")
            if msg:
                return msg.strip()
        if "error" in data:
            raise RuntimeError(data["error"].get("message"))
    except Exception as e:
        print("[AI-AutoReply] Error:", e)
        traceback.print_exc(limit=1)
    return None

# === Footer ===
def get_footer(mood):
    if mood == "Positive":
        return "<b>🔥 WENBNB Neural Engine</b> — Vibing at full spark"
    if mood == "Reflective":
        return "<b>✨ WENBNB Neural Engine</b> — Calm. Aware. Grounded."
    return "<b>⚡ WENBNB Neural Engine</b> — Always emotionally synced"

# === Fallback ===
FALLBACK = [
    "Hehe neural static hit me 😅 — but I got the vibe:",
    "Signal blinked 💫 switching to human mode for you:",
    "AI brain took a tiny nap 🤖 — still, my heart says:",
]

FALLBACK_CONT = [
    "Sounds like something worth smiling about.",
    "Keep that energy going — it suits you 😉",
    "Haha feels relatable, honestly ✨"
]

# === Main handler ===
def ai_auto_chat(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return

    user = update.effective_user
    chat_id = update.effective_chat.id
    text = msg.text.strip()
    user_name = user.first_name or user.username or "you"

    try:
        context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass

    mood, icon = last_user_mood(user.id)
    wants_hinglish = contains_devanagari(text) or any(
        w in text.lower() for w in ["bhai", "yaar", "kya", "acha", "ha", "na"]
    )

    ai_reply = call_openai(text, user_name, mood, wants_hinglish)
    if not ai_reply:
        ai_reply = random.choice(FALLBACK) + "\n\n" + random.choice(FALLBACK_CONT)

    footer = get_footer(mood)
    final_reply = f"{icon} {ai_reply}\n\n{footer}"

    # Save mood continuity
    try:
        mem = load_memory()
        uid = str(user.id)
        if uid not in mem:
            mem[uid] = {"entries": []}
        mem[uid]["entries"].append({
            "text": text, "reply": ai_reply, "mood": mood,
            "time": datetime.now().isoformat()
        })
        mem[uid]["entries"] = mem[uid]["entries"][-10:]
        save_memory(mem)
    except Exception as e:
        print("[AI-AutoReply] memory save fail:", e)

    try:
        msg.reply_text(final_reply, parse_mode=ParseMode.HTML)
    except Exception:
        msg.reply_text(final_reply)

# === Register ===
def register_handlers(dp):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
    print("✅ Loaded plugin: ai_auto_reply_dev.py v8.6.9-ProStable++ (Flirty + Warm Medium Build)")
