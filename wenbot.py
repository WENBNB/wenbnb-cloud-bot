#!/usr/bin/env python3
"""
WENBNB Neural Engine V2 - Smart+Chill Hybrid Telegram Bot
Paste into wenbot.py, set TELEGRAM_TOKEN and other env vars, then run.
Dependencies: python-telegram-bot, requests
pip install python-telegram-bot requests
"""

try:
    import imghdr
except ModuleNotFoundError:
    import mimetypes as imghdr

try:
    import imghdr
except ModuleNotFoundError:
    import mimetypes as imghdr

# 🌐 Flask setup for Render port
from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ WENBNB Bot is alive and running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# Thread start for Flask server
threading.Thread(target=run_flask).start()


import os
import logging
import random
import requests
from html import escape
from typing import Optional

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Optional OpenAI integration (uncomment if you want OpenAI fallback)
# import openai
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# if OPENAI_API_KEY:
#     openai.api_key = OPENAI_API_KEY

# Logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("wenbnb_bot")

# Brand signature (do NOT forget to keep this)
NEURAL_TAGLINE = "🚀 Powered by WENBNB Neural Engine — AI Core Intelligence 24×7"

# ----------------------
# Utility helpers
# ----------------------
def safe_get_json(url: str, timeout: int = 6) -> Optional[dict]:
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.warning("safe_get_json failed for %s: %s", url, str(e))
        return None

def format_money(v):
    try:
        return f"${float(v):,.6f}"
    except:
        return str(v)

# ----------------------
# Commands
# ----------------------
def start(update: Update, context: CallbackContext):
    name = escape(update.effective_user.first_name or "friend")
    keyboard = [
        ["💰 Token Info", "📈 Price"],
        ["🎁 Airdrop Check", "🧠 AI Analyze"],
        ["😂 Meme Generator", "🎉 Giveaway Info"],
        ["💫 About WENBNB", "🍀 Help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    welcome_text = (
        f"<b>👋 Hey {name}!</b>\n\n"
        "🤖 <b>Welcome to WENBNB Bot</b> — your smart + chill Web3 assistant.\n\n"
        "🧠 I operate on the <b>WENBNB Neural Engine</b> — an AI Core built to empower your crypto journey 24×7.\n\n"
        "💫 What I can do:\n"
        "• 💰 Live token & BSC stats\n"
        "• 📈 Price & chart tracking\n"
        "• 🎁 Airdrop eligibility checks\n"
        "• 😂 AI meme captions\n"
        "• 🧠 AI-powered analysis & sentiment\n\n"
        f"✨ Type /help or tap a button below 👇\n\n<b>{NEURAL_TAGLINE}</b>"
    )
    update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)

def help_cmd(update: Update, context: CallbackContext):
    help_text = (
        "🧩 <b>WENBNB Bot Command Center</b>\n\n"
        "🚀 Core:\n"
        "/start — Activate the assistant\n"
        "/help — This message\n"
        "/menu — Quick button menu\n\n"
        "💰 Market & Token:\n"
        "/tokeninfo — Token stats (BscScan)\n"
        "/price — Live BNB + WENBNB price\n"
        "/aianalyze — Deep AI market analysis\n\n"
        "🎁 Community & Fun:\n"
        "/airdropcheck <wallet> — Check airdrop eligibility\n"
        "/meme — Generate a meme caption\n"
        "/giveaway_start — Start giveaway (admin)\n"
        "/giveaway_end — End giveaway (admin)\n\n"
        f"{NEURAL_TAGLINE}"
    )
    update.message.reply_text(help_text, parse_mode="HTML", disable_web_page_preview=True)

