"""
😂 WENBNB Meme Intelligence v8.1 — Hybrid Generator
• /meme <topic> → AI caption generator
• Photo upload → auto meme caption overlay
• Uses GPT humor engine with fallback templates
🔥 Powered by WENBNB Neural Engine — Meme Intelligence v8.1
"""

import os, io, re, random, requests
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InputFile
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

# === CONFIG ===
AI_API = os.getenv("OPENAI_API_KEY", "")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BRAND_TAG = "😂 Powered by WENBNB Neural Engine — Meme Intelligence v8.1 ⚡"

# === UTILITIES ===
def ai_caption_idea(topic: str):
    """Generate witty meme caption via GPT or fallback."""
    prompt = (
        f"Create a short, funny crypto meme caption about {topic}. "
        "Keep it witty, relatable, and viral — max 12 words."
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
            "My portfolio after saying ‘just one more trade’ 😂",
            "Trust me bro, it's a long-term investment 🚀",
            "That moment when gas fees > profit 😭",
        ])

def add_caption(image_bytes: bytes, caption: str):
    """Draw caption text over image."""
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

# === COMMANDS ===
def meme_cmd(update: Update, context: CallbackContext):
    msg = update.message
    args = context.args
    if not args and not msg.photo:
        msg.reply_text("📸 Send an image or use `/meme <topic>` to create a meme!", parse_mode="HTML")
        return

    topic = " ".join(args) if args else "crypto market"
    caption = ai_caption_idea(topic)
    msg.reply_text(f"🧠 Meme Idea: {caption}\n\n{BRAND_TAG}", parse_mode="HTML")

def meme_photo(update: Update, context: CallbackContext):
    """Auto-caption user photo."""
    photo = update.message.photo[-1]
    file = photo.get_file()
    image_bytes = requests.get(file.file_path).content
    caption = ai_caption_idea("crypto traders")
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
    print("✅ Loaded plugin: meme_ai.py (v8.1 Meme Intelligence Hybrid)")
