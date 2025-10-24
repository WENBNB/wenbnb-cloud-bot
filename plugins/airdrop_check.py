"""
🎁 WENBNB Airdrop Intelligence v3.5 — Hybrid Multi-Source Engine
✔ Works even if BscScan 'tokenholderlist' fails.
✔ Tracks token distribution via transfers + DexScreener fallback.
🔥 Powered by WENBNB Neural Engine — Market Intelligence 24×7 ⚡
"""

import os
import requests
from telegram.ext import CommandHandler

BRAND_TAG = "🎁 Powered by WENBNB Neural Engine — Airdrop Intelligence v3.5 💫"

# === MAIN CHAIN MAP ===
SCAN_APIS = {
    "bsc": "https://api.bscscan.com/api",
    "eth": "https://api.etherscan.io/api",
    "arb": "https://api.arbiscan.io/api",
    "base": "https://api.basescan.org/api",
}

# === SMART FETCH ===
def fetch_airdrop_data(contract_address):
    result_lines = []
    found_any = False

    # --- Try across chains ---
    for chain, base_url in SCAN_APIS.items():
        api_key = os.getenv(f"{chain.upper()}SCAN_API_KEY") or os.getenv("BSCSCAN_API_KEY")
        if not api_key:
            continue

        # use transfers instead of holderlist (more reliable)
        url = (
            f"{base_url}?module=account&action=tokentx"
            f"&contractaddress={contract_address}&page=1&offset=20&sort=desc&apikey={api_key}"
        )

        try:
            r = requests.get(url, timeout=10)
            data = r.json()

            if data.get("status") == "1" and data.get("result"):
                txs = data["result"]
                recent = txs[:5]
                unique_wallets = {tx["to"].lower() for tx in txs}
                found_any = True

                result_lines.append(
                    f"✅ <b>{chain.upper()}:</b> {len(unique_wallets)} holders (recent {len(recent)} airdrop txns)"
                )
            else:
                continue
        except Exception:
            continue

    # --- Fallback DexScreener ---
    if not found_any:
        try:
            dex_url = f"https://api.dexscreener.io/latest/dex/search?q={contract_address}"
            dex_data = requests.get(dex_url, timeout=8).json()
            pairs = dex_data.get("pairs", [])
            if pairs:
                token_name = pairs[0].get("baseToken", {}).get("name", "Unknown Token")
                liquidity = pairs[0].get("liquidity", {}).get("usd", "N/A")
                return (
                    f"💎 <b>{token_name}</b> — live on DEX with liquidity ${liquidity}\n"
                    f"⚠️ No direct airdrop data found.\n\n{BRAND_TAG}"
                )
        except Exception as e:
            return f"⚠️ Dex fallback failed: {e}"

    if found_any:
        return "\n".join(result_lines) + f"\n\n{BRAND_TAG}"
    else:
        return f"⚠️ Airdrop data unavailable — check contract activity manually.\n\n{BRAND_TAG}"

# === COMMAND HANDLER ===
def airdrop_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        args = context.args
        token_address = args[0] if args else os.getenv("WEN_TOKEN_ADDRESS")

        if not token_address:
            update.message.reply_text(
                "⚠️ No token specified and no default WENBNB address set.",
                parse_mode="HTML"
            )
            return

        result = fetch_airdrop_data(token_address)
        update.message.reply_text(result, parse_mode="HTML")

    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {e}", parse_mode="HTML")

# === REGISTER FOR PLUGIN MANAGER ===
def register(dispatcher):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdrop_cmd))
    print("🎁 Loaded plugin: airdrop_check.py (Hybrid Airdrop Intelligence Module)")
