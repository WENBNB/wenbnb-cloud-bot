# ============================================================
# WENBNB • AI Auto-Reply v9.4.3 Stability Patch
# Ultra Queen • No repeat cringe • Smart smalltalk exit
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
def mood_icon(m): return random.choice(MOOD_ICON.get(m,["🙂"]))

def cname(u): return u.username if getattr(u,"username",None) else (u.first_name or "friend")

HING=["bhai","yaar","kya","acha","accha","nahi","haan","bolo","karna","kaise","earning","plan","guide","randi","raand","love","baby"]
def hinglish(t): return any("\u0900"<=c<="\u097F" for c in t) or any(w in t.lower() for w in HING)

TOPICS = {
 "market":["bnb","btc","eth","crypto","token","price","chart","trade"],
 "airdrop":["airdrop","quest","claim","points"],
 "web3":["wallet","metamask","contract","stake","dex","deploy","bot"],
 "life":["love","sleep","work","tired","busy","mood"],
 "fun":["meme","joke","lol","funny"]
}
def detect_topic(t):
    t=t.lower()
    for k,v in TOPICS.items():
        if any(x in t for x in v): return k
    return "general"

TASK_KW=["kaise","steps","guide","plan","setup","earning","process","banado","karao"]
def wants_task(t): return any(k in t.lower() for k in TASK_KW)

def topic_lock(mem,uid):
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

def sys_prompt(name,mood,h,rec,lock,task):
    p="You are WENBNB girlfriend-coach AI. Warm, teasing but purpose-driven.\n"
    p+="Short replies (2–4 lines). Real human tone.\n"
    p+="Don't over-greet. Don't repeat same questions.\n"
    p+="If user does casual chat, reply once then move to value topic.\n"
    p+="Light flirt okay, but discipline > drama.\n"
    if h: p+="Use Hinglish.\n"
    if lock: p+=f"Stay on topic: {lock}\n"
    if task: p+="User needs steps — give crisp action.\n"
    if rec: p+=f"Context: {', '.join(rec)}\n"
    p+=f"User: {name}. Mood:{mood}."
    return p

def call_ai(prompt,sys):
    body={"model":"gpt-4o-mini","messages":[
        {"role":"system","content":sys},
        {"role":"user","content":prompt}],
        "temperature":0.85,"max_tokens":200}
    url=AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    h={"Content-Type":"application/json"}
    if not AI_PROXY_URL: h["Authorization"]=f"Bearer {AI_API_KEY}"
    try:
        r=requests.post(url,json=body,headers=h,timeout=20).json()
        return r.get("choices",[{}])[0].get("message",{}).get("content","")
    except:
        return "Network glitch aaya baby 😅 par main yahin hoon 💞"

SMALL=re.compile(r"(hi|hello|baby|love|😘|❤️|😉|🥰|😏|kya chal)",re.I)
def is_small(t): return bool(SMALL.search(t))

def greet(mem,uid,name,h,mood):
    u=mem.get(uid,{})
    if u.get("g",False) or random.random()>0.55:
        return "",mem
    u["g"]=True; mem[uid]=u
    if h:
        bank=[f"Arey sun, ",f"Accha bata, ",f"Sun na, "]
    else:
        bank=[f"Hey, ",f"So tell me, ",f"Okay, "]
    return random.choice(bank),mem

def ai_auto_chat(update:Update, context:CallbackContext):
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

    seen=[]
    for e in reversed(st["e"]):
        tp=e.get("t")
        if tp and tp not in seen: seen.append(tp)
        if len(seen)>=3: break

    # smalltalk fix — casual? → answer once then turn to goal
    chit = is_small(t)

    SYS=sys_prompt(name,last_m,h,seen[::-1],lock,wants_task(t))
    ai=call_ai(t,SYS).strip()

    if chit:
        ai += "\n\nChalo ab batao — aaj ka goal kya hai? 🎯"

    if ai and ai[0].isalpha(): ai=ai[0].upper()+ai[1:]

    ic=mood_icon(last_m); g,mem=greet(mem,uid,name,h,last_m)
    tail=" 😉" if chit else ""
    final=f"{ic} {g}{ai}{tail}\n\n<b>⚡ WENBNB Neural Engine</b> — Focus + Emotion 24×7"

    st["e"].append({"u":t,"r":ai,"m":last_m,"t":cur,"time":datetime.utcnow().isoformat()})
    st["e"]=st["e"][-18:]
    mem[uid]=st; save_memory(mem)

    try: msg.reply_text(final,parse_mode=ParseMode.HTML,disable_web_page_preview=True)
    except: msg.reply_text(final)

def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
