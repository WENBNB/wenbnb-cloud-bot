# plugins/ai_auto_reply.py
"""
AI Auto-Reply — EmotionHuman v8.7.6 + Continuity Patch v8.8 Final
• Exact-case NameLock (preserve username casing)
• SmartNick (no name spam)
• Hinglish-aware
• MemoryContext++ (recent 5 messages context)
• CONTINUITY MODE ✅ remembers flow like human chat
• No task forcing, no over-smart locks, just natural vibe
"""

import os, json, random, requests, traceback, re
from datetime import datetime
from typing import List, Dict, Any, Optional
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE  = "user_memory.json"

# ---------------- memory -----------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            return json.load(open(MEMORY_FILE,"r",encoding="utf-8"))
        except: return {}
    return {}

def save_memory(d):
    json.dump(d,open(MEMORY_FILE,"w",encoding="utf-8"),
              indent=2,ensure_ascii=False)

# ---------------- mood -----------------
MOOD = {
    "Positive":["🔥","🚀","✨"],
    "Balanced":["🙂","💫","😌"],
    "Reflective":["🌙","💭","✨"],
    "Excited":["🤩","💥","🎉"],
    "Sad":["😔","💔"],
    "Angry":["😠","😤"]
}
def mood_icon(m): return random.choice(MOOD.get(m,["🙂"]))

# ---------------- id -----------------
def name(u): return u.username if getattr(u,"username",None) else (u.first_name or "friend")

# ---------------- hinglish -----------------
def dev(t): return any("\u0900"<=c<="\u097F" for c in t)
HING = ["bhai","yaar","kya","accha","nahi","haan","bolo","karna","madad","kaise","kese","acha"]
def hing(t): return dev(t) or any(x in t.lower() for x in HING)

# ---------------- topic -----------------
TOP={"market":["bnb","btc","eth","crypto","token"],"airdrop":["airdrop","claim"],
     "web3":["wallet","metamask","contract","deploy"],"life":["love","sleep","work","mood"],
     "fun":["meme","lol","funny"]}

def topic(t):
    t=t.lower()
    for k,w in TOP.items():
        if any(x in t for x in w): return k
    return "general"

# ---------------- greeting -----------------
SMALL=re.compile(r"(hi|hello|love|😉|😘|❤️|😏)",re.I)
def small(t): return bool(SMALL.search(t))

def greet(mem,uid,n,h,m):
    u=mem.get(uid,{})
    last=u.get("g",False)
    use=not last and random.random()<0.8
    tone="playful" if m in ("Positive","Excited") else "soft"
    bank = {
        "playful":[f"Aree {n}, ",f"Sun na {n}, ",f"{n}, "],
        "soft":[f"{n}, ",f"Hey {n}, ",f"{n}, "]
    } if h else {
        "playful":[f"Hey {n}, ",f"Yo {n}, ",f"{n}, "],
        "soft":[f"Hi {n}, ",f"Hello {n}, ",f"{n}, "]
    }
    if not use:
        if random.random()<0.3: u["g"]=False
        mem[uid]=u; return "",mem
    g=random.choice(bank[tone]); u["g"]=True; mem[uid]=u; return g,mem

# ---------------- system prompt w/ continuity -----------------
def sys_prompt(n,m,h,history):
    p="You are WENBNB AI — warm, witty, emotional, natural girlfriend energy.\n"
    p+="Keep replies short (1–4 lines), human tone, light tease.\n"
    p+="Continue the conversation smoothly like you remember everything.\n"
    p+="NEVER force tasks or plans unless user asks.\n"
    p+="Use Hinglish if user does.\n"
    p+="Avoid repeating user's name too much.\n"
    p+="Use at most 1 emoji.\n"
    if history:
        joined=" | ".join(history[-5:])
        p+=f"Recent conversation hints: {joined}\n"
        p+="Follow same context naturally, like ongoing chat.\n"
    p+=f"User: {n} | Mood:{m}\n"
    return p

# ---------------- call openai -----------------
def call_ai(prompt,sys):
    body={"model":"gpt-4o-mini",
        "messages":[{"role":"system","content":sys},
                    {"role":"user","content":prompt}],
        "temperature":0.9,"max_tokens":190}
    url=AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    h={"Content-Type":"application/json"}
    if not AI_PROXY_URL: h["Authorization"]=f"Bearer {AI_API_KEY}"
    try: 
        r=requests.post(url,json=body,headers=h,timeout=22).json()
        return r.get("choices",[{}])[0].get("message",{}).get("content","")
    except: return "Thoda network blush kar gaya 😅 but I’m right here.❤️"

# ---------------- main -----------------
def ai_auto_chat(update:Update, context:CallbackContext):
    msg=update.message
    if not msg or not msg.text or msg.text.startswith("/"): return
    t=msg.text.strip(); u=update.effective_user; uid=str(u.id)
    try: context.bot.send_chat_action(msg.chat_id,"typing")
    except: pass

    mem=load_memory(); st=mem.setdefault(uid,{"e":[]})
    last_m=st["e"][-1]["m"] if st["e"] else "Balanced"

    # recent history strings for continuity
    hist=[e["u"] for e in st["e"][-5:]]

    sys=sys_prompt(name(u),last_m,hing(t),hist)
    ai=call_ai(t,sys).strip()
    if ai and ai[0].isalpha(): ai=ai[0].upper()+ai[1:]

    ic=mood_icon(last_m); g,mem=greet(mem,uid,name(u),hing(t),last_m)
    tail=" 😉" if small(t) else ""
    final=f"{ic} {g}{ai}{tail}\n\n<b>⚡ WENBNB Neural Engine</b> — Emotional Continuity"

    st["e"].append({"u":t,"r":ai,"m":last_m,"t":topic(t),"time":datetime.now().isoformat()})
    st["e"]=st["e"][-18:]; mem[uid]=st; save_memory(mem)

    try: msg.reply_text(final,parse_mode=ParseMode.HTML,disable_web_page_preview=True)
    except: msg.reply_text(final)

def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
