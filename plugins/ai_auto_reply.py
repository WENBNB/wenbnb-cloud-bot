# plugins/ai_auto_reply.py
"""
AI Auto-Reply — EmotionHuman Classic Partner Revival Edition (v8.8.1)
───────────────────────────────────────────────────────────────────────────────
• Natural, human-feeling replies (Hinglish + English mix)
• MemoryContext++ integration — remembers last topics & mood
• Smart greetings that avoid repetition of username
• Minimal, relevant emoji (never spammy)
• Render-safe OpenAI proxy / direct call fallback
• Safe fallbacks when AI or network fails
"""

import os
import json
import random
import requests
import traceback
import re
from datetime import datetime
from typing import List

from telegram import Update, ParseMode
from telegram.ext import CallbackContext

# === Config / env ===
AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")  # optional proxy (preferred on Render)
MEMORY_FILE = "user_memory.json"
MAX_CONTEXT_ENTRIES = 15

# === Helpers: memory ===
def load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_memory(data: dict):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("[ai_auto_reply] save_memory failed:", e)

# === Mood / emoji mapping ===
MOOD_ICON = {
    "Positive": "🔥", "Reflective": "✨", "Balanced": "🙂",
    "Angry": "😠", "Sad": "😔", "Excited": "🤩"
}

def last_user_mood(uid: int):
    mem = load_memory()
    s = str(uid)
    if s not in mem or not mem[s].get("entries"):
        return "Balanced", MOOD_ICON.get("Balanced", "🙂")
    last = mem[s]["entries"][-1]
    mood = last.get("mood", "Balanced")
    return mood, MOOD_ICON.get(mood, "🙂")

# minimal Devanagari check (Hindi)
def contains_devanagari(t: str) -> bool:
    return any("\u0900" <= ch <= "\u097F" for ch in t)

# Detect topics for light context
def detect_topic(text: str) -> str:
    t = text.lower()
    mappings = {
        "market": ["bnb", "btc", "crypto", "token", "price", "chart", "pump", "dump"],
        "airdrop": ["airdrop", "claim", "reward", "task"],
        "giveaway": ["giveaway", "join", "winner", "round"],
        "life": ["sleep", "love", "work", "tired", "busy"],
        "meme": ["meme", "joke", "funny", "lol"],
        "web3": ["wallet", "metamask", "contract", "gas"]
    }
    for k, keys in mappings.items():
        if any(kw in t for kw in keys):
            return k
    return "general"

# === System prompt builder (keeps it short & human) ===
def build_system_prompt(user_name: str, mood: str, hinglish: bool, memory_context: List[str]) -> str:
    base = (
        "You are WENBNB AI — a warm, slightly witty, emotionally-aware human-like assistant. "
        "Keep replies short (1-4 sentences), conversational, and natural. Avoid robotic phrasing."
    )
    if hinglish:
        base += " If the user uses Hindi/Devanagari or Hinglish phrases, reply naturally in a Hinglish mix."
    if memory_context:
        base += f" Recently you and {user_name} talked about: {', '.join(memory_context)}. Keep continuity with that vibe."
    base += f" Current mood: {mood}. Use at most one inline emoji if it feels natural. Do not start every message with an emoji."
    return base

# === AI call (proxy or direct) ===
def call_ai(prompt: str, user_name: str, mood: str, hinglish: bool, memory_context: List[str]) -> str:
    sys_prompt = build_system_prompt(user_name, mood, hinglish, memory_context)
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85,
        "max_tokens": 160
    }

    url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    if not AI_PROXY_URL:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=18)
        data = r.json()
        # support different response shapes
        if "choices" in data and data["choices"]:
            choice = data["choices"][0]
            # chat style
            if isinstance(choice.get("message"), dict):
                text = choice["message"].get("content")
            else:
                text = choice.get("text") or None
            if text:
                return text.strip()
        # if error, raise to fallback
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "OpenAI error"))
    except Exception as e:
        print("[ai_auto_reply] AI call failed:", e)
        try:
            traceback.print_exc(limit=1)
        except Exception:
            pass
    return None

# === Footer (brand) ===
def footer(mood: str) -> str:
    if mood == "Positive":
        return "<b>🔥 WENBNB Neural Engine</b> — Synced at Peak Vibes"
    if mood == "Reflective":
        return "<b>✨ WENBNB Neural Engine</b> — Calm & Thoughtful"
    return "<b>🚀 WENBNB Neural Engine</b> — Where Emotion Meets Intelligence 24×7"

