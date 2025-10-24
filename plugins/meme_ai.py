from telegram import ParseMode
from telegram.ext import CommandHandler
import random, html

# === WENBNB Meme Vision v8.6 ===
BRAND = "💫 Powered by <b>WENBNB Meme Engine</b> — Emotion Synced 24×7 ⚡"

# --- Meme templates ---
TEMPLATES = [
    "😂 “When {topic} pumps harder than my motivation on Monday 🚀💎”",
    "🤣 “When {topic} dumps and I start refreshing charts like Netflix 📉🍿”",
    "😎 “When {topic} mooning turns into my new personality 😏🌙”",
    "🤖 “AI told me to buy {topic}... now I'm emotionally attached 💘🤯”",
    "🔥 “When {topic} is pumping but my coffee’s still cold ☕📈”",
    "🚀 “When {topic} hits ATH and I act like I planned it all along 💼📊”",
    "💰 “My wallet after {topic}: emotional damage = 0, gains = 100 % 💎”",
]

HASHTAGS = [
    "#CryptoLife", "#WENBNB", "#MemeDrop", "#DeFiMood", "#HODL",
    "#BullVibes", "#AiEnergy", "#StayBased", "#MemeMode", "#CryptoFeels"
]

def meme_cmd(update, context):
    """Cinematic text-only meme illusion"""
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # --- user input / default topic ---
        topic = "crypto"
        if context.args:
            topic = " ".join(context.args).capitalize()

        # --- pretend to render ---
        update.message.reply_text(
            f"🔥 Meme Reactor Online\n🧠 Syncing humor levels...\n💫 Generating viral scene for <b>{html.escape(topic)}</b> ...",
            parse_mode=ParseMode.HTML
        )

        # --- select dynamic caption ---
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
            "⚙️ Neural Meme Reactor cooling down — try again soon 😅",
            parse_mode=ParseMode.HTML
        )

def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("meme", meme_cmd))
    print("✅ Loaded plugin: plugins.meme_ai (v8.6 Meme Vision Mode)")
