# plugins/ai_auto_reply.py
"""
AI Auto-Reply — EmotionHuman v8.7.6-HybridFeel Update (Ready-to-paste)
• Exact-case NameLock (preserve username casing where available)
• SmartNick Engine (avoids repeating username too often)
• MoodIcon Variation (not a single boring emoji)
• Contextual Signature (bold for energetic vibes, softer otherwise)
• MemoryContext++ (remembers recent topics + last names used)
• Hinglish-aware replies
• Render/OpenAI proxy safe fallback
"""

import os
import json
import random
import requests
import traceback
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")  # optional proxy to use instead of direct OpenAI
MEMORY_FILE = "user_memory.json"

# -------------------------
# Memory helpers
# -------------------------
def load_memory() -> Dict[str, Any]:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_memory(data: Dict[str, Any]) -> None:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# -------------------------
# Mood / emoji helpers
# -------------------------
MOOD_ICON_VARIANTS = {
    "Positive": ["🔥", "🚀", "✨"],
    "Reflective": ["🌙", "💭", "✨"],
    "Balanced": ["🙂", "💫", "😌"],
    "Angry": ["😠", "😤"],
    "Sad": ["😔", "💔"],
    "Excited": ["🤩", "💥", "🎉"]
}

def pick_mood_icon(mood: str) -> str:
    variants = MOOD_ICON_VARIANTS.get(mood, MOOD_ICON_VARIANTS["Balanced"])
    return random.choice(variants)

# -------------------------
# username / NameLock helpers
# -------------------------
def canonical_username(user) -> str:
    """
    Preserve exact case for username when available; fallback to first_name.
    Telegram's .username may be None. Keep nickname exactly as provided.
    """
    if getattr(user, "username", None):
        # username on Telegram is returned without @ but with original case sometimes,
        # preserve exactly as returned and keep the @ when used publically.
        return user.username  # exact returned value
    return user.first_name or "friend"

def display_handle(user) -> str:
    """
    A display string like '@CrypTechKing™👑' if username exists,
    otherwise the preserved first_name.
    """
    if getattr(user, "username", None):
        # Keep exact case and prefix with @ in chat lines
        return f"@{user.username}"
    return user.first_name or "friend"

# -------------------------
# language/hybrid helpers
# -------------------------
def contains_devanagari(text: str) -> bool:
    return any("\u0900" <= ch <= "\u097F" for ch in text)

def wants_hinglish(text: str) -> bool:
    # detect Devanagari or common Hinglish tokens
    tokens = ["bhai", "yaar", "kya", "accha", "nahi", "haan", "bolo", "kise", "chal", "kuch"]
    text_l = text.lower()
    return contains_devanagari(text) or any(t in text_l for t in tokens)

# -------------------------
# topic detector (basic)
# -------------------------
def detect_topic(text: str) -> str:
    topics = {
        "market": ["bnb", "btc", "crypto", "token", "coin", "chart", "pump", "dump", "market"],
        "airdrop": ["airdrop", "claim", "reward", "points", "task"],
        "life": ["sleep", "love", "work", "tired", "busy"],
        "fun": ["meme", "joke", "haha", "funny", "lol"],
        "web3": ["wallet", "connect", "metamask", "gas", "contract"]
    }
    t = text.lower()
    for k, keywords in topics.items():
        if any(kword in t for kword in keywords):
            return k
    return "general"

# -------------------------
# dynamic signature
# -------------------------
def build_signature(mood: str) -> str:
    """
    - Energetic moods -> bold brand signature
    - Reflective/Calm -> softer signature wording
    """
    if mood in ("Positive", "Excited"):
        return "<b>🚀 WENBNB Neural Engine</b> — Always on, always empathic"
    if mood == "Reflective":
        return "<i>✨ WENBNB Neural Engine — Calm & Thoughtful</i>"
    # default
    return "<b>⚡ WENBNB Neural Engine</b> — Emotional Intelligence 24×7"

# -------------------------
# smart greeting / SmartNick Engine
# -------------------------
def smart_greeting(user_id: int, display_name: str, hinglish: bool, mood: str, mem: Dict[str, Any]) -> (str, Dict[str, Any]):
    """
    Use the display_name but avoid repeating it too often.
    Track last_name_used boolean in memory per-user. Return greeting fragment + updated mem.
    """
    uid = str(user_id)
    user_data = mem.get(uid, {})
    last_used = user_data.get("last_name_used", False)
    # Decide whether to include name: higher chance for first message or when not used recently
    include_name = not last_used and random.random() < 0.85  # 85% chance to greet when not used recently

    vibe = "chill"
    if mood in ("Positive", "Excited"):
        vibe = "playful"
    elif mood == "Reflective":
        vibe = "gentle"

    greeting = ""
    if include_name:
        if hinglish:
            opts = {
                "playful": [f"Are {display_name} 😄,", f"{display_name} yaar,", f"Sun na {display_name},"],
                "gentle":  [f"{display_name} bhai,", f"Arey {display_name},", f"{display_name},"],
                "chill":   [f"Bas vibe dekh {display_name},", f"{display_name},", f"Yo {display_name},"]
            }
        else:
            opts = {
                "playful": [f"Hey {display_name} 👋,", f"Yo {display_name},", f"{display_name}, good to see you!"],
                "gentle":  [f"Hey {display_name},", f"{display_name},", f"Hello {display_name},"],
                "chill":   [f"Yo {display_name},", f"Sup {display_name},", f"{display_name},"]
            }
        greeting = random.choice(opts[vibe]) + " "
        user_data["last_name_used"] = True
    else:
        # occasionally reset the flag so next messages may include the name again later
        if random.random() < 0.25:
            user_data["last_name_used"] = False

    mem[uid] = user_data
    return greeting, mem

