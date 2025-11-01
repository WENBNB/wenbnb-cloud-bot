# ============================================================
# WENBNB • AI Auto-Reply v9.4.1
# Ultra Queen Mode — Polished
# Focus + Soft flirt + Direct Answers + Intent Discipline
# ============================================================

import os, json, random, requests, re
from datetime import datetime, timedelta
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE  = os.getenv("WENBNB_MEMORY_FILE", "user_memory.json")
TOPIC_LOCK_WINDOW_SEC = 420

# ==== Memory ====
def load_memory():
    try:
        if os.path.exists(MEMORY_FILE):
            return json.load(open(MEMORY_FILE,"r",encoding="utf-8"))
    except: pass
    return {}

def save_memory(m):
    try: json.dump(m,open(MEMORY_FILE,"w",encoding="utf-8"),indent=2,ensure_ascii=False)
    except: pass

# ==== Icons / Names ====
MOOD_ICON={
    "Positive":["🔥","🚀","✨"],
    "Balanced":["🙂","💫","😌"],
    "Reflective":["🌙","💭","✨"],
    "Excited":["🤩","💥","🎉"],
    "Sad":["😔","💔"],
    "Angry":["😠","😤"]
}
def mood_icon(m): return random.choice(MOOD_ICON.get(m,["🙂"]))
def cname(u): return u.username if getattr(u,"username",None) else (u.first_name or "friend")

# ==== Hinglish detect ====
HING=["bhai","yaar","kya","acha","accha","nahi","haan","bolo","karna","madad","kaise","earning","plan","guide"]
def hinglish(t): 
    return any("\u0900"<=c<="\u097F" for c in t) or any(w in t.lower() for w in HING)

# ==== Topics ====
TOP={
 "market":["bnb","btc","eth","crypto","token","chart","pump","market","price","trade"],
 "airdrop":["airdrop","claim","reward","points","quest","farm"],
 "web3":["wallet","metamask","contract","dex","stake","bot","deploy"],
 "life":["love","sleep","work","tired","busy","relationship","mood"],
 "fun":["meme","joke","lol","funny"]
}
def detect_topic(t):
    t=t.lower()
    for k,v in TOP.items():
        if any(x in t for x in v): return k
    return "general"

# ==== Task keywords ====
TASK=["kaise","steps","guide","plan","setup","earning","banao","karao","workflow"]
def wants_task(t): return any(k in t.lower() for k in TASK)

# ==== Topic lock ====
def topic_lock(mem,uid):
    st=mem.get(uid,{}).get("lock")
    if not st: return None
    try:
        if datetime.utcnow()-datetime.fromisoformat(st["t"]) <= timedelta(seconds=TOPIC_LOCK_WINDOW_SEC):
            return st["topic"]
    except: pass
    return None

def set_lock(mem,uid,tp):
    mem.setdefault(uid,{})
    mem[uid]["lock"]={"topic":tp,"t":datetime.utcnow().isoformat()}

def refresh(mem,uid):
    if "lock" in mem.get(uid,{}):
        mem[uid]["lock"]["t"]=datetime.utcnow().isoformat()

# ==== Intent Lock ====
def set_intent(mem,uid,intent):
    mem.setdefault(uid,{})
    mem[uid]["intent"]=intent
    mem[uid]["intent_time"]=datetime.utcnow().isoformat()

def get_intent(mem,uid):
    u=mem.get(uid,{})
    t=u.get("intent_time")
    if not t: return ""
    try:
        if datetime.utcnow()-datetime.fromisoformat(t)<timedelta(minutes=10):
            return u.get("intent","")
    except: pass
    return ""

def detect_intent(t):
    t=t.lower()
    if "bot" in t: return "telegram bot"
    if "travel" in t: return "travel"
    if "earning" in t: return "earning"
    if "website" in t: return "website"
    return ""

# ==== Direct Command Triggers ====
DIRECT = [
 "tum batao","best bolo","best batayo","tum decide",
 "recommend","kya kare","kya karu","suggest"
]
def direct_mode(t): return any(x in t.lower() for x in DIRECT)

