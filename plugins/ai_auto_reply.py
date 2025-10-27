# plugins/ai_auto_reply.py
"""
AI Auto-Reply — EmotionHuman Adaptive Build (v8.6.8-ProStable++)
───────────────────────────────────────────────────────────────────────────────
• Adaptive mood emoji (no 🌙 spam)
• Personalized user greetings (Hey {name} / Are {name})
• Hinglish fallback (auto-detects Hindi or Hinglish)
• Emotionally natural, slightly witty replies (no robotic tone)
• Render-safe OpenAI/proxy handling
• Emotional continuity via user_memory.json
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
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE = "user_memory.json"

# -------------------
# Memory Helpers
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
# Mood / Emoji Helpers
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

# Hindi detector (basic Devanagari check)
def contains_devanagari(text: str) -> bool:
    for ch in text:
        if "\u0900" <= ch <= "\u097F":
            return True
    return False

# -------------------
# System Prompt Builder
# -------------------
def build_system_prompt(user_name: str, mood: str, wants_hinglish: bool):
    base = (
        "You are WENBNB AI — a warm, witty, emotionally-aware crypto companion. "
        "Keep replies short (1–4 sentences), natural, and human-like. "
        "Inject gentle humor or emotion, never robotic tone."
    )
    if wants_hinglish:
        base += " If user speaks Hindi or Hinglish, reply naturally in Hinglish (mix Hindi + English)."
    base += f" User name: {user_name}. Current emotional tone: {mood}. "
    base += "Avoid starting every message with emoji — use 1 relevant emoji max inline."
    base += " Keep the tone casual and emotionally alive."
    return base

# -------------------
# Call OpenAI/Proxy Safely
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

    target_url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    if not AI_PROXY_URL:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"

    try:
        r = requests.post(target_url, headers=headers, json=payload, timeout=20)
        data = r.json()
        if "choices" in data and data["choices"]:
            text = data["choices"][0].get("message", {}).get("content") or data["choices"][0].get("text")
            if text:
                return text.strip()
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "OpenAI error"))
    except Exception as e:
        print("[AI Auto-Reply] OpenAI/proxy call failed:", e)
        traceback.print_exc(limit=1)
    return None

# -------------------
# Branding Footer
# -------------------
def get_footer(mood: str):
    if mood == "Positive":
        return "<b>🔥 WENBNB Neural Engine</b> — Synced at Peak Vibes"
    if mood == "Reflective":
        return "<b>✨ WENBNB Neural Engine</b> — Calm & Thoughtful"
    return "<b>🚀 WENBNB Neural Engine</b> — Emotional Intelligence 24×7"

# -------------------
# Fallback Phrases (Human-like)
# -------------------
FALLBACK_LINES = [
    "Hmm — neural cloud thoda glitch hua, but here’s my take:",
    "Signal blinked for a sec 😅 — still catching your vibe:",
    "AI link lost, but my human side says:",
]

FALLBACK_CONT = [
    "Stay patient, things will flow your way.",
    "Looks like energy shift — stay aware.",
    "Trust the process; the vibe’s stabilizing.",
]

# -------------------
# Main Handler
# -------------------
def ai_auto_chat(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return

    user = update.effective_user
    text = msg.text.strip()
    chat_id = update.effective_chat.id
    user_name = user.first_name or (user.username or "friend")

    try:
        context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass

    mood, icon = last_user_mood(user.id)
    wants_hinglish = contains_devanagari(text) or any(
        w in text.lower() for w in ["bhai", "yaar", "acha", "nahi", "ha", "haan", "kya", "bata"]
    )

    ai_reply = call_openai(text, user_name, mood, wants_hinglish)
    if not ai_reply:
        ai_reply = random.choice(FALLBACK_LINES) + "\n\n" + random.choice(FALLBACK_CONT)

    # --- Personalized Greeting Layer ---
    greeting = ""
    if random.random() > 0.5:  # 50% of messages get personal greeting
        if wants_hinglish:
            greeting = random.choice([
                f"Are {user_name}, ",
                f"{user_name} yaar, ",
                f"Sun na {user_name}, ",
                f"{user_name} bhai, "
            ])
        else:
            greeting = random.choice([
                f"Hey {user_name}, ",
                f"{user_name}, ",
                f"Hey there {user_name}! ",
                f"Yo {user_name}, "
            ])

    ai_reply = f"{greeting}{ai_reply.strip().capitalize()}"

    footer = get_footer(mood)
    final_reply = f"{icon} {ai_reply}\n\n{footer}"

    # --- Memory Save ---
    try:
        memory = load_memory()
        uid = str(user.id)
        if uid not in memory:
            memory[uid] = {"entries": []}
        memory[uid]["entries"].append({
            "text": text,
            "reply": ai_reply,
            "mood": mood,
            "time": datetime.now().isoformat()
        })
        memory[uid]["entries"] = memory[uid]["entries"][-12:]
        save_memory(memory)
    except Exception as e:
        print("[AI Auto-Reply] Memory save failed:", e)

    try:
        msg.reply_text(final_reply, parse_mode=ParseMode.HTML)
    except Exception:
        msg.reply_text(final_reply)

# -------------------
# Register Handler
# -------------------
def register_handlers(dp):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
    print("✅ Loaded plugin: ai_auto_reply.py v8.6.8-ProStable++ (Adaptive HumanTone + Username Greeting)")
