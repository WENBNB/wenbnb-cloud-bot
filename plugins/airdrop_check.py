"""
🎁 WENBNB Airdrop Intelligence v3.9 — Synthetic Whale Analyzer
Estimates token distribution using liquidity pool data + DEX metrics.
✔ Works across BSC, ETH, ARB, BASE
✔ DexScreener fallback with synthetic whale/retail ratio
🔥 Powered by WENBNB Neural Engine — Market Intelligence 24×7 💫
"""

import os
import requests
from telegram.ext import CommandHandler

BRAND_TAG = "🎁 Powered by WENBNB Neural Engine — Airdrop Intelligence v3.9 💫"

SCAN_APIS = {
    "bsc": "https://api.bscscan.com/api",
    "eth": "https://api.etherscan.io/api",
    "arb": "https://api.arbiscan.io/api",
    "base": "https://api.basescan.org/api",
}


def analyze_distribution_synthetic(liquidity_usd, volume24_usd):
    """Estimate whale vs retail ratio when holder data missing."""
    if not liquidity_usd or not volume24_usd:
        return "⚠️ Insufficient data for synthetic analysis."

    ratio = float(liquidity_usd) / float(volume24_usd)
    if ratio > 5:
        mood = "🐋 Heavy whale control detected — low retail rotation."
    elif ratio > 2:
        mood = "🦈 Moderate whale influence — steady but cautious market."
    elif ratio > 1:
        mood = "💎 Balanced distribution — healthy liquidity."
    else:
        mood = "🌱 High retail activity — fresh inflow and strong interest."

    return mood


def fetch_airdrop_data(contract_address):
    found_any = False
    report_lines = []

    for chain, base_url in SCAN_APIS.items():
        api_key = os.getenv(f"{chain.upper()}SCAN_API_KEY") or os.getenv("BSCSCAN_API_KEY")
        if not api_key:
            continue

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
                unique_wallets = len(set(tx["to"].lower() for tx in txs))
                recent_tx = len(txs)
                report_lines.append(
                    f"💠 <b>{chain.upper()}</b> — {recent_tx} recent transfers across {unique_wallets} wallets\n"
                    f"🧠 Neural Insight: Active chain with healthy user flow."
                )
        except Exception:
            continue

    # === DexScreener fallback ===
    try:
        dex_url = f"https://api.dexscreener.io/latest/dex/search?q={contract_address}"
        dex_data = requests.get(dex_url, timeout=8).json()
        pairs = dex_data.get("pairs", [])
        if pairs:
            token_name = pairs[0].get("baseToken", {}).get("name", "Unknown Token")
            liquidity = pairs[0].get("liquidity", {}).get("usd", 0)
            volume24 = pairs[0].get("volume", {}).get("h24", 1)
            dex_name = pairs[0].get("dexId", "DEX").capitalize()

            mood = analyze_distribution_synthetic(liquidity, volume24)
            return (
                f"💎 <b>{token_name}</b> — live on {dex_name}\n"
                f"💧 Liquidity: ${liquidity:,.2f}\n"
                f"📊 24h Volume: ${volume24:,.2f}\n"
                f"🧠 Neural Insight: {mood}\n\n{BRAND_TAG}"
            )
    except Exception as e:
        return f"⚠️ Dex fallback failed: {e}"

    if found_any:
        return "\n".join(report_lines) + f"\n\n{BRAND_TAG}"
    else:
        return f"⚠️ Airdrop data unavailable — fallback analysis only.\n\n{BRAND_TAG}"


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


def register(dispatcher):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdrop_cmd))
    print("🎁 Loaded plugin: airdrop_check.py (Synthetic Whale Analyzer v3.9)")
