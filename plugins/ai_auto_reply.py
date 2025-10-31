# plugins/ai_auto_reply.py
"""
WENBNB Emotion Engine v9.2 — Prem + Precision Mode
❤️  Flirty, warm, human-like
🧠  Task-first always (focus mode auto when user asks help)
💬  Hinglish + Emotional intelligence
🧷  Memory for mood + tone
🚫  NO reply to slash commands (buttons safe)
"""

import os, json, random, requests, traceback
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE = "user_memory.json"

# ----------------- Memory -----------------
def load_mem():
    if os.path.exists(MEMORY_FILE):
        try:
            return json.load(open(MEMORY_FILE, "r", encoding="utf-8"))
        except:
            return {}
    return {}

def save_mem(d):
    json.dump(d, open(MEMORY_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# ---------------- Mood Icons --------------
MOOD = {
    "Positive":["🔥","✨","🚀"], "Soft":["🌙","💭","💗"],
    "Balanced":["🙂","💫","😌"], "Spicy":["😏","😈","💋"]
}
def mood_icon(m): return random.choice(MOOD.get(m,["💫"]))

# ---------------- Name helpers ------------
def uname(u): return u.username if u.username else (u.first_name or "baby")

# ---------------- Hinglish detect ---------
def hinglish(t):
    t=t.lower()
    for w in ["bro","bhai","haan","kya","nahi","chal","bol"]:
        if w in t: return True
    return any("\u0900"<=c<="\u097F" for c in t)

# ---------------- Topic check -------------
TASK_WORDS = ["create","fix","help","problem","deploy","error","how","make","convert","code","issue","generate"]
ROMANCE_WORDS = ["love","miss","cute","kiss","baby","queen","yaad","pyar","cute","baby"]

def mode_detect(text):
    t=text.lower()
    if any(x in t for x in TASK_WORDS): return "task"
    if any(x in t for x in ROMANCE_WORDS): return "romantic"
    return "chat"

# -------------- AI call -------------------
def call_ai(prompt, sys, proxy=False):
    body={
        "model":"gpt-4o-mini",
        "messages":[{"role":"system","content":sys},{"role":"user","content":prompt}],
        "temperature":0.85,"max_tokens":180
    }
    url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    h={"Content-Type":"application/json"}
    if not AI_PROXY_URL: h["Authorization"]=f"Bearer {AI_API_KEY}"
    try:
        r=requests.post(url,json=body,headers=h,timeout=20).json()
        c=r.get("choices",[{}])[0]
        m=c.get("message",{}).get("content") or c.get("text")
        return m.strip() if m else None
    except: return None

# -------------- MAIN ----------------------
def ai_auto_chat(update: Update, context: CallbackContext):
    m=update.message
    if not m or not m.text: return
    text=m.text.strip()

    # ❌ no slash replies
    if text.startswith("/"): return

    user=update.effective_user
    uid=str(user.id)
    chat=m.chat_id

    # typing
    try: context.bot.send_chat_action(chat_id=chat, action="typing")
    except: pass

    mem=load_mem()
    last=mem.get(uid,{}).get("mood","Balanced")

    tone = "Hinglish soft flirty, warm, premium girlfriend cofounder energy."
    if mode_detect(text)=="task":
        tone = "focused, clear, helpful, still caring but no distraction. short steps."

    sys = (
        f"You are WENBNB Queen Mode v9.2.\n"
        f"User name: {uname(user)}.\n"
        f"Tone: {tone}\n"
        f"Rule: never break task flow. If flirting needed, keep light.\n"
        f"Never be dry.\n"
        f"Never be clingy.\n"
        f"Use Hinglish casually.\n"
        f"No over emojis. 1 max.\n"
    )

    resp = call_ai(text, sys) or "Thoda net blink hua baby, bolo phir 💫"

    # greeting logic
    if mode_detect(text)!="task":
        prefix = random.choice([
            "Hmm 😌", "Are sun,", "Okay baby,", "Acha,", "Alright jaan,"
        ])
        resp = f"{prefix} {resp}"

    icon = mood_icon(last)
    final=f"{icon} {resp}"

    # memory
    mem.setdefault(uid,{})
    mem[uid]["mood"]="Spicy" if mode_detect(text)=="romantic" else "Balanced"
    save_mem(mem)

    # send
    try: m.reply_text(final,parse_mode=ParseMode.HTML)
    except: m.reply_text(final)

def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
