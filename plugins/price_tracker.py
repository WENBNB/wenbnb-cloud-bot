"""
WENBNB Price Tracker v5.5-Pro Sync — Unified Market Engine
─────────────────────────────────────────────────────────────
Hybrid data system combining Binance, CoinGecko & DexScreener.
AI-enhanced insights with Neural Rank analysis.

💫 Powered by WENBNB Neural Engine — Market Intelligence 24×7 ⚡
"""

import requests, html, random, math, time
from telegram.ext import CommandHandler

# === BRANDING ===
BRAND_TAG = "🚀 WENBNB Neural Engine — Market Intelligence 24×7 ⚡"

# === API SOURCES ===
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
DEX_URL = "https://api.dexscreener.com/latest/dex/search?q={token}"

# === UTILS ===
def short_float(v):
    try:
        val = float(v)
        if val >= 1:
            return f"{val:,.4f}"
        else:
            return f"{val:.8f}"
    except:
        return str(v)

def detect_chain(dex_id: str):
    d = (dex_id or "").lower()
    if "pancake" in d: return "BSC"
    if "uniswap" in d: return "Ethereum"
    if "base" in d: return "Base"
    if "arbitrum" in d: return "Arbitrum"
    return "Unknown"

def neural_rank(liq, vol):
    try:
        L = max(1.0, float(liq))
        V = max(1.0, float(vol))
        score = (math.log10(L) * 0.6 + math.log10(V) * 0.4) * 10
        if score >= 85: return "A+"
        elif score >= 70: return "A"
        elif score >= 55: return "B"
        elif score >= 40: return "C"
        else: return "D"
    except:
        return "N/A"

# === DATA ENGINE ===
def get_token_data(token):
    token = token.lower().strip()
    token_symbol = token.upper()
    token_price, liquidity, volume24, chain, source = "N/A", 0, 0, "Unknown", "N/A"

    # 1️⃣ Binance (for major pairs)
    try:
        pair = token_symbol + "USDT"
        data = requests.get(BINANCE_URL.format(symbol=pair), timeout=4).json()
        if "price" in data:
            return {
                "name": token_symbol,
                "price": float(data["price"]),
                "liquidity": 0,
                "volume": 0,
                "chain": "Centralized",
                "rank": "A+",
                "source": "Binance"
            }
    except Exception:
        pass

    # 2️⃣ CoinGecko (for listed altcoins)
    try:
        data = requests.get(COINGECKO_URL.format(id=token), timeout=6).json()
        if token in data:
            price = data[token]["usd"]
            return {
                "name": token_symbol,
                "price": price,
                "liquidity": 0,
                "volume": 0,
                "chain": "Global",
                "rank": "A",
                "source": "CoinGecko"
            }
    except Exception:
        pass

    # 3️⃣ DexScreener fallback
    try:
        dex = requests.get(DEX_URL.format(token=token), timeout=6).json()
        pairs = dex.get("pairs", [])
        if pairs:
            p = pairs[0]
            token_name = p.get("baseToken", {}).get("name", token_symbol)
            token_price = p.get("priceUsd", "N/A")
            chain = detect_chain(p.get("dexId"))
            liquidity = p.get("liquidity", {}).get("usd", 0)
            volume24 = p.get("volume", {}).get("h24", 0)
            return {
                "name": token_name,
                "price": token_price,
                "liquidity": liquidity,
                "volume": volume24,
                "chain": chain,
                "rank": neural_rank(liquidity, volume24),
                "source": p.get("dexId", "DEX").capitalize()
            }
    except Exception as e:
        print(f"[Dex Error] {e}")

    return {"name": token_symbol, "price": "N/A", "rank": "N/A", "chain": chain, "source": source}

# === COMMAND ===
def price_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        token = context.args[0] if context.args else "wenbnb"
        data = get_token_data(token)
        timestamp = time.strftime("%H:%M:%S", time.localtime())

        insights = [
            "is showing <b>strong market confidence</b> 💎",
            "is <b>consolidating</b> after volatility ⚙️",
            "is <b>gaining traction</b> among traders 🔥",
            "shows <b>organic activity</b> and positive flow 🌿",
            "is <b>cooling off</b> — monitor closely 🪶"
        ]
        insight = random.choice(insights)

        msg = (
            f"💹 <b>Neural Market Update</b>\n\n"
            f"💎 <b>{html.escape(data['name'])}</b>\n"
            f"🌐 <b>Chain:</b> {data['chain']}\n"
            f"💰 <b>Price:</b> ${short_float(data['price'])}\n"
            f"💧 <b>Liquidity:</b> ${short_float(data['liquidity'])}\n"
            f"📊 <b>24h Volume:</b> ${short_float(data['volume'])}\n"
            f"🏅 <b>Neural Market Rank:</b> {data['rank']}\n"
            f"📈 <i>Source:</i> {data['source']}\n\n"
            f"🧠 Insight: <b>{data['name']}</b> {insight}\n\n"
            f"{BRAND_TAG}\n⏱️ {timestamp}"
        )

        update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        print(f"[Error in /price] {e}")
        update.message.reply_text("⚙️ Neural Engine syncing... please retry soon.", parse_mode="HTML")

# === REGISTER ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
    print("✅ Loaded plugin: plugins.price_tracker (v5.5-Pro Sync)")
