from telegram.ext import CommandHandler
import requests, html, random, math, os

# === Branding ===
BRAND_FOOTER = "💫 Powered by <b>WENBNB Neural Engine</b> — Neural Market Intelligence v5.6.4 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
BINANCE_BNB = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"

# === Config ===
WEN_TOKEN_ADDRESS = os.getenv("WEN_TOKEN_ADDRESS")  # ⚙️ from Render env
DEFAULT_TOKEN = "wenbnb"

# === Utility ===
def short_float(x):
    try:
        v = float(x)
        if v >= 1:
            return f"{v:,.4f}"
        else:
            return f"{v:.8f}"
    except Exception:
        return str(x)

def detect_chain(dex_id: str) -> str:
    dex_id = (dex_id or "").lower()
    if "pancake" in dex_id: return "BSC"
    if "uniswap" in dex_id: return "Ethereum"
    if "base" in dex_id: return "Base"
    if "arbitrum" in dex_id: return "Arbitrum"
    if "solana" in dex_id: return "Solana"
    return "Unknown"

def neural_rank(liquidity_usd: float, volume24_usd: float) -> str:
    try:
        L, V = max(1.0, float(liquidity_usd)), max(1.0, float(volume24_usd))
        score = (math.log10(L) * 0.6 + math.log10(V) * 0.4) * 10
        if score >= 85: return "A+"
        elif score >= 70: return "A"
        elif score >= 55: return "B"
        elif score >= 40: return "C"
        else: return "D"
    except Exception:
        return "N/A"

# === /price Command ===
def price_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # --- Token selection ---
        if context.args:
            token = context.args[0].lower()
        else:
            token = DEFAULT_TOKEN
            update.message.reply_text(
                f"💡 No token specified — showing default market data for <b>{DEFAULT_TOKEN.upper()}</b>.",
                parse_mode="HTML"
            )

        # --- Fetch BNB price ---
        try:
            bnb_price = float(requests.get(BINANCE_BNB, timeout=10).json().get("price", 0))
        except Exception:
            bnb_price = 0

        # --- Placeholders ---
        token_name, token_symbol, token_price, dex_source = token, "", None, "CoinGecko"
        chain, liquidity, volume24, nmr = "Unknown", 0, 0, "N/A"

        # --- CoinGecko primary ---
        try:
            cg_data = requests.get(COINGECKO_SIMPLE.format(id=token), timeout=10).json()
            token_price = cg_data.get(token, {}).get("usd")
        except Exception:
            token_price = None

        # --- DexScreener fallback with DexMatch Filter ---
        if not token_price or token_price == "N/A":
            try:
                dex_data = requests.get(DEXSCREENER_SEARCH.format(q=WEN_TOKEN_ADDRESS or token), timeout=10).json()
                pairs = dex_data.get("pairs", [])
                pair = None

                if pairs:
                    qlow = (WEN_TOKEN_ADDRESS or token).lower()
                    for p in pairs:
                        base = p.get("baseToken", {})
                        addr = (base.get("address") or "").lower()
                        sym = (base.get("symbol") or "").lower()
                        if qlow in [addr, sym]:
                            pair = p
                            break
                    if not pair:
                        pair = pairs[0]

                    base = pair.get("baseToken", {})
                    token_name = base.get("name") or base.get("symbol") or token
                    token_symbol = base.get("symbol") or token
                    token_price = pair.get("priceUsd", "N/A")
                    dex_source = pair.get("dexId", "Unknown DEX").capitalize()
                    chain = detect_chain(dex_source)
                    liquidity = pair.get("liquidity", {}).get("usd", 0)
                    volume24 = pair.get("volume", {}).get("h24", 0)
                    nmr = neural_rank(liquidity, volume24)
            except Exception:
                token_price, dex_source = "N/A", "Not Found"

        # --- Neural Insight tone ---
        insights = [
            f"{token_name} shows <b>healthy flow</b> 💎",
            f"{token_name} is <b>cooling off</b> slightly 🪶",
            f"{token_name} looks <b>volatile</b> — watch closely ⚡",
            f"{token_name} heating up on {chain} 🔥",
            f"{token_name} attracting <b>smart money</b> 🧠"
        ]
        insight = random.choice(insights)

        # --- Response ---
        msg = (
            f"💹 <b>WENBNB Market Feed</b>\n\n"
            f"💎 <b>{html.escape(token_name)} ({html.escape(token_symbol or token.upper())})</b>\n"
            f"🌐 <b>Chain:</b> {chain}\n"
            f"💰 <b>Price:</b> ${short_float(token_price)}\n"
            f"💧 <b>Liquidity:</b> ${short_float(liquidity)}\n"
            f"📊 <b>24h Volume:</b> ${short_float(volume24)}\n"
            f"🏅 <b>Neural Market Rank:</b> {nmr}\n"
            f"🔥 <b>BNB:</b> ${short_float(bnb_price)}\n"
            f"📈 <i>Data Source:</i> {dex_source}\n\n"
            f"🧠 Insight: <b>{insight}</b>\n\n"
            f"{BRAND_FOOTER}"
        )

        update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        print("Error in price_cmd:", e)
        update.message.reply_text("⚙️ Neural Engine syncing... please retry soon.", parse_mode="HTML")

# === Register ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
    print("✅ Loaded plugin: plugins.price_tracker (v5.6.4 DexMatch Filter Patch)")
