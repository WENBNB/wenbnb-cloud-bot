# ============================================================
# WENBNB • AI Auto-Reply v9.4.2 Micro-Polish
# Smooth Queen • No name spam • Short replies • TaskLock++
# ============================================================

import os, json, random, requests, re
from datetime import datetime, timedelta
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE  = os.getenv("WENBNB_MEMORY_FILE", "user_memory.json")

TOPIC_LOCK_WINDOW_SEC = 420

# --- memory helpers ---
def load_memory():
    if os.path.exists(MEMORY_FILE):
        try: return json.load(open(MEMORY_FILE,"r",encoding="utf-8"))
        except: return {}
    return {}

def save_memory(d):
    try: json.dump(d,open(MEMORY_FILE,"w",encoding="utf-8"),indent=2,ensure_ascii=False)
    except: pass

# --- icons / mood ---
MOOD_ICON = {
    "Positive":["🔥","🚀","✨"],
    "Balanced":["🙂","💫","😌"],
    "Reflective":["🌙","💭","✨"],
    "Excited":["🤩","💥","🎉"],
    "Sad":["😔","💔"],
    "Angry":["😠","😤"]
}
def icon(m): return random.choice(MOOD_ICON.get(m,["🙂"]))

# --- name lock ---
def cname(u): return u.username if getattr(u,"username",None) else (u.first_name or "friend")

# --- Hinglish ---
HING=["bhai","yaar","kya","accha","acha","nahi","haan","bolo","karna","madad","kaise","earning","plan","guide"]
def hn(t): 
    return any("\u0900"<=c<="\u097F" for c in t) or any(w in t.lower() for w in HING)

# --- topics ---
TOP={"market":["bnb","btc","eth","crypto","chart","price","trade"],
     "airdrop":["airdrop","claim","reward","points","farm"],
     "web3":["wallet","metamask","contract","deploy","stake","bot"],
     "life":["love","sleep","work","tired","busy","mood"],
     "fun":["meme","joke","lol","funny"]}

def topic(t):
    t=t.lower()
    for k,v in TOP.items():
        if any(x in t for x in v): return k
    return "general"

# --- task intent ---
TASK=["kaise","steps","guide","process","plan","setup","earning","banado","karao"]
def task(t): return any(k in t.lower() for k in TASK)

# --- locks ---
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

# --- system prompt ---
def sys_prompt(name,mood,hing,rec,lock,tsk):
    p="You are WENBNB AI — girlfriend vibe + CEO discipline.\n"
    p+="Short replies only (2–3 lines max). Direct. Human.\n"
    p+="Stay on topic. Focus on user goal. Light flirt is okay.\n"
    p+="Don't repeat user's name too much. No cringe.\n"
    if hing: p+="Use natural Hinglish.\n"
    if lock: p+=f"Current topic: {lock}. Don't drift.\n"
    if tsk: p+="User wants steps — give crisp guidance.\n"
    if rec: p+=f"Recent themes: {', '.join(rec)}\n"
    p+=f"User: {name}. Mood:{mood}."
    return p

# --- call AI ---
def call_ai(prompt,sys):
    body={"model":"gpt-4o-mini",
          "messages":[{"role":"system","content":sys},
                      {"role":"user","content":prompt}],
          "temperature":0.85,"max_tokens":160}
    url=AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    h={"Content-Type":"application/json"}
    if not AI_PROXY_URL: h["Authorization"]=f"Bearer {AI_API_KEY}"
    try:
        r=requests.post(url,json=body,headers=h,timeout=22).json()
        return r.get("choices",[{}])[0].get("message",{}).get("content","")
    except:
        return "Thoda network drama tha 😅 but I'm right here."

# --- smalltalk ---
SMALL = re.compile(r"(hi|hello|love|😉|😘|❤️|😏)",re.I)
def sm(t): return bool(SMALL.search(t))

# --- greeting ---
def greet(mem,uid,name,hing,mood):
    u=mem.get(uid,{})
    last=u.get("g",False)
    use=not last and random.random()<0.75
    tone="playful" if mood in ("Positive","Excited") else "soft"
    bank = {
        "playful":[f"Arey {name}, ",f"Sun na {name}, ",f"{name}, "],
        "soft":[f"{name}, ",f"Hey, ",f"Listen, "]
    }
    if not use:
        if random.random()<0.3: u["g"]=False
        mem[uid]=u; return "",mem
    u["g"]=True; mem[uid]=u
    return random.choice(bank[tone])+" ",mem

# --- handler ---
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

    cur = topic(t)
    lock = get_lock(mem,uid) or cur
    set_lock(mem,uid,lock); refresh(mem,uid)

    seen=[]
    for e in reversed(st["e"]):
        tp=e.get("t")
        if tp and tp not in seen: seen.append(tp)
        if len(seen)>=3: break

    sys=sys_prompt(name,last_m,hing,seen[::-1],lock,task(t))
    ai=call_ai(t,sys).strip()
    if ai and ai[0].isalpha(): ai=ai[0].upper()+ai[1:]

    ic=icon(last_m); g,mem=greet(mem,uid,name,hing,last_m)
    tail=" 😉" if sm(t) and lock in ("general","fun") else ""
    final=f"{ic} {g}{ai}{tail}\n\n<b>⚡ WENBNB Neural Engine</b> — Focus + Emotion"

    st["e"].append({"u":t,"r":ai,"m":last_m,"t":cur,"time":datetime.utcnow().isoformat()})
    st["e"]=st["e"][-18:]
    mem[uid]=st; save_memory(mem)

    try: msg.reply_text(final,parse_mode=ParseMode.HTML,disable_web_page_preview=True)
    except: msg.reply_text(final)

def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
