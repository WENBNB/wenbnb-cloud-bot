"""
🎭 WENBNB Meme Engine v8.5.5 — Emotion Sync Text Mode
• Generates AI-based meme captions with human tone + organic hashtags
• Fully compatible with WENBNB Neural Engine v8.0.5 and wenbot.py
• Safe: no image font dependencies or rendering errors
"""

import os, random, requests
from telegram import Update, InputFile
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

# === CONFIG ===
AI_API = os.getenv("OPENAI_API_KEY", "")
BRAND_TAG = "💫 Powered by WENBNB Meme Engine — Emotion Synced 24×7 ⚡"

# === CORE: AI Caption Generator ===
def ai_caption(topic: str):
    """Generate short, witty meme-style captions."""
    prompt = (
        f"Write a short viral crypto meme caption about {topic}. "
        "Tone: funny, human, casual, slightly sarcastic, Gen Z internet style. "
        "Include emojis where natural, max 1 line."
    )
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API}"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 60,
            },
            timeout=15,
        )
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        fallback = [
            "When the chart looks bullish… but your wallet says otherwise 😭📉",
            "That awkward moment when gas fees > your balance ⛽😂",
            "When you said ‘HODL’ but your emotions didn’t 😅💎",
            "Just another day pretending I understand on-chain metrics 🤡📊",
            "When Bitcoin sneezes and your altcoins catch pneumonia 😭💀"
        ]
        return random.choice(fallback)

# === AUTO HASHTAGS ===
def random_hashtags():
    tags = [
        "#WENBNB", "#MemeDrop", "#CryptoFeels", "#StayBased", "#DeFiMood",
        "#HODL", "#BullVibes", "#WenLambo", "#MemecoinLife", "#AiEnergy"
    ]
    return " ".join(random.sample(tags, k=4))

# === /meme Command ===
def meme_cmd(update: Update, context: CallbackContext):
    msg = update.message
    topic = "crypto" if not context.args else " ".join(context.args)
    caption = ai_caption(topic)
    hashtags = random_hashtags()

    reply = (
        f"😂 “{caption}”\n"
        f"{hashtags}\n\n"
        f"🧠 Meme Lab says: laughter = bullish sentiment 😎\n"
        f"{BRAND_TAG}"
    )

    msg.reply_text(reply, parse_mode="HTML")

# === Photo Handler (No rendering mode) ===
def meme_photo(update: Update, context: CallbackContext):
    caption = ai_caption("crypto markets and trading emotions")
    hashtags = random_hashtags()

    reply = (
        f"🎨 “{caption}”\n"
        f"{hashtags}\n\n"
        f"⚡ Visual mode active — meme energy syncing live 🤙🏻\n"
        f"{BRAND_TAG}"
    )
    update.message.reply_text(reply, parse_mode="HTML")

# === Register ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("meme", meme_cmd))
    dispatcher.add_handler(MessageHandler(Filters.photo, meme_photo))
    print("✅ Loaded plugin: plugins.meme_ai (v8.5.5 Emotion Sync Text Mode)")
