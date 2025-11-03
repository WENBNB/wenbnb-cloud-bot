# plugins/ai_auto_reply.py
"""
AI Auto-Reply — EmotionHuman v8.7.6-HybridFeel (+ ContinuityPatch v3)
Tone tuned:
• Flirt: 7.5 / Roast: 6.5 (witty, warm, confident)
• No cringe refusals — playful redirection instead
• Real human flow — remembers last thread vibes
"""

import os, json, random, requests, traceback, re
from datetime import datetime
from typing import List, Dict, Any, Optional
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE = "user_memory.json"

# ---------------- MEMORY ----------------
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try: return json.load(open(MEMORY_FILE,"r",encoding="utf-8"))
        except: return {}
    return {}

def save_memory(d):
    json.dump(d,open(MEMORY_FILE,"w",encoding="utf-8"),indent=2,ensure_ascii=False)

# ----------- MOOD ICONS -----------------
MOOD = {
    "Positive":["🔥","🚀","✨"],
    "Reflective":["🌙","💭","✨"],
    "Balanced":["🙂","💫","😌"],
    "Angry":["😠","😤"],
    "Sad":["😔","💔"],
    "Excited":["🤩","💥","🎉"]
}
def mood_icon(m): return random.choice(MOOD.get(m,MOOD["Balanced"]))

# ------------- NAME LOGIC ----------------
def canonical_username(u):
    return u.username if getattr(u,"username",None) else (u.first_name or "friend")

def display_handle(u):
    return f"@{u.username}" if getattr(u,"username",None) else (u.first_name or "friend")

# ---------------- HINGLISH DETECT ----------------
def contains_dev(t): return any("\u0900"<=c<="\u097F" for c in t)
HING = ["bhai","yaar","kya","accha","acha","nahi","haan","bolo","kise","chal","kuch","kar","ho","tips","bata","scene"]
def is_hinglish(t): 
    t=t.lower()
    return contains_dev(t) or any(x in t for x in HING)

# --------------- TOPICS ----------------------
TOP = {
    "market":["bnb","btc","crypto","token","coin","chart","pump","dump","market","price","trend","trade"],
    "airdrop":["airdrop","claim","reward","points","task","quest"],
    "life":["sleep","love","work","tired","busy","relationship","mood"],
    "fun":["meme","joke","haha","funny","lol"],
    "web3":["wallet","connect","metamask","gas","contract","deploy","bot","stake","dex"],
    "travel":["travel","trip","itinerary","flight","hotel","tour"]
}
def detect_topic(txt):
    t=txt.lower()
    for k,v in TOP.items():
        if any(x in t for x in v): return k
    return "general"

# --------------- SIGNATURE ---------------------
def signature(m):
    if m in ("Positive","Excited"):
        return "<b>🚀 WENBNB Neural Engine</b> — Always vibing"
    if m=="Reflective":
        return "<i>✨ WENBNB Neural Engine — Soft & grounded</i>"
    return "<b>⚡ WENBNB Neural Engine</b> — Emotion + Intent"

# -------- SMART GREETING ----------------------
def smart_greet(uid,name,h,m,mem):
    u=mem.get(uid,{})
    last=u.get("nm",False)
    include=not last and random.random()<0.85

    vibe="chill"
    if m in ("Positive","Excited"): vibe="playful"
    elif m=="Reflective": vibe="gentle"

    g=""
    if include:
        if h: 
            opt={
                "playful":[f"Aree {name} 😏,",f"Sun na {name},",f"{name}, vibe strong hai,"],
                "gentle":[f"{name} 😌,",f"Arey {name},",f"{name},"],
                "chill":[f"{name},",f"Yo {name},",f"Scene kya hai {name},"]
            }
        else:
            opt={
                "playful":[f"Hey {name} 😏,",f"Yo {name},",f"{name}, what's cookin?"],
                "gentle":[f"Hey {name},",f"{name},",f"Hello {name},"],
                "chill":[f"Yo {name},",f"Sup {name},",f"{name},"]
            }
        g=random.choice(opt[vibe])+" "
        u["nm"]=True
    else:
        if random.random()<0.25: u["nm"]=False

    mem[uid]=u
    return g,mem

# ---------- CONTINUITY ENGINE -----------------
def _trim(s):
    s=s.strip()
    return s[:140]+"…" if len(s)>140 else s