def menu_cmd(update: Update, context: CallbackContext):
    keyboard = [
        ["💰 Token Info", "📈 Price"],
        ["🎁 Airdrop Check", "🧠 AI Analyze"],
        ["😂 Meme Generator", "🎉 Giveaway Info"],
        ["💫 About WENBNB", "🍀 Help"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    menu_text = (
        "🪄 <b>WENBNB Quick Menu</b>\n\n"
        "Choose an option — each powered by the WENBNB Neural Engine.\n\n"
        f"{NEURAL_TAGLINE}"
    )
    update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode="HTML", disable_web_page_preview=True)

# Token info using BscScan (basic)
def tokeninfo(update: Update, context: CallbackContext):
    contract = os.getenv("TOKEN_CONTRACT")
    bsc_api = os.getenv("BSCSCAN_API_KEY")
    if not contract or not bsc_api:
        update.message.reply_text("⚠️ Token contract or BscScan API key not configured.")
        return
    try:
        url = f"https://api.bscscan.com/api?module=stats&action=tokensupply&contractaddress={contract}&apikey={bsc_api}"
        data = safe_get_json(url)
        total = int(data.get("result", 0)) / 1e18 if data else 0
        msg = (
            f"💎 <b>WENBNB Token Report</b>\n\n"
            f"🪙 <b>Total Supply:</b> {total:,.0f} WENBNB\n"
            f"🔗 <a href='https://bscscan.com/token/{contract}'>View on BscScan</a>\n\n"
            f"{NEURAL_TAGLINE}"
        )
        update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=False)
    except Exception as e:
        update.message.reply_text(f"⚠️ Error fetching token info: {e}")

# Price - BNB + WENBNB (CoinGecko + Binance with fallback)
def price(update: Update, context: CallbackContext):
    try:
        # Binance BNB
        bnb_json = safe_get_json("https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT")
        bnb_price = float(bnb_json["price"]) if bnb_json and "price" in bnb_json else None

        # CoinGecko WENBNB + BNB
        cg_json = safe_get_json("https://api.coingecko.com/api/v3/simple/price?ids=wenbnb,binancecoin&vs_currencies=usd&include_24hr_change=true")
        wen_price = cg_json.get("wenbnb", {}).get("usd") if cg_json else None
        wen_change = cg_json.get("wenbnb", {}).get("usd_24h_change") if cg_json else None

        if wen_price is None:
            # DexScreener fallback
            ds = safe_get_json("https://api.dexscreener.com/latest/dex/search?q=wenbnb")
            pairs = ds.get("pairs", []) if ds else []
            if pairs:
                wen_price = float(pairs[0].get("priceUsd", 0))
                source = "DexScreener"
            else:
                source = "N/A"
        else:
            source = "CoinGecko"

        text = (
            f"📊 <b>Live Market Intelligence</b>\n\n"
            f"💰 <b>BNB:</b> {format_money(bnb_price) if bnb_price else 'N/A'}\n"
            f"💎 <b>WENBNB:</b> {format_money(wen_price) if wen_price else 'N/A'}\n\n"
            f"📈 Source: {source}\n\n"
            f"{NEURAL_TAGLINE}"
        )
        update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=False)
    except Exception as e:
        update.message.reply_text(f"⚠️ Error fetching prices: {e}")

