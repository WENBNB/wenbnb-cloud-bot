"""
AI Auto-Conversation System v9.2 — Thread-Locked Emotional Engine
• Remembers topic until user clearly switches
• Flirt allowed, but task priority stays #1
• No random drift
• “Pehle kya bolaa?” answers properly
"""

import os, time, requests, json
from telegram import Update
from telegram.ext import MessageHandler, Filters, CallbackContext

# === Config ===
AI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AI_MODEL = "gpt-4o-mini"
BRAND_TAG = "⚡ WENBNB Emotional Intelligence 24×7"

STATE_FILE = "ctx_state.json"

def load_state():
    try:
        return json.load(open(STATE_FILE, "r"))
    except:
        return {}

def save_state(s):
    json.dump(s, open(STATE_FILE, "w"), indent=2, ensure_ascii=False)

ctx = load_state()

# === Topic Keywords ===
TOPIC_MAP = {
    "travel": ["travel", "trip", "manali", "dubai", "ticket", "flight"],
    "earning": ["earn", "earning", "income", "money", "website", "blog", "affiliate"],
    "telegram_bot": ["bot", "telegram", "alert", "price bot"],
    "crypto": ["crypto", "bnb", "btc", "token", "wallet"],
    "love": ["love", "baby", "meri jaan", "queen", "kiss"],
    "general": []
}

HARD_SWITCH = [
    "new topic", "next topic", "switch topic", 
    "chhod", "ignore", "done", "khatam", "leave it"
]

def detect_topic(text: str):
    text = text.lower()
    for topic, words in TOPIC_MAP.items():
        if any(w in text for w in words):
            return topic
    return "general"

# === OpenAI Call ===
def ai_generate(system, user):
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API_KEY}"},
            json={
                "model": AI_MODEL,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                "temperature": 0.8,
                "max_tokens": 250,
            },
            timeout=25,
        )
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ Neural core reconnecting…"

# === MAIN Chat Driver ===
def generate_ai_reply(uid, user_msg):
    global ctx

    u = ctx.get(str(uid), {"topic": None, "log": []})

    # Hard reset keywords
    if any(k in user_msg.lower() for k in HARD_SWITCH):
        u = {"topic": None, "log": []}

    # Detect new topic
    detected = detect_topic(user_msg)

    # Lock logic — only switch if no current thread OR clear intent
    if u["topic"] is None or (detected != u["topic"] and len(user_msg) > 8):
        u["topic"] = detected

    # Append memory (short stack)
    u["log"].append(f"User: {user_msg}")
    u["log"] = u["log"][-10:]

    ctx[str(uid)] = u
    save_state(ctx)

    system = (
        "You are WENBNB Emotional AI.\n"
        "Priority: stay on SAME TOPIC unless user clearly switches.\n"
        "Flirt tone allowed but TASK > flirty vibes.\n"
        "If user asks 'pehle kya bola', tell them & continue thread.\n"
        f"Active topic: {u['topic']}\n"
        "Conversation memory:\n" + "\n".join(u["log"])
    )

    reply = ai_generate(system, user_msg)

    u["log"].append(f"AI: {reply}")
    u["log"] = u["log"][-10:]
    ctx[str(uid)] = u
    save_state(ctx)

    return reply

# === Telegram Handler ===
def ai_auto_reply(update: Update, context: CallbackContext):
    uid = update.effective_user.id
    text = update.message.text.strip()

    if text.startswith("/"):
        return

    update.message.chat.send_action("typing")
    time.sleep(0.8)

    ai = generate_ai_reply(uid, text)
    update.message.reply_text(f"{ai}\n\n{BRAND_TAG}")

# === Register ===
def register_handlers(dp):
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply))
