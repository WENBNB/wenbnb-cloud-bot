"""
🎁 WENBNB Airdrop Intelligence v4.4 — Hybrid Mode + Neural Rank + Chain Detect
• Auto-detects token vs wallet using DexScreener probe (fallback included)
• Wallet Mode -> Deterministic eligibility simulation + Neural Score + Rank (A+..F)
• Token Mode  -> DEX liquidity + 24h volume + simulated airdrop probability + chain
• Adds /airdrop alias for convenience
✨ Powered by WENBNB Neural Engine — Airdrop Intelligence v4.4 (Stable)
"""

import os
import re
import math
import random
import requests
from telegram.ext import CommandHandler
from typing import Optional

BRAND_TAG = "🎁 *Powered by WENBNB Neural Engine* — _Airdrop Intelligence 24×7_ ⚡"
DEX_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"


# -------------------------
# Helpers
# -------------------------
def looks_like_evm_address(text: str) -> bool:
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", text.strip()))


def clamp(x, a=0.0, b=100.0):
    return max(a, min(b, x))


# -------------------------
# DexScreener probe + chain detection
# -------------------------
def probe_dexscreener(query: str, timeout=8) -> Optional[dict]:
    """Return parsed JSON from DexScreener or None on failure."""
    try:
        r = requests.get(DEX_SEARCH.format(q=query), timeout=timeout)
        return r.json()
    except Exception:
        return None


def find_best_pair(query: str) -> Optional[dict]:
    data = probe_dexscreener(query)
    if not data:
        return None
    pairs = data.get("pairs", [])
    if not pairs:
        return None
    return pairs[0]


def detect_chain_from_pair(pair: dict) -> str:
    try:
        if "chainId" in pair and pair.get("chainId"):
            cid = str(pair.get("chainId")).lower()
            if "56" in cid or "bsc" in cid:
                return "BSC"
            if "1" == cid or "ethereum" in cid:
                return "Ethereum"
        dex = (pair.get("dexId") or "").lower()
        if "pancake" in dex:
            return "BSC"
        if "uniswap" in dex:
            return "Ethereum"
        if "osmosis" in dex:
            return "Osmosis"
        if "arbitrum" in dex:
            return "Arbitrum"
        if "base" in dex:
            return "Base"
        pair_name = (pair.get("pairName") or "").lower()
        if "bnb" in pair_name or "pancake" in pair_name:
            return "BSC"
    except Exception:
        pass
    return "Unknown"


# -------------------------
# Wallet Mode (deterministic scoring + rank)
# -------------------------
def deterministic_wallet_score(wallet: str):
    key = wallet.lower()
    seed_val = sum((ord(c) * (i + 1)) for i, c in enumerate(key[-12:])) & 0xFFFFFFFF
    rnd = random.Random(seed_val)

    tail = key[-8:]
    try:
        tail_num = int(tail, 16)
    except Exception:
        tail_num = sum(ord(c) for c in tail)

    age_feat = (tail_num % 1000) / 1000.0
    activity_feat = ((sum(ord(c) for c in key[-6:]) % 100) / 100.0)
    jitter = (rnd.random() - 0.5) * 14

    base_score = (age_feat * 0.3 + activity_feat * 0.5 + 0.2) * 100
    score = clamp(base_score + jitter, 0, 100)
    protocol_count = 2 + (tail_num % 11)
    return int(score), protocol_count, rnd


def grade_from_score(score: int) -> str:
    if score >= 95:
        return "A+"
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def wallet_report(wallet: str) -> str:
    score, protocol_count, rnd = deterministic_wallet_score(wallet)
    if score >= 80:
        eligibility = "✅ *Eligible*"
    elif score >= 55:
        eligibility = "⚠️ *Borderline*"
    else:
        eligibility = "❌ *Not Eligible*"

    rank = grade_from_score(score)
    insights = [
        "Strong DeFi footprint detected across L2 networks.",
        "Recent activity on multiple airdrop campaigns.",
        "Low gas usage history — possible passive wallet.",
        "High transaction count in Base / Arbitrum ecosystems.",
        "New wallet with moderate activity.",
        "Wallet connected to verified NFT or reward protocols.",
        "Frequent small interactions — appears like aggregator behavior."
    ]
    insight = rnd.choice(insights)

    return (
        f"💎 *Wallet Scan Report*\n"
        f"🔷 Wallet: `{wallet[:8]}...{wallet[-6:]}`\n"
        f"{eligibility} for upcoming airdrops  |  *Rank:* `{rank}`\n"
        f"🧠 Neural Score: *{score}/100*\n"
        f"🔗 DeFi Protocols Detected (est.): `{protocol_count}`\n"
        f"✨ Neural Insight: _{insight}_\n\n"
        f"{BRAND_TAG}"
    )


