# plugins/memory_engine.py
"""
WENBNB Neural Memory Engine v9.1 — Pure Continuity Core
────────────────────────────────────────────────────────
• Emotional memory + tone sync (48h auto-cleanup)
• Conversation Continuity: remembers last themes + last lines
• Zero goal/intent forcing (fits human-first ai_auto_reply)
• 100% compatible with user_memory.json used by ai_auto_reply
"""

import os
import json
import time
from datetime import datetime, timedelta
from textblob import TextBlob
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === Files ===
MEMORY_FILE = "user_memory.json"
EMOTION_SYNC_FILE = "emotion_sync.db"         # optional external signals (if present)
STABILIZER_FILE   = "emotion_stabilizer.db"   # optional external signals (if present)

BRAND_TAG = "🚀 Powered by WENBNB Neural Engine — Emotional Intelligence 24×7"

# ============================================================
#                     JSON helpers
# ============================================================
def _load_json(path, default=None):
    if not os.path.exists(path):
        return default or {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default or {}

def _save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def load_memory():
    return _load_json(MEMORY_FILE, {})

def save_memory(data):
    _save_json(MEMORY_FILE, data)

# ============================================================
#               Emotion analysis (lightweight)
# ============================================================
def analyze_emotion(text: str) -> str:
    """
    Very simple polarity→mood mapping using TextBlob.
    Positive > 0.3, Negative < -0.3, otherwise Balanced.
    """
    try:
        p = TextBlob(text).sentiment.polarity
    except Exception:
        p = 0.0
    if p > 0.3:
        return "Positive"
    if p < -0.3:
        return "Negative"
    return "Balanced"

# ============================================================
#                External emotion merge (optional)
# ============================================================
def _merge_external_emotion(user_id: int, mood: str):
    """
    If external files exist, merge some signals for richer context.
    All fields are optional — safe if files don’t exist.
    """
    sync = _load_json(EMOTION_SYNC_FILE, {})
    stab = _load_json(STABILIZER_FILE, {})

    uid = str(user_id)
    e = sync.get(uid, {})
    s = stab.get(uid, {})

    return {
        "score":       e.get("emotion_score", s.get("emotion_score", 0)),
        "label":       s.get("emotion_label", "🤖 neutral"),
        "last_emoji":  e.get("last_emojis", "🙂"),
        "last_updated": s.get("last_updated", time.strftime("%Y-%m-%d %H:%M:%S")),
        "context_tags": f"{mood} | {s.get('emotion_label', '🤖 neutral')}"
    }

# ============================================================
#                    Continuity helpers
# ============================================================
def _trim_line(s: str) -> str:
    s = (s or "").strip()
    return (s[:140] + "…") if len(s) > 140 else s

def continuity_update(mem: dict, uid: str, user_text: str) -> dict:
    """
    Store light-weight continuity:
      • thread: last 5 topic tags
      • last_lines: last 6 raw user messages (trimmed)
    NOTE: topic tags are inferred by ai_auto_reply; we only manage structure here.
    """
    u = mem.setdefault(uid, {})
    # Basic topic guess for thread (kept minimal; ai_auto_reply also tags per entry)
    topic = _guess_topic(user_text)
    thr = u.setdefault("thread", [])
    if not thr or thr[-1] != topic:
        thr.append(topic)
        u["thread"] = thr[-5:]

    lines = u.setdefault("last_lines", [])
    lines.append(_trim_line(user_text))
    u["last_lines"] = lines[-6:]

    mem[uid] = u
    return mem

def continuity_snapshot(mem: dict, uid: str):
    u = mem.get(uid, {})
    return {
        "thread": u.get("thread", []),
        "last_lines": u.get("last_lines", [])
    }

# Tiny topic guess (kept aligned with ai_auto_reply buckets)
TOPIC_KEYS = {
    "market": ["bnb","btc","eth","crypto","token","coin","chart","pump","dump","market","price","trade"],
    "airdrop": ["airdrop","claim","reward","points","task","quest","farm"],
    "web3": ["wallet","connect","metamask","gas","contract","deploy","bot","stake","dex","bridge"],
    "life": ["sleep","love","work","tired","busy","relationship","mood"],
    "fun": ["meme","joke","haha","lol","funny"],
    "travel": ["travel","trip","itinerary","flight","hotel","visa"]
}
def _guess_topic(text: str) -> str:
    t = (text or "").lower()
    for k, vocab in TOPIC_KEYS.items():
        if any(word in t for word in vocab):
            return k
    return "general"

# ============================================================
#                 Entry cleanup (48 hours)
# ============================================================
def _clean_entries(entries: list):
    """
    Keep entries within 48h sliding window and limit tail to last 15.
    """
    if not entries:
        return []
    out = []
    now = datetime.now()
    for e in entries:
        try:
            ts = datetime.fromisoformat(e["time"])
        except Exception:
            # backward compatibility with "%Y-%m-%d %H:%M:%S"
            try:
                ts = datetime.strptime(e["time"], "%Y-%m-%d %H:%M:%S")
            except Exception:
                ts = now
        if now - ts <= timedelta(hours=48):
            out.append(e)
    return out[-15:]

# ============================================================
#                     Memory update API
# ============================================================
def update_memory(user_id: int, message: str, memory: dict):
    """
    Core updater used by /aianalyze (and can be used by other plugins).
    Saves:
      • entries[] with text/mood/tags/time
      • continuity (thread + last_lines)
    """
    mood = analyze_emotion(message)
    emo  = _merge_external_emotion(user_id, mood)
    uid  = str(user_id)

    u = memory.setdefault(uid, {})
    entries = u.setdefault("entries", [])

    entry = {
        "text": message,
        "mood": mood,
        "emotion_label": emo["label"],
        "emoji": emo["last_emoji"],
        "context_tags": emo["context_tags"],
        "time": datetime.now().isoformat()
    }
    entries.append(entry)
    u["entries"] = _clean_entries(entries)

    # Update continuity (no goals/intent)
    continuity_update(memory, uid, message)

    memory[uid] = u
    save_memory(memory)
    return mood, emo

# ============================================================
#                        Commands
# ============================================================
def aianalyze(update: Update, context: CallbackContext):
    """
    /aianalyze <text> — quick emotion sync & store continuity.
    """
    user = update.effective_user
    memory = load_memory()
    args = context.args or []

    if not args:
        update.message.reply_text(
            "💭 Use like:\n<code>/aianalyze I'm feeling bullish about WENBNB!</code>",
            parse_mode="HTML"
        )
        return

    text = " ".join(args).strip()
    mood, emo = update_memory(user.id, text, memory)

    reply = (
        f"🪞 <b>Emotional Sync:</b> {mood}\n"
        f"<b>Context:</b> {emo['context_tags']}\n\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(reply, parse_mode="HTML")

def show_memory(update: Update, context: CallbackContext):
    """
    /memory — show last few entries + continuity snapshot.
    """
    user = update.effective_user
    mem = load_memory()
    u = mem.get(str(user.id), {})

    entries = u.get("entries", [])
    cont = continuity_snapshot(mem, str(user.id))

    if not entries:
        update.message.reply_text("🫧 No memory yet. Try /aianalyze to start syncing.")
        return

    text = "<b>🧠 WENBNB Memory Snapshot — v9.1 Continuity Core</b>\n\n"
    if cont.get("thread"):
        text += "🔖 <b>Recent themes:</b> " + " • ".join(cont["thread"]) + "\n"
    if cont.get("last_lines"):
        text += "🗒️ <b>Last lines:</b> " + " | ".join(cont["last_lines"]) + "\n\n"

    for item in entries[-5:]:
        text += (
            f"🕒 {item['time']}\n"
            f"💬 {item['text']}\n"
            f"Mood: {item['mood']} | {item['emotion_label']} {item['emoji']}\n"
            f"Tags: {item['context_tags']}\n\n"
        )

    text += f"{BRAND_TAG}"
    update.message.reply_text(text, parse_mode="HTML")

def reset_memory(update: Update, context: CallbackContext):
    """
    /forget — clear only this user's memory block (safe to others).
    """
    mem = load_memory()
    uid = str(update.effective_user.id)

    if uid in mem:
        del mem[uid]
        save_memory(mem)
        update.message.reply_text("🧹 Memory cleared. Fresh start 🤝✨")
    else:
        update.message.reply_text("🫧 No stored memory to reset.")

# ============================================================
#                    Register Handlers
# ============================================================
def register_handlers(dp):
    dp.add_handler(CommandHandler("aianalyze", aianalyze))
    dp.add_handler(CommandHandler("memory", show_memory))
    dp.add_handler(CommandHandler("forget", reset_memory))
    print("✅ Loaded plugin: memory_engine v9.1 (Pure Continuity Core)")
