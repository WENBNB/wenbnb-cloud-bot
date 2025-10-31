"""
WENBNB AI Auto-Reply — Queen Street Mode v9.5
Focus + Flirt + Hustle Energy + Emotional Sync
- Does NOT reply to slash commands
- Maintains topic thread
- Light teasing, not over-flirt
- Street smart + warmth + ambition
"""

import os, json, random, requests
from datetime import datetime
from telegram import Update, ParseMode
from telegram.ext import CallbackContext, MessageHandler, Filters

AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_PROXY_URL = os.getenv("AI_PROXY_URL", "")
MEMORY_FILE = "user_memory.json"

# ---------------- Memory ----------------
def load_mem():
    if os.path.exists(MEMORY_FILE):
        try: return json.load(open(MEMORY_FILE, "r", encoding="utf-8"))
        except: return {}
    return {}

def save_mem(data):
    json.dump(data, open(MEMORY_FILE, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)

# ---------------- Utils ----------------
def is_hinglish(t):
    words=["bhai","yaar","acha","accha","nahi","haan","bolo","kuch","chal"]
    return any(w in t.lower() for w in words)

def detect_topic(text):
    t = text.lower()
    mapping = {
        "business":["earning","website","startup","project","money","bot"],
        "travel":["travel","trip","goa","manali","holiday"],
        "crypto":["bnb","btc","eth","crypto","token","price","chart"],
        "love":["love","miss","baby","queen","kiss"],
        "info":["how","kese","kya","guide","help","sikhna","learn"]
    }
    for topic,keys in mapping.items():
        if any(k in t for k in keys): return topic
    return "general"

def call_ai(history, text, topic, hing):
    system = (
        "You are WENBNB Queen Mode — flirty, savage, warm, motivational, street smart. "
        "Tone: 60% sweet tease, 40% bossy hustler sister. "
        "Never break topic. Be playful but stay helpful. "
        "Keep responses short, emotional, and real. "
        "Hinglish allowed if user uses it. "
        "If user jumps topics, lightly call it out funnily and redirect."
    )
    if hing: system += " Reply in Hinglish tone."

    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role":"system","content":system}]
            + [{"role":"user","content":m} for m in history]
            + [{"role":"user","content":text}],
        "temperature": 0.9,
        "max_tokens": 180,
    }

    url = AI_PROXY_URL or "https://api.openai.com/v1/chat/completions"
    headers={"Content-Type":"application/json"}
    if not AI_PROXY_URL: headers["Authorization"]=f"Bearer {AI_API_KEY}"

    try:
        res = requests.post(url, json=body, headers=headers, timeout=25).json()
        return res["choices"][0]["message"]["content"].strip()
    except:
        return "Network thoda nakhre dikha raha hai 😒 try once more."

# ---------------- Main Handler ----------------
def ai_reply(update: Update, context: CallbackContext):
    msg = update.message
    if not msg or not msg.text: return
    text = msg.text.strip()
    if text.startswith("/"): return  # ignore commands

    uid = str(msg.from_user.id)
    chat_id = msg.chat_id
    user = msg.from_user.first_name or "you"

    try: context.bot.send_chat_action(chat_id, "typing")
    except: pass

    mem = load_mem()
    history = mem.get(uid, {}).get("h", [])[-6:]

    hing = is_hinglish(text)
    topic = detect_topic(text)

    # AI call
    reply = call_ai(history, text, topic, hing)

    # store memory
    mem.setdefault(uid, {"h": []})
    mem[uid]["h"].append(text)
    mem[uid]["h"].append(reply)
    mem[uid]["h"] = mem[uid]["h"][-10:]
    save_mem(mem)

    signature = "⚡ WENBNB Neural Engine — Queen Street Mode"
    final = f"{reply}\n\n{signature}"

    try: msg.reply_text(final, parse_mode=ParseMode.HTML)
    except: msg.reply_text(final)

# ---------------- Register ----------------
def register_handlers(dp, config=None):
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_reply))
