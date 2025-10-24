"""
😂 WENBNB Meme Intelligence v8.4 — AI Scene Creator Mode
• /meme <topic> — generates meme image from text using AI (no photo needed)
• /meme ai <prompt> — full creative meme generation mode
• Auto top/bottom captions, Emotion Sync color tuning, and Glow Styling
🔥 Powered by WENBNB Neural Engine — Emotion Sync + Visual AI Fusion ⚡
"""

import os, io, random, requests
from telegram import Update, InputFile
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from PIL import Image, ImageDraw, ImageFont
from base64 import b64decode

# === CONFIG ===
OPENAI_API = os.getenv("OPENAI_API_KEY", "")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BRAND_TAG = "😂 Powered by WENBNB Neural Engine — AI Scene Creator v8.4 💫"

# === UTILITIES ===
def ai_caption_idea(topic: str):
    prompt = f"Write a short, funny meme caption (max 12 words) about {topic}. Tone: witty, crypto, internet humor."
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API}"},
            json={
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 50,
            },
            timeout=10,
        )
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception:
        return random.choice([
            "When the dip dips harder than your patience 😭",
            "I told you, mom — it’s decentralized luck 🚀",
            "Just another day holding bags 💎🙌",
        ])

def generate_ai_image(prompt: str):
    try:
        payload = {
            "model": "gpt-image-1",
            "prompt": f"A meme-style digital art about {prompt}, realistic lighting, centered subject, bold contrast.",
            "size": "1024x1024",
        }
        headers = {"Authorization": f"Bearer {OPENAI_API}"}
        r = requests.post("https://api.openai.com/v1/images/generations", json=payload, headers=headers, timeout=30)
        data = r.json()
        img_base64 = data["data"][0]["b64_json"]
        return io.BytesIO(b64decode(img_base64))
    except Exception as e:
        print("AI Image generation failed:", e)
        return None

def add_meme_text(img_bytes, caption: str):
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    draw = ImageDraw.Draw(img)
    font_size = max(28, int(img.width / 12))
    font = ImageFont.truetype(FONT_PATH, font_size)

    parts = caption.split()
    top_text = " ".join(parts[:len(parts)//2])
    bottom_text = " ".join(parts[len(parts)//2:])

    outline_color, fill_color = "black", "white"

    def draw_text_centered(text, y):
        w, h = draw.textsize(text, font=font)
        x = (img.width - w) / 2
        for dx in [-2, 2]:
            for dy in [-2, 2]:
                draw.text((x+dx, y+dy), text, font=font, fill=outline_color)
        draw.text((x, y), text, font=font, fill=fill_color)

    draw_text_centered(top_text, 30)
    draw_text_centered(bottom_text, img.height - font_size * 2)

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

# === MAIN COMMAND ===
def meme_cmd(update: Update, context: CallbackContext):
    msg = update.message
    args = context.args

    if not args:
        msg.reply_text("🧠 Use `/meme <topic>` or `/meme ai <prompt>` to create a meme.", parse_mode="HTML")
        return

    if args[0].lower() == "ai" and len(args) > 1:
        topic = " ".join(args[1:])
    else:
        topic = " ".join(args)

    msg.reply_text(f"🎨 Creating your meme scene for: <b>{topic}</b> ...", parse_mode="HTML")

    caption = ai_caption_idea(topic)
    image_data = generate_ai_image(topic)

    if not image_data:
        msg.reply_text("⚠️ Image generation failed. Try again later.", parse_mode="HTML")
        return

    meme = add_meme_text(image_data.read(), caption)
    msg.reply_photo(photo=InputFile(meme, filename="meme.jpg"),
                    caption=f"{caption}\n\n{BRAND_TAG}",
                    parse_mode="HTML")

# === PHOTO HANDLER ===
def meme_photo(update: Update, context: CallbackContext):
    photo = update.message.photo[-1]
    file = photo.get_file()
    image_bytes = requests.get(file.file_path).content
    caption = ai_caption_idea("crypto market")
    meme = add_meme_text(image_bytes, caption)
    update.message.reply_photo(photo=InputFile(meme, filename="meme.jpg"),
                               caption=f"{caption}\n\n{BRAND_TAG}",
                               parse_mode="HTML")

# === REGISTER ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("meme", meme_cmd))
    dispatcher.add_handler(MessageHandler(Filters.photo, meme_photo))
    print("✅ Loaded plugin: meme_ai.py (v8.4 AI Scene Creator Mode)")
