# plugins/meme_ai.py
"""
AI Meme Generator — WENBNB Neural Engine
Version: 8.4.1 (Stable DALL·E Patch)
Mode: Hybrid (AI Scene + Caption Intelligence)
"""

import os, io, re, requests, random
from telegram import Update, InputFile
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image, ImageDraw, ImageFont

# === CONFIG ===
AI_API = os.getenv("OPENAI_API_KEY", "")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BRAND_FOOTER = "😂 Powered by WENBNB Neural Engine — Meme Intelligence v8.1 ⚡"

# === AI Caption Generator ===
def ai_caption_idea(topic: str):
    prompt = f"Write a short, viral, crypto-style meme caption about {topic}. Tone: funny, witty, emotional, and relatable."
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {AI_API}"},
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 60,
            },
            timeout=30,
        )
        data = r.json()
        caption = data["choices"][0]["message"]["content"].strip()
        return caption
    except Exception as e:
        print("AI Caption Error:", e)
        fallback = [
            "When you check your wallet and it’s mooning 🚀😂",
            "That face when gas fees ruin your trade 😭💸",
            "Me watching my portfolio like it’s Netflix 📉📈",
        ]
        return random.choice(fallback)

# === AI Meme Image Generator (DALL·E) ===
def ai_generate_image(prompt: str):
    try:
        headers = {
            "Authorization": f"Bearer {AI_API}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "dall-e-3",
            "prompt": f"A funny meme scene about {prompt}, in the style of viral crypto memes, expressive faces, bold contrast, vivid colors, square layout.",
            "size": "1024x1024",
            "quality": "standard"
        }
        r = requests.post("https://api.openai.com/v1/images/generations", json=payload, headers=headers, timeout=60)
        data = r.json()
        if "data" in data and len(data["data"]) > 0:
            url = data["data"][0]["url"]
            img_bytes = requests.get(url, timeout=30).content
            return img_bytes
        else:
            print("Image API error:", data)
            return None
    except Exception as e:
        print("AI Image Error:", e)
        return None

# === Caption Overlay Helper ===
def add_caption(image_bytes: bytes, caption: str):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)
    font_size = int(img.width / 15)
    font = ImageFont.truetype(FONT_PATH, font_size)

    text_w, text_h = draw.textsize(caption, font=font)
    x = (img.width - text_w) / 2
    y = img.height - text_h - 30

    # Outline
    for dx in [-2, 2]:
        for dy in [-2, 2]:
            draw.text((x+dx, y+dy), caption, font=font, fill="black")
    draw.text((x, y), caption, font=font, fill="white")

    output = io.BytesIO()
    img.save(output, format="JPEG")
    output.seek(0)
    return output

# === /meme Command Handler ===
def meme_command(update: Update, context: CallbackContext):
    msg = update.message
    args = context.args
    chat_id = msg.chat_id

    if not args:
        msg.reply_text("💡 Use `/meme ai <topic>` or send an image to caption it.")
        return

    topic = " ".join(args).strip().lower()
    if topic.startswith("ai "):
        topic = topic.replace("ai ", "").strip()
        msg.reply_text(f"🎨 Creating your meme scene for: <b>{topic}</b> ...", parse_mode="HTML")
        image_data = ai_generate_image(topic)
        if not image_data:
            msg.reply_text("⚠️ Image generation failed. Try again later.")
            return
        caption = ai_caption_idea(topic)
        final_img = add_caption(image_data, caption)
        msg.reply_photo(
            photo=InputFile(final_img, filename="meme.jpg"),
            caption=f"🧠 Meme Idea: {caption}\n\n{BRAND_FOOTER}",
            parse_mode="HTML"
        )
    else:
        caption = ai_caption_idea(topic)
        msg.reply_text(f"🧠 Meme Idea: {caption}\n\n{BRAND_FOOTER}", parse_mode="HTML")

# === When user sends a photo ===
def meme_with_photo(update: Update, context: CallbackContext):
    msg = update.message
    photo = msg.photo[-1]
    file = photo.get_file()
    image_bytes = requests.get(file.file_path).content
    caption = ai_caption_idea("crypto markets or traders")
    meme_image = add_caption(image_bytes, caption)
    msg.reply_photo(photo=InputFile(meme_image, filename="meme.jpg"),
                    caption=f"{caption}\n\n{BRAND_FOOTER}")

# === Register Handlers ===
def register_handlers(dp):
    dp.add_handler(CommandHandler("meme", meme_command))
    dp.add_handler(MessageHandler(Filters.photo, meme_with_photo))
    print("✅ Loaded plugin: plugins.meme_ai (v8.4.1 Stable DALL·E Patch)")
