# plugins/meme_ai.py
"""
AI Meme Generator — WENBNB Bot Plugin
Version: 3.2 (Locked & Approved)
Mode: Hybrid (Command + Passive Caption AI)
"""

import os, requests, random, io, re
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InputFile
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

# === CONFIG ===
AI_API = os.getenv("OPENAI_API_KEY", "")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BRAND_FOOTER = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"

# === UTILITIES ===

def ai_caption_idea(topic: str):
    """Generate funny or viral caption idea using AI"""
    prompt = f"Create a short, witty, meme-style caption about {topic}. Tone: funny, viral, crypto, casual."
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API}"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
            },
            timeout=15,
        )
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return random.choice([
            "When the market dips... but your faith doesn’t 💪😂",
            "HODL mode: Activated 🚀",
            "That face when gas fees are higher than your portfolio 😭",
        ])

def add_caption(image_bytes: bytes, caption: str):
    """Overlay caption text on an image."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)

    font_size = int(img.width / 15)
    font = ImageFont.truetype(FONT_PATH, font_size)

    text_w, text_h = draw.textsize(caption, font=font)
    x = (img.width - text_w) / 2
    y = img.height - text_h - 30

    outline_color = "black"
    for dx in [-2, 2]:
        for dy in [-2, 2]:
            draw.text((x+dx, y+dy), caption, font=font, fill=outline_color)
    draw.text((x, y), caption, font=font, fill="white")

    output = io.BytesIO()
    img.save(output, format="JPEG")
    output.seek(0)
    return output

# === COMMAND HANDLER ===

def meme_command(update: Update, context: CallbackContext):
    """/meme command - takes image + topic"""
    msg = update.message
    if not msg.photo and not context.args:
        msg.reply_text("📸 Send an image or use `/meme <topic>` to generate a caption.")
        return

    if msg.photo:
        topic = "crypto"
    else:
        topic = " ".join(context.args)

    caption = ai_caption_idea(topic)
    msg.reply_text(f"🧠 AI Caption Idea: {caption}\n\n{BRAND_FOOTER}")

def meme_with_photo(update: Update, context: CallbackContext):
    """When user sends a photo, auto-caption it"""
    photo = update.message.photo[-1]
    file = photo.get_file()
    image_bytes = requests.get(file.file_path).content

    caption = ai_caption_idea("crypto market or trading")
    meme_image = add_caption(image_bytes, caption)

    update.message.reply_photo(
        photo=InputFile(meme_image, filename="meme.jpg"),
        caption=f"{caption}\n\n{BRAND_FOOTER}",
    )

# === REGISTRATION ===

def register_handlers(dp):
    dp.add_handler(CommandHandler("meme", meme_command))
    dp.add_handler(MessageHandler(Filters.photo, meme_with_photo))
