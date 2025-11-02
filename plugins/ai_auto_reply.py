# ========================================================
# WENBNB AI Auto-Reply v9.5 Hybrid Ultra (Final)
# Girlfriend Warmth + CEO Focus (Only When Asked)
# Romantic Priority | Marwadi Toggle | Name Polishing
# ========================================================

import os, json, random, requests, re
from datetime import datetime, timedelta
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

AI_KEY = os.getenv("OPENAI_API_KEY","")
PROXY  = os.getenv("AI_PROXY_URL","")
MEM    = "user_memory.json"

# Load/save memory
def load(): return json.load(open(MEM,"r",encoding="utf-8")) if os.path.exists(MEM) else {}
def save(d): json.dump(d,open(MEM,"w",encoding="utf-8"),indent=2,ensure_ascii=False)

# Mood icons
MOOD = {
 "love":["💋","❤️‍🔥","😘","💞"],
 "calm":["🙂","✨","😊"],
 "focus":["⚡","🚀","🔥"],
 "fun":["😏","😂","😉"],
}
def emo(mode): return random.choice(MOOD.get(mode,["✨"]))

# Hinglish detect
HING = ["kya","haan","nahi","kar","karo","batao","yaar","bhai","chalo","tum","me","mera"]
def hing(t): t=t.lower(); return any(h in t for h in HING) or any("\u0900"<=c<="\u097F" for c in t)

# Romance trigger
LOVE = ["baby","jaan","love","miss","kiss","meri","chhori","princess","queen"]
def romantic(t): return any(x in t.lower() for x in LOVE)

# Work trigger
WORK = ["earning","kaise","banao","plan","steps","help","guide","crypto","bot","website","business","target"]
def wants_work(t): return any(x in t.lower() for x in WORK)

# Marwadi trigger
MARU = ["marwadi","rajasthani","chhori","ghani","mharo","sa"]
def maru(t): return any(x.lower() in t.lower() for x in MARU)

# Topic memory small
def history(uid,mem):
    e=mem.get(uid,[]); seen=[]
    for x in reversed(e):
        if x.get("topic") not in seen:
            seen.append(x.get("topic"))
        if len(seen)>=3: break
    return ", ".join(seen)

def detect_topic(t):
    t=t.lower()
    if "crypto" in t or "bnb" in t or "btc" in t: return "crypto"
    if "bot" in t: return "bot"
    if "site" in t or "website" in t: return "website"
    if romantic(t): return "romance"
    return "general"

# System prompt
def build_sys(name, romo, focus, mar, h, hist):
    p="You are WENBNB girlfriend AI.\nWarm, witty, teasing, loyal.\n"
    p+="Reply max 2-4 lines.\nNever robotic.\nNo lecturing.\n"
    if romo: p+="User is in ROMANCE mode. Prioritize love, softness, playful flirty tone.\n"
    if focus: p+="User asked WORK. Provide short, actionable steps. Be motivating.\n"
    if mar: p+="Reply in light Marwadi + Hinglish flavor.\n"
    if h: p+="Use Hinglish naturally.\n"
    if hist: p+=f"Recent vibe: {hist}\n"
    p+=f"User name: {name}\n"
    p+="Use max 1 emoji inline.\n"
    p+="Avoid repeating user name every sentence.\n"
    return p

# API call
def ask(prompt, sys):
    body={
        "model":"gpt-4o-mini",
        "messages":[{"role":"system","content":sys},{"role":"user","content":prompt}],
        "temperature":0.8,"max_tokens":170
    }
    url = PROXY or "https://api.openai.com/v1/chat/completions"
    head={"Content-Type":"application/json"}
    if not PROXY: head["Authorization"]=f"Bearer {AI_KEY}"
    try:
        r=requests.post(url,json=body,headers=head,timeout=20).json()
        return r["choices"][0]["message"]["content"].strip()
    except:
        return "Network blush kar gaya 😅 thoda paas baith ❤️"

def ai_auto_chat(update:Update,context:CallbackContext):
    msg=update.message
    if not msg or not msg.text or msg.text.startswith("/"): return
    text=msg.text.strip()
    user=update.effective_user
    uid=str(user.id)
    try: context.bot.send_chat_action(msg.chat_id,"typing")
    except: pass

    mem=load()
    mem.setdefault(uid,[])
    past=mem[uid]
    last="calm"
    if past: last=past[-1]["mood"]

    # STATES
    romantic_mode = romantic(text)
    focus_mode    = wants_work(text) and not romantic_mode
    mar_mode      = maru(text)
    h             = hing(text)
    name          = user.first_name or "love"
    top           = detect_topic(text)
    hist          = history(uid,mem)

    sys = build_sys(name, romantic_mode, focus_mode, mar_mode, h, hist)
    ans = ask(text, sys)

    # mood icon
    mode = "love" if romantic_mode else ("focus" if focus_mode else ("fun" if mar_mode else "calm"))
    icon = emo(mode)

    # greet logic short
    greet = ""
    if random.random()<0.7 and not romantic_mode:
        greet = ""

    final = f"{icon} {ans}\n\n<b>⚡ WENBNB Neural Engine</b> — Feel + Focus"

    # save mem
    mem[uid].append({"text":text,"reply":ans,"mood":mode,"topic":top,"time":datetime.utcnow().isoformat()})
    mem[uid]=mem[uid][-20:]
    save(mem)

    try: msg.reply_text(final,parse_mode=ParseMode.HTML)
    except: msg.reply_text(final)

def register_handlers(dp,config=None):
    from telegram.ext import MessageHandler, Filters
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_chat))
