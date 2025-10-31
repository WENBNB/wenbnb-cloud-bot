# ============================================================
# WENBNB • AI Auto-Reply v9.2 "Balanced Queen Mode"
# Human girlfriend energy + CEO discipline + TopicLock++
# ============================================================

import os, json, random, requests, traceback, re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE  = os.getenv("WENBNB_MEMORY_FILE", "user_memory.json")

TOPIC_LOCK_WINDOW_SEC = 420  # 7 mins

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try: return json.load(open(MEMORY_FILE,"r",encoding="utf-8"))
        except: return {}
    return {}

def save_memory(data):
    try: json.dump(data,open(MEMORY_FILE,"w",encoding="utf-8"),indent=2,ensure_ascii=False)
    except: pass

MOOD_ICON = {
    "Positive":["🔥","🚀","✨"],
    "Reflective":["🌙","💭","✨"],
    "Balanced":["🙂","💫","😌"],
    "Angry":["😠","😤"], "Sad":["😔","💔"], "Excited":["🤩","💥","🎉"]
}

def mood_icon(m): return random.choice(MOOD_ICON.get(m,["🙂"]))

def canonical_name(u): return u.username if getattr(u,"username",None) else (u.first_name or "friend")

def devanagari(t): return any("\u0900"<=c<="\u097F" for c in t)
def hinglish(t): 
    w=["bhai","yaar","kya","accha","nahi","haan","bolo","karna","madad","chalo"]
    return devanagari(t) or any(x in t.lower() for x in w)

TOPICS = {
    "market":["bnb","btc","eth","crypto","token","chart","pump","market","price"],
    "airdrop":["airdrop","claim","reward","points","quest"],
    "web3":["wallet","metamask","contract","web3","dex","stake"],
    "life":["sleep","love","work","tired","busy","mood"],
    "fun":["meme","joke","lol","funny"],
}

def detect_topic(t):
    t=t.lower()
    for k,v in TOPICS.items():
        if any(x in t for x in v): return k
    return "general"

def build_sig(m):
    if m in ("Positive","Excited"): return "<b>🚀 WENBNB Neural Engine</b> — Vibes + Hustle"
    if m=="Reflective": return "<i>✨ WENBNB Neural Engine — Calm & Sharp</i>"
    return "<b>⚡ WENBNB Neural Engine</b> — Emotional Intelligence 24×7"

SMALL = re.compile(r"(hi|hello|hey|love|😘|❤️|😉|🥰|😏)",re.I)
def smalltalk(t): return bool(SMALL.search(t))

def topic_lock(mem,uid):
    st=mem.get(uid,{}).get("lock")
    if not st: return None
    try: last=datetime.fromisoformat(st["t"])
    except: return None
    if datetime.utcnow()-last<=timedelta(seconds=TOPIC_LOCK_WINDOW_SEC):
        return st["topic"]
    return None

def set_lock(mem,uid,topic):
    mem.setdefault(uid,{})
    mem[uid]["lock"]={"topic":topic,"t":datetime.utcnow().isoformat()}

def refresh(mem,uid):
    if "lock" in mem.get(uid,{}):
        mem[uid]["lock"]["t"]=datetime.utcnow().isoformat()

def sys_prompt(name, mood, h, rec, lock):
    p="You are WENBNB AI — warm, teasing, focused, girlfriend energy + mentor. "
    p+="Keep answers short (2–4 lines), human tone, Hinglish if natural. "
    p+="Flirt light, but focus strong — user goal is priority. "
    p+="Never forget ongoing topic; don't switch unless user clearly does. "
    if h: p+="Use Hinglish naturally. "
    if rec: p+=f"Recent: {', '.join(rec)}. "
    if lock: p+=f"TopicLock: Stay on '{lock}'. "
    p+=f"User name = {name}. Mood = {mood}."
    return p

def call_ai(prompt, name, mood, h, rec, lock):
    body={
        "model":"gpt-4o-mini",
        "messages":[
            {"role":"system","content":sys_prompt(name,mood,h,rec,lock)},
            {"role":"user","content":prompt}
        ],
        "temperature":0.9,"max_tokens":180
    }
    url=AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers={"Content-Type":"application/json"}
    if not AI_PROXY_URL: headers["Authorization"]=f"Bearer {AI_API_KEY}"
    try:
        r=requests.post(url,json=body,headers=headers,timeout=22).json()
        c=r.get("choices",[{}])[0]
        return c.get("message",{}).get("content") or c.get("text")
    except: return None

FALL1=["Network thoda blush kar gaya 😅 — suno:","Thoda glitch aaya par vibe clear hai:"]
FALL2=["Focus rakho, result aayega.","Iss flow me perfect jaa rahe ho."]

def greet(uid,name,h,m,mem):
    u=mem.get(uid,{})
    last=u.get("g",False)
    use=not last and random.random()<0.8
    tone="chill"
    if m in ("Positive","Excited"): tone="playful"
    elif m=="Reflective": tone="soft"

    bank={
        "playful":[f"Aree {name} 😎, ",f"Sun na {name}, ",f"{name} boss, "],
        "soft":[f"{name}, ",f"Hey {name}, ",f"Arey {name}, "],
        "chill":[f"{name}, ",f"Yo {name}, ",f"Okay {name}, "],
    } if h else {
        "playful":[f"Hey {name} 😏, ",f"Yo {name}, ",f"{name}, you there? "],
        "soft":[f"Hi {name}, ",f"Hello {name}, ",f"{name}, "],
        "chill":[f"Yo {name}, ",f"Sup {name}, ",f"{name}, "],
    }
    if use:
        g=random.choice(bank[tone])
        u["g"]=True
    else:
        if random.random()<0.3: u["g"]=False
        g=""
    mem[uid]=u
    return g,mem

def ai_auto_chat(update:Update, context:CallbackContext):
    msg=update.message
    if not msg or not msg.text: return
    text=msg.text.strip()
    if text.startswith("/") or update.effective_user.is_bot: return

    chat=msg.chat_id
    user=update.effective_user
    uid=str(user.id)
    try: context.bot.send_chat_action(chat, "typing")
    except: pass

    name=canonical_name(user)
    h=hinglish(text)
    mem=load_memory()
    st=mem.setdefault(uid,{"e":[]})

    last_m = st["e"][-1]["m"] if st["e"] else "Balanced"

    cur_topic=detect_topic(text)
    lock=topic_lock(mem,uid) or cur_topic
    set_lock(mem,uid,lock); refresh(mem,uid)

    seen=[]
    for e in reversed(st["e"]):
        t=e.get("t"); 
        if t and t not in seen: seen.append(t)
        if len(seen)>=3: break
    rec=list(reversed(seen))

    ai=call_ai(text,name,last_m,h,rec,lock) or random.choice(FALL1)+" "+random.choice(FALL2)
    ai=ai.replace("{name}",name).strip()
    if ai and ai[0].isalpha(): ai = ai[0].upper() + ai[1:]

    tail = " 😉" if smalltalk(text) and lock in ("general","fun") else ""
    icon=mood_icon(last_m)
    g,mem=greet(uid,name,h,last_m,mem)
    final=f"{icon} {g}{ai}{tail}\n\n{build_sig(last_m)}"

    try:
        st["e"].append({"u":text,"r":ai,"m":last_m,"t":cur_topic,"time":datetime.utcnow().isoformat()})
        st["e"]=st["e"][-18:]
        mem[uid]=st; save_memory(mem)
    except: pass

    try: msg.reply_text(final,parse_mode=ParseMode.HTML,disable_web_page_preview=True)
    except: msg.reply_text(final)

def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
