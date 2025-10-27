# plugins/ai_auto_reply.py
"""
AI Auto-Reply — EmotionHuman Adaptive Build (v8.6.7-ProStable++)
• Adaptive mood emoji (no 🌙 spam)
• Hinglish fallback when input contains Devanagari (Hindi) chars
• Human-feeling, slightly witty replies, minimal emoji
• Render-safe OpenAI proxy / direct OpenAI call with fallback text
• Memory continuity stored in user_memory.json
"""

import os
import json
import random
import requests
import traceback
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")  # optional proxy endpoint
MEMORY_FILE = "user_memory.json"

# -------------------
# Memory helpers
# -------------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_memory(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# -------------------
# Mood / emoji helpers
# -------------------
MOOD_ICON_MAP = {
    "Positive": "🔥",
    "Reflective": "✨",
    "Balanced": "🙂",
    "Angry": "😠",
    "Sad": "😔",
    "Excited": "🤩",
}

def last_user_mood(user_id):
    mem = load_memory()
    uid = str(user_id)
    if uid not in mem or not mem[uid].get("entries"):
        return "Balanced", "🙂"
    last = mem[uid]["entries"][-1]
    mood = last.get("mood", "Balanced")
    icon = MOOD_ICON_MAP.get(mood, "🙂")
    return mood, icon

# detect basic Devanagari (Hindi) presence — lightweight check
def contains_devanagari(text: str) -> bool:
    for ch in text:
        if "\u0900" <= ch <= "\u097F":
            return True
    return False

# -------------------
# Build system prompt
# -------------------
def build_system_prompt(user_name: str, mood: str, wants_hinglish: bool):
    base = (
        "You are WENBNB AI — a warm, witty, emotionally-aware crypto companion. "
        "Reply short, human, slightly humorous, and helpful. Avoid sounding robotic."
        " Keep replies concise (1-4 sentences) and friendly."
    )
    if wants_hinglish:
        base += " If user input is Hindi (Devanagari) or Hinglish, prefer a casual Hinglish mix (Hindi + English)."
    base += f" Keep in mind the user's current mood: {mood}."
    base += " Do NOT start every reply with emoji; use at most one relevant emoji inline."
    base += " Sign-off or branding should be minimal."
    return base

# -------------------
# Call OpenAI (or proxy) with safe handling
# -------------------
def call_openai(prompt: str, user_name: str, mood: str, wants_hinglish: bool):
    sys_prompt = build_system_prompt(user_name, mood, wants_hinglish)
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85,
        "max_tokens": 170,
    }

    # prefer proxy if configured (helps with Render setups)
    target_url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    if not AI_PROXY_URL:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"

    try:
        r = requests.post(target_url, headers=headers, json=payload, timeout=20)
        data = r.json()
        if "choices" in data and data["choices"]:
            # support both chat response structures
            text = data["choices"][0].get("message", {}).get("content") or data["choices"][0].get("text")
            if text:
                return text.strip()
        # fallback to explicit error message if available
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "OpenAI error"))
    except Exception as e:
        # log for Render console; keep trace concise
        print("[AI Auto-Reply] OpenAI/proxy call failed:", e)
        try:
            traceback.print_exc(limit=1)
        except Exception:
            pass
    return None

# -------------------
# Footer + branding
# -------------------
def get_footer(mood: str):
    # Bold the brand name for premium feel (HTML)
    if mood == "Positive":
        return "<b>🔥 WENBNB Neural Engine</b> — Synced at Peak Vibes"
    if mood == "Reflective":
        return "<b>✨ WENBNB Neural Engine</b> — Calm & Thoughtful"
    return "<b>🚀 WENBNB Neural Engine</b> — Emotional Intelligence 24×7"

# -------------------
# Fallback lines (human casual)
# -------------------
FALLBACK_LINES = [
    "Hmm — small glitch with the neural cloud, but here's my take:",
    "Lost the AI beat for a sec 😅 — still, this feels like:",
    "Signal blinked, switching to human mode — I'd say:",
]

FALLBACK_CONT = [
    "Trust your gut; this looks promising.",
    "Take it slow and watch momentum.",
    "Looks like a good opportunity — keep an eye on it."
]

# -------------------
# Main auto-reply handler
# -------------------
def ai_auto_chat(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return

    user = update.effective_user
    text = msg.text.strip()
    chat_id = update.effective_chat.id
    user_name = user.first_name or (user.username or "friend")

    # typing indicator
    try:
        context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass

    # mood continuity & language hint
    mood, icon = last_user_mood(user.id)
    wants_hinglish = contains_devanagari(text) or any(word in text.lower() for word in ["bhai", "yaar", "kya", "accha", "kuch"])

    # call AI
    ai_reply = call_openai(text, user_name, mood, wants_hinglish)
    if not ai_reply:
        # fallback friendly human reply
        ai_reply = random.choice(FALLBACK_LINES) + "\n\n" + random.choice(FALLBACK_CONT)

    # ensure not too emoji-heavy; pick one emoji only (prefer mood icon)
    chosen_icon = icon  # already a single icon from mapping

    footer = get_footer(mood)
    final_reply = f"{chosen_icon} {ai_reply}\n\n{footer}"

    # Save memory entry (continuity)
    try:
        memory = load_memory()
        uid = str(user.id)
        if uid not in memory:
            memory[uid] = {"entries": []}
        entry = {"text": text, "reply": ai_reply, "mood": mood, "time": datetime.now().isoformat()}
        memory[uid]["entries"].append(entry)
        memory[uid]["entries"] = memory[uid]["entries"][-12:]
        save_memory(memory)
    except Exception as e:
        print("[AI Auto-Reply] memory save failed:", e)

    # send reply (HTML allowed)
    try:
        msg.reply_text(final_reply, parse_mode=ParseMode.HTML)
    except Exception:
        # last fallback plain text
        try:
            msg.reply_text(final_reply)
        except Exception:
            pass

# -------------------
# Register handler
# -------------------
def register_handlers(dp):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
    print("✅ Loaded plugin: ai_auto_reply.py v8.6.7-ProStable++ (EmotionHuman Adaptive Build)")
