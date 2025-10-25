# --- WENBNB Market Feed v8.5.2 “Easter Pulse Edition” ⚡ ---
# (Upgraded from v8.5.1 - Zero data impact, flavor + health monitoring added)

from telegram.ext import CommandHandler
import requests, html, random, math, time, logging

# === Branding ===
BRAND_FOOTER = "💫 Powered by <b>WENBNB Neural Engine</b> — Neural Market Feed v8.5.2 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
BINANCE_SIMPLE = "https://api.binance.com/api/v3/ticker/price?symbol={symbol}"

# === Cache / Metrics ===
price_cache = {}
CACHE_EXPIRY = 300
HEARTBEAT = {"calls": 0, "success": 0, "fails": 0, "last_sync": time.time()}

# === Tokens ===
DEFAULT_WENBNB_CONTRACT = "0x78525f54e46d2821ec59bfae27201058881b4444"
KNOWN_TOKENS = {
    "BNB": "BNBUSDT", "BTC": "BTCUSDT", "ETH": "ETHUSDT",
    "PEPE": "PEPEUSDT", "SOL": "SOLUSDT", "WENBNB": DEFAULT_WENBNB_CONTRACT
}

# === Utils ===
def short_float(x):
    try:
        v = float(x)
        return f"{v:,.4f}" if v >= 1 else f"{v:.8f}"
    except Exception:
        return str(x)

def detect_chain(dex_id):
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
        s = (math.log10(L)*0.6 + math.log10(V)*0.4)*10
        if s >= 85: return "A+"
        elif s >= 70: return "A"
        elif s >= 55: return "B"
        elif s >= 40: return "C"
        else: return "D"
    except: return "N/A"

def cache_get(t):
    if t in price_cache and time.time() - price_cache[t][1] < CACHE_EXPIRY:
        return price_cache[t][0]
    return None

def cache_set(t, p):
    price_cache[t] = (p, time.time())

# === Neural Pulse Easter Egg ===
def neural_easter():
    if random.randint(1, 25) == 7:  # 1 in 25 calls
        return "👁 <i>I observe you, CrypTechKing™… the Neural Pulse never sleeps.</i> ⚡\n\n"
    return ""

# === Heartbeat Monitor ===
def log_heartbeat(success=True):
    HEARTBEAT["calls"] += 1
    if success: HEARTBEAT["success"] += 1
    else: HEARTBEAT["fails"] += 1
    if HEARTBEAT["calls"] % 25 == 0:
        uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - HEARTBEAT["last_sync"]))
        logging.info(f"❤️‍🔥 WENBNB Pulse: {HEARTBEAT['success']} ok / {HEARTBEAT['fails']} fail | Uptime {uptime}")
        HEARTBEAT["last_sync"] = time.time()

# === Command ===
def price_cmd(update, context):
    try:
        token = "WENBNB"
        if context.args:
            token = context.args[0].upper()

        # --- WENBNB fallback ---
        if token == "WENBNB":
            msg = (
                "💫 <b>WENBNB is evolving...</b>\n"
                "Official token feed coming online soon — stay tuned, Neural King 👑⚡\n\n"
                f"{BRAND_FOOTER}"
            )
            update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)
            log_heartbeat(success=True)
            return

        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        price, source = cache_get(token), "Binance (cached)"
        if not price:
            # 1️⃣ Binance
            try:
                if token in KNOWN_TOKENS:
                    data = requests.get(BINANCE_SIMPLE.format(symbol=KNOWN_TOKENS[token]), timeout=6).json()
                    price = data.get("price"); source = "Binance"
                    if price: cache_set(token, price)
            except: pass

            # 2️⃣ CoinGecko
            if not price:
                try:
                    cg = requests.get(COINGECKO_SIMPLE.format(id=token.lower()), timeout=6).json()
                    price = cg.get(token.lower(), {}).get("usd"); source = "CoinGecko"
                    if price: cache_set(token, price)
                except: pass

            # 3️⃣ Dex Screener Fallback
            if not price:
                try:
                    dex = requests.get(DEXSCREENER_SEARCH.format(q=token), timeout=6).json()
                    pair = dex.get("pairs", [])[0]
                    base = pair.get("baseToken", {})
                    name, symbol = base.get("name", token), base.get("symbol", token)
                    price = pair.get("priceUsd"); source = pair.get("dexId", "DexScreener")
                    liq, vol = pair.get("liquidity", {}).get("usd", 0), pair.get("volume", {}).get("h24", 0)
                    rank, chain = neural_rank(liq, vol), detect_chain(source)
                    chart = pair.get("url", "")
                    insight = random.choice([
                        f"{symbol} volatility rising — traders alert 🔥",
                        f"{symbol} gaining strong momentum 💎",
                        f"{symbol} showing smart-money inflow 🧠",
                        f"{symbol} trending with neural confidence ⚡"
                    ])
                    msg = (
                        f"💹 <b>WENBNB Market Feed</b>\n\n"
                        f"💎 <b>{name} ({symbol})</b>\n"
                        f"🌐 <b>Chain:</b> {chain}\n"
                        f"💰 <b>Price:</b> ${short_float(price)}\n"
                        f"💧 <b>Liquidity:</b> ${short_float(liq)}\n"
                        f"📊 <b>24h Volume:</b> ${short_float(vol)}\n"
                        f"🏅 <b>Neural Rank:</b> {rank}\n"
                        f"📈 <i>Data Source:</i> {source}\n\n"
                        f"🧠 Insight: {insight}\n\n"
                        f"🔗 <a href='{chart}'>View Chart / Buy</a>\n\n"
                        f"{neural_easter()}{BRAND_FOOTER}"
                    )
                    update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=False)
                    log_heartbeat(success=True)
                    return
                except:
                    log_heartbeat(success=False)

        if price:
            msg = (
                f"💹 <b>WENBNB Market Feed</b>\n\n"
                f"💎 <b>{html.escape(token)}</b>\n"
                f"💰 <b>Price:</b> ${short_float(price)}\n"
                f"📈 <i>Data Source:</i> {source}\n\n"
                f"🧠 Neural Pulse: {token} neural signal steady — confidence high ⚡\n\n"
                f"{neural_easter()}{BRAND_FOOTER}"
            )
            update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)
            log_heartbeat(success=True)
        else:
            update.message.reply_text(
                "⚠️ Neural Feed unavailable — system will auto-sync soon.\n\n" + BRAND_FOOTER,
                parse_mode="HTML"
            )
            log_heartbeat(success=False)

    except Exception as e:
        log_heartbeat(success=False)
        update.message.reply_text("⚙️ Neural Engine syncing... please retry soon.", parse_mode="HTML")

def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
    print("✅ Loaded plugin: plugins.price_tracker (v8.5.2 Easter Pulse Edition)")
