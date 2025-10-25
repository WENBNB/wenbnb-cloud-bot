from telegram.ext import CommandHandler
import requests, html, random, math, time

# === Branding ===
BRAND_FOOTER = "💫 Powered by <b>WENBNB Neural Engine</b> — Neural Market Feed v8.5.1 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
BINANCE_SIMPLE = "https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

# === Cache ===
price_cache = {}
CACHE_EXPIRY = 300  # seconds

# === Token Map ===
DEFAULT_WENBNB_CONTRACT = "0x78525f54e46d2821ec59bfae27201058881b4444"
KNOWN_TOKENS = {
    "BNB": "BNBUSDT",
    "BTC": "BTCUSDT",
    "ETH": "ETHUSDT",
    "PEPE": "PEPEUSDT",
    "SOL": "SOLUSDT",
    "WENBNB": DEFAULT_WENBNB_CONTRACT
}

# === Utility ===
def short_float(x):
    try:
        v = float(x)
        return f"{v:,.4f}" if v >= 1 else f"{v:.8f}"
    except Exception:
        return str(x)

def detect_chain(dex_id: str) -> str:
    dex_id = (dex_id or "").lower()
    if "pancake" in dex_id: return "BSC"
    if "uniswap" in dex_id: return "Ethereum"
    if "base" in dex_id: return "Base"
    if "arbitrum" in dex_id: return "Arbitrum"
    return "Unknown"

def neural_rank(liquidity_usd: float, volume24_usd: float) -> str:
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

def get_cached_price(token):
    now = time.time()
    if token in price_cache:
        price, ts = price_cache[token]
        if now - ts < CACHE_EXPIRY:
            return price
    return None

def set_cached_price(token, price):
    price_cache[token] = (price, time.time())

# === /price Command ===
def price_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        token = "WENBNB"
        if context.args:
            token = context.args[0].upper()

        # === Fallback message for WENBNB ===
        if token == "WENBNB":
            update.message.reply_text(
                "💫 <b>WENBNB is evolving...</b>\n"
                "Official token feed coming online soon — stay tuned, Neural King 👑⚡\n\n"
                f"{BRAND_FOOTER}",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            return

        cached = get_cached_price(token)
        if cached:
            price, source = cached, "Binance (Cached)"
        else:
            price, source = None, None

            # === 1️⃣ Binance ===
            if token in KNOWN_TOKENS:
                try:
                    symbol = KNOWN_TOKENS[token]
                    data = requests.get(BINANCE_SIMPLE.format(symbol=symbol), timeout=10).json()
                    price = data.get("price")
                    source = "Binance"
                    if price:
                        set_cached_price(token, price)
                except Exception:
                    price = None

            # === 2️⃣ CoinGecko Fallback ===
            if not price:
                try:
                    cg = requests.get(COINGECKO_SIMPLE.format(id=token.lower()), timeout=10).json()
                    price = cg.get(token.lower(), {}).get("usd")
                    source = "CoinGecko"
                    if price:
                        set_cached_price(token, price)
                except Exception:
                    price = None

            # === 3️⃣ DexScreener ===
            if not price:
                try:
                    dex = requests.get(DEXSCREENER_SEARCH.format(q=token), timeout=10).json()
                    pairs = dex.get("pairs", [])
                    if pairs:
                        pair = pairs[0]
                        base = pair.get("baseToken", {})
                        token_name = base.get("name") or base.get("symbol") or token
                        token_symbol = base.get("symbol") or token
                        price = pair.get("priceUsd", "N/A")
                        dex_source = pair.get("dexId", "Unknown DEX").capitalize()
                        chain = detect_chain(dex_source)
                        liquidity = pair.get("liquidity", {}).get("usd", 0)
                        volume24 = pair.get("volume", {}).get("h24", 0)
                        rank = neural_rank(liquidity, volume24)
                        chart_link = pair.get("url", "")
                        insight = random.choice([
                            f"{token_symbol} volatility rising — traders alert 🔥",
                            f"{token_symbol} gaining strong momentum 💎",
                            f"{token_symbol} showing smart-money inflow 🧠",
                            f"{token_symbol} trending with neural confidence ⚡"
                        ])

                        msg = (
                            f"💹 <b>WENBNB Market Feed</b>\n\n"
                            f"💎 <b>{html.escape(token_name)} ({html.escape(token_symbol)})</b>\n"
                            f"🌐 <b>Chain:</b> {chain}\n"
                            f"💰 <b>Price:</b> ${short_float(price)}\n"
                            f"💧 <b>Liquidity:</b> ${short_float(liquidity)}\n"
                            f"📊 <b>24h Volume:</b> ${short_float(volume24)}\n"
                            f"🏅 <b>Neural Rank:</b> {rank}\n"
                            f"📈 <i>Data Source:</i> {dex_source}\n\n"
                            f"🧠 Insight: {insight}\n\n"
                            f"🔗 <a href='{chart_link}'>View Chart / Buy</a>\n\n"
                            f"{BRAND_FOOTER}"
                        )
                        update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=False)
                        return
                except Exception:
                    price = None

        # === Neural Pulse Section ===
        if price:
            insight = f"{token} neural signal steady — confidence high ⚡" if token in ["BTC", "ETH", "BNB", "PEPE"] \
                else f"{token} trending with neural confidence ⚡"

            msg = (
                f"💹 <b>WENBNB Market Feed</b>\n\n"
                f"💎 <b>{html.escape(token)}</b>\n"
                f"💰 <b>Price:</b> ${short_float(price)}\n"
                f"📈 <i>Data Source:</i> {source}\n\n"
                f"🧠 Neural Pulse: {insight}\n\n"
                f"{BRAND_FOOTER}"
            )
            update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)
        else:
            update.message.reply_text(
                "⚠️ Neural Feed could not fetch this token right now — please retry soon.\n\n"
                f"{BRAND_FOOTER}",
                parse_mode="HTML"
            )

    except Exception as e:
        print("Error:", e)
        update.message.reply_text(
            "⚙️ Neural Engine syncing... please retry soon.",
            parse_mode="HTML"
        )

# === Register ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
    print("✅ Loaded plugin: plugins.price_tracker (v8.5.1 Neural Fallback Edition)")
