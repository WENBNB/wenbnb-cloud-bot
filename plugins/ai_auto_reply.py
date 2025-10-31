# plugins/ai_auto_reply.py
# ============================================================
# WENBNB • AI Auto-Reply v9.1 "Queen Mode" (Option A Classic)
# Hybrid flirt + TopicLock • Hinglish-aware • MemoryContext++
# ------------------------------------------------------------
# ✅ Ignores /commands and bot messages (no double trigger)
# ✅ Works in DMs + Groups (balanced tone)
# ✅ Keeps replies short, warm, a little flirty (but not cringe)
# ✅ TopicLock: stays on the user's task until it's wrapped
# ✅ NameLock: preserves user's exact username/first_name casing
# ✅ Mood icons with dynamic signature based on vibe
# ✅ Uses OpenAI or your proxy (AI_PROXY_URL) with fallback lines
# ============================================================

import os, json, random, requests, traceback, re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

# --------------------------
# Config / Env
# --------------------------
AI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")  # If set, used instead of OpenAI
MEMORY_FILE  = os.getenv("WENBNB_MEMORY_FILE", "user_memory.json")

# TopicLock timing: if user talks within this window, keep on-topic
TOPIC_LOCK_WINDOW_SEC = 420  # 7 minutes

# --------------------------
# Storage (very small JSON)
# --------------------------
def load_memory() -> Dict[str, Any]:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_memory(data: Dict[str, Any]) -> None:
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# --------------------------
# Mood / Icons
# --------------------------
MOOD_ICON_VARIANTS = {
    "Positive":  ["🔥", "🚀", "✨"],
    "Reflective":["🌙", "💭", "✨"],
    "Balanced":  ["🙂", "💫", "😌"],
    "Angry":     ["😠", "😤"],
    "Sad":       ["😔", "💔"],
    "Excited":   ["🤩", "💥", "🎉"]
}

def pick_mood_icon(mood: str) -> str:
    return random.choice(MOOD_ICON_VARIANTS.get(mood, MOOD_ICON_VARIANTS["Balanced"]))

# --------------------------
# Username / NameLock
# --------------------------
def canonical_name(user) -> str:
    # Preserve exact case if username exists; else first_name
    if getattr(user, "username", None):
        return user.username
    return user.first_name or "friend"

def display_handle(user) -> str:
    if getattr(user, "username", None):
        return f"@{user.username}"
    return user.first_name or "friend"

# --------------------------
# Language / Hinglish
# --------------------------
def contains_devanagari(text: str) -> bool:
    return any("\u0900" <= ch <= "\u097F" for ch in text)

def wants_hinglish(text: str) -> bool:
    tokens = ["bhai", "yaar", "kya", "accha", "acha", "nahi", "haan", "bolo", "chal", "kuch", "karna", "madad"]
    t = text.lower()
    return contains_devanagari(text) or any(tok in t for tok in tokens)

# --------------------------
# Topic detection (light)
# --------------------------
TOPIC_MAP = {
    "market":   ["bnb", "btc", "eth", "crypto", "coin", "token", "chart", "pump", "dump", "market", "price"],
    "airdrop":  ["airdrop", "claim", "reward", "points", "task", "quest"],
    "web3":     ["wallet", "metamask", "gas", "contract", "web3", "bridge", "dex", "stake"],
    "fun":      ["meme", "joke", "haha", "lol", "funny"],
    "life":     ["sleep", "love", "work", "tired", "busy", "mood"],
    "general":  []
}

def detect_topic(text: str) -> str:
    t = text.lower()
    for topic, keys in TOPIC_MAP.items():
        if any(k in t for k in keys):
            return topic
    return "general"

# --------------------------
# Dynamic signature
# --------------------------
def build_signature(mood: str) -> str:
    if mood in ("Positive", "Excited"):
        return "<b>🚀 WENBNB Neural Engine</b> — Always on, always empathic"
    if mood == "Reflective":
        return "<i>✨ WENBNB Neural Engine — Calm • Thoughtful</i>"
    return "<b>⚡ WENBNB Neural Engine</b> — Emotional Intelligence 24×7"

