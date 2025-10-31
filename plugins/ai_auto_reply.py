# plugins/ai_auto_reply.py
"""
Emotion Patch v9 — WENBNB AI Auto-Reply (drop-in)
• Smart mood from emojis + keywords + recent context
• Hinglish-aware, short replies (≤4 sentences)
• Skips /commands and button-triggered slashes
• Per-user cooldown (default 2.5s) to prevent spam
• NameLock (preserve exact @username / first_name), no {name} leaks
• Lightweight memory of last 15 turns per user
"""

import os, json, re, time, random, requests, traceback
from datetime import datetime
from typing import Dict, Any, List, Optional
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")     # optional
MEMORY_FILE  = "user_memory.json"
COOLDOWN_SEC = 2.5                                # per-user anti-spam

# ---------------- Memory ----------------
def _load() -> Dict[str, Any]:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def _save(data: Dict[str, Any]) -> None:
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --------------- Helpers ----------------
def _contains_devanagari(t: str) -> bool:
    return any("\u0900" <= ch <= "\u097F" for ch in t)

def _wants_hinglish(t: str) -> bool:
    common = ["bhai", "yaar", "kya", "haan", "nahi", "accha", "bolo", "chalo", "kuch", "kaise"]
    tl = t.lower()
    return _contains_devanagari(t) or any(w in tl for w in common)

def _canon_name(user) -> str:
    return user.username if getattr(user, "username", None) else (user.first_name or "friend")

# quick mood from emojis/words + light memory
POS_WORDS = {"great","nice","love","super","amazing","op","bull","pump","moon","profit","win","happy"}
NEG_WORDS = {"bad","sad","down","loss","lose","dump","bear","angry","fuck","tension","problem"}
EMO_POS   = set("😄🙂😊🤩😍🔥🚀✨🎉👍💪")
EMO_NEG   = set("😔☹️😢😭😡🤬😤💔👎")

def _guess_mood(text: str, recent: Optional[str]) -> str:
    t = text.lower()
    score = 0
    score += sum(1 for ch in text if ch in EMO_POS)
    score -= sum(1 for ch in text if ch in EMO_NEG)
    score += sum(1 for w in POS_WORDS if w in t)
    score -= sum(1 for w in NEG_WORDS if w in t)
    if recent == "fun": score += 1
    if recent == "market" and ("crash" in t or "down" in t): score -= 1
    if score >= 2: return "Excited"
    if score == 1: return "Positive"
    if score <= -2: return "Sad"
    if score == -1: return "Angry"
    return "Balanced"

def _topic(text: str) -> str:
    buckets = {
        "market": ["bnb","btc","eth","crypto","token","coin","chart","pump","dump","market","price"],
        "airdrop": ["airdrop","claim","points","reward","galxe","zealy"],
        "web3": ["wallet","metamask","contract","gas","swap","dex","bridge"],
        "fun": ["meme","joke","funny","lol","haha"],
        "life": ["work","study","sleep","love","bored","busy"]
    }
    tl = text.lower()
    for k, arr in buckets.items():
        if any(w in tl for w in arr): return k
    return "general"

def _signature(mood: str) -> str:
    if mood in ("Excited","Positive"): return "<b>🚀 WENBNB Neural Engine</b> — always on"
    if mood == "Sad":                 return "<i>✨ WENBNB Neural Engine — here for you</i>"
    if mood == "Angry":               return "<i>⚡ WENBNB Neural Engine — steady & calm</i>"
    return "<b>⚡ WENBNB Neural Engine</b>"

def _greet_once(mem: Dict[str, Any], uid: str, name: str, hinglish: bool, mood: str) -> str:
    u = mem.get(uid, {})
    last_flag = u.get("last_name_used", False)
    use_name = not last_flag and random.random() < 0.85
    tone = ("yo", "gentle", "playful")[
        0 if mood in ("Balanced","Angry") else (1 if mood=="Sad" else 2)
    ]
    if not use_name:
        if random.random() < 0.25: u["last_name_used"] = False
        mem[uid] = u
        return ""
    if hinglish:
        options = {
            "yo": [f"Yo {name}, ", f"{name}, ", f"Sun na {name}, "],
            "gentle": [f"{name}, ", f"Arey {name}, ", f"{name} bhai, "],
            "playful": [f"Hey {name} 👋, ", f"Are {name} 😄, ", f"Yo {name}, "],
        }
    else:
        options = {
            "yo": [f"Yo {name}, ", f"{name}, ", f"Sup {name}, "],
            "gentle": [f"Hey {name}, ", f"Hello {name}, ", f"{name}, "],
            "playful": [f"Hey {name} 👋, ", f"Yo {name}, ", f"Good to see you, {name}! "],
        }
    u["last_name_used"] = True
    mem[uid] = u
    return random.choice(options[tone])