# Airdrop check (simple simulation or hook to real logic)
def airdropcheck(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("💳 Please send wallet address: /airdropcheck 0xYourAddress")
        return
    wallet = context.args[0]
    # Simple simulated logic — replace with real eligibility checks as needed
    resp = random.choice([
        "✅ Eligible — congratulations! Claim instructions will be posted soon.",
        "❌ Not eligible currently. Stay active in the community!",
        "⚠️ Pending verification — re-check in a few minutes."
    ])
    update.message.reply_text(f"🎁 <b>Airdrop Check</b>\nWallet: <code>{escape(wallet)}</code>\n\n{resp}\n\n{NEURAL_TAGLINE}", parse_mode="HTML")

# Meme generator (simple caption generator; optionally call an AI API)
def meme(update: Update, context: CallbackContext):
    samples = [
        "When BNB pumps and your coffee spills ☕📈",
        "Bought the dip. It dipped more. 😭",
        "WENBNB to the moon? Hold tight and HODL 🚀",
        "Me: 'I’ll sell at profit'. Market: 'LOL' 😂"
    ]
    caption = random.choice(samples)
    update.message.reply_text(f"😂 <b>WENBNB Meme</b>\n\n{caption}\n\n{NEURAL_TAGLINE}", parse_mode="HTML")

# Giveaway stubs (admin only enforcement should be added)
def giveaway_start(update: Update, context: CallbackContext):
    # Add admin checks here (e.g., owner IDs)
    update.message.reply_text("🎉 Giveaway started! Follow pinned message to participate.")

def giveaway_end(update: Update, context: CallbackContext):
    update.message.reply_text("🔒 Giveaway ended. Winners will be announced shortly.")

# AI analyze - hybrid, with CoinGecko & DexScreener fallback, sentiment bar
def aianalyze(update: Update, context: CallbackContext):
    query = " ".join(context.args) if context.args else ""
    try:
        update.message.reply_text("🧠 WENBNB Neural Engine — analyzing... ⏳")

        # Basic market data
        bnb_json = safe_get_json("https://api.binance.com/api/v3/ticker/24hr?symbol=BNBUSDT")
        bnb_price = float(bnb_json.get("lastPrice", 0)) if bnb_json else 0
        bnb_change = float(bnb_json.get("priceChangePercent", 0)) if bnb_json else 0

        # Try CoinGecko for a token name if query contains token symbol or 'wenbnb'
        # If query is a wallet (0x...), reply that wallet analysis is currently limited
        wen_price = None
        wen_change = 0
        source = "CoinGecko"
        cg = safe_get_json("https://api.coingecko.com/api/v3/simple/price?ids=wenbnb,binancecoin&vs_currencies=usd&include_24hr_change=true")
        if cg:
            wen_price = cg.get("wenbnb", {}).get("usd")
            wen_change = cg.get("wenbnb", {}).get("usd_24h_change", 0)

        if wen_price is None:
            # DexScreener fallback
            ds = safe_get_json("https://api.dexscreener.com/latest/dex/search?q=wenbnb")
            pairs = ds.get("pairs", []) if ds else []
            if pairs:
                wen_price = float(pairs[0].get("priceUsd", 0))
                wen_change = float(pairs[0].get("priceChange", {}).get("h24", 0) if pairs[0].get("priceChange") else 0)
                source = "DexScreener"
            else:
                source = "N/A"

        # sentiment logic (based on BNB change)
        if bnb_change > 2:
            sentiment_text = "🟢 Bullish momentum detected — accumulation likely."
        elif bnb_change < -2:
            sentiment_text = "🔴 Bearish pressure — caution advised."
        else:
            sentiment_text = "🟡 Market showing neutral/sideways action."

        # sentiment bar
        if bnb_change > 3:
            bar = "🟢🟢🟢🟢🟢 Strong Bull"
        elif bnb_change > 1:
            bar = "🟢🟢🟢🟡⚪ Moderate Bull"
        elif bnb_change < -3:
            bar = "🔴🔴🔴🔴⚪ Strong Bear"
        elif bnb_change < -1:
            bar = "🔴🔴🟠⚪⚪ Mild Bear"
        else:
            bar = "🟡🟡🟡⚪⚪ Neutral"

        analysis = (
            "<b>🧠 WENBNB Neural Market Analysis</b>\n\n"
            f"💰 <b>BNB:</b> {format_money(bnb_price)} ({bnb_change:+.2f}% 24h)\n"
            f"💎 <b>WENBNB:</b> {format_money(wen_price) if wen_price else 'N/A'} ({wen_change:+.2f}% 24h)\n"
            f"📈 Source: {source}\n\n"
            f"{sentiment_text}\n\n"
            f"📊 <b>AI Sentiment Bar:</b>\n{bar}\n\n"
            f"🤖 AI Insight: Combining exchange trends, volume & momentum.\n\n"
            f"{NEURAL_TAGLINE}"
        )
        update.message.reply_text(analysis, parse_mode="HTML", disable_web_page_preview=True)
    except Exception as e:
        update.message.reply_text(f"⚠️ Neural Engine failed to analyze data.\n\n<b>Error:</b> {escape(str(e))}", parse_mode="HTML")

# About
def about(update: Update, context: CallbackContext):
    text = (
        "<b>WENBNB Ecosystem</b>\n\n"
        "WENBNB is a hybrid meme-AI project on BSC — built for community, memes, and utility.\n\n"
        f"{NEURAL_TAGLINE}"
    )
    update.message.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)

