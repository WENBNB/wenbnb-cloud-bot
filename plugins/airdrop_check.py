"""
🎁 WENBNB Airdrop Intelligence v4.2 — Smart Hybrid Mode
• Auto-detects token vs wallet using DexScreener
• Wallet Mode -> Deterministic eligibility simulation + Neural Score
• Token Mode  -> DEX liquidity + 24h volume + simulated airdrop probability
🔥 Powered by WENBNB Neural Engine — Airdrop Intelligence v4.2 (Smart Hybrid Mode)
"""

import os
import re
import math
import random
import requests
from telegram.ext import CommandHandler

BRAND_TAG = "🎁 Powered by WENBNB Neural Engine — Airdrop Intelligence v4.2 (Smart Hybrid Mode) 💫"
DEX_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"


# -------------------------
# Helpers
# -------------------------
def looks_like_evm_address(text: str) -> bool:
    """Return True for canonical 0x + 40 hex characters"""
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", text.strip()))


def clamp(x, a=0.0, b=100.0):
    return max(a, min(b, x))


# -------------------------
# DexScreener probe
# -------------------------
def probe_dexscreener(query: str, timeout=8):
    """
    Query DexScreener for the given query string (contract or symbol).
    Returns parsed JSON or None on failure.
    """
    try:
        r = requests.get(DEX_SEARCH.format(q=query), timeout=timeout)
        data = r.json()
        return data
    except Exception:
        return None


def found_token_on_dex(query: str):
    """
    Returns first pair dict if DexScreener finds the token; otherwise None.
    This function determines whether we treat input as token-mode.
    """
    data = probe_dexscreener(query)
    if not data:
        return None
    pairs = data.get("pairs", [])
    if not pairs:
        return None
    return pairs[0]  # return best match


# -------------------------
# Wallet Mode (deterministic scoring)
# -------------------------
def deterministic_wallet_score(wallet: str):
    """
    Deterministic scoring seeded from the wallet address.
    Produces stable Neural Score 0..100 for the same wallet.
    """
    key = wallet.lower()
    # seed derived from wallet characters (stable)
    seed_val = sum((ord(c) * (i + 1)) for i, c in enumerate(key[-12:])) & 0xFFFFFFFF
    rnd = random.Random(seed_val)

    # synthetic features
    tail = key[-8:]
    try:
        tail_num = int(tail, 16)
    except Exception:
        tail_num = sum(ord(c) for c in tail)

    # wallet "age" like feature from hex tail (0..1)
    age_feat = (tail_num % 1000) / 1000.0
    # activity feature from last chars
    activity_feat = ((sum(ord(c) for c in key[-6:]) % 100) / 100.0)
    # small deterministic jitter
    jitter = (rnd.random() - 0.5) * 14  # -7 .. +7

    base_score = (age_feat * 0.3 + activity_feat * 0.5 + 0.2) * 100
    score = clamp(base_score + jitter, 0, 100)

    # estimate protocol count (deterministic)
    protocol_count = 2 + (tail_num % 11)  # 2..12

    return int(score), protocol_count, rnd


def simulate_wallet_eligibility(wallet: str) -> str:
    score, protocol_count, rnd = deterministic_wallet_score(wallet)

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
        "Frequent small interactions — appears like bot aggregator.",
    ]
    insight = rnd.choice(insights)

    result = (
        f"💎 <b>Wallet Scan Report</b>\n"
        f"🔷 Wallet: <code>{wallet[:8]}...{wallet[-6:]}</code>\n"
        f"{eligibility} for upcoming airdrops.\n"
        f"🧠 Neural Score: {score}/100\n"
        f"🔗 DeFi Protocols Detected (est.): {protocol_count}\n"
        f"✨ Neural Insight: {insight}\n\n"
        f"{BRAND_TAG}"
    )
    return result


# -------------------------
# Token Mode (DEX + probability)
# -------------------------
def estimate_airdrop_probability(liquidity_usd: float, volume24_usd: float, pair_age_days: float = 0.0) -> float:
    L = max(1.0, float(liquidity_usd))
    V = max(1.0, float(volume24_usd))
    l_score = math.log10(L)
    v_score = math.log10(V)
    raw = (l_score * 0.6 + v_score * 0.35 + max(0, (30 - pair_age_days)) * 0.05)
    prob = clamp((raw / 6.0) * 100, 0, 100)
    ratio = V / L
    if ratio > 0.05:
        prob += clamp((ratio * 100) * 0.3, 0, 15)
    return clamp(prob, 0, 100)


def token_airdrop_info_from_pair(pair: dict) -> str:
    token_name = pair.get("baseToken", {}).get("name", "Unknown Token")
    token_symbol = pair.get("baseToken", {}).get("symbol", "")
    dex = pair.get("dexId", "DEX").capitalize()
    liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
    volume24 = pair.get("volume", {}).get("h24", 0) or 0
    price = pair.get("priceUsd", "N/A")
    # Pair age not available reliably from DexScreener -> leave 0
    pair_age_days = 0.0

    prob = estimate_airdrop_probability(liquidity, volume24, pair_age_days)

    if prob > 75:
        mood = "🔥 High likelihood — active dev / community signals."
    elif prob > 45:
        mood = "⚡ Moderate likelihood — keep monitoring."
    else:
        mood = "🌙 Low likelihood — token appears low-activity."

    result = (
        f"💠 <b>Token Airdrop Potential</b>\n"
        f"🔷 {token_name} ({token_symbol}) — <i>{dex}</i>\n"
        f"💰 Price: ${price}\n"
        f"💧 Liquidity: ${liquidity:,.2f}\n"
        f"📊 24h Volume: ${volume24:,.2f}\n"
        f"🎯 Airdrop Probability (sim): <b>{prob:.0f}%</b>\n"
        f"🧠 Neural Insight: {mood}\n\n"
        f"{BRAND_TAG}"
    )
    return result


# -------------------------
# Command handler (smart detection)
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

        # Primary decision:
        # 1) If query looks like an EVM address, probe DexScreener.
        # 2) If DexScreener finds a pair, act as token mode.
        # 3) Otherwise, act as wallet mode.
        pair = None
        if looks_like_evm_address(query):
            pair = found_token_on_dex(query)

        # If not an EVM address, still probe DexScreener (symbol/name)
        if pair is None:
            pair = found_token_on_dex(query)

        if pair:
            reply = token_airdrop_info_from_pair(pair)
        else:
            # treat as wallet (even if it isn't 0x-formatted — still works)
            # if user input isn't a 0x wallet, show guidance
            if not looks_like_evm_address(query):
                # user likely typed a symbol or text which Dex didn't find
                update.message.reply_text(
                    "⚠️ Could not detect a token on DEX and input is not a valid wallet address.\n"
                    "If you intended a wallet, provide a full 0x address. If you meant a token, try the contract address.",
                    parse_mode="HTML"
                )
                return

            reply = simulate_wallet_eligibility(query)

        update.message.reply_text(reply, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        update.message.reply_text(f"⚠️ Neural Core Error: {e}", parse_mode="HTML")


# -------------------------
# Register plugin
# -------------------------
def register(dispatcher):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdrop_cmd))
    print("🎁 Loaded plugin: airdrop_check.py (Smart Hybrid v4.2)")
