"""
🎁 WENBNB Airdrop Intelligence v3.0 — Multi-Chain Adaptive Module
Auto-detects token airdrops and holder distribution across BSC, ETH, ARB, and BASE.
Falls back to DexScreener if chain API fails.
🔥 Powered by WENBNB Neural Engine — Market Intelligence 24×7
"""

import os
import requests
from telegram.ext import CommandHandler

BRAND_TAG = "🎁 Powered by WENBNB Neural Engine — Airdrop Intelligence v3.0 💫"

# === CHAIN ENDPOINT MAP ===
CHAIN_APIS = {
    "bsc": "https://api.bscscan.com/api",
    "eth": "https://api.etherscan.io/api",
    "arb": "https://api.arbiscan.io/api",
    "base": "https://api.basescan.org/api",
}

# === TRY MULTI-CHAIN FETCH ===
def fetch_airdrop_data(contract_address):
    for chain, base_url in CHAIN_APIS.items():
        api_key = os.getenv(f"{chain.upper()}SCAN_API_KEY") or os.getenv("BSCSCAN_API_KEY")
        if not api_key:
            continue

        url = (
            f"{base_url}?module=token&action=tokenholderlist"
            f"&contractaddress={contract_address}&apikey={api_key}"
        )

        try:
            r = requests.get(url, timeout=10)
            data = r.json()

            if data.get("status") == "1":
                holders = len(data.get("result", []))
                return f"✅ <b>{chain.upper()}:</b> Airdrop active — {holders} holders detected!"
            elif data.get("status") == "0" and data.get("message") == "NOTOK":
                continue  # Try next chain
        except Exception:
            continue

    # Fallback — DexScreener
    try:
        dex_url = f"https://api.dexscreener.io/latest/dex/search?q={contract_address}"
        dex_data = requests.get(dex_url, timeout=8).json()
        pairs = dex_data.get("pairs", [])
        if pairs:
            token_name = pairs[0].get("baseToken", {}).get("name", "Unknown Token")
            liquidity = pairs[0].get("liquidity", {}).get("usd", "N/A")
            return (
                f"💎 Fallback data (DexScreener):\n"
                f"<b>{token_name}</b> — Liquidity ${liquidity}\n\n"
                f"⚠️ Airdrop data unavailable on chain scanners.\n\n{BRAND_TAG}"
            )
    except Exception as e:
        return f"⚠️ DexScreener fetch failed: {e}"

    return (
        f"⚠️ Airdrop data temporarily unavailable — please try again later.\n\n{BRAND_TAG}"
    )

# === COMMAND HANDLER ===
def airdrop_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        args = context.args
        token_address = args[0] if args else os.getenv("WEN_TOKEN_ADDRESS")

        if not token_address:
            update.message.reply_text(
                "⚠️ No token specified and no default WENBNB address found.", parse_mode="HTML"
            )
            return

        result = fetch_airdrop_data(token_address)
        update.message.reply_text(result, parse_mode="HTML")

    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {str(e)}", parse_mode="HTML")

# === REGISTER FOR PLUGIN MANAGER ===
def register(dispatcher):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdrop_cmd))
    print("🎁 Loaded plugin: airdrop_check.py (Multi-Chain Airdrop Intelligence Module)")