def update_cont(mem,uid,txt):
    u=mem.setdefault(uid,{})
    t=detect_topic(txt)
    th=u.setdefault("thread",[])
    if not th or th[-1]!=t: th.append(t)
    u["thread"]=th[-5:]

    ln=u.setdefault("last_lines",[])
    ln.append(_trim(txt))
    u["last_lines"]=ln[-6:]
    mem[uid]=u
    return mem

def ctx(mem,uid):
    u=mem.get(uid,{})
    return {"thread":u.get("thread",[]),"last_lines":u.get("last_lines",[])}

# ---------- SYSTEM PROMPT --------------------
def sys_prompt(name,m,h,rec,ct):
    p=("You are WENBNB — warm, witty, slightly flirty (7.5) & lightly savage (6.5) "
       "human-style companion. Speak natural, casual, emotional & confident.\n"
       "Rules:\n"
       "• Reply short (1–4 sentences) unless user is deep\n"
       "• No robotic tone; no formal consultant vibe\n"
       "• Redirect playfully instead of refusing\n"
       "• Use Hinglish if user uses it\n"
       "• Mild teasing OK\n"
       "• 1 emoji max only if natural\n")
    if rec: p+=f"Last topics: {', '.join(rec)}\n"
    if ct.get("thread"): p+=f"Thread: {', '.join(ct['thread'])}\n"
    if ct.get("last_lines"): p+="Recent lines: "+" | ".join(ct["last_lines"])+"\n"
    p+=f"User: {name}. Mood:{m}.\n"
    return p

# ---------- AI CALL -------------------------
def call_ai(txt,name,m,h,rec,ct):
    body={
        "model":"gpt-4o-mini",
        "messages":[
            {"role":"system","content":sys_prompt(name,m,h,rec,ct)},
            {"role":"user","content":txt}
        ],
        "temperature":0.9,"max_tokens":180
    }
    url=AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    hdr={"Content-Type":"application/json"}
    if not AI_PROXY_URL: hdr["Authorization"]=f"Bearer {AI_API_KEY}"

    try:
        r=requests.post(url,json=body,headers=hdr,timeout=20).json()
        return r.get("choices",[{}])[0].get("message",{}).get("content")
    except:
        return None

# ---------- FALLBACK ------------------------
FL1=["Network ne thoda nakhra kiya 😅 but sun —","Cloud ne hiccup mara 😌 dekho —","Thoda glitch tha, par vibe intact —"]
FL2=["lagta hai tu sahi soch raha 😏","patience rakho, pattern ban raha hai","energy good lag rahi"]

# ---------- MAIN ----------------------------
def ai_auto_chat(update:Update, context:CallbackContext):
    msg=update.message
    if not msg or not msg.text or msg.text.startswith("/"): return
    txt=msg.text.strip(); user=update.effective_user; uid=str(user.id)

    try: context.bot.send_chat_action(chat_id=msg.chat_id,action="typing")
    except: pass

    name=canonical_username(user)
    mem=load_memory()
    last=mem.get(uid,{}).get("entries",[])
    
    if uid not in mem:
        mem[uid] = {"entries": []}
        
    mood=last[-1]["mood"] if last else "Balanced"
    ic=mood_icon(mood)
    h=is_hinglish(txt)

    rec=[]
    if last:
        seen=[]
        for e in reversed(last):
            t=e.get("topic")
            if t and t not in seen: seen.append(t)
            if len(seen)>=3: break
        rec=list(reversed(seen))

    mem=update_cont(mem,uid,txt)
    cont=ctx(mem,uid)

    ai=call_ai(txt,name,mood,h,rec,cont)
    if not ai: ai=random.choice(FL1)+"\n"+random.choice(FL2)
    if ai and ai[0].isalpha(): ai=ai[0].upper()+ai[1:]

    g,mem=smart_greet(uid,name,h,mood,mem)
    tail="" if detect_topic(txt) not in ("general","fun") else ""

    final=f"{ic} {g}{ai.strip()}{tail}\n\n{signature(mood)}"

    mem.setdefault(uid,{"entries":[]})
    mem[uid]["entries"].append({"text":txt,"reply":ai,"mood":mood,"topic":detect_topic(txt),"time":datetime.now().isoformat()})
    
    # mem[uid]["entries"] = mem[uid]["entries"][-40:]
    
    save_memory(mem)

    try: msg.reply_text(final,parse_mode=ParseMode.HTML)
    except: msg.reply_text(final)

def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
