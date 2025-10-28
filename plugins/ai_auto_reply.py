# plugins/ai_auto_reply.py
"""
WENBNB AI Auto-Reply v8.8.4 — EmotionHuman++ FeelSync Edition
• Brings back the "feel": natural tone, context-mirroring, dynamic emoji palette
• MemoryContext++ friendly, safe for reloads (supports register_handlers(dp, config=None))
• Avoids robotic repeated greetings, mirrors user tone (baby/jaan if user uses it)
• Short footers, single inline emoji, playful & warm replies
"""

import os
import json
import random
import requests
import traceback
import re
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

# -------- CONFIG --------
AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE = "user_memory.json"
MAX_MEMORY_ENTRIES = 15

# -------- UTIL: memory --------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_memory(data):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("[ai_auto_reply] save_memory error:", e)

# -------- UTIL: mood & emoji --------
MOOD_ICON = {
    "Positive": ["🔥","🤩","💥"],
    "Reflective": ["✨","🫡","🌙"],
    "Balanced": ["🙂","🤖","💫"],
    "Angry": ["😠","😤"],
    "Sad": ["😔","💔"],
    "Excited": ["🤩","🚀","🎉"]
}

def last_user_mood(uid):
    mem = load_memory()
    u = mem.get(str(uid), {})
    entries = u.get("entries") or []
    if not entries:
        return "Balanced", random.choice(MOOD_ICON["Balanced"])
    last = entries[-1]
    mood = last.get("mood", "Balanced")
    # pick a mood icon dynamically (avoid fixed emoji)
    icon = random.choice(MOOD_ICON.get(mood, MOOD_ICON["Balanced"]))
    return mood, icon

# -------- UTIL: language/topic detection --------
def contains_devanagari(t):
    return any("\u0900" <= ch <= "\u097F" for ch in t)

def detect_topic(text: str):
    text = text.lower()
    topics = {
        "market": ["bnb","btc","eth","crypto","token","coin","chart","pump","dump"],
        "airdrop": ["airdrop","claim","reward","task","points"],
        "life": ["sleep","love","work","tired","busy","time"],
        "fun": ["meme","joke","haha","lol"],
        "web3": ["wallet","metamask","connect","gas","contract"]
    }
    for k, v in topics.items():
        if any(x in text for x in v):
            return k
    return "general"

# -------- GREETING/MIRROR LOGIC (feel-focused) --------
def smart_greeting(user_id, name, hinglish, mood, mem):
    """
    Greet naturally but avoid repeating the name every message.
    Mirror user terms: if user uses 'baby' or 'jaan' we may mirror once in a while.
    Stores 'last_name_used' and 'last_mirror' in memory for subtlety.
    """
    uid = str(user_id)
    mem.setdefault(uid, {"entries": []})
    meta = mem.get(uid, {}).get("meta", {}) or {}
    greet = ""
    # Mirror tokens
    mirror_tokens = ["baby", "jaan", "yaar", "bro", "sis"]
    # If user recently used a mirror word, increase chance to mirror
    recent_texts = [e.get("text","").lower() for e in mem[uid].get("entries", [])[-4:]]
    used_mirror = any(any(tok in t for tok in mirror_tokens) for t in recent_texts)

    # name usage logic
    used_name = meta.get("last_name_used", False)
    # 65% chance to greet, less if name used just before
    greet_chance = 0.65 if not used_name else 0.25
    if random.random() < greet_chance:
        vibe = "chill"
        if mood in ["Positive","Excited"]: vibe = "playful"
        elif mood in ["Reflective","Sad"]: vibe = "gentle"

        if hinglish:
            opts = {
                "playful": [f"Are {name} 😊,", f"{name} yaar,", f"Sun na {name},"],
                "gentle":  [f"{name} bhai,", f"{name},", f"Arey {name},"],
                "chill":   [f"{name},", f"Yo {name},", f"Bas {name},"]
            }
        else:
            opts = {
                "playful": [f"Hey {name} 👋,", f"Yo {name},", f"{name}, good to see you!"],
                "gentle":  [f"Hey {name},", f"{name},", f"Hello {name},"],
                "chill":   [f"Yo {name},", f"Sup {name},", f"{name},"]
            }
        greet = random.choice(opts[vibe]) + " "
        meta["last_name_used"] = True
    else:
        meta["last_name_used"] = False

    # mirror "baby/jaan" occasionally if user used it recently
    mirror = ""
    if used_mirror and random.random() < 0.35:
        # pick a natural mirror phrase
        mirror = random.choice(["love ya", "meri jaan", "baby", "yaar"]) + " "
        # store mirror usage so we don't spam next message
        meta["last_mirror"] = datetime.now().isoformat()
    else:
        meta["last_mirror"] = meta.get("last_mirror")

    # update meta into memory
    mem[uid].setdefault("meta", {}).update(meta)
    return f"{mirror}{greet}".strip(), mem