# ----------------------
# AI Auto Context Reply (intent detection)
# ----------------------
def ai_auto_reply(update: Update, context: CallbackContext):
    # Hybrid behavior: adjust tone for groups vs private chat
    chat_type = update.effective_chat.type
    text = update.message.text or ""
    text_lower = text.lower()

    # Priority intent detection
    if any(k in text_lower for k in ["price", "bnb", "wenbnb", "chart", "token"]):
        # trigger price command
        context.bot.send_message(chat_id=update.effective_chat.id, text="/price")
        return

    if any(k in text_lower for k in ["airdrop", "wallet", "eligible", "claim"]):
        context.bot.send_message(chat_id=update.effective_chat.id, text="/airdropcheck")
        return

    if any(k in text_lower for k in ["analyze", "analysis", "ai", "sentiment", "trend"]):
        # if there's a specific token or wallet, pass as args when possible
        if "0x" in text_lower:
            # pass wallet as argument to aianalyze
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"/aianalyze {text}")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="/aianalyze")
        return

    if any(k in text_lower for k in ["meme", "funny", "caption", "joke"]):
        context.bot.send_message(chat_id=update.effective_chat.id, text="/meme")
        return

    if any(k in text_lower for k in ["about", "wenbnb", "what is wenbnb", "info"]):
        context.bot.send_message(chat_id=update.effective_chat.id, text="/about")
        return

    # Fallback: Use local witty replies or OpenAI fallback if configured
    fallback_options = [
        "🤖 Nice question — I can check that. Try phrasing like 'price', 'analyze', or 'airdrop'.",
        "🧠 I’m here — ask me about prices, airdrops, or say 'analyze' to get insights.",
        "✨ Want a meme? Type 'meme' or ask for token info."
    ]
    # If OpenAI is configured and you'd like a conversational fallback, call it here (optional)
    # if OPENAI_API_KEY:
    #     try:
    #         ai_resp = openai.Completion.create(
    #             engine="text-davinci-003",
    #             prompt=f"User asked: {text}\nAnswer in a friendly, concise style about crypto.",
    #             max_tokens=120
    #         )
    #         reply = ai_resp.choices[0].text.strip()
    #         context.bot.send_message(chat_id=update.effective_chat.id, text=reply)
    #         return
    #     except Exception as e:
    #         log.warning("OpenAI fallback failed: %s", e)

    context.bot.send_message(chat_id=update.effective_chat.id, text=random.choice(fallback_options))

# ----------------------
# Register handlers
# ----------------------
def register_menu_handlers(dp):
    # Core
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_cmd))
    dp.add_handler(CommandHandler("menu", menu_cmd))

    # AI + API commands
    dp.add_handler(CommandHandler("tokeninfo", tokeninfo))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("airdropcheck", airdropcheck))
    dp.add_handler(CommandHandler("meme", meme))
    dp.add_handler(CommandHandler("giveaway_start", giveaway_start))
    dp.add_handler(CommandHandler("giveaway_end", giveaway_end))
    dp.add_handler(CommandHandler("aianalyze", aianalyze))
    dp.add_handler(CommandHandler("about", about))

    # Button interactions (UI shortcuts)
    dp.add_handler(MessageHandler(Filters.regex(r"^💰 Token Info$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/tokeninfo")))
    dp.add_handler(MessageHandler(Filters.regex(r"^📈 Price$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/price")))
    dp.add_handler(MessageHandler(Filters.regex(r"^🎁 Airdrop Check$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/airdropcheck")))
    dp.add_handler(MessageHandler(Filters.regex(r"^😂 Meme Generator$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/meme")))
    dp.add_handler(MessageHandler(Filters.regex(r"^🎉 Giveaway Info$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/giveaway_start")))
    dp.add_handler(MessageHandler(Filters.regex(r"^🧠 AI Analyze$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/aianalyze")))
    dp.add_handler(MessageHandler(Filters.regex(r"^💫 About WENBNB$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/about")))
    dp.add_handler(MessageHandler(Filters.regex(r"^🍀 Help$"), lambda u, c: c.bot.send_message(u.effective_chat.id, text="/help")))

    # Auto context replies for any plain text
    from plugins.ai_auto_reply import ai_auto_reply
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ai_auto_reply))


    log.info("✅ Handlers registered")

# ----------------------
# Main runner
# ----------------------
def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        log.error("TELEGRAM_TOKEN not set in environment variables.")
        return

    updater = Updater(token=token, use_context=True)
    dp = updater.dispatcher

    register_menu_handlers(dp)

    # Start
    updater.start_polling()
    log.info("WENBNB Neural Engine bot started. %s", NEURAL_TAGLINE)
    updater.idle()

if __name__ == "__main__":
    main()



