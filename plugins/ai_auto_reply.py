# plugins/ai_auto_reply.py
"""
Queen Neural Reply — v9.1
Soft-dominant, flirty, emotional girlfriend AI
Keeps Hinglish + memory + slash-ignore + vibe
"""

import os, json, random, requests, traceback
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE = "user_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            return json.load(open(MEMORY_FILE, "r", encoding="utf-8"))
        except:
            return {}
    return {}

def save_memory(d):
    json.dump(d, open(MEMORY_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

MOOD_ICON = {
    "Positive":["✨","🔥","🚀"], "Reflective":["✨","🌙","💭"], "Balanced":["😌","🙂","💫"],
    "Angry":["😠","😤"], "Sad":["😔","💔"], "Excited":["🤩","🎉","💥"]
}
pick_icon=lambda m:random.choice(MOOD_ICON.get(m,["🙂"]))

def canonical_username(u): return u.username if getattr(u,"username",None) else u.first_name or "friend"
def wants_hinglish(t):
    t=t.lower()
    keys=["bhai","yaar","kya","accha","nahi","haan","bolo","chal","kuch"]
    return any(k in t for k in keys) or any("\u0900" <= ch <= "\u097F" for ch in t)

def detect_topic(t):
    t=t.lower()
    cats={
        "market":["crypto","bnb","btc","chart","pump","token"],
        "airdrop":["airdrop","reward","points"],
        "life":["sleep","tired","work"],
        "fun":["lol","meme","joke"],
        "web3":["wallet","metamask","gas","contract"]
    }
    for k,v in cats.items():
        if any(x in t for x in v): return k
    return "general"

# QUEEN MODE SYSTEM PROMPT
def build_prompt(name, hinglish, mem_ctx):
    p=(
        "You are WENBNB AI — Queen Neural Sync v9.1. "
        "Confident, teasing, soft-dominant, flirty, premium best-friend energy. "
        "Short replies (1-4 lines). Warm, emotional, bold. "
        "Never robotic. No cringe TikTok tone. "
        "If user rude → classy savage reply. "
        "One subtle emoji max. "
    )
    if hinglish: p+="Hinglish natural tone. "
    if mem_ctx: p+=f"Recent topics: {', '.join(mem_ctx)}. "
    p+=f"User: {name}."
    return p

def call_ai(prompt, name, mood, hinglish, ctx):
    body={
        "model":"gpt-4o-mini",
        "messages":[
            {"role":"system","content":build_prompt(name,hinglish,ctx)},
            {"role":"user","content":prompt}
        ],
        "temperature":0.9,"max_tokens":150
    }
    url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers={"Content-Type":"application/json"}
    if not AI_PROXY_URL: headers["Authorization"]=f"Bearer {AI_API_KEY}"

    try:
        r=requests.post(url,json=body,headers=headers,timeout=20).json()
        c=r.get("choices",[{}])[0]
        out=c.get("message",{}).get("content") or c.get("text")
        return out.strip() if out else None
    except:
        return None

# 👑 Queen greetings
def greet(uid,name,hinglish,mood,mem):
    d=mem.get(uid,{})
    last=d.get("last_name_used",False)
    include=not last and random.random()<0.85

    if include:
        if hinglish:
            opts={
                "playful":[f"Aree {name} 😌,",
                           f"Sun na {name},",
                           f"{name}, guess what 😏"],
                "gentle":[f"{name},",
                          f"Mmh {name},",
                          f"Aaja {name},"],
                "chill":[f"{name},",
                         f"Yo {name},",
                         f"Bas aa gaya tu 😏,"]
            }
        else:
            opts={
                "playful":[f"Hey {name} 😏,",
                           f"Look who showed up, {name},",
                           f"{name}, don't act busy 😉"],
                "gentle":[f"Hi {name},",
                          f"{name},",
                          f"Come here {name},"],
                "chill":[f"Yo {name},",
                         f"{name},",
                         f"There you are 😌,"]
            }
        vibe="playful" if mood in("Positive","Excited") else ("gentle" if mood=="Reflective" else "chill")
        g=random.choice(opts[vibe])+" "
        d["last_name_used"]=True
    else:
        g=""
        if random.random()<0.25: d["last_name_used"]=False

    mem[uid]=d
    return g,mem

# ------------------- MAIN HANDLER -------------------
def ai_auto_chat(update:Update, context:CallbackContext):
    msg=update.message
    if not msg or not msg.text: return
    text=msg.text.strip()

    if text.startswith("/"): return  # ignore slash

    chat=msg.chat_id
    user=update.effective_user
    uid=str(user.id)

    try: context.bot.send_chat_action(chat_id=chat, action="typing")
    except: pass

    name = canonical_username(user)
    hing = wants_hinglish(text)
    mem = load_memory()

    last = mem.get(uid,{}).get("entries",[{"mood":"Balanced"}])[-1]["mood"]
    icon = pick_icon(last)

    # context topics
    ctx=[]
    if uid in mem:
        ts=[e.get("topic") for e in mem[uid].get("entries",[])]
        seen=[]
        for t in reversed(ts):
            if t and t not in seen: seen.append(t)
        ctx=list(reversed(seen))[:3]

    ai = call_ai(text,name,last,hing,ctx)
    if not ai:
        ai="Network drama tha for a sec… but I'm here 😌"

    g,mem = greet(uid,name,hing,last,mem)

    final = f"{icon} {g}{ai.strip().capitalize()}\n\n<b>⚡ WENBNB Neural Engine — Queen Mode</b>"

    # memory
    try:
        mem.setdefault(uid,{"entries":[]})
        mem[uid]["entries"].append({
            "text":text,"reply":ai,"mood":last,
            "topic":detect_topic(text),
            "time":datetime.now().isoformat()
        })
        mem[uid]["entries"]=mem[uid]["entries"][-15:]
        save_memory(mem)
    except: pass

    try: msg.reply_text(final,parse_mode=ParseMode.HTML)
    except: msg.reply_text(final)

def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