# -------- PROMPT BUILD --------
def build_prompt(user_name, mood, hinglish, recent_topics):
    p = (
        "You are WENBNB AI — a warm, witty and emotionally-aware companion. "
        "Write short, natural replies (1-4 sentences). Be playful but respectful. "
        "Use at most one emoji inline and never start with a robotic header like 'Mood vibe detected'. "
    )
    if hinglish:
        p += "If user writes in Hindi or Hinglish, reply casually in Hinglish (mix of Hindi + English). "
    if recent_topics:
        p += f"Recently talked about: {', '.join(recent_topics)}. Keep continuity and reference them when natural. "
    p += f"User name: {user_name}. Current mood: {mood}."
    return p

# -------- OPENAI / PROXY CALL (safe) --------
def call_ai(prompt, user_name, mood, hinglish, recent_topics):
    sys = build_prompt(user_name, mood, hinglish, recent_topics)
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": sys},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.8,
        "max_tokens": 160
    }
    url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    if not AI_PROXY_URL and AI_API_KEY:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"
    try:
        r = requests.post(url, headers=headers, json=body, timeout=18).json()
        if isinstance(r, dict) and "choices" in r and r["choices"]:
            return r["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("[ai_auto_reply] call_ai error:", e)
        traceback.print_exc(limit=1)
    return None

# -------- FOOTER --------
def footer(mood):
    # subtle, short footer that doesn't break feel
    if mood == "Positive": return "💫 Synced with your vibe — WENBNB Neural Engine"
    if mood == "Reflective": return "✨ Synced with your vibe — WENBNB Neural Engine"
    return "🚀 Synced with your vibe — WENBNB Neural Engine"

# -------- MAIN MESSAGE HANDLER --------
def ai_auto_chat(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not msg.text:
        return
    # ignore commands (they have slashes)
    if msg.text.strip().startswith("/"):
        return

    user = update.effective_user
    text = msg.text.strip()
    chat_id = update.effective_chat.id
    name = (user.first_name or user.username or "friend")
    try:
        context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass

    # mood + dynamic icon
    mood, icon = last_user_mood(user.id)
    hinglish = contains_devanagari(text) or any(w in text.lower() for w in ["bhai","yaar","kya","acha","nahi","haan","bolo","baby","jaan"])
    topic = detect_topic(text)

    # load memory and compute recent topics to pass to model
    mem = load_memory()
    uid = str(user.id)
    recent_topics = []
    if uid in mem:
        recent_topics = [e.get("topic") for e in mem[uid].get("entries", []) if e.get("topic")]
        # unique preserve order
        seen = set(); recent_topics = [x for x in recent_topics if x and not (x in seen or seen.add(x))]
        recent_topics = recent_topics[-4:]

    # call AI
    reply = call_ai(text, name, mood, hinglish, recent_topics)
    if not reply:
        # graceful fallback preserving "feel"
        fallback_phrases = [
            "Hmm, thoda glitch hua — still feeling this:",
            "Signal thoda weak hua 🤖 — here's the vibe I get:",
            "Lagta hai AI thoda confuse hua, but this should help:"
        ]
        fallback_tail = [
            "Keep your focus.", "Stay grounded, still strong.", "Patience and discipline."
        ]
        reply = f"{random.choice(fallback_phrases)}\n\n{random.choice(fallback_tail)}"

    # greeting & mirror
    greet, mem = smart_greeting(user.id, name, hinglish, mood, mem)
    # ensure only one inline emoji — we already have dynamic icon
    if greet:
        # prefer not to start with emoji in greet; place icon before greet for warmth
        final = f"{icon} {greet} {reply.strip().capitalize()}\n\n{footer(mood)}"
    else:
        final = f"{icon} {reply.strip().capitalize()}\n\n{footer(mood)}"

    # Save memory (text, reply, topic, mood)
    mem.setdefault(uid, {"entries": []})
    mem[uid]["entries"].append({
        "text": text,
        "reply": reply,
        "mood": mood,
        "topic": topic,
        "time": datetime.now().isoformat()
    })
    # cap entries
    mem[uid]["entries"] = mem[uid]["entries"][-MAX_MEMORY_ENTRIES:]
    save_memory(mem)

    # send reply HTML-safe; avoid parse errors if reply contains HTML
    try:
        msg.reply_text(final, parse_mode=ParseMode.HTML)
    except Exception:
        try:
            # fallback plain text
            msg.reply_text(re.sub(r"<.*?>", "", final))
        except Exception:
            # last resort: single-line reply
            msg.reply_text((icon + " " + reply)[:4000])

# -------- REGISTER --------
def register_handlers(dp, config=None):
    # used by plugin manager — supports new signature or legacy.
    try:
        from telegram.ext import MessageHandler, Filters
    except Exception:
        # compatibility fallback if Filters location differs (older/newer)
        from telegram.ext import MessageHandler
        try:
            # attempt to import old style
            from telegram.ext.filters import Filters
        except Exception:
            class _F:
                text = lambda x: True
            Filters = _F

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
    print("✅ Loaded plugin: ai_auto_reply.py v8.8.4 — EmotionHuman++ FeelSync Edition")