# -------------------------
# OpenAI / proxy call
# -------------------------
def build_system_prompt(user_name: str, mood: str, hinglish: bool, memory_context: Optional[List[str]]):
    p = (
        "You are WENBNB AI — a warm, witty, emotionally-aware companion. "
        "Keep replies short (1-4 sentences), natural, and slightly playful. "
        "Avoid robotic phrasing and avoid repeating the user's handle twice. "
    )
    if hinglish:
        p += "Prefer a casual Hinglish mix (Hindi + English) when appropriate. "
    if memory_context:
        p += f"Recently discussed: {', '.join(memory_context)}. Stay consistent with that vibe. "
    p += f"User name: {user_name}. Mood context: {mood}."
    p += " Use at most one emoji inline only if natural."
    return p

def call_ai(prompt: str, user_name: str, mood: str, hinglish: bool, memory_context: Optional[List[str]]) -> Optional[str]:
    sys_prompt = build_system_prompt(user_name, mood, hinglish, memory_context)
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9,
        "max_tokens": 170
    }
    url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    if not AI_PROXY_URL:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"

    try:
        r = requests.post(url, headers=headers, json=body, timeout=20)
        data = r.json()
        if "choices" in data and data["choices"]:
            # chat format
            msg = data["choices"][0].get("message", {}).get("content") or data["choices"][0].get("text")
            if msg:
                return msg.strip()
        # if openai returned an error field
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "OpenAI error"))
    except Exception as e:
        # small console trace for diagnostics on Render
        print("[AI Auto-Reply] call failed:", e)
        try:
            traceback.print_exc(limit=1)
        except Exception:
            pass
    return None

# -------------------------
# Fallbacks (human-style)
# -------------------------
FALLBACK_LINES = [
    "Hmm — small glitch with the neural cloud, but here's my take:",
    "Signal blinked for a sec 😅 — still feeling the energy:",
    "AI hiccuped — switching to human mode. I'd say:"
]

FALLBACK_CONT = [
    "Trust your instinct; this looks promising.",
    "Patience pays; keep an eye on momentum.",
    "That vibe deserves a careful look — good instincts."
]

# -------------------------
# main handler
# -------------------------
def ai_auto_chat(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return

    text = msg.text.strip()
    user = update.effective_user
    uid = str(user.id)
    chat_id = update.effective_chat.id

    # typing indicator
    try:
        context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass

    # prepare identity: prefer exact-case username if available, else first_name
    name_lock = canonical_username(user)        # keep exact-case username or first_name
    display_handle_str = display_handle(user)   # @username or first_name for public mention

    # mood & language
    mem = load_memory()
    last_mood = "Balanced"
    if uid in mem and mem[uid].get("entries"):
        last_mood = mem[uid]["entries"][-1].get("mood", "Balanced")
    mood = last_mood
    icon = pick_mood_icon(mood)
    hinglish = wants_hinglish(text)

    # build memory_context (recent topics)
    recent_topics = []
    if uid in mem:
        context_list = [e.get("topic") for e in mem[uid].get("entries", []) if e.get("topic")]
        # last 3 unique topics
        seen = []
        for t in reversed(context_list):
            if t not in seen:
                seen.append(t)
        recent_topics = list(reversed(seen))[:3]

    # call AI
    ai_reply = call_ai(text, name_lock, mood, hinglish, recent_topics)
    if not ai_reply:
        ai_reply = random.choice(FALLBACK_LINES) + "\n\n" + random.choice(FALLBACK_CONT)

    # Smart greeting: avoid repeating name too often & preserve exact-case
    greet_fragment, mem = smart_greeting(user.id, name_lock, hinglish, mood, mem)

    # finalize message: prefer display handle when announcing publicly, keep name_lock for greeting
    footer = build_signature(mood)
    # If name is an @ handle, show without duplicating (smart_greeting already used the name_lock)
    final = f"{icon} {greet_fragment}{ai_reply.strip().capitalize()}\n\n{footer}"

    # save memory entry
    try:
        mem.setdefault(uid, {"entries": []})
        entry = {
            "text": text,
            "reply": ai_reply,
            "mood": mood,
            "topic": detect_topic(text),
            "time": datetime.now().isoformat()
        }
        mem[uid]["entries"].append(entry)
        # keep last 15 entries
        mem[uid]["entries"] = mem[uid]["entries"][-15:]
        save_memory(mem)
    except Exception as e:
        print("[AI Auto-Reply] memory save failed:", e)

    # send (HTML allowed)
    try:
        msg.reply_text(final, parse_mode=ParseMode.HTML)
    except Exception:
        try:
            msg.reply_text(final)
        except Exception:
            pass

# -------------------------
# register handler (plugin loader expects register_handlers)
# -------------------------
def register_handlers(dp, config=None):
    # legacy compatibility: plugin_manager may call without config
    try:
        from telegram.ext import MessageHandler, Filters
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
    except Exception as e:
        print("[ai_auto_reply] register failed:", e)

# quick standalone test
if __name__ == "__main__":
    print("ai_auto_reply v8.7.6 — paste into plugins/ and load via your plugin manager.")