def _shorten_sentences(txt: str, max_sents: int = 4) -> str:
    # split naive by punctuation
    parts = re.split(r'(?<=[.!?])\s+', txt.strip())
    return " ".join(parts[:max_sents])

# --------------- OpenAI ----------------
def _ai(text: str, name: str, mood: str, hinglish: bool, mem_ctx: List[str]) -> Optional[str]:
    sys = (
        "You are WENBNB AI — warm, witty, emotionally aware. "
        "Reply in 1–4 short sentences, natural and playful, no boilerplate. "
        "Avoid repeating the user's handle twice. "
    )
    if hinglish: sys += "Use light Hinglish (Hindi+English) if it fits. "
    if mem_ctx:  sys += f"Recent topics: {', '.join(mem_ctx)}. "
    # temperature light-tuned by mood
    temp = 0.85 if mood in ("Balanced","Reflective") else 1.0

    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": sys},
            {"role": "user",   "content": text}
        ],
        "temperature": temp,
        "max_tokens": 180,
    }
    url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    if not AI_PROXY_URL:
        headers["Authorization"] = f"Bearer {AI_API_KEY}"

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=20)
        data = resp.json()
        ch = (data.get("choices") or [{}])[0]
        msg = ch.get("message", {}).get("content") or ch.get("text")
        if msg:
            return _shorten_sentences(msg.strip(), 4)
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "OpenAI error"))
    except Exception as e:
        print("[EmotionPatch v9] OpenAI fail:", e)
        try: traceback.print_exc(limit=1)
        except: pass
    return None

# --------------- MAIN ------------------
def ai_auto_chat(update: Update, context: CallbackContext):
    m = update.message
    if not m or not m.text:
        return

    text = m.text.strip()
    # ❌ never reply to slash commands
    if text.startswith("/"): 
        return

    user = update.effective_user
    uid  = str(user.id)
    chat_id = m.chat_id

    mem = _load()
    # Cooldown per user
    now = time.time()
    last_ts = mem.get(uid, {}).get("_last_ts", 0)
    if now - last_ts < COOLDOWN_SEC:
        return
    mem.setdefault(uid, {})["_last_ts"] = now

    name = _canon_name(user)
    hinglish = _wants_hinglish(text)

    # memory topics for context
    recent_topics = []
    if "entries" in mem.get(uid, {}):
        seen = []
        for e in reversed(mem[uid]["entries"]):
            t = e.get("topic")
            if t and t not in seen:
                seen.append(t)
        recent_topics = list(reversed(seen))[:3]

    # mood guess
    last_topic = recent_topics[-1] if recent_topics else None
    mood = _guess_mood(text, last_topic)

    # UX: typing
    try: context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except: pass

    # generate
    ai = _ai(text, name, mood, hinglish, recent_topics)
    if not ai:
        ai = "Signal blinked for a moment 😅 — but here’s a crisp take: trust your read and move steady."

    # cleanup any accidental placeholders
    ai = ai.replace("{name}", name)

    greet = _greet_once(mem, uid, name, hinglish, mood)
    footer = _signature(mood)
    icon = {"Excited":"🤩","Positive":"✨","Balanced":"🙂","Sad":"💛","Angry":"🛟"}.get(mood, "💫")

    final = f"{icon} {greet}{ai}\n\n{footer}"

    # persist memory
    try:
        mem.setdefault(uid, {}).setdefault("entries", [])
        mem[uid]["entries"].append({
            "text": text,
            "reply": ai,
            "mood": mood,
            "topic": _topic(text),
            "time": datetime.now().isoformat()
        })
        mem[uid]["entries"] = mem[uid]["entries"][-15:]
        _save(mem)
    except Exception as e:
        print("[EmotionPatch v9] memory save fail:", e)

    # send
    try:
        m.reply_text(final, parse_mode=ParseMode.HTML)
    except Exception:
        m.reply_text(final)

# Plugin loader hook
def register_handlers(dp, config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
