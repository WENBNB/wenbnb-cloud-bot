# plugins/meme_ai.py
"""
WENBNB Neural Engine — Meme Intelligence Core
Version: 8.5.2 (Text-Only Stable)
Mode: Hybrid (Command + AI Caption)
"""

import os, requests, random
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext

# === CONFIG ===
AI_API = os.getenv("OPENAI_API_KEY", "")
BRAND_FOOTER = "😂 Powered by WENBNB Neural Engine — Meme Intelligence v8.5.2 ⚡"

# === UTILITIES ===
def ai_caption_idea(topic: str):
    """Generate witty meme caption using AI or fallback."""
    prompt = f"Create a short, viral crypto meme caption about {topic}. Keep it funny, clever, and tweetable."
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 60,
            },
            timeout=15,
        )
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return random.choice([
            "When BNB pumps and your ex texts back 😂📈",
            "That feeling when your portfolio finally smiles again 💎",
            "When crypto dips, but your faith doesn’t 😎",
            "Still HODLing like it’s my full-time job 🚀",
        ])

# === COMMAND HANDLER ===
def meme_cmd(update: Update, context: CallbackContext):
    """Responds to /meme command with AI-generated caption idea"""
    msg = update.message
    context.bot.send_chat_action(chat_id=msg.chat_id, action="typing")

    # Topic selection
    if context.args:
        topic = " ".join(context.args)
    else:
        topic = "crypto"

    msg.reply_text(f"🎨 Creating your meme scene for: <b>{topic}</b> ...", parse_mode="HTML")

    # Generate meme caption
    caption = ai_caption_idea(topic)

    # Send meme idea
    msg.reply_text(
        f"🧠 Meme Idea: {caption}\n\n{BRAND_FOOTER}",
        parse_mode="HTML"
    )

# === REGISTER HANDLER ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("meme", meme_cmd))
    print("✅ Loaded plugin: plugins.meme_ai (v8.5.2 Text-Only Stable)")
