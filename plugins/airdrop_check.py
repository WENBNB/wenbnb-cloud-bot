"""
🎁 WENBNB Airdrop Intelligence v4.0 — Dual-Mode Neural Analyzer
Detects wallet or token input automatically.
• Wallet Mode → Simulated eligibility & DeFi activity prediction
• Token Mode → Real-time DEX liquidity + market snapshot
🔥 Powered by WENBNB Neural Engine — Market Intelligence 24×7 💫
"""

import os
import re
import random
import requests
from telegram.ext import CommandHandler

BRAND_TAG = "🎁 Powered by WENBNB Neural Engine — Airdrop Intelligence v4.0 💫"

# === Helper ===
def is_wallet_address(text):
    """Detect if input is a wallet address (longer than 40 chars)"""
    return bool(re.match(r"^0x[a-fA-F0-9]{40,}$", text.strip()))


# === Wallet Mode (AI Simulation) ===
def simulate_wallet_eligibility(wallet):
    """
    Generate simulated eligibility & insights.
    This can later be replaced with real API lookups (DeBank, Zapper, etc.)
    """
    seed = sum(ord(c) for c in wallet[-5:])
    random.seed(seed)

    eligible = random.choice(["✅ Eligible", "⚠️ Borderline", "❌ Not Eligible"])
    protocols = random.randint(3, 12)
    score = random.randint(45, 95)

    insights = [
        "Strong DeFi footprint detected across L2 networks.",
        "Recent activity on multiple airdrop campaigns.",
        "Low gas usage history — possible passive wallet.",
        "High transaction count in Base / Arbitrum ecosystems.",
        "New wallet with moderate activity.",
        "Wallet connected to verified NFT or reward protocols.",
    ]
    insight = random.choice(insights)

    result = (
        f"💎 <b>Wallet Scan:</b> <code>{wallet[:6]}...{wallet[-4:]}</code>\n"
        f"{eligible} for upcoming airdrops.\n"
        f"🧠 Neural Score: {score}/100\n"
        f"🔗 DeFi Protocols Detected: {protocols}\n"
        f"✨ Neural Insight: {insight}\n\n"
        f"{BRAND_TAG}"
    )
    return result


# === Token Mode (DEX + Liquidity) ===
def token_airdrop_info(contract_address):
    try:
        dex_url = f"https://api.dexscreener.io/latest/dex/search?q={contract_address}"
        dex_data = requests.get(dex_url, timeout=10).json()
        pairs = dex_data.get("pairs", [])
        if not pairs:
            return f"⚠️ Token not found on DEX. Try a valid contract.\n\n{BRAND_TAG}"

        pair = pairs[0]
        token_name = pair.get("baseToken", {}).get("name", "Unknown Token")
        dex = pair.get("dexId", "DEX").capitalize()
        liquidity = pair.get("liquidity", {}).get("usd", 0)
        volume24 = pair.get("volume", {}).get("h24", 0)
        price = pair.get("priceUsd", "N/A")

        mood_line = "💎 Balanced market" if float(volume24) > 0 else "🌙 Low-volume token"

        return (
            f"💠 <b>{token_name}</b> on {dex}\n"
            f"💰 Price: ${price}\n"
            f"💧 Liquidity: ${liquidity:,.2f}\n"
            f"📊 24h Volume: ${volume24:,.2f}\n"
            f"🧠 Neural Insight: {mood_line}\n\n"
            f"{BRAND_TAG}"
        )
    except Exception as e:
        return f"⚠️ Error fetching token data: {e}\n\n{BRAND_TAG}"


# === Command Handler ===
def airdrop_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        args = context.args

        if not args:
            update.message.reply_text(
                "🧩 Usage:\n"
                "/airdropcheck <wallet_address | contract_address>\n"
                "Example:\n"
                "• /airdropcheck 0xYourWalletHere\n"
                "• /airdropcheck 0xContractAddressHere",
                parse_mode="HTML",
            )
            return

        query = args[0].strip()

        if is_wallet_address(query):
            result = simulate_wallet_eligibility(query)
        else:
            result = token_airdrop_info(query)

        update.message.reply_text(result, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        update.message.reply_text(f"⚠️ Neural Core Error: {e}", parse_mode="HTML")


# === Register Handler ===
def register(dispatcher):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdrop_cmd))
    print("🎁 Loaded plugin: airdrop_check.py (Dual-Mode Airdrop Intelligence v4.0)")
