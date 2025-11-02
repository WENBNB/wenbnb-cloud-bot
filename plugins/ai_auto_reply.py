# ============================================================
# WENBNB • AI Auto-Reply v9.4.1 "Balanced Queen Patch"
# (Ultra Queen + Less Name Repeats + Smart Short Replies)
# ============================================================

import os, json, random, requests, re
from datetime import datetime, timedelta
from typing import Dict, Any, List
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE  = os.getenv("WENBNB_MEMORY_FILE", "user_memory.json")

TOPIC_LOCK_WINDOW_SEC = 420

# === Load / Save Memory ===
def load_memory(): 
    if os.path.exists(MEMORY_FILE):
        try: return json.load(open(MEMORY_FILE,"r",encoding="utf-8"))
        except: return {}
    return {}

def save_memory(data):
    try: json.dump(data,open(MEMORY_FILE,"w",encoding="utf-8"),indent=2,ensure_ascii=False)
    except: pass

# === Mood icons ===
MOOD_ICON = {
    "Positive":["🔥","🚀","✨"],
    "Balanced":["🙂","💫","😌"],
    "Reflective":["🌙","💭","✨"],
    "Excited":["🤩","💥","🎉"],
    "Sad":["😔","💔"],
    "Angry":["😠","😤"]
}

def mood_icon(m): return random.choice(MOOD_ICON.get(m,["🙂"]))

def canonical_name(u): return u.username if getattr(u,"username",None) else (u.first_name or "friend")

# Hinglish detector
def devanagari(t): return any("\u0900"<=c<="\u097F" for c in t)
HING = ["bhai","yaar","kya","accha","nahi","haan","bolo","karna","madad","chalo","kaise","kese","tips","earning"]
def hinglish(t): return devanagari(t) or any(x in t.lower() for x in HING)

# Topic clusters
TOPICS = {
    "market":["bnb","btc","eth","crypto","token","chart","pump","market","price","trade"],
    "airdrop":["airdrop","claim","reward","points","quest","farm"],
    "web3":["wallet","metamask","contract","web3","dex","stake","bot","deploy"],
    "life":["love","sleep","work","tired","busy","mood","relationship"],
    "fun":["meme","joke","lol","funny"],
}

def detect_topic(t):
    t=t.lower()
    for k,v in TOPICS.items():
        if any(x in t for x in v): return k
    return "general"

# --- Task Mode keywords ---
TASK_KEYWORDS = ["kaise","kese","steps","plan","help","madad","guide","process","workflow","banao","setup","banani","earning","kro","karao"]
def wants_task(text):
    t=text.lower()
    return any(k in t for k in TASK_KEYWORDS)

# === Topic Lock ===
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

# === Intent Lock ===
def set_intent(mem,uid,intent):
    mem.setdefault(uid,{})
    mem[uid]["intent"]=intent
    mem[uid]["intent_time"]=datetime.utcnow().isoformat()

def get_intent(mem,uid):
    u=mem.get(uid,{}); t=u.get("intent_time")
    if not t: return ""
    try:
        if datetime.utcnow()-datetime.fromisoformat(t)<timedelta(minutes=10):
            return u.get("intent","")
    except: pass
    return ""

def detect_intent(text):
    txt=text.lower()
    if "website" in txt: return "website earning"
    if "bot" in txt: return "telegram bot"
    if "travel" in txt: return "travel plan"
    if "crypto" in txt and "learn" in txt: return "crypto learning"
    if "earning" in txt: return "earning"
    return ""

# === Prompt Builder ===
def sys_prompt(name, mood, h, rec, lock, intent, task):
    p="You are WENBNB girlfriend-coach AI. Warm, playful, loyal but balanced.\n"
    p+="Short replies unless user asks deep.\n"
    p+="Don't repeat user's name too much.\n"
    p+="Focus + soft flirt. No over push.\n"
    if lock: p+=f"TopicLock: stay on {lock}\n"
    if intent: p+=f"User goal = {intent}. Support without nagging.\n"
    if task: p+="User wants steps — crisp actions then ask next input.\n"
    if h: p+="Use Hinglish.\n"
    if rec: p+=f"Recent thoughts: {', '.join(rec)}\n"
    p+=f"Mood = {mood}.\n"
    return p

