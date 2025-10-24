"""
😂 WENBNB Meme Intelligence v8.1 — Emotion Sync Edition
• /meme <topic> → AI caption generator
• Send any photo → auto meme caption overlay
• Emotion-aware captions when Emotion Sync active
🔥 Powered by WENBNB Neural Engine — Meme Intelligence v8.1 ⚡
"""

import os, io, random, requests
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InputFile
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

# === CONFIG ===
AI_API = os.getenv("OPENAI_API_KEY", "")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BRAND_TAG = "😂 Powered by WENBNB Neural Engine — Meme Intelligence v8.1 ⚡"

# === UTILITIES ===
def ai_caption_idea(topic: str, mood: str = None):
    """Generate witty meme caption with AI or fallback."""
    mood_part = f"Make it feel {mood}." if mood else ""
    prompt = (
        f"Create a short, funny crypto meme caption about {topic}. "
        f"Keep it viral, casual, and witty. {mood_part} Max 12 words."
    )
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API}"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 40,
            },
            timeout=10,
        )
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return random.choice([
            "When you buy the dip... and it keeps dipping 💀",
            "That face when gas fees > profits 😭",
            "HODL until your coffee turns to dust ☕🚀",
            "Portfolio down bad, but vibes still bullish 💎",
        ])

def add_caption(image_bytes: bytes, caption: str):
    """Overlay caption text on image."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)
    font_size = int(img.width / 13)
    font = ImageFont.truetype(FONT_PATH, font_size)
    text_w, text_h = draw.textsize(caption, font=font)
    x = (img.width - text_w) / 2
    y = img.height - text_h - 35
    for dx in [-2, 2]:
        for dy in [-2, 2]:
            draw.text((x+dx, y+dy), caption, font=font, fill="black")
    draw.text((x, y), caption, font=font, fill="white")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

# === COMMAND ===
def meme_cmd(update: Update, context: CallbackContext):
    """Handle /meme command."""
    msg = update.message
    args = context.args
    if not args and not msg.photo:
        msg.reply_text("📸 Send an image or use `/meme <topic>` to create a meme!", parse_mode="HTML")
        return

    topic = " ".join(args) if args else "crypto"
    mood = None

    # Emotion Sync — use mood from Emotion AI if present
    if "emotion" in context.bot_data:
        mood = context.bot_data["emotion"]

    caption = ai_caption_idea(topic, mood)
    msg.reply_text(f"🧠 Meme Idea: {caption}\n\n{BRAND_TAG}", parse_mode="HTML")

# === AUTO-PHOTO ===
def meme_photo(update: Update, context: CallbackContext):
    """Auto caption a user photo with emotion context."""
    photo = update.message.photo[-1]
    file = photo.get_file()
    image_bytes = requests.get(file.file_path).content
    mood = context.bot_data.get("emotion", "funny")
    caption = ai_caption_idea("crypto traders", mood)
    meme_img = add_caption(image_bytes, caption)
    update.message.reply_photo(
        photo=InputFile(meme_img, filename="meme.jpg"),
        caption=f"{caption}\n\n{BRAND_TAG}",
        parse_mode="HTML",
    )

# === REGISTER ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("meme", meme_cmd))
    dispatcher.add_handler(MessageHandler(Filters.photo, meme_photo))
    print("✅ Loaded plugin: meme_ai.py (v8.1 Emotion Sync Edition)")
