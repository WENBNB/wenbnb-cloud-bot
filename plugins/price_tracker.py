# plugins/price_tracker.py
"""
WENBNB Market Feed v8.3 — Tri-Fusion Data Sync
Combines CoinGecko + DexScreener + Binance (BNB) with smart fallback,
chain detection emojis, and a short Neural Pulse insight.
"""

from telegram.ext import CommandHandler
from telegram import Update
from telegram.ext import CallbackContext
import requests, html, random, math, os, time

# Branding
BRAND_FOOTER = "💫 Powered by <b>WENBNB Neural Engine</b> — Market Feed v8.3 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
BINANCE_BNB = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"

# Default token id (CoinGecko-style id) when user omits args
DEFAULT_TOKEN_ID = os.getenv("DEFAULT_TOKEN_ID", "wenbnb")  # keep lowercase id

# Utilities
def short_float(x):
    try:
        v = float(x)
        if v >= 1:
            return f"{v:,.4f}"
        else:
            return f"{v:.8f}"
    except Exception:
        return str(x)

def chain_emoji(name: str) -> str:
    s = (name or "").lower()
    if "bsc" in s or "pancake" in s or "bnb" in s:
        return "🔶 BSC"
    if "ethereum" in s or "uni" in s or "uniswap" in s:
        return "💎 Ethereum"
    if "base" in s:
        return "🪩 Base"
    if "arbitrum" in s:
        return "🛰️ Arbitrum"
    if "solana" in s:
        return "🟣 Solana"
    return "❓ Unknown"

def neural_market_rank(liquidity_usd: float, volume24_usd: float) -> str:
    try:
        L = max(1.0, float(liquidity_usd))
        V = max(1.0, float(volume24_usd))
        score = (math.log10(L) * 0.6 + math.log10(V) * 0.4) * 10
        if score >= 85: return "A+"
        elif score >= 70: return "A"
        elif score >= 55: return "B"
        elif score >= 40: return "C"
        else: return "D"
    except Exception:
        return "N/A"

# Core helpers
def fetch_bnb_price():
    """Return float BNB price or None."""
    try:
        r = requests.get(BINANCE_BNB, timeout=8)
        j = r.json()
        return float(j.get("price", 0))
    except Exception:
        return None

def try_coingecko_price(token_id: str):
    """Try CoinGecko simple price (token_id should be coingecko id)."""
    try:
        url = COINGECKO_SIMPLE.format(id=token_id)
        j = requests.get(url, timeout=8).json()
        return j.get(token_id, {}).get("usd")
    except Exception:
        return None

def try_dexscreener(token_query: str):
    """Probe DexScreener; return first pair dict or None."""
    try:
        url = DEXSCREENER_SEARCH.format(q=token_query)
        j = requests.get(url, timeout=8).json()
        pairs = j.get("pairs", [])
        if not pairs:
            return None
        # prefer pair with highest liquidity
        pairs_sorted = sorted(pairs, key=lambda p: (p.get("liquidity", {}).get("usd") or 0), reverse=True)
        return pairs_sorted[0]
    except Exception:
        return None

def build_insight(token_name: str, token_symbol: str, prob_source: str, rank: str):
    """Small neural-like insight to make output feel human."""
    templates = [
        f"{token_name} is showing {('strong momentum' if rank in ['A+','A'] else 'moderate activity')} — watch volume spikes.",
        f"Signals: {('smart money accumulation' if rank in ['A+','A'] else 'low liquidity risk')}.",
        f"Community chatter rising — keep an eye on {token_symbol or token_name}.",
        f"Liquidity/volume profile: {rank} — developer/market activity may be {('high' if rank in ['A+','A'] else 'low')}."
    ]
    # prefer shorter, crisp insight
    return random.choice(templates) + f" (source: {prob_source})"