# === Call AI ===
def call_ai(prompt, SYS):
    body={
        "model":"gpt-4o-mini",
        "messages":[{"role":"system","content":SYS},{"role":"user","content":prompt}],
        "temperature":0.9,"max_tokens":200
    }
    url=AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers={"Content-Type":"application/json"}
    if not AI_PROXY_URL: headers["Authorization"]=f"Bearer {AI_API_KEY}"
    try:
        r=requests.post(url,json=body,headers=headers,timeout=22).json()
        return r.get("choices",[{}])[0].get("message",{}).get("content","")
    except:
        return "Network thoda blush kar gaya 😅 but hum yahin hai ❤️"

# === Smalltalk flair ===
SMALL = re.compile(r"(hi|hello|hey|love|😘|❤️|😉|🥰|😏)",re.I)
def smalltalk(t): return bool(SMALL.search(t))

# === Greeting logic (softer + name cap) ===
def greet(mem,uid,name,h,m):
    u=mem.get(uid,{})
    count=u.get("name_used",0)
    last=u.get("g",False)

    # inject name rarely
    allow_name = count < 1 and random.random()<0.7

    tone="playful" if m in ("Positive","Excited") else "soft"
    if h:
        bank={
            "playful":[f"Aree {name}, ","Sun na, ","Oye "],
            "soft":[f"Hey, ","Arey suno, ","Hmm "]
        }
    else:
        bank={
            "playful":[f"Hey, ","Yo ","You there? "],
            "soft":[f"Hi, ","Hello, ","Suno, "]
        }

    if not last and random.random()<0.65:
        g=random.choice(bank[tone])
        u["g"]=True
        if allow_name: u["name_used"]=count+1
        mem[uid]=u
        return g,mem

    if random.random()<0.25: u["g"]=False
    mem[uid]=u
    return "",mem

# === MAIN Handler ===
def ai_auto_chat(update:Update, context:CallbackContext):
    msg=update.message
    if not msg or not msg.text: return
    text=msg.text.strip()
    if text.startswith("/") or update.effective_user.is_bot: return

    chat=msg.chat_id
    user=update.effective_user
    uid=str(user.id)
    try: context.bot.send_chat_action(chat,"typing")
    except: pass

    name=canonical_name(user)
    h = hinglish(text)
    mem = load_memory()
    st  = mem.setdefault(uid,{"e":[],"name_used":0})
    last_m = st["e"][-1]["m"] if st["e"] else "Balanced"

    # short-user input -> short bot output mode
    short_trigger = len(text.split()) <= 3

    cur_topic = detect_topic(text)
    lock = topic_lock(mem,uid) or cur_topic
    set_lock(mem,uid,lock); refresh(mem,uid)

    intent = get_intent(mem,uid)
    new_intent = detect_intent(text)
    if new_intent: 
        intent = new_intent
        set_intent(mem,uid,intent)

    task = wants_task(text)

    seen=[]
    for e in reversed(st["e"]):
        t=e.get("t")
        if t and t not in seen: seen.append(t)
        if len(seen)>=3: break
    rec=list(reversed(seen))

    SYS = sys_prompt(name,last_m,h,rec,lock,intent,task)
    ai = call_ai(text,SYS)

    # shorten if small user input
    if short_trigger:
        ai = ai.split(".")[0].strip()[:120]

    if ai and ai[0].isalpha(): ai = ai[0].upper() + ai[1:]

    icon = mood_icon(last_m)
    g,mem = greet(mem,uid,name,h,last_m)

    tail = " 😉" if smalltalk(text) and lock in ("general","fun") else ""
    final = f"{icon} {g}{ai}{tail}\n\n<b>⚡ WENBNB Neural Engine</b> — Focus + Emotion 24×7"

    st["e"].append({"u":text,"r":ai,"m":last_m,"t":cur_topic,"time":datetime.utcnow().isoformat()})
    st["e"]=st["e"][-18:]
    mem[uid]=st; save_memory(mem)

    try: msg.reply_text(final,parse_mode=ParseMode.HTML,disable_web_page_preview=True)
    except: msg.reply_text(final)

def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
