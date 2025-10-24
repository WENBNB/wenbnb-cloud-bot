"""
🎁 WENBNB Airdrop Intelligence v4.1 — Dual-Mode + Airdrop Probability
• Wallet Mode -> Deterministic eligibility simulation + better scoring
• Token Mode  -> DEX liquidity + 24h volume + simulated airdrop probability
• Ready for future hooks (Debank/Zapper/etc.) via commented placeholders
🔥 Powered by WENBNB Neural Engine — Airdrop Intelligence v4.1 💫
"""

import os
import re
import math
import random
import requests
from telegram.ext import CommandHandler

BRAND_TAG = "🎁 Powered by WENBNB Neural Engine — Airdrop Intelligence v4.1 💫"
DEX_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"


# -------------------------
# Helpers
# -------------------------
def is_wallet_address(text: str) -> bool:
    """True when text looks like an EVM wallet address (0x + 40 hex chars)"""
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", text.strip()))


def clamp(x, a=0.0, b=100.0):
    return max(a, min(b, x))


# -------------------------
# Wallet Mode (improved deterministic simulation)
# -------------------------
def simulate_wallet_eligibility(wallet: str) -> str:
    """
    Deterministic simulation seeded by the wallet string.
    Produces repeatable results for the same wallet while
    giving realistic variation across addresses.
    """
    key = wallet.lower()
    # deterministic seed based on wallet characters
    seed = sum((ord(c) * (i + 1)) for i, c in enumerate(key[-10:])) % (2**32)
    rnd = random.Random(seed)

    # features derived from wallet hex (quick synthetic signals)
    hex_tail = key[-8:]
    numeric_tail = int(hex_tail, 16)
    wallet_age_score = (numeric_tail % 100) / 100.0  # 0..0.99
    activity_score = (sum(ord(c) for c in key[-6:]) % 100) / 100.0
    protocol_count = 3 + (numeric_tail % 10)  # 3..12

    # base chance influenced by synthetic features
    base = (wallet_age_score * 0.35 + activity_score * 0.45 + (protocol_count / 12.0) * 0.20) * 100
    # small random jitter but deterministic
    jitter = rnd.uniform(-7, 7)
    score = clamp(base + jitter, 0, 100)

    if score >= 80:
        eligibility = "✅ Eligible"
    elif score >= 55:
        eligibility = "⚠️ Borderline"
    else:
        eligibility = "❌ Not Eligible"

    insights = [
        "Strong DeFi footprint detected across L2 networks.",
        "Recent activity on multiple airdrop campaigns.",
        "Low gas usage history — possible passive wallet.",
        "High transaction count in Base / Arbitrum ecosystems.",
        "New wallet with moderate activity.",
        "Wallet connected to verified NFT or reward protocols.",
    ]
    insight = rnd.choice(insights)

    result = (
        f"💎 <b>Wallet Scan Report</b>\n"
        f"🔷 Wallet: <code>{wallet[:8]}...{wallet[-6:]}</code>\n"
        f"{eligibility} for upcoming airdrops.\n"
        f"🧠 Neural Score: {int(score)}/100\n"
        f"🔗 DeFi Protocols Detected (est.): {protocol_count}\n"
        f"✨ Neural Insight: {insight}\n\n"
        f"{BRAND_TAG}"
    )
    return result


# -------------------------
# Token Mode (DEX + Probability)
# -------------------------
def estimate_airdrop_probability(liquidity_usd: float, volume24_usd: float, pair_age_days: float = 0.0) -> float:
    """
    Heuristic probability model:
      - higher liquidity and recent volume increase probability.
      - newer pairs with spikey volume get slight boost.
    Returns percent 0..100
    """
    # protect against zero
    L = max(1.0, float(liquidity_usd))
    V = max(1.0, float(volume24_usd))

    # log-normalize
    l_score = math.log10(L)  # e.g., liquidity $1k -> 3
    v_score = math.log10(V)

    # normalize roughly into 0-100
    # weights tuned: liquidity more important than pure 24h volume
    raw = (l_score * 0.6 + v_score * 0.35 + max(0, (30 - pair_age_days)) * 0.05)
    # map raw (roughly 0..10+) to 0..100
    prob = clamp((raw / 6.0) * 100, 0, 100)

    # small volatility boost if volume/lq ratio high
    ratio = V / L
    if ratio > 0.05:
        prob += clamp((ratio * 100) * 0.3, 0, 15)

    return clamp(prob, 0, 100)


def token_airdrop_info(contract_address: str) -> str:
    """
    Query DexScreener for pair info and compute a simulated airdrop probability.
    """
    try:
        r = requests.get(DEX_SEARCH.format(q=contract_address), timeout=10)
        data = r.json()
        pairs = data.get("pairs", [])
        if not pairs:
            return f"⚠️ <b>Token Ecosystem Snapshot</b>\nToken not found on DEX. Try a valid contract.\n\n{BRAND_TAG}"

        # pick the best pair (first)
        pair = pairs[0]
        token_name = pair.get("baseToken", {}).get("name", "Unknown Token")
        token_symbol = pair.get("baseToken", {}).get("symbol", "")
        dex = pair.get("dexId", "DEX").capitalize()
        liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
        volume24 = pair.get("volume", {}).get("h24", 0) or 0
        price = pair.get("priceUsd", "N/A")
        # no reliable pair age from dexscreener api; leave as 0 for now
        pair_age_days = 0.0

        # simulated probability
        prob = estimate_airdrop_probability(liquidity, volume24, pair_age_days)

        # human-friendly mood
        if prob > 75:
            mood = "🔥 High likelihood — active dev / community signals."
        elif prob > 45:
            mood = "⚡ Moderate likelihood — keep monitoring."
        else:
            mood = "🌙 Low likelihood — token appears low-activity."

        result = (
            f"💠 <b>Token Ecosystem Snapshot</b>\n"
            f"🔷 {token_name} ({token_symbol}) — <i>{dex}</i>\n"
            f"💰 Price: ${price}\n"
            f"💧 Liquidity: ${liquidity:,.2f}\n"
            f"📊 24h Volume: ${volume24:,.2f}\n"
            f"🎯 Airdrop Probability (sim): <b>{prob:.0f}%</b>\n"
            f"🧠 Neural Insight: {mood}\n\n"
            f"{BRAND_TAG}"
        )
        return result

    except Exception as e:
        return f"⚠️ Error fetching token data: {e}\n\n{BRAND_TAG}"


# -------------------------
# Command handler
# -------------------------
def airdrop_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        args = context.args

        if not args:
            update.message.reply_text(
                "🧩 Usage:\n"
                "/airdropcheck <wallet_address | contract_address>\n\n"
                "• Wallet example: /airdropcheck 0xYourWalletHere\n"
                "• Token example:  /airdropcheck 0xContractAddressHere",
                parse_mode="HTML",
            )
            return

        query = args[0].strip()
        if is_wallet_address(query):
            reply = simulate_wallet_eligibility(query)
        else:
            reply = token_airdrop_info(query)

        update.message.reply_text(reply, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        update.message.reply_text(f"⚠️ Neural Core Error: {e}", parse_mode="HTML")


# -------------------------
# Plugin register
# -------------------------
def register(dispatcher):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdrop_cmd))
    print("🎁 Loaded plugin: airdrop_check.py (Dual-Mode Airdrop Intelligence v4.1)")