# === Smart greeting (avoid repeating name) ===
def smart_greeting(user_id: int, name: str, hinglish: bool, mood: str, mem: dict):
    uid = str(user_id)
    user_data = mem.get(uid, {}) if isinstance(mem, dict) else {}
    last_used = user_data.get("last_name_used", False)

    vibe = "chill"
    if mood in ["Positive", "Excited"]:
        vibe = "playful"
    elif mood in ["Reflective", "Sad"]:
        vibe = "gentle"

    greet = ""
    # Use the name in ~65% cases, but avoid repeating back-to-back
    if not last_used and random.random() < 0.65:
        if hinglish:
            opts = {
                "playful": [f"Are {name} 😄,", f"{name} yaar,", f"Sun na {name},"],
                "gentle":  [f"{name} bhai,", f"{name},", f"Arey {name},"],
                "chill":   [f"{name},", f"Yo {name},", f"{name},"]
            }
        else:
            opts = {
                "playful": [f"Hey {name} 👋,", f"Yo {name},", f"{name}, good to see you!"],
                "gentle":  [f"Hey {name},", f"{name},", f"Hello {name},"],
                "chill":   [f"Yo {name},", f"Sup {name},", f"{name},"]
            }
        greet = random.choice(opts[vibe]) + " "
        user_data["last_name_used"] = True
    else:
        user_data["last_name_used"] = False

    mem[uid] = user_data
    return greet, mem

# === Fallback friendly lines ===
FALLBACK_LINES = [
    "Hmm, thoda AI glitch hua — still, here's what I feel:",
    "Signal blinked for a sec, but my human-sense says:",
    "AI paused briefly — switching to human mode, I'd say:"
]
FALLBACK_CONT = [
    "Trust your gut on this.",
    "Take it slow, keep an eye on momentum.",
    "Feels like a steady move — be mindful."
]

# === Main handler ===
def ai_auto_chat(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return

    user = update.effective_user
    text = msg.text.strip()
    chat_id = update.effective_chat.id
    name = user.first_name or user.username or "friend"

    # typing indicator
    try:
        context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass

    # mood and language detection
    mood, icon = last_user_mood(user.id)
    hinglish = contains_devanagari(text) or bool(re.search(r"\b(bhai|yaar|kya|acha|nahi|haan|bolo)\b", text.lower()))
    topic = detect_topic(text)

    # build memory context (recent topics)
    mem = load_memory()
    uid = str(user.id)
    context_list = [e.get("topic") for e in mem.get(uid, {}).get("entries", []) if e.get("topic")]
    recent_topics = list(dict.fromkeys(context_list[-4:]))  # unique last 4

    # call AI
    ai_reply = call_ai(text, name, mood, hinglish, recent_topics)
    if not ai_reply:
        ai_reply = random.choice(FALLBACK_LINES) + "\n\n" + random.choice(FALLBACK_CONT)

    # greeting + final assembly
    greet, mem = smart_greeting(user.id, name, hinglish, mood, mem)
    # ensure first letter capitalized for neatness
    ai_reply = ai_reply.strip()
    ai_reply = ai_reply[0].upper() + ai_reply[1:] if ai_reply else ai_reply

    # prefer mood icon, but keep it minimal
    final = f"{icon} {greet}{ai_reply}\n\n{footer(mood)}"

    # save memory entry
    try:
        mem.setdefault(uid, {"entries": []})
        mem[uid]["entries"].append({
            "text": text,
            "reply": ai_reply,
            "mood": mood,
            "topic": topic,
            "time": datetime.now().isoformat()
        })
        mem[uid]["entries"] = mem[uid]["entries"][-MAX_CONTEXT_ENTRIES:]
        save_memory(mem)
    except Exception as e:
        print("[ai_auto_reply] memory save failed:", e)

    # send (HTML allowed)
    try:
        msg.reply_text(final, parse_mode=ParseMode.HTML)
    except Exception:
        try:
            msg.reply_text(final)
        except Exception:
            pass

# === Register helper for plugin manager ===
def register_handlers(dp, config=None):
    # import locally to avoid early circular imports
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
    print("✅ Loaded plugin: ai_auto_reply.py v8.8.1 — EmotionHuman Classic Partner Revival Edition")
