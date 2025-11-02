"""
WENBNB AI Auto-Context v9.1 — Global Human Vibe Engine 🌍❤️
• World-wide audience friendly (auto tone adjust)
• Soft continuity memory (supports ai_auto_reply)
• NEVER force topic / NEVER override vibe
• Flirt+Roast balance intact
• Asks clarifying questions instead of assuming
"""

import json, os, time
from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext

CTX_FILE = "ctx_state.json"

def load_state():
    if not os.path.exists(CTX_FILE): return {}
    try: return json.load(open(CTX_FILE, "r"))
    except: return {}

def save_state(data):
    json.dump(data, open(CTX_FILE, "w"), indent=2, ensure_ascii=False)

state = load_state()

# Light-touch keywords, no hard lock
LANG_HINT = {
    "hi": "Hinglish",
    "en": "English",
    "ar": "Arabic",
    "es": "Spanish",
    "ru": "Russian"
}

def guess_lang(text):
    t = text.lower()
    if any(c in t for c in ["ह","क","त","म","ं"]): return "Hinglish"
    if any(ord(c) > 122 for c in t): return "Non-Latin"
    return "English"

def update_context(uid, msg):
    user = state.setdefault(str(uid), {})
    user.setdefault("recent", [])
    user["recent"].append(msg[-160:])
    user["recent"] = user["recent"][-6:]  # last ~6 lines
    user["lang"] = guess_lang(msg)
    state[str(uid)] = user
    save_state(state)
    return user

def build_flavor_prompt(user):
    lines = " | ".join(user.get("recent", []))
    lang = user.get("lang", "English")
    return (
        f"User language vibe: {lang}. "
        f"Last lines: {lines}. "
        "Maintain soft flirt, tiny sarcasm, supportive tone. "
        "If unsure of topic, ask gently. "
        "Do NOT push productivity unless user starts it."
    )

# This file does NOT respond — it only enriches context.
def ai_auto_context(update: Update, context: CallbackContext):
    text = update.message.text.strip()
    if text.startswith("/"): return
    uid = update.effective_user.id
    update_context(uid, text)

# Wire as silent middleware
def register_handlers(dp):
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_context))
    print("✅ Loaded context module v9.1 — vibe enhancer mode")