# === /price handler ===
def price_cmd(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_chat_action(chat_id=chat_id, action="typing")

    # token arg: try to accept contract, symbol or coingecko id
    if context.args:
        query_raw = context.args[0].strip()
    else:
        query_raw = DEFAULT_TOKEN_ID

    # Normalize
    query = query_raw.strip()
    token_name = query.upper()
    token_symbol = ""
    token_price = None
    dex_source = "CoinGecko"
    chain_display = "❓ Unknown"
    liquidity = 0
    volume24 = 0
    rank = "N/A"
    bnb_price = fetch_bnb_price()

    # 1) Try CoinGecko by id (best for official tokens)
    cg_id = query.lower()
    token_price = try_coingecko_price(cg_id)

    # 2) If CoinGecko fails, try DexScreener probe (accepts symbol/contract)
    pair = None
    if not token_price:
        pair = try_dexscreener(query)
        if pair:
            base = pair.get("baseToken", {}) or {}
            token_name = base.get("name") or base.get("symbol") or query
            token_symbol = base.get("symbol") or token_symbol or query
            token_price = pair.get("priceUsd") or pair.get("baseToken", {}).get("priceUsd")
            dex_source = pair.get("dexId", "DexScreener").capitalize()
            chain_display = chain_emoji(pair.get("dexId") or pair.get("chainId") or pair.get("pairName"))
            liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
            volume24 = pair.get("volume", {}).get("h24", 0) or 0
            rank = neural_market_rank(liquidity, volume24)

    # 3) If CoinGecko gave price, try to enrich with DexScreener for liquidity/chain
    if token_price and not pair:
        # attempt to get pair to show liquidity/chain info (best-effort)
        try:
            pair = try_dexscreener(query) or try_dexscreener(token_symbol or token_name)
            if pair:
                liquidity = pair.get("liquidity", {}).get("usd", 0) or 0
                volume24 = pair.get("volume", {}).get("h24", 0) or 0
                dex_source = pair.get("dexId", dex_source).capitalize()
                chain_display = chain_emoji(pair.get("dexId") or pair.get("pairName"))
                rank = neural_market_rank(liquidity, volume24)
        except Exception:
            pass

    # Final safety: if still no price, present friendly error
    if token_price in (None, "", "N/A"):
        update.message.reply_text(
            f"⚠️ Could not find price for '<b>{html.escape(query)}</b>'.\n"
            "Try a coin ID (CoinGecko), contract address or token symbol. Example:\n"
            "/price bitcoin  or  /price 0xContractAddress  or  /price WENBNB",
            parse_mode="HTML"
        )
        return

    # Format values
    try:
        token_price_f = float(token_price)
    except Exception:
        token_price_f = token_price

    # Build message
    lines = []
    lines.append(f"💹 <b>WENBNB Market Feed</b>\n")
    lines.append(f"💎 <b>{html.escape(str(token_name))} {f'({html.escape(token_symbol)})' if token_symbol else ''}</b>")
    lines.append(f"🌐 <b>Chain:</b> {chain_display}")
    lines.append(f"💰 <b>Price:</b> ${short_float(token_price_f)}")
    if liquidity:
        lines.append(f"💧 <b>Liquidity:</b> ${short_float(liquidity)}")
    if volume24:
        lines.append(f"📊 <b>24h Volume:</b> ${short_float(volume24)}")
    if rank and rank != "N/A":
        lines.append(f"🏅 <b>Neural Rank:</b> {rank}")
    if bnb_price:
        lines.append(f"🔥 <b>BNB:</b> ${short_float(bnb_price)}")
    lines.append(f"📈 <i>Data Source:</i> {dex_source}")
    lines.append("")  # spacer

    # Neural Pulse insight
    insight = build_insight(token_name, token_symbol or token_name, dex_source, rank)
    lines.append(f"🧠 Neural Pulse: <i>{html.escape(insight)}</i>")
    lines.append("")  # spacer
    lines.append(BRAND_FOOTER)

    reply = "\n".join(lines)
    update.message.reply_text(reply, parse_mode="HTML", disable_web_page_preview=True)

# Registration for loader
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
    print("✅ Loaded plugin: plugins.price_tracker (v8.3 Tri-Fusion)")
