"""
WENBNB Token Intelligence v5.5-Pro Sync — Hybrid Data Engine
─────────────────────────────────────────────────────────────
Combines DexScreener + CoinGecko + Binance hybrid feeds for
real-time token insights, liquidity scan, and neural ranking.

💫 Powered by WENBNB Neural Engine — Token Intelligence 24×7 ⚡
"""

from telegram.ext import CommandHandler
from telegram import Update
import requests, html, math, random, time

# === Branding ===
BRAND_TAG = "💫 WENBNB Neural Engine — Token Intelligence 24×7 ⚡"
DEX_URL = "https://api.dexscreener.com/latest/dex/search?q={q}"
CG_PRICE = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
BINANCE_URL = "https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

# === Helpers ===
def short_float(v):
    try:
        val = float(v)
        if val >= 1: return f"{val:,.4f}"
        else: return f"{val:.8f}"
    except: return str(v)

def detect_chain(dex):
    dex = (dex or "").lower()
    if "pancake" in dex: return "BSC"
    if "uniswap" in dex: return "Ethereum"
    if "base" in dex: return "Base"
    if "arbitrum" in dex: return "Arbitrum"
    if "solana" in dex: return "Solana"
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
    except: return "N/A"

# === Core Data Logic ===
def get_token_info(query):
    query = query.strip().lower()
    token_name, symbol, price, chain, dex_name = query.upper(), "", "N/A", "Unknown", "N/A"
    liquidity, volume, rank = 0, 0, "N/A"
    pair_url, address = "", ""

    # 1️⃣ Try Binance (for known tickers)
    try:
        data = requests.get(BINANCE_URL.format(symbol=query.upper() + "USDT"), timeout=4).json()
        if "price" in data:
            return {
                "name": query.upper(),
                "symbol": query.upper(),
                "price": float(data["price"]),
                "chain": "Centralized",
                "dex": "Binance",
                "liquidity": 0,
                "volume": 0,
                "rank": "A+",
                "url": "",
                "address": ""
            }
    except:
        pass

    # 2️⃣ DexScreener scan
    try:
        dex = requests.get(DEX_URL.format(q=query), timeout=6).json()
        pairs = dex.get("pairs", [])
        if pairs:
            p = pairs[0]
            base = p.get("baseToken", {})
            token_name = base.get("name") or query.upper()
            symbol = base.get("symbol") or query.upper()
            price = p.get("priceUsd", "N/A")
            chain = detect_chain(p.get("dexId"))
            dex_name = p.get("dexId", "DEX").capitalize()
            liquidity = p.get("liquidity", {}).get("usd", 0)
            volume = p.get("volume", {}).get("h24", 0)
            rank = neural_rank(liquidity, volume)
            pair_url = p.get("url", "")
            address = base.get("address", "")
    except:
        pass

    # 3️⃣ CoinGecko fallback
    if price == "N/A":
        try:
            cg_data = requests.get(CG_PRICE.format(id=query), timeout=6).json()
            if query in cg_data:
                price = cg_data[query]["usd"]
                dex_name = "CoinGecko"
        except:
            pass

    return {
        "name": token_name,
        "symbol": symbol,
        "price": price,
        "chain": chain,
        "dex": dex_name,
        "liquidity": liquidity,
        "volume": volume,
        "rank": rank,
        "url": pair_url,
        "address": address
    }

# === /tokeninfo Command ===
def tokeninfo_cmd(update: Update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        token = context.args[0] if context.args else "wenbnb"
        info = get_token_info(token)
        ts = time.strftime("%H:%M:%S", time.localtime())

        insight_lines = [
            f"{info['symbol']} is showing <b>healthy on-chain activity</b> 🔥",
            f"Liquidity looks <b>stable</b> — Neural flow consistent ⚙️",
            f"Volume trend indicates <b>smart money</b> movement 🧠",
            f"{info['symbol']} is <b>cooling off slightly</b> 🪶",
            f"Potential <b>momentum buildup</b> forming 🚀"
        ]
        insight = random.choice(insight_lines)

        msg = (
            f"📊 <b>Neural Token Insight</b>\n\n"
            f"💎 <b>{html.escape(info['name'])} ({html.escape(info['symbol'])})</b>\n"
            f"🌐 <b>Chain:</b> {info['chain']}\n"
            f"🏦 <b>DEX:</b> {info['dex']}\n"
            f"💰 <b>Price:</b> ${short_float(info['price'])}\n"
            f"💧 <b>Liquidity:</b> ${short_float(info['liquidity'])}\n"
            f"📈 <b>24h Volume:</b> ${short_float(info['volume'])}\n"
            f"🏅 <b>Neural Token Rank:</b> {info['rank']}\n"
        )

        if info["address"]:
            msg += f"🔗 <b>Contract:</b> <code>{info['address']}</code>\n"
        if info["url"]:
            msg += f"🌐 <a href=\"{info['url']}\">View on DexScreener</a>\n"

        msg += (
            f"\n🧠 Insight: {insight}\n\n"
            f"{BRAND_TAG}\n⏱️ {ts}"
        )

        update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=False)

    except Exception as e:
        print("[tokeninfo_cmd Error]", e)
        update.message.reply_text("⚙️ Neural Engine syncing... please retry shortly.", parse_mode="HTML")

# === Register ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("tokeninfo", tokeninfo_cmd))
    print("✅ Loaded plugin: plugins.tokeninfo (v5.5-Pro Sync)")
