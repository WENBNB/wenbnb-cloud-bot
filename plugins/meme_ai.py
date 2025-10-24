"""
🎭 WENBNB Meme Engine v8.5.6 — Emotion Sync Hybrid Mode
• AI caption generator + organic hashtags
• Reacts to both /meme command and user photo uploads
• Includes startup "Meme Reactor Online" intro
"""

import os, random, requests
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

AI_API = os.getenv("OPENAI_API_KEY", "")
BRAND_TAG = "💫 Powered by WENBNB Meme Engine — Emotion Synced 24×7 ⚡"

# Track if intro has been shown
intro_shown = False

# === AI caption generator ===
def ai_caption(topic: str):
    prompt = (
        f"Write a short viral crypto meme caption about {topic}. "
        "Keep it witty, playful, relatable. Add emojis where it feels natural."
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
        return random.choice([
            "When the market dips right after you ape in 😭📉",
            "That moment when gas fees > your bag size ⛽😂",
            "Still holding like it’s a yoga pose 💎🧘‍♂️",
            "When Bitcoin sneezes and my altcoins faint 💀📊",
        ])

# === Hashtag generator ===
def random_hashtags():
    tags = [
        "#WENBNB", "#MemeDrop", "#CryptoFeels", "#StayBased", "#HODL",
        "#BullVibes", "#DeFiMood", "#AiEnergy", "#WenLambo", "#MemeMode"
    ]
    return " ".join(random.sample(tags, 4))

# === /meme Command ===
def meme_cmd(update: Update, context: CallbackContext):
    global intro_shown
    msg = update.message
    topic = "crypto" if not context.args else " ".join(context.args)

    if not intro_shown:
        msg.reply_text("🔥 Meme Reactor Online\n🎭 Syncing humor levels...\n💫 Ready to generate viral moments.")
        intro_shown = True

    caption = ai_caption(topic)
    hashtags = random_hashtags()
    reply = (
        f"😂 “{caption}”\n{hashtags}\n\n"
        f"🧠 Meme Lab says: laughter = bullish sentiment 😎\n{BRAND_TAG}"
    )
    msg.reply_text(reply, parse_mode="HTML")

# === Photo reaction ===
def meme_photo(update: Update, context: CallbackContext):
    caption = ai_caption("crypto memes")
    hashtags = random_hashtags()
    reply = (
        f"🎨 “{caption}”\n{hashtags}\n\n"
        f"⚡ Visual mode active — syncing meme vibes 🤙🏻\n{BRAND_TAG}"
    )
    update.message.reply_text(reply, parse_mode="HTML")

# === Register ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("meme", meme_cmd))
    dispatcher.add_handler(MessageHandler(Filters.photo, meme_photo))
    print("✅ Loaded plugin: plugins.meme_ai (v8.5.6 Emotion Sync Hybrid Mode)")
