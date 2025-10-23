import os
import requests
from datetime import datetime

# ✅ WENBNB Airdrop Check Plugin
# Automatically checks token airdrop or distribution activity

def check_airdrop_status(contract_address):
    """Fetch basic token airdrop status or holder summary"""
    bscscan_api = os.getenv("BSCSCAN_API_KEY")
    if not bscscan_api:
        return "❌ BscScan API key not configured."

    url = f"https://api.bscscan.com/api?module=token&action=tokenholderlist&contractaddress={contract_address}&apikey={bscscan_api}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("status") == "1":
            holders = len(data.get("result", []))
            return f"✅ Airdrop active! {holders} holders detected."
        else:
            return f"⚠️ Unable to fetch airdrop data: {data.get('message', 'Unknown error')}"

    except Exception as e:
        return f"⚠️ Error fetching data: {e}"

def run(update, context):
    """Triggered by /airdrop command"""
    token_address = os.getenv("WEN_TOKEN_ADDRESS")
    if not token_address:
        update.message.reply_text("⚠️ Token address not set in environment variables.")
        return

    result = check_airdrop_status(token_address)
    update.message.reply_text(result)
