# plugins/ai_auto_reply.py
"""
AI Auto-Reply — EmotionHuman v8.7.6-HybridFeel Update (+ ContinuityPatch v2)
• Exact-case NameLock (preserve username casing where available)
• SmartNick Engine (avoids repeating username too often)
• MoodIcon Variation (not a single boring emoji)
• Contextual Signature (bold for energetic vibes, softer otherwise)
• MemoryContext++ (remembers recent topics + last names used)
• Hinglish-aware replies
• Render/OpenAI proxy safe fallback
• NEW: Conversation Continuity — last themes + last user lines recall (no goal forcing)
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

def canonical_username(user) -> str:
    if getattr(user, "username", None):
        return user.username
    return user.first_name or "friend"

def display_handle(user) -> str:
    if getattr(user, "username", None):
        return f"@{user.username}"
    return user.first_name or "friend"

def contains_devanagari(text: str) -> bool:
    return any("\u0900" <= ch <= "\u097F" for ch in text)

def wants_hinglish(text: str) -> bool:
    tokens = ["bhai", "yaar", "kya", "accha", "acha", "nahi", "haan", "bolo", "kise", "chal", "kuch", "kar", "ho", "tips"]
    text_l = text.lower()
    return contains_devanagari(text) or any(t in text_l for t in tokens)

def detect_topic(text: str) -> str:
    topics = {
        "market": ["bnb", "btc", "crypto", "token", "coin", "chart", "pump", "dump", "market", "price", "trend"],
        "airdrop": ["airdrop", "claim", "reward", "points", "task", "quest"],
        "life": ["sleep", "love", "work", "tired", "busy", "relationship", "mood"],
        "fun": ["meme", "joke", "haha", "funny", "lol"],
        "web3": ["wallet", "connect", "metamask", "gas", "contract", "deploy", "bot", "stake", "dex"],
        "travel": ["travel", "trip", "itinerary", "flight", "hotel", "tour"]
    }
    t = text.lower()
    for k, keywords in topics.items():
        if any(kword in t for kword in keywords):
            return k
    return "general"

def build_signature(mood: str) -> str:
    if mood in ("Positive", "Excited"):
        return "<b>🚀 WENBNB Neural Engine</b> — Always on, always empathic"
    if mood == "Reflective":
        return "<i>✨ WENBNB Neural Engine — Calm & Thoughtful</i>"
    return "<b>⚡ WENBNB Neural Engine</b> — Emotional Intelligence 24×7"

def smart_greeting(user_id: int, display_name: str, hinglish: bool, mood: str, mem: Dict[str, Any]) -> (str, Dict[str, Any]):
    uid = str(user_id)
    user_data = mem.get(uid, {})
    last_used = user_data.get("last_name_used", False)
    include_name = not last_used and random.random() < 0.85

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

                # ✅ patched chill options
                "chill": [
                    f"{display_name},",
                    f"Sun na {display_name},",
                    f"Arre {display_name}, kya chal raha hai?",
                    f"Tell me {display_name},",
                    f"Aaja baat karein {display_name},"
                ]
            }
        else:
            opts = {
                "playful": [f"Hey {display_name} 👋,", f"Yo {display_name},", f"{display_name}, good to see you!"],
                "gentle":  [f"Hey {display_name},", f"{display_name},", f"Hello {display_name},"],

                # ✅ patched English chill
                "chill": [
                    f"Hey {display_name},",
                    f"So what's up {display_name}?",
                    f"Talk to me {display_name},",
                    f"{display_name}, you there?",
                    f"Alright tell me {display_name},"
                ]
            }
        greeting = random.choice(opts[vibe]) + " "
        user_data["last_name_used"] = True
    else:
        if random.random() < 0.25:
            user_data["last_name_used"] = False

    mem[uid] = user_data
    return greeting, mem

def _trim_line(s: str) -> str:
    s = (s or "").strip()
    if len(s) > 140:
        return s[:140].rstrip() + "…"
    return s

def continuity_update(mem: Dict[str, Any], uid: str, user_text: str) -> Dict[str, Any]:
    u = mem.setdefault(uid, {})
    topic = detect_topic(user_text)
    thr: List[str] = u.setdefault("thread", [])
    if not thr or thr[-1] != topic:
        thr.append(topic)
        u["thread"] = thr[-5:]
    lines: List[str] = u.setdefault("last_lines", [])
    lines.append(_trim_line(user_text))
    u["last_lines"] = lines[-6:]
    mem[uid] = u
    return mem

def continuity_context(mem: Dict[str, Any], uid: str) -> Dict[str, List[str]]:
    u = mem.get(uid, {})
    return {
        "thread": u.get("thread", []),
        "last_lines": u.get("last_lines", [])
    }

def build_system_prompt(user_name: str, mood: str, hinglish: bool, memory_context: Optional[List[str]], contx: Dict[str, List[str]]):
    p = (
        "You are WENBNB AI — a warm, witty, emotionally-aware companion. "
        "Continue the conversation naturally with short (1–4 sentences) replies. "
        "Stay casual and human; slight flirt is fine. Do NOT impose goals. "
        "Avoid robotic phrasing and avoid repeating the user's handle twice. "
    )
    if hinglish:
        p += "Prefer a casual Hinglish mix. "
    if memory_context:
        p += f"Recently talked about: {', '.join(memory_context)}. "
    if contx.get('thread'):
        p += f"Conversation thread tags: {', '.join(contx['thread'])}. "
    if contx.get('last_lines'):
        p += "Recent user lines: " + " | ".join(contx["last_lines"]) + ". "
    p += f"User name: {user_name}. Mood: {mood}. Use max 1 emoji if natural."
    return p

def call_ai(prompt: str, user_name: str, mood: str, hinglish: bool, memory_context: Optional[List[str]], contx: Dict[str, List[str]]) -> Optional[str]:
    sys_prompt = build_system_prompt(user_name, mood, hinglish, memory_context, contx)
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
            msg = data["choices"][0].get("message", {}).get("content") or data["choices"][0].get("text")
            if msg:
                return msg.strip()
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "OpenAI error"))
    except Exception as e:
        print("[AI Auto-Reply] call failed:", e)
        try: traceback.print_exc(limit=1)
        except: pass
    return None

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

def ai_auto_chat(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not msg.text or msg.text.startswith("/"):
        return

    text = msg.text.strip()
    user = update.effective_user
    uid = str(user.id)
    chat_id = update.effective_chat.id

    try: context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except: pass

    name_lock = canonical_username(user)
    display_handle_str = display_handle(user)

    mem = load_memory()
    last_mood = "Balanced"
    if uid in mem and mem[uid].get("entries"):
        last_mood = mem[uid]["entries"][-1].get("mood", "Balanced")
    mood = last_mood
    icon = pick_mood_icon(mood)
    hinglish = wants_hinglish(text)

    recent_topics = []
    if uid in mem:
        context_list = [e.get("topic") for e in mem[uid].get("entries", []) if e.get("topic")]
        seen = []
        for t in reversed(context_list):
            if t not in seen:
                seen.append(t)
        recent_topics = list(reversed(seen))[:3]
        mem = continuity_update(mem, uid, text)
        contx = continuity_context(mem, uid)

    mem = continuity_update(mem, uid, text)
    contx = continuity_context(mem, uid)

    ai_reply = call_ai(text, name_lock, mood, hinglish, recent_topics, contx)
    if not ai_reply:
        ai_reply = random.choice(FALLBACK_LINES) + "\n\n" + random.choice(FALLBACK_CONT)

    greet_fragment, mem = smart_greeting(user.id, name_lock, hinglish, mood, mem)
    footer = build_signature(mood)
    final = f"{icon} {greet_fragment}{ai_reply.strip().capitalize()}\n\n{footer}"

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
        mem[uid]["entries"] = mem[uid]["entries"][-15:]
        save_memory(mem)
    except Exception as e:
        print("[AI Auto-Reply] memory save failed:", e)

    try: msg.reply_text(final, parse_mode=ParseMode.HTML)
    except Exception:
        try: msg.reply_text(final)
        except: pass

def register_handlers(dp, config=None):
    try:
        from telegram.ext import MessageHandler, Filters
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
    except Exception as e:
        print("[ai_auto_reply] register failed:", e)

if __name__ == "__main__":
    print("ai_auto_reply v8.7.6 — paste into plugins/ and load via your plugin manager. (ContinuityPatch v2)")