# --------------------------
# Smart Greeting (no spam)
# --------------------------
def smart_greeting(uid: str, name: str, hinglish: bool, mood: str, mem: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    udata = mem.get(uid, {})
    last_used = udata.get("last_name_used", False)
    include = not last_used and random.random() < 0.85

    vibe = "chill"
    if mood in ("Positive", "Excited"): vibe = "playful"
    elif mood == "Reflective":          vibe = "gentle"

    greeting = ""
    if include:
        if hinglish:
            bank = {
                "playful": [f"Are {name} 😄,", f"Sun na {name},", f"{name} yaar,"],
                "gentle":  [f"{name},", f"Arey {name},", f"Hello {name},"],
                "chill":   [f"{name},", f"Yo {name},", f"Bas vibe dekh {name},"],
            }
        else:
            bank = {
                "playful": [f"Hey {name} 👋,", f"Yo {name},", f"{name}, good to see you!"],
                "gentle":  [f"Hello {name},", f"Hey {name},", f"{name},"],
                "chill":   [f"Yo {name},", f"Sup {name},", f"{name},"],
            }
        greeting = random.choice(bank[vibe]) + " "
        udata["last_name_used"] = True
    else:
        if random.random() < 0.25:
            udata["last_name_used"] = False

    mem[uid] = udata
    return greeting, mem

# --------------------------
# Small talk detector
# --------------------------
SMALL_TALK_PATTERNS = [
    r"\b(hi|hello|hey|yo|sup)\b",
    r"\b(kaisi|kaise|kya haal|how r u|how are you|kya scene)\b",
    r"❤️|💋|😘|😉|😜|🥰|😏"
]
small_talk_re = re.compile("|".join(SMALL_TALK_PATTERNS), re.IGNORECASE)

def is_small_talk(text: str) -> bool:
    return bool(small_talk_re.search(text))

# --------------------------
# TopicLock memory helpers
# --------------------------
def get_user_state(mem: Dict[str, Any], uid: str) -> Dict[str, Any]:
    return mem.setdefault(uid, {"entries": [], "topic_lock": None})

def set_topic_lock(mem: Dict[str, Any], uid: str, topic: str) -> None:
    mem.setdefault(uid, {"entries": []})
    mem[uid]["topic_lock"] = {
        "topic": topic,
        "last_at": datetime.utcnow().isoformat()
    }

def topic_locked_topic(mem: Dict[str, Any], uid: str) -> Optional[str]:
    st = mem.get(uid, {}).get("topic_lock")
    if not st: return None
    try:
        last_at = datetime.fromisoformat(st["last_at"])
    except Exception:
        return None
    if datetime.utcnow() - last_at <= timedelta(seconds=TOPIC_LOCK_WINDOW_SEC):
        return st["topic"]
    return None

def refresh_topic_lock(mem: Dict[str, Any], uid: str) -> None:
    st = mem.get(uid, {}).get("topic_lock")
    if st:
        st["last_at"] = datetime.utcnow().isoformat()

# --------------------------
# OpenAI / Proxy call
# --------------------------
def build_system_prompt(user_name: str, mood: str, hinglish: bool,
                        memory_context: Optional[List[str]],
                        locked_topic: Optional[str]) -> str:
    p = (
        "You are WENBNB — warm, witty, emotionally-aware. "
        "Keep replies short (1–4 sentences), natural, playful but helpful. "
        "Never derail the user's current task; if TopicLock is active, stay tight on it. "
        "Avoid robotic phrasing; 1 emoji max if it fits.\n"
    )
    if hinglish:
        p += "Prefer casual Hinglish (Hindi+English) where natural. "
    if memory_context:
        p += f"Recently discussed: {', '.join(memory_context)}. "
    if locked_topic:
        p += f"TopicLock: Focus on '{locked_topic}' right now; do not switch topic unless user clearly changes it. "
    p += f"User: {user_name}. Mood: {mood}."
    return p

def call_ai(user_prompt: str, user_name: str, mood: str, hinglish: bool,
            memory_context: Optional[List[str]], locked_topic: Optional[str]) -> Optional[str]:
    sys_prompt = build_system_prompt(user_name, mood, hinglish, memory_context, locked_topic)
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        "temperature": 0.9,
        "max_tokens": 180
    }
    url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    if not AI_PROXY_URL:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"

    try:
        resp = requests.post(url, headers=headers, json=body, timeout=22)
        data = resp.json()
        if "choices" in data and data["choices"]:
            msg = data["choices"][0].get("message", {}).get("content") or data["choices"][0].get("text")
            if msg:
                return msg.strip()
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "OpenAI error"))
    except Exception as e:
        print("[ai_auto_reply] OpenAI/proxy call failed:", e)
        try:
            traceback.print_exc(limit=1)
        except Exception:
            pass
    return None

