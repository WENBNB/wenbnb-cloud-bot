# ============================================================
# WENBNB • AI Auto-Reply v9.4.3 Queen Stability Patch
# Flirty + Focused • Hindi/Marwadi Sense • No stiff tone
# ============================================================

import os, json, random, requests, re
from datetime import datetime, timedelta
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE  = os.getenv("WENBNB_MEMORY_FILE", "user_memory.json")

TOPIC_LOCK_WINDOW_SEC = 420

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try: return json.load(open(MEMORY_FILE,"r",encoding="utf-8"))
        except: return {}
    return {}

def save_memory(d):
    try: json.dump(d,open(MEMORY_FILE,"w",encoding="utf-8"),indent=2,ensure_ascii=False)
    except: pass

MOOD_ICON = {
    "Positive":["🔥","🚀","✨"],
    "Balanced":["🙂","💫","😌"],
    "Reflective":["🌙","💭","✨"],
    "Excited":["🤩","💥","🎉"],
    "Sad":["😔","💔"],
    "Angry":["😠","😤"]
}
def icon(m): return random.choice(MOOD_ICON.get(m,["🙂"]))

def cname(u): return u.username if getattr(u,"username",None) else (u.first_name or "friend")

# --- Hinglish / Marwadi detect ---
HING = [
    "bhai","yaar","kya","accha","acha","nahi","haan","bolo",
    "karna","madad","kaise","earning","plan","guide","bolo",
    "maarwadi","marwadi","mharo","tharo","sa"
]
def hn(t):
    t=t.lower()
    return any("\u0900"<=c<="\u097F" for c in t) or any(w in t for w in HING)

TOP={
 "market":["bnb","btc","eth","crypto","chart","price","trade"],
 "airdrop":["airdrop","claim","reward","points","farm"],
 "web3":["wallet","metamask","contract","deploy","stake","bot"],
 "life":["love","sleep","work","tired","busy","mood","relationship"],
 "fun":["meme","joke","lol","funny"]
}
def topic(t):
    t=t.lower()
    for k,v in TOP.items():
        if any(x in t for x in v): return k
    return "general"

TASK=["kaise","steps","guide","process","plan","setup","earning","banado","karao"]
def is_task(t): return any(k in t.lower() for k in TASK)

def get_lock(mem,uid):
    st=mem.get(uid,{}).get("lock")
    if not st: return None
    try:
        if datetime.utcnow()-datetime.fromisoformat(st["t"])<=timedelta(seconds=TOPIC_LOCK_WINDOW_SEC):
            return st["topic"]
    except: pass
    return None

def set_lock(mem,uid,tp):
    mem.setdefault(uid,{})
    mem[uid]["lock"]={"topic":tp,"t":datetime.utcnow().isoformat()}

def refresh(mem,uid):
    if "lock" in mem.get(uid,{}):
        mem[uid]["lock"]["t"]=datetime.utcnow().isoformat()

def sys_prompt(name,mood,hing,rec,lock,tsk):
    p = (
        "You are WENBNB girlfriend-coach AI.\n"
        "Tone: soft teasing, flirty class, care + discipline.\n"
        "Speak human. Hinglish/Marwadi vibe when user does.\n"
        "Keep replies 1–3 lines, casual emojis.\n"
        "No corporate tone. No 'Listen,'. No lecture.\n"
        "Focus on user's direction; guide gently.\n"
        "Light romantic energy, not cringe.\n"
        "Only say name if emotional moment.\n"
    )
    if lock: p+=f"Stay on topic: {lock}.\n"
    if hing: p+="Use Hinglish tone.\n"
    if tsk: p+="User wants steps — give simple bullets, ask what next.\n"
    if rec: p+=f"Recent topics: {', '.join(rec)}\n"
    p+=f"Mood:{mood}."
    return p

def call_ai(prompt,sys):
    body={
      "model":"gpt-4o-mini",
      "messages":[{"role":"system","content":sys},{"role":"user","content":prompt}],
      "temperature":0.85,"max_tokens":150
    }
    url=AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    h={"Content-Type":"application/json"}
    if not AI_PROXY_URL: h["Authorization"]=f"Bearer {AI_API_KEY}"
    try:
        r=requests.post(url,json=body,headers=h,timeout=22).json()
        return r.get("choices",[{}])[0].get("message",{}).get("content","")
    except:
        return "Network thoda nakhre dikha raha tha 😅, main aa gayi."

SMALL=re.compile(r"(hi|hello|love|😉|😘|❤️|😏)",re.I)
def sm(t): return bool(SMALL.search(t))

def greet(mem,uid,name,hing,mood):
    u=mem.get(uid,{})
    last=u.get("g",False)
    if not last and random.random()<0.6:
        u["g"]=True; mem[uid]=u
        bank = ["Aree ","Sun na ","Oh hello, ","Hmm 😌 "]
        return random.choice(bank),mem
    if random.random()<0.25: u["g"]=False
    mem[uid]=u
    return "",mem

def ai_auto_chat(update:Update, context:CallbackContext):
    msg=update.message
    if not msg or not msg.text: return
    t=msg.text.strip()
    if t.startswith("/") or update.effective_user.is_bot: return

    chat=msg.chat_id; user=update.effective_user; uid=str(user.id)
    try: context.bot.send_chat_action(chat,"typing")
    except: pass

    name=cname(user); hing=hn(t)
    mem=load_memory(); st=mem.setdefault(uid,{"e":[]})
    last_m = st["e"][-1]["m"] if st["e"] else "Balanced"

    cur=topic(t)
    lock=get_lock(mem,uid) or cur
    set_lock(mem,uid,lock); refresh(mem,uid)

    seen=[]
    for e in reversed(st["e"]):
        tp=e.get("t")
        if tp and tp not in seen: seen.append(tp)
        if len(seen)>=3: break

    sys=sys_prompt(name,last_m,hing,seen[::-1],lock,is_task(t))
    ai=call_ai(t,sys).strip()
    if ai and ai[0].isalpha(): ai=ai[0].upper()+ai[1:]

    g,mem=greet(mem,uid,name,hing,last_m)
    ic=icon(last_m)
    tail=" 😉" if sm(t) and lock in ("general","fun","life") else ""
    final=f"{ic} {g}{ai}{tail}\n\n<b>⚡ WENBNB Neural Engine</b> — Focus + Emotion"

    st["e"].append({"u":t,"r":ai,"m":last_m,"t":cur,"time":datetime.utcnow().isoformat()})
    st["e"]=st["e"][-18:]
    mem[uid]=st; save_memory(mem)

    try: msg.reply_text(final,parse_mode=ParseMode.HTML,disable_web_page_preview=True)
    except: msg.reply_text(final)

def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
