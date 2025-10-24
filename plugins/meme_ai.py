"""
AI Meme Generator — WENBNB Bot Plugin
Version: 8.4.2 Hybrid-Fix + DALL·E Fallback
Mode: Command + Auto Caption
"""

import os, io, requests, random
from PIL import Image, ImageDraw, ImageFont
from telegram import Update, InputFile
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext

# === CONFIG ===
AI_API = os.getenv("OPENAI_API_KEY", "")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BRAND_FOOTER = "😂 Powered by WENBNB Neural Engine — Meme Intelligence v8.1 ⚡"

# === UTILITIES ===

def ai_caption_idea(topic: str):
    """Generate witty meme caption via OpenAI."""
    prompt = f"Create a short, funny meme caption about {topic}. Tone: crypto, witty, viral, casual."
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 60,
            },
            timeout=20,
        )
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return random.choice([
            "When BNB pumps and your ex texts back 💀📈",
            "Me checking my wallet after every green candle 😎",
            "Crypto traders be like: 'I’ll sell tomorrow'... and never do 🚀",
        ])

def ai_generate_image(prompt: str):
    """Generate meme scene via DALL·E 3 or fallback image."""
    try:
        headers = {
            "Authorization": f"Bearer {AI_API}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "dall-e-3",
            "prompt": f"A funny meme scene about {prompt}, cartoonish, viral crypto meme style, colorful, expressive faces.",
            "size": "1024x1024",
            "quality": "standard"
        }
        r = requests.post("https://api.openai.com/v1/images/generations", json=payload, headers=headers, timeout=60)
        data = r.json()

        if "data" in data and len(data["data"]) > 0:
            url = data["data"][0]["url"]
        else:
            # 🔁 Fallback to Unsplash if DALL·E not available
            print("⚠️ DALL·E unavailable — using fallback Unsplash image.")
            url = f"https://source.unsplash.com/1024x1024/?{prompt.replace(' ', ',')}"
        return requests.get(url, timeout=30).content
    except Exception as e:
        print("AI Image Error:", e)
        return None

def add_caption(image_bytes: bytes, caption: str):
    """Overlay caption text on the image."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)

    font_size = int(img.width / 14)
    font = ImageFont.truetype(FONT_PATH, font_size)

    text_w, text_h = draw.textsize(caption, font=font)
    x = (img.width - text_w) / 2
    y = img.height - text_h - 40

    # Add outline
    for dx in [-2, 2]:
        for dy in [-2, 2]:
            draw.text((x + dx, y + dy), caption, font=font, fill="black")
    draw.text((x, y), caption, font=font, fill="white")

    output = io.BytesIO()
    img.save(output, format="JPEG")
    output.seek(0)
    return output

# === COMMAND HANDLER ===

def meme_cmd(update: Update, context: CallbackContext):
    """Main /meme command"""
    msg = update.message
    topic = " ".join(context.args) if context.args else "crypto"
    msg.reply_text(f"🎨 Creating your meme scene for: <b>{topic}</b> ...", parse_mode="HTML")

    # Generate caption & image
    caption = ai_caption_idea(topic)
    image_bytes = ai_generate_image(topic)
    if not image_bytes:
        msg.reply_text("⚠️ Image generation failed. Try again later.")
        return

    meme_image = add_caption(image_bytes, caption)
    msg.reply_photo(
        photo=InputFile(meme_image, filename="meme.jpg"),
        caption=f"🧠 Meme Idea: {caption}\n\n{BRAND_FOOTER}",
        parse_mode="HTML",
    )

def meme_with_photo(update: Update, context: CallbackContext):
    """Auto-caption any photo sent."""
    photo = update.message.photo[-1]
    file = photo.get_file()
    image_bytes = requests.get(file.file_path).content

    caption = ai_caption_idea("crypto trading")
    meme_image = add_caption(image_bytes, caption)
    update.message.reply_photo(
        photo=InputFile(meme_image, filename="meme.jpg"),
        caption=f"{caption}\n\n{BRAND_FOOTER}",
    )

# === REGISTER ===

def register_handlers(dp):
    dp.add_handler(CommandHandler("meme", meme_cmd))
    dp.add_handler(MessageHandler(Filters.photo, meme_with_photo))
    print("✅ Loaded plugin: plugins.meme_ai (v8.4.2 Hybrid-Fix)")
