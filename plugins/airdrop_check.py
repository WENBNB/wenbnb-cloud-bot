"""
🎁 WENBNB Airdrop Check Plugin v2.0
Auto-detects token airdrops and holder distribution stats
Integrated with BscScan + Neural Engine Insight
"""

import os
import requests
from telegram.ext import CommandHandler

BRAND_TAG = "🎁 Powered by WENBNB Neural Engine — Airdrop Intelligence Module 💫"


def check_airdrop_status(contract_address):
    bscscan_api = os.getenv("BSCSCAN_API_KEY")
    if not bscscan_api:
        return "❌ BscScan API key not configured."

    url = (
        f"https://api.bscscan.com/api?module=token&action=tokenholderlist"
        f"&contractaddress={contract_address}&apikey={bscscan_api}"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("status") == "1":
            holders = len(data.get("result", []))
            return f"✅ Airdrop Active — {holders} holders detected.\n\n{BRAND_TAG}"
        else:
            return f"⚠️ Unable to fetch airdrop data: {data.get('message', 'Unknown error')}"
    except Exception as e:
        return f"⚠️ Error fetching data: {e}"


def airdrop_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        args = context.args

        token_address = args[0] if args else os.getenv("WEN_TOKEN_ADDRESS")
        if not token_address:
            update.message.reply_text("⚠️ No token specified and default WENBNB address not configured.")
            return

        result = check_airdrop_status(token_address)
        update.message.reply_text(result, parse_mode="HTML")

    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {str(e)}", parse_mode="HTML")


# === Register Handler for Plugin Manager ===
def register(dispatcher):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdrop_cmd))
    print("🎁 Loaded plugin: airdrop_check.py (Airdrop Intelligence Module)")
