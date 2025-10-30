# plugins/ai_auto_reply.py
"""
AI Auto-Reply — EmotionHuman v8.7.7-StableHybrid Fix
• Keeps Hinglish + memory + vibes
• Does NOT reply to /commands or button-triggered slash
• Replies in groups + DMs
"""

import os
import json
import random
import requests
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE = "user_memory.json"

# -------------- Memory ----------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            return json.load(open(MEMORY_FILE, "r", encoding="utf-8"))
        except:
            return {}
    return {}

def save_memory(data):
    json.dump(data, open(MEMORY_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

# -------------- Mood Icons ------------
MOOD_ICON_VARIANTS = {
    "Positive": ["🔥","🚀","✨"], "Reflective":["🌙","💭","✨"], "Balanced":["🙂","💫","😌"],
    "Angry":["😠","😤"], "Sad":["😔","💔"], "Excited":["🤩","💥","🎉"]
}
def pick_mood_icon(m): return random.choice(MOOD_ICON_VARIANTS.get(m,["🙂"]))

# -------------- Username helpers ------
def canonical_username(user):
    return user.username if getattr(user,"username",None) else user.first_name or "friend"

def display_handle(user):
    return f"@{user.username}" if getattr(user,"username",None) else (user.first_name or "friend")

# -------------- Language --------------
def contains_devanagari(t): return any("\u0900" <= ch <= "\u097F" for ch in t)
def wants_hinglish(t):
    tokens=["bhai","yaar","kya","accha","nahi","haan","bolo","chal","kuch"]
    t2=t.lower()
    return contains_devanagari(t) or any(x in t2 for x in tokens)

# -------------- Topic detect ----------
def detect_topic(t):
    topics={
        "market":["bnb","btc","crypto","coin","chart","pump","market"],
        "airdrop":["airdrop","claim","reward","points"],
        "life":["sleep","love","work","tired"],
        "fun":["meme","lol","joke"],
        "web3":["wallet","metamask","gas","contract"]
    }
    t2=t.lower()
    for k,v in topics.items(): 
        if any(w in t2 for w in v): return k
    return "general"

# -------------- signature --------------
def build_signature(m):
    if m in ("Positive","Excited"): return "<b>🚀 WENBNB Neural Engine</b>"
    if m=="Reflective": return "<i>✨ WENBNB Neural Engine</i>"
    return "<b>⚡ WENBNB Neural Engine</b>"

# -------------- greet engine -----------
def smart_greeting(uid, name, hinglish, mood, mem):
    data = mem.get(uid,{})
    last = data.get("last_name_used", False)
    include = not last and random.random() < 0.85
    vibe = "chill"
    if mood in ("Positive","Excited"): vibe="playful"
    elif mood=="Reflective": vibe="gentle"

    greet=""
    if include:
        opts={
            "playful":[f"Are {name} 😄,","Yo {name},","Sun na {name},"],
            "gentle":[f"{name},","Hey {name},","Arey {name},"],
            "chill":[f"{name},","Yo {name},","Bas vibe dekh {name},"]
        } if hinglish else {
            "playful":[f"Hey {name} 👋,","Yo {name},","Good to see you {name},"],
            "gentle":[f"Hello {name},",f"Hey {name},",f"{name},"],
            "chill":[f"Yo {name},","Sup {name},",f"{name},"]
        }
        greet = random.choice(opts[vibe])+" "
        data["last_name_used"] = True
    else:
        if random.random()<0.25: data["last_name_used"]=False
    mem[uid]=data
    return greet,mem

# -------------- OpenAI ----------------
def call_ai(prompt,user_name,mood,hinglish,mem_ctx):
    sys = "Keep replies short, playful, emotional. Avoid robotic tone."
    if hinglish: sys+=" Hinglish allowed."
    if mem_ctx: sys+=f" Recent topics: {', '.join(mem_ctx)}."
    body={
        "model":"gpt-4o-mini",
        "messages":[{"role":"system","content":sys},{"role":"user","content":prompt}],
        "temperature":0.9,"max_tokens":170
    }
    url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers={"Content-Type":"application/json"}
    if not AI_PROXY_URL: headers["Authorization"]=f"Bearer {AI_API_KEY}"
    try:
        r=requests.post(url,json=body,headers=headers,timeout=20).json()
        c=r.get("choices",[{}])[0]
        msg=c.get("message",{}).get("content") or c.get("text")
        return msg.strip() if msg else None
    except: return None

FALLBACK_LINES=["Signal blinked 😅, but here’s my take:"]
FALLBACK_CONT=["Feels promising — trust vibes ✨"]

# -------------- MAIN -------------------
def ai_auto_chat(update: Update, context: CallbackContext):
    msg=update.message
    if not msg or not msg.text: return
    text=msg.text.strip()

    # ✅ DO NOT reply to slash commands (user or button)
    if text.startswith("/"):
        return

    chat_id = msg.chat_id
    user = update.effective_user
    uid = str(user.id)

    try: context.bot.send_chat_action(chat_id=chat_id, action="typing")
    except: pass

    name = canonical_username(user)
    hinglish = wants_hinglish(text)
    mem = load_memory()
    last_mood = mem.get(uid,{}).get("entries",[{"mood":"Balanced"}])[-1]["mood"]
    icon = pick_mood_icon(last_mood)

    # memory context
    rec = []
    if uid in mem:
        topics=[e.get("topic") for e in mem[uid].get("entries",[])]
        seen=[]
        for t in reversed(topics):
            if t and t not in seen: seen.append(t)
        rec=list(reversed(seen))[:3]

    ai = call_ai(text,name,last_mood,hinglish,rec) or random.choice(FALLBACK_LINES)+" "+random.choice(FALLBACK_CONT)
    greet,mem = smart_greeting(uid,name,hinglish,last_mood,mem)
    footer = build_signature(last_mood)

    final = f"{icon} {greet}{ai.strip().capitalize()}\n\n{footer}"

    # log to memory
    try:
        mem.setdefault(uid,{"entries":[]})
        mem[uid]["entries"].append({"text":text,"reply":ai,"mood":last_mood,"topic":detect_topic(text),"time":datetime.now().isoformat()})
        mem[uid]["entries"]=mem[uid]["entries"][-15:]
        save_memory(mem)
    except: pass

    try: msg.reply_text(final,parse_mode=ParseMode.HTML)
    except: msg.reply_text(final)

# registration
def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
