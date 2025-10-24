"""
🎁 WENBNB Airdrop Intelligence v3.8 — Whale & Retail Distribution Analyzer
Tracks top wallets, holder concentration, and gives real-time neural insights.
✔ Works across BSC, ETH, ARB, BASE
✔ DexScreener fallback for liquidity and DEX pairs
🔥 Powered by WENBNB Neural Engine — Market Intelligence 24×7 💫
"""

import os
import requests
from telegram.ext import CommandHandler

BRAND_TAG = "🎁 Powered by WENBNB Neural Engine — Airdrop Intelligence v3.8 💫"

# === CHAIN ENDPOINTS ===
SCAN_APIS = {
    "bsc": "https://api.bscscan.com/api",
    "eth": "https://api.etherscan.io/api",
    "arb": "https://api.arbiscan.io/api",
    "base": "https://api.basescan.org/api",
}


# === DISTRIBUTION ANALYZER ===
def analyze_distribution(transactions):
    wallet_balances = {}

    for tx in transactions:
        to_addr = tx.get("to", "").lower()
        value = float(tx.get("value", 0)) / (10 ** 18)  # assuming 18 decimals
        wallet_balances[to_addr] = wallet_balances.get(to_addr, 0) + value

    # Sort wallets
    sorted_wallets = sorted(wallet_balances.items(), key=lambda x: x[1], reverse=True)
    total_value = sum(wallet_balances.values()) or 1
    top5 = sorted_wallets[:5]

    # Calculate percentages
    whale_share = sum(v for _, v in top5) / total_value * 100
    retail_share = 100 - whale_share

    # Generate insights
    if whale_share > 80:
        mood = "⚠️ High whale control — risky distribution."
    elif whale_share > 50:
        mood = "🦈 Moderate whale presence — watch for volatility."
    elif whale_share > 25:
        mood = "💎 Balanced distribution — good mix of whales and retail."
    else:
        mood = "🌱 Retail-dominated distribution — healthy and decentralized."

    return whale_share, retail_share, mood


# === CORE DATA FETCH ===
def fetch_airdrop_data(contract_address):
    found_any = False
    report_lines = []

    for chain, base_url in SCAN_APIS.items():
        api_key = os.getenv(f"{chain.upper()}SCAN_API_KEY") or os.getenv("BSCSCAN_API_KEY")
        if not api_key:
            continue

        # Fetch token transactions instead of holderlist
        url = (
            f"{base_url}?module=account&action=tokentx"
            f"&contractaddress={contract_address}&page=1&offset=100&sort=desc&apikey={api_key}"
        )

        try:
            r = requests.get(url, timeout=10)
            data = r.json()

            if data.get("status") == "1" and data.get("result"):
                txs = data["result"]
                found_any = True

                # Analyze distribution
                whale, retail, mood = analyze_distribution(txs)

                report_lines.append(
                    f"💠 <b>{chain.upper()}</b> — Airdrop Activity Detected\n"
                    f"🐋 Whale Share: {whale:.2f}%\n"
                    f"👥 Retail Share: {retail:.2f}%\n"
                    f"🧠 Neural Insight: {mood}\n"
                )
        except Exception:
            continue

    # === DexScreener fallback ===
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
        return "\n".join(report_lines) + f"\n{BRAND_TAG}"
    else:
        return f"⚠️ Airdrop data unavailable — no recent transactions found.\n\n{BRAND_TAG}"


# === COMMAND HANDLER ===
def airdrop_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        args = context.args
        token_address = args[0] if args else os.getenv("WEN_TOKEN_ADDRESS")

        if not token_address:
            update.message.reply_text(
                "⚠️ No token specified and no default WENBNB address set.",
                parse_mode="HTML",
            )
            return

        result = fetch_airdrop_data(token_address)
        update.message.reply_text(result, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        update.message.reply_text(f"⚠️ Error: {e}", parse_mode="HTML")


# === REGISTER HANDLER ===
def register(dispatcher):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdrop_cmd))
    print("🎁 Loaded plugin: airdrop_check.py (Whale Distribution Intelligence v3.8)")