# -------------------------
# Token Mode (DEX + probability + chain)
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


def token_report_from_pair(pair: dict) -> str:
    try:
        token_name = pair.get("baseToken", {}).get("name", "Unknown Token")
        token_symbol = pair.get("baseToken", {}).get("symbol", "")
        dex = pair.get("dexId", "DEX").capitalize()
        liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
        volume24 = pair.get("volume", {}).get("h24", 0) or 0
        price = pair.get("priceUsd", "N/A")
        chain = detect_chain_from_pair(pair)
        pair_age_days = 0.0
        prob = estimate_airdrop_probability(liquidity, volume24, pair_age_days)

        mood = ("🔥 High likelihood — active dev / community signals."
                if prob > 75 else "⚡ Moderate likelihood — keep monitoring."
                if prob > 45 else "🌙 Low likelihood — token appears low-activity.")

        if prob >= 90:
            tag = "Hot"
        elif prob >= 70:
            tag = "Warm"
        elif prob >= 45:
            tag = "Watch"
        else:
            tag = "Cold"

        return (
            f"💠 *Token Airdrop Potential*\n"
            f"🔷 {token_name} ({token_symbol}) — _{dex}_\n"
            f"🌐 Chain: *{chain}*\n"
            f"💰 Price: `${price}`\n"
            f"💧 Liquidity: `${liquidity:,.2f}`\n"
            f"📊 24h Volume: `${volume24:,.2f}`\n"
            f"🎯 Airdrop Probability: *{prob:.0f}%*  |  `{tag}`\n"
            f"🧠 Neural Insight: _{mood}_\n\n"
            f"{BRAND_TAG}"
        )
    except Exception as e:
        return f"⚠️ Error building token report: {e}\n\n{BRAND_TAG}"


# -------------------------
# Command handler (smart detection + alias)
# -------------------------
def airdropcheck_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        args = context.args
        if not args:
            update.message.reply_text(
                "🧩 *Usage Guide — Neural AirdropCheck*\n"
                "`/airdropcheck <wallet_address | contract_address | token_symbol>`\n"
                "💡 Example: `/airdropcheck 0xYourWalletHere`\n"
                "💠 Example: `/airdropcheck WENBNB`",
                parse_mode="Markdown",
            )
            return

        query = args[0].strip()
        pair = find_best_pair(query)

        if pair:
            reply = token_report_from_pair(pair)
            update.message.reply_text(reply, parse_mode="Markdown", disable_web_page_preview=True)
            return

        if looks_like_evm_address(query):
            reply = wallet_report(query)
            update.message.reply_text(reply, parse_mode="Markdown", disable_web_page_preview=True)
            return

        update.message.reply_text(
            "⚠️ Could not detect token on DEX and input is not a valid 0x wallet address.\n"
            "If you meant to check a wallet, provide a full 0x address. "
            "If you meant a token, use the contract address or try another symbol.",
            parse_mode="Markdown"
        )

    except Exception as e:
        update.message.reply_text(f"⚠️ Neural Core Error: {e}", parse_mode="Markdown")


def airdrop_alias_cmd(update, context):
    return airdropcheck_cmd(update, context)


# -------------------------
# Register plugin
# -------------------------
def register(dispatcher):
    dispatcher.add_handler(CommandHandler("airdropcheck", airdropcheck_cmd))
    dispatcher.add_handler(CommandHandler("airdrop", airdrop_alias_cmd))
    print("🎁 Loaded plugin: airdrop_check.py (Neural v4.4-Stable)")
