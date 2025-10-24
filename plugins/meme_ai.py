"""
AI Meme Generator — WENBNB Bot Plugin
Version: 8.5 (Visual Mode)
Mode: Hybrid (Command + Image AI Caption)
"""

import os, requests, random, io, re
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InputFile
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

# === CONFIG ===
AI_API = os.getenv("OPENAI_API_KEY", "")
BRAND_FOOTER = "😂 Powered by WENBNB Neural Engine — Meme Intelligence v8.5 ⚡"

# --- Font Configuration ---
from PIL import ImageFont
try:
    FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    ImageFont.truetype(FONT_PATH, 20)
except OSError:
    FONT_PATH = None  # fallback to default font if missing


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
                "max_tokens": 60,
            },
            timeout=25,
        )
        data = r.json()
        caption = data["choices"][0]["message"]["content"].strip()
        if not caption:
            raise ValueError("Empty caption response")
        return caption
    except Exception:
        return random.choice([
            "When the market dips but your faith doesn’t 💪😂",
            "HODL mode: activated 🚀",
            "That face when gas fees cost more than your bag 😭",
            "Trading vibes: win some, learn some 💸",
            "When BNB pumps and your ex texts back 👀",
        ])


def ai_generate_image(prompt: str):
    """Generate meme image using DALL·E via OpenAI API"""
    try:
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={"Authorization": f"Bearer {AI_API}", "Content-Type": "application/json"},
            json={"model": "gpt-image-1", "prompt": prompt, "size": "512x512"},
            timeout=40,
        )
        data = r.json()
        if "data" in data and len(data["data"]) > 0:
            image_url = data["data"][0]["url"]
            image_bytes = requests.get(image_url).content
            return image_bytes
    except Exception as e:
        print("Image generation error:", e)
    return None


def add_caption(image_bytes: bytes, caption: str):
    """Overlay caption text on an image with outline for visibility."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Dynamic font sizing
    font_size = max(24, int(img.width / 18))
    font = ImageFont.truetype(FONT_PATH, font_size) if FONT_PATH else ImageFont.load_default()

    # Wrap text if too long
    lines = []
    words = caption.split()
    line = ""
    for word in words:
        if draw.textlength(line + " " + word, font=font) < img.width * 0.9:
            line += " " + word
        else:
            lines.append(line.strip())
            line = word
    lines.append(line.strip())

    text = "\n".join(lines)
    text_w, text_h = draw.multiline_textsize(text, font=font, spacing=5)
    x = (img.width - text_w) / 2
    y = img.height - text_h - 40

    # Draw outline + fill
    for dx in (-2, 2):
        for dy in (-2, 2):
            draw.multiline_text((x + dx, y + dy), text, font=font, fill="black", spacing=5)
    draw.multiline_text((x, y), text, font=font, fill="white", spacing=5)

    output = io.BytesIO()
    img.save(output, format="JPEG")
    output.seek(0)
    return output


# === COMMAND HANDLER ===
def meme_cmd(update: Update, context: CallbackContext):
    """ /meme command — AI caption + image generation """
    msg = update.message
    try:
        topic = " ".join(context.args) if context.args else "crypto"
        msg.reply_text(f"🎨 Creating your meme scene for: {topic} ...")

        caption = ai_caption_idea(topic)

        # 🧠 Generate image via DALL·E
        image_bytes = ai_generate_image(f"{topic}, crypto, meme style, funny")

        if image_bytes:
            meme_image = add_caption(image_bytes, caption)
            msg.reply_photo(
                photo=InputFile(meme_image, filename="meme.jpg"),
                caption=f"🧠 Meme Idea: {caption}\n\n{BRAND_FOOTER}",
            )
        else:
            msg.reply_text(f"🧠 Meme Idea: {caption}\n\n{BRAND_FOOTER}")

    except Exception as e:
        msg.reply_text(f"⚠️ Internal meme error: {e}")
        raise


def meme_with_photo(update: Update, context: CallbackContext):
    """When user sends a photo, auto-caption it"""
    try:
        photo = update.message.photo[-1]
        file = photo.get_file()
        image_bytes = requests.get(file.file_path).content

        caption = ai_caption_idea("crypto trading or market moves")
        meme_image = add_caption(image_bytes, caption)

        update.message.reply_photo(
            photo=InputFile(meme_image, filename="meme.jpg"),
            caption=f"{caption}\n\n{BRAND_FOOTER}",
        )
    except Exception as e:
        update.message.reply_text(f"⚠️ Meme generation failed: {e}")


# === REGISTRATION ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("meme", meme_cmd))
    dp.add_handler(MessageHandler(Filters.photo, meme_with_photo))