# ==== System Prompt ====
def sys_prompt(name,mood,h,rec,lock,intent,task,focus):
    p="You are WENBNB girlfriend-coach AI. Loyal, warm, playful but FOCUSED.\n"
    p+="Rules:\n"
    p+="• Default: short + crisp (2-3 lines)\n"
    p+="• If user asks steps: give steps\n"
    p+="• If direct suggestion requested: ANSWER, don't ask\n"
    p+="• No too much greeting, no over-flirt\n"
    p+="• Never break topic focus\n"
    if h: p+="• Hinglish tone\n"
    if lock: p+=f"• TopicLock: stay on {lock}\n"
    if intent: p+=f"• Goal: {intent}\n"
    if task: p+="• User wants actionable steps\n"
    if focus: p+="• USER SAID 'tum batao': give direct answer\n"
    if rec: p+=f"Recent themes: {', '.join(rec)}\n"
    p+=f"User: {name}, Mood:{mood}."
    return p

# ==== Call LLM ====
def call_ai(prompt,S):
    body={
        "model":"gpt-4o-mini",
        "messages":[{"role":"system","content":S},{"role":"user","content":prompt}],
        "temperature":0.85,"max_tokens":200
    }
    url=AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    h={"Content-Type":"application/json"}
    if not AI_PROXY_URL: h["Authorization"]=f"Bearer {AI_API_KEY}"
    try: 
        r=requests.post(url,json=body,headers=h,timeout=22).json()
        return r.get("choices",[{}])[0].get("message",{}).get("content","")
    except:
        return "Thoda network drama hua baby, but I'm here 💛"

# ==== Greeting Filter ====
def greet(mem,uid,name,h,m):
    # Less greeting, no spam
    return "", mem

# ==== SMALLTALK emoji ====
SMALL=re.compile(r"(hi|hello|love|😉|😘|❤️|😏)",re.I)
def smalltalk(t): return bool(SMALL.search(t))

# ==== MAIN HANDLER ====
def ai_auto_chat(update:Update,context:CallbackContext):
    msg=update.message
    if not msg or not msg.text: return
    t=msg.text.strip()
    if t.startswith("/") or update.effective_user.is_bot: return

    chat=msg.chat_id; user=update.effective_user; uid=str(user.id)
    try: context.bot.send_chat_action(chat,"typing")
    except: pass

    name=cname(user); h=hinglish(t)
    mem=load_memory(); st=mem.setdefault(uid,{"e":[]})
    last_m=st["e"][-1]["m"] if st["e"] else "Balanced"

    cur=detect_topic(t)
    lock=topic_lock(mem,uid) or cur
    set_lock(mem,uid,lock); refresh(mem,uid)

    # Intent
    intent=get_intent(mem,uid)
    ni=detect_intent(t)
    if ni: set_intent(mem,uid,ni); intent=ni

    seen=[]
    for e in reversed(st["e"]):
        tp=e.get("t")
        if tp and tp not in seen: seen.append(tp)
        if len(seen)>=3: break
    rec=list(reversed(seen))

    focus = direct_mode(t)
    S=sys_prompt(name,last_m,h,rec,lock,intent,wants_task(t),focus)
    ai=call_ai(t,S)
    if ai and ai[0].isalpha(): ai=ai[0].upper()+ai[1:]

    g,mem = greet(mem,uid,name,h,last_m)
    tail=" 😉" if smalltalk(t) and lock in ("general","fun") else ""
    final=f"{mood_icon(last_m)} {g}{ai}{tail}\n\n<b>⚡ WENBNB Neural Engine</b> — Focus + Emotion 24×7"

    st["e"].append({"u":t,"r":ai,"m":last_m,"t":cur,"time":datetime.utcnow().isoformat()})
    st["e"]=st["e"][-18:]
    mem[uid]=st; save_memory(mem)

    try: msg.reply_text(final,parse_mode=ParseMode.HTML,disable_web_page_preview=True)
    except: msg.reply_text(final)

def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
