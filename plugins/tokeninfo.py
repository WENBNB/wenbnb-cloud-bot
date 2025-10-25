"""
WENBNB Neural Market Engine — v5.5-Pro Sync
────────────────────────────────────────────
Live token analytics powered by CoinGecko + DexScreener + Binance.
Includes AI-style Neural Rank & Insight generator for Telegram bot.

💫 Powered by WENBNB Neural Engine — Market Intelligence 24×7 ⚡
"""

from telegram.ext import CommandHandler
import requests, html, random, math, time

# === Branding ===
BRAND_FOOTER = "🚀 WENBNB Neural Engine — Market Intelligence 24×7 ⚡"
DEXSCREENER_SEARCH = "https://api.dexscreener.io/latest/dex/search?q={q}"
COINGECKO_SIMPLE = "https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd"
BINANCE_BNB = "https://api.binance.com/api/v3/ticker/price?symbol=BNBUSDT"

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

# === /price Command ===
def price_cmd(update, context):
    try:
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # 🧠 Token selection with fallback
        if context.args:
            token = context.args[0].upper()
        else:
            token = "WENBNB"
            update.message.reply_text(
                "💡 No token specified — showing default <b>WENBNB</b> market data.",
                parse_mode="HTML"
            )

        # --- Fetch BNB price from Binance ---
        try:
            bnb_data = requests.get(BINANCE_BNB, timeout=10).json()
            bnb_price = float(bnb_data.get("price", 0))
        except:
            bnb_price = 0

        token_name, token_symbol, token_price, dex_source = token, "", None, "CoinGecko"
        chain, liquidity, volume24, nmr = "Unknown", 0, 0, "N/A"

        # --- Try CoinGecko first ---
        try:
            cg_data = requests.get(COINGECKO_SIMPLE.format(id=token.lower()), timeout=10).json()
            token_price = cg_data.get(token.lower(), {}).get("usd")
        except:
            token_price = None

        # --- DexScreener fallback ---
        if not token_price or token_price in [None, "N/A", 0]:
            try:
                dex_data = requests.get(DEXSCREENER_SEARCH.format(q=token), timeout=10).json()
                pairs = dex_data.get("pairs", [])
                if pairs:
                    pair = pairs[0]
                    base = pair.get("baseToken", {})
                    token_name = base.get("name") or base.get("symbol") or token
                    token_symbol = base.get("symbol") or token
                    token_price = pair.get("priceUsd", "N/A")
                    dex_source = pair.get("dexId", "Unknown DEX").capitalize()
                    chain = detect_chain(dex_source)
                    liquidity = pair.get("liquidity", {}).get("usd", 0)
                    volume24 = pair.get("volume", {}).get("h24", 0)
                    nmr = neural_market_rank(liquidity, volume24)
                else:
                    token_price = "N/A"
            except:
                token_price = "N/A"

        # 🧠 Smart fallback — if all sources fail, give human-readable note
        if token_price in [None, "N/A", 0]:
            update.message.reply_text(
                f"⚠️ No live price data found for <b>{html.escape(token)}</b>.\n"
                f"Tip: Try using a verified token symbol or contract address.",
                parse_mode="HTML"
            )
            return

        # --- Neural AI Insight ---
        insights = [
            f"is <b>gaining traction</b> among traders 🔥",
            f"is <b>steady</b> with stable volume 💎",
            f"shows <b>momentum buildup</b> 🧠",
            f"is <b>cooling off</b> after volatility 🪶",
            f"is <b>heating up</b> on {chain} ⚡"
        ]
        insight = random.choice(insights)
        ts = time.strftime("%H:%M:%S", time.localtime())

        # --- Build Final Output ---
        msg = (
            f"📈 <b>Neural Market Update</b>\n\n"
            f"💎 <b>{html.escape(token_name)}</b>\n"
            f"🌐 <b>Chain:</b> {chain}\n"
            f"💰 <b>Price:</b> ${short_float(token_price)}\n"
            f"💧 <b>Liquidity:</b> ${short_float(liquidity)}\n"
            f"📊 <b>24h Volume:</b> ${short_float(volume24)}\n"
            f"🏅 <b>Neural Market Rank:</b> {nmr}\n"
            f"🔹 <i>Source:</i> {dex_source}\n\n"
            f"🧠 Insight: <b>{token_name}</b> {insight}\n\n"
            f"{BRAND_FOOTER}\n⏱️ {ts}"
        )

        update.message.reply_text(msg, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        print("Error in price_cmd:", e)
        update.message.reply_text("⚙️ Neural Engine syncing... please retry soon.", parse_mode="HTML")

# === Register ===
def register(dispatcher, core=None):
    dispatcher.add_handler(CommandHandler("price", price_cmd))
    print("✅ Loaded plugin: plugins.price_tracker (v5.5-Pro Sync)")