# --------------------------
# Fallbacks
# --------------------------
FALLBACK_OPENERS = [
    "Signal blinked for a sec 😅 — meri taraf se:",
    "Neural cloud thoda busy tha, but listen:",
    "Small hiccup aaya, par vibe clear hai:"
]
FALLBACK_LINERS = [
    "Chill raho; isi flow me aage badhte hain.",
    "Yeh direction sahi lag raha — continue karo.",
    "Focus pakdo; result milne wale hain."
]

# --------------------------
# MAIN HANDLER
# --------------------------
def ai_auto_chat(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not getattr(msg, "text", None):
        return

    # 🚫 Ignore slash commands and bots
    text = msg.text.strip()
    if text.startswith("/"):
        return
    if getattr(update.effective_user, "is_bot", False):
        return

    chat_id = msg.chat_id
    user    = update.effective_user
    uid     = str(user.id)

    # Typing indicator (best-effort)
    try:
        context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception:
        pass

    # Identity
    name_lock = canonical_name(user)       # exact-case name
    handle    = display_handle(user)

    # Preferences
    hinglish  = wants_hinglish(text)

    # Memory / Mood
    mem = load_memory()
    ustate = get_user_state(mem, uid)
    last_mood = "Balanced"
    if ustate.get("entries"):
        last_mood = ustate["entries"][-1].get("mood", "Balanced")

    # TopicLock infer
    current_topic = detect_topic(text)
    locked_topic  = topic_locked_topic(mem, uid) or current_topic
    # if user is engaging again soon, refresh lock
    set_topic_lock(mem, uid, locked_topic)
    refresh_topic_lock(mem, uid)

    # Recent topics summary (for system prompt)
    recent_topics: List[str] = []
    if ustate.get("entries"):
        seen = []
        for e in reversed(ustate["entries"]):
            tpc = e.get("topic")
            if tpc and tpc not in seen:
                seen.append(tpc)
            if len(seen) >= 3:
                break
        recent_topics = list(reversed(seen))

    # Call AI
    ai_text = call_ai(text, name_lock, last_mood, hinglish, recent_topics, locked_topic)
    if not ai_text or not ai_text.strip():
        ai_text = random.choice(FALLBACK_OPENERS) + " " + random.choice(FALLBACK_LINERS)

    # Small talk guard: add a tiny playful tag only when not locked into a serious topic
    playful_tail = ""
    if is_small_talk(text) and locked_topic in ("general", "fun"):
        playful_tail = " 😉"

    # Smart greeting
    icon = pick_mood_icon(last_mood)
    greet, mem = smart_greeting(uid, name_lock, hinglish, last_mood, mem)

    # Build signature
    footer = build_signature(last_mood)

    # Final message polish
    # Avoid double name if model echoes placeholders
    ai_text = ai_text.replace("{name}", name_lock).strip()
    # Capitalize first char softly
    if ai_text and ai_text[0].isalpha():
        ai_text = ai_text[0].upper() + ai_text[1:]

    final = f"{icon} {greet}{ai_text}{playful_tail}\n\n{footer}"

    # Save memory
    try:
        entry = {
            "text": text,
            "reply": ai_text,
            "mood": last_mood,
            "topic": current_topic,
            "time": datetime.utcnow().isoformat()
        }
        ustate["entries"].append(entry)
        ustate["entries"] = ustate["entries"][-18:]  # keep last 18
        mem[uid] = ustate
        save_memory(mem)
    except Exception:
        pass

    # Send
    try:
        msg.reply_text(final, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except Exception:
        try:
            msg.reply_text(final)
        except Exception:
            pass

# --------------------------
# Registration hook (plugin_manager)
# --------------------------
def register_handlers(dp, config=None):
    try:
        from telegram.ext import MessageHandler, Filters
        # IMPORTANT: only non-command text (prevents double trigger)
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
    except Exception as e:
        print("[ai_auto_reply] register failed:", e)

# Standalone quick check
if __name__ == "__main__":
    print("ai_auto_reply v9.1 — drop into plugins/ and let plugin_manager load it.")
