from telegram import ParseMode
from telegram.ext import CommandHandler
import random, html

# === WENBNB Meme Engine v8.7 ===
BRAND = "💫 Powered by <b>WENBNB Meme Engine</b> — Emotion Synced 24×7 ⚡"

TEMPLATES = [
    "😂 “When {topic} pumps harder than my motivation on Monday 🚀💎”",
    "🤣 “When {topic} dumps and I start refreshing charts like Netflix 📉🍿”",
    "😎 “When {topic} mooning becomes my new personality 😏🌙”",
    "🤖 “AI told me to buy {topic}... now I'm emotionally attached 💘🤯”",
    "🔥 “When {topic} is pumping but my coffee’s still cold ☕📈”",
    "💰 “My wallet after {topic}: emotional damage = 0, gains = 100% 💎”",
    "🪙 “When {topic} hits ATH and suddenly I’m a financial advisor 💼📊”",
    "😏 “{topic}? Nah, I prefer emotional stability... oh wait, I trade crypto.”",
    "🚀 “When {topic} moons before I even finish my ramen 🍜💎”",
]

HASHTAGS = [
    "#CryptoLife", "#WENBNB", "#MemeDrop", "#DeFiMood", "#HODL",
    "#BullVibes", "#AiEnergy", "#StayBased", "#MemeMode", "#CryptoFeels"
]

def meme_cmd(update, context):
    """Instant Meme Drop Mode"""
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        topic = "crypto"
        if context.args:
            topic = " ".join(context.args).capitalize()

        caption = random.choice(TEMPLATES).format(topic=html.escape(topic))
        tags = " ".join(random.sample(HASHTAGS, 4))
        emotion_line = "🧠 Meme Lab says: laughter = bullish sentiment 😎"

        msg = (
            f"{caption}\n"
            f"{tags}\n\n"
            f"{emotion_line}\n"
            f"{BRAND}"
        )

        update.message.reply_text(msg, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    except Exception as e:
        print("Error in meme_cmd:", e)
        update.message.reply_text(
            "⚙️ Meme engine had a tiny brain-freeze... try again shortly 😅",
            parse_mode=ParseMode.HTML
        )

def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("meme", meme_cmd))
    print("✅ Loaded plugin: plugins.meme_ai (v8.7 Meme Drop Mode)")
